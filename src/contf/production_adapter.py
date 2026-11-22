"""Offline, provider-neutral handoff for real generated shot media.

No provider calls, uploads, billing or publishing. An external producer supplies
owned/licensed media and a JSON receipt; the adapter validates and records it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from contf.production_qa import inspect
from contf.shot_pipeline import compile_plan, validate_media_container

RECEIPT_VERSION = "0.2.0"
APPROVAL_VERSION = "0.1.0"
PRODUCER_FIELDS = (
    "receipt_version", "shot_id", "fingerprint", "producer", "model_version",
    "media_path", "source_rights", "paid_generation", "human_spend_approval", "cost",
)
REQUIRED_REVIEW = (
    "character_identity", "costume_and_prop_continuity",
    "actual_character_motion", "dialogue_intelligibility", "lip_sync",
    "shot_transitions", "rights_and_originality",
)


def _safe_media(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("media_path must be relative to media root")
    root = root.resolve()
    media = (root / relative).resolve()
    if root not in media.parents or not media.is_file():
        raise ValueError("media_path escapes root or is missing")
    validate_media_container(root / relative)
    return media


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def production_fingerprint(project_id: str, cache_key: str) -> str:
    return hashlib.sha256(json.dumps([project_id, cache_key], ensure_ascii=False).encode()).hexdigest()


def receipt_from_report(report: dict) -> dict:
    return {key: report[key] for key in PRODUCER_FIELDS if key in report}


def approval_errors(approval: object, receipt: dict, media_sha256: str | None) -> list[str]:
    if not isinstance(approval, dict):
        return ["approval must be an object"]
    errors = []
    if approval.get("approval_version") != APPROVAL_VERSION:
        errors.append("approval_version invalid")
    for key, expected in (("shot_id", receipt.get("shot_id")),
                          ("fingerprint", receipt.get("fingerprint")),
                          ("media_sha256", media_sha256)):
        if not isinstance(expected, str) or not expected or approval.get(key) != expected:
            errors.append("approval " + key + " mismatch")
    reviewer = approval.get("reviewer")
    producer = receipt.get("producer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        errors.append("approval reviewer must be a non-empty string")
    elif isinstance(producer, str) and "".join(reviewer.split()).casefold() == "".join(producer.split()).casefold():
        errors.append("approval reviewer must differ from producer")
    manual = approval.get("manual_review")
    if not isinstance(manual, dict) or any(manual.get(gate) not in ("pass", "fail", "pending") for gate in REQUIRED_REVIEW):
        errors.append("approval manual_review gates must be pass/fail/pending")
    return errors


def ingest(project: dict, receipt: dict, root: Path, *, approval: object = None, width: int = 640,
           height: int = 360, fps: int = 12) -> dict:
    """Produce an auditable shot candidate; never silently mark accepted."""
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be an object")
    errors = []
    if "reviewer" in receipt or "manual_review" in receipt:
        errors.append("approval fields belong in a separate approval record")
    plan = compile_plan(project, root, width=width, height=height, fps=fps)
    expected_key = next((production_fingerprint(project["project_id"], s["cache_key"]) for s in plan["shots"]
                         if s["shot_id"] == receipt.get("shot_id")), None)
    if not receipt.get("fingerprint") or receipt.get("fingerprint") != expected_key:
        errors.append("fingerprint missing or does not match current shot plan")
    cost = receipt.get("cost")
    if cost is not None:
        if (not isinstance(cost, dict)
                or isinstance(cost.get("amount"), bool)
                or not isinstance(cost.get("amount"), (int, float))
                or not math.isfinite(cost["amount"]) or cost["amount"] < 0
                or not isinstance(cost.get("currency"), str)
                or len(cost["currency"]) != 3 or not cost["currency"].isupper()
                or not isinstance(cost.get("source"), str) or not cost["source"].strip()):
            errors.append("cost must contain nonnegative finite amount, currency and source")
            cost = None
    shots = project.get("shots", [])
    if project.get("rights") != "owned-original":
        errors.append("project rights not approved for this pilot")
    if receipt.get("receipt_version") != RECEIPT_VERSION:
        errors.append("receipt_version invalid")
    shot_id = receipt.get("shot_id")
    shot = next((s for s in shots if s.get("shot_id") == shot_id), None)
    if shot is None:
        errors.append("shot_id not found in project")
    if receipt.get("source_rights") not in ("owned", "licensed"):
        errors.append("source_rights missing")
    if not isinstance(receipt.get("producer"), str) or not receipt["producer"].strip():
        errors.append("producer missing")
    if not isinstance(receipt.get("model_version"), str) or not receipt["model_version"].strip():
        errors.append("model_version missing")
    if receipt.get("paid_generation") is True and receipt.get("human_spend_approval") is not True:
        errors.append("paid generation without documented human approval")
    media = None
    try:
        media = _safe_media(root, receipt.get("media_path"))
    except (ValueError, TypeError) as exc:
        errors.append(str(exc))
    preflight = None
    if media:
        # A single shot may be shorter than the 15-25s multi-shot pilot.
        expected = shot.get("duration_s") if shot else None
        if isinstance(expected, (int, float)) and not isinstance(expected, bool) and math.isfinite(expected) and expected > 0:
            preflight = inspect(media, min_seconds=max(0.1, expected - 0.5),
                                max_seconds=expected + 0.5)
        else:
            errors.append("invalid expected shot duration")
        if preflight and not preflight["passed"]:
            errors.extend(preflight["errors"])
    media_sha256 = _sha256(media) if media else None
    approval_issues = approval_errors(approval, receipt, media_sha256) if approval is not None else []
    errors.extend(approval_issues)
    approval_data = approval if isinstance(approval, dict) else {}
    manual = approval_data.get("manual_review")
    manual = manual if isinstance(manual, dict) else {}
    reviewer = approval_data.get("reviewer")
    manual_pass = all(manual.get(gate) == "pass" for gate in REQUIRED_REVIEW)
    accepted = not errors and approval is not None and manual_pass
    return {
        "receipt_version": RECEIPT_VERSION,
        "shot_id": shot_id,
        "fingerprint": receipt.get("fingerprint"),
        "cost": cost,
        "producer": receipt.get("producer"),
        "model_version": receipt.get("model_version"),
        "media_path": receipt.get("media_path"),
        "source_rights": receipt.get("source_rights"),
        "paid_generation": receipt.get("paid_generation"),
        "human_spend_approval": receipt.get("human_spend_approval"),
        "media_sha256": media_sha256,
        "preflight": preflight,
        "manual_review": {gate: manual.get(gate, "pending") for gate in REQUIRED_REVIEW},
        "reviewer": reviewer,
        "approval": approval if approval is not None and not approval_issues else None,
        "accepted": accepted,
        "status": "accepted" if accepted else "blocked" if errors else "pending-human-review",
        "errors": errors,
        "published": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline producer receipt ingestion")
    parser.add_argument("project", type=Path)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--approval", type=Path)
    args = parser.parse_args()
    report = ingest(json.loads(args.project.read_text(encoding="utf-8")),
                    json.loads(args.receipt.read_text(encoding="utf-8")), args.root,
                    approval=json.loads(args.approval.read_text(encoding="utf-8")) if args.approval else None)
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    return 0 if not report["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

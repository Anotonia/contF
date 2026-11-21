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
from contf.shot_pipeline import compile_plan

RECEIPT_VERSION = "0.1.0"
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
    return media


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ingest(project: dict, receipt: dict, root: Path, *, width: int = 640,
           height: int = 360, fps: int = 12) -> dict:
    """Produce an auditable shot candidate; never silently mark accepted."""
    if not isinstance(receipt, dict):
        raise ValueError("receipt must be an object")
    errors = []
    plan = compile_plan(project, root, width=width, height=height, fps=fps)
    expected_key = next((s["cache_key"] for s in plan["shots"]
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
    manual = receipt.get("manual_review", {})
    if not isinstance(manual, dict):
        manual = {}
        errors.append("manual_review must be an object")
    if any(manual.get(gate) not in ("pass", "fail", "pending") for gate in REQUIRED_REVIEW):
        errors.append("all manual_review gates must be pass/fail/pending")
    if receipt.get("reviewer") and not isinstance(receipt["reviewer"], str):
        errors.append("reviewer must be a string")
    manual_pass = all(manual.get(gate) == "pass" for gate in REQUIRED_REVIEW)
    # A reviewer must be explicitly named before an accepted status is possible.
    accepted = not errors and manual_pass and bool((receipt.get("reviewer") or "").strip())
    return {
        "receipt_version": RECEIPT_VERSION,
        "shot_id": shot_id,
        "fingerprint": receipt.get("fingerprint"),
        "cost": cost,
        "producer": receipt.get("producer"),
        "model_version": receipt.get("model_version"),
        "media_path": receipt.get("media_path"),
        "source_rights": receipt.get("source_rights"),
        "media_sha256": _sha256(media) if media else None,
        "preflight": preflight,
        "manual_review": {gate: manual.get(gate, "pending") for gate in REQUIRED_REVIEW},
        "reviewer": receipt.get("reviewer"),
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
    args = parser.parse_args()
    report = ingest(json.loads(args.project.read_text(encoding="utf-8")),
                    json.loads(args.receipt.read_text(encoding="utf-8")), args.root)
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    print(data, end="")
    return 0 if not report["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

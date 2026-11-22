"""Local shot job orchestration: deterministic planning, receipts and selective retry.

Provider execution is deliberately external. No credentials, paid requests or
publication; a provider worker may consume an approved job contract separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from contf.production_adapter import RECEIPT_VERSION, REQUIRED_REVIEW, approval_errors, ingest, production_fingerprint
from contf.shot_pipeline import compile_plan

VERSION = "0.2.0"


def build_jobs(project: dict, root: Path, *, width: int = 640,
               height: int = 360, fps: int = 12) -> dict:
    plan = compile_plan(project, root, width=width, height=height, fps=fps)
    jobs = []
    for source, item in zip(project["shots"], plan["shots"]):
        fingerprint = production_fingerprint(project["project_id"], item["cache_key"])
        jobs.append({
            "job_id": item["shot_id"] + "-" + fingerprint[:16],
            "shot_id": item["shot_id"],
            "fingerprint": fingerprint,
            "duration_s": item["duration_s"],
            "beat": item["beat"],
            "prompt": {
                "title": source["title"], "action": source["action"],
                "dialogue": source["dialogue"],
            },
            "state": "awaiting-human-approval",
            "attempt": 0,
            "media_receipt": None,
        })
    return {"version": VERSION, "project_id": project["project_id"],
            "plan_settings": {"width": width, "height": height, "fps": fps},
            "rights": project["rights"], "jobs": jobs,
            "automatic_provider_execution": False,
            "is_final_video": False}


def _verified_receipt(receipt: dict) -> bool:
    """Only a complete local ingestion report can promote a shot to accepted."""
    return (receipt.get("accepted") is True
            and receipt.get("receipt_version") == RECEIPT_VERSION
            and isinstance(receipt.get("producer"), str)
            and bool(receipt["producer"].strip())
            and receipt.get("status") == "accepted"
            and receipt.get("errors") == []
            and isinstance(receipt.get("media_sha256"), str)
            and len(receipt["media_sha256"]) == 64
            and isinstance(receipt.get("reviewer"), str)
            and bool(receipt["reviewer"].strip())
            and isinstance(receipt.get("approval"), dict)
            and not approval_errors(receipt["approval"], receipt, receipt.get("media_sha256"))
            and receipt["approval"].get("reviewer") == receipt["reviewer"]
            and isinstance(receipt.get("preflight"), dict)
            and receipt["preflight"].get("passed") is True
            and isinstance(receipt.get("manual_review"), dict)
            and all(receipt["manual_review"].get(k) == "pass"
                    and receipt["approval"]["manual_review"].get(k) == "pass" for k in REQUIRED_REVIEW))


def reconcile(queue: dict, previous: dict | None = None,
              receipts: dict | None = None) -> dict:
    """Retain accepted, fingerprint-matched results only; no stale media reuse."""
    if previous and previous.get("project_id") != queue["project_id"]:
        previous = None
    previous_jobs = {j["shot_id"]: j for j in (previous or {}).get("jobs", [])}
    receipts = receipts or {}
    jobs = []
    rejected_receipts = []
    for planned in queue["jobs"]:
        job = dict(planned)
        old = previous_jobs.get(job["shot_id"])
        if old and old.get("fingerprint") == job["fingerprint"]:
            for key in ("state", "attempt", "media_receipt"):
                job[key] = old.get(key, job[key])
        # Previous acceptance is not authoritative without the linked QA report.
        if job["state"] == "accepted" and (not _verified_receipt(job.get("media_receipt") or {})
                or job["media_receipt"].get("fingerprint") != job["fingerprint"]):
            job["state"] = "pending-human-review"
        receipt = receipts.get(job["shot_id"])
        if receipt is not None:
            if receipt.get("fingerprint") != job["fingerprint"]:
                rejected_receipts.append({"shot_id": job["shot_id"],
                                          "reason": "stale-fingerprint", "receipt": receipt})
                if job["state"] != "accepted":
                    job["state"] = "blocked-stale-receipt"
                    job["media_receipt"] = None
            else:
                job["media_receipt"] = receipt
                job["state"] = ("accepted" if _verified_receipt(receipt)
                                else "blocked" if receipt.get("errors")
                                else "pending-human-review")
        jobs.append(job)
    return {**queue, "jobs": jobs, "rejected_receipts": rejected_receipts}


def audit(queue: dict) -> dict:
    """Summarize current shot evidence; never combine currencies or impute cost."""
    shots = []
    counts = {}
    sums = {}
    unknown = 0
    not_produced = 0
    accepted_seconds = 0
    for job in queue["jobs"]:
        receipt = job.get("media_receipt") or {}
        cost = receipt.get("cost")
        counts[job["state"]] = counts.get(job["state"], 0) + 1
        if job.get("media_receipt") is None:
            not_produced += 1
        elif cost is None:
            unknown += 1
        else:
            currency = cost["currency"]
            sums[currency] = sums.get(currency, 0) + cost["amount"]
        if job["state"] == "accepted":
            accepted_seconds += job["duration_s"]
        shots.append({
            "shot_id": job["shot_id"], "fingerprint": job["fingerprint"],
            "state": job["state"], "attempt": job["attempt"],
            **{key: receipt.get(key) for key in
               ("producer", "model_version", "media_sha256", "reviewer", "cost")},
        })
    currency = next(iter(sums)) if len(sums) == 1 else None
    known_sum = sums[currency] if currency else None
    return {
        "schema_version": VERSION, "project_id": queue["project_id"],
        "shots": shots, "is_final_video": False, "published": False,
        "every_shot_accepted": bool(shots) and all(s["state"] == "accepted" for s in shots),
        "totals": {"counts_by_state": counts, "known_cost_sum": known_sum,
                   "currency": currency, "known_cost_by_currency": sums,
                   "unknown_cost_count": unknown,
                   "not_produced_count": not_produced,
                   "accepted_seconds": accepted_seconds,
                   "cost_per_accepted_minute": (
                       known_sum / (accepted_seconds / 60)
                       if currency and not unknown and accepted_seconds > 0 else None)},
    }


def prepare_retry(queue: dict, shot_id: str, *, human_approved: bool = False) -> dict:
    """Only an explicitly approved, non-accepted shot can be queued for rerun."""
    jobs = [dict(job) for job in queue["jobs"]]
    matching = [job for job in jobs if job["shot_id"] == shot_id]
    if len(matching) != 1:
        raise ValueError("shot_id not found or duplicated")
    job = matching[0]
    if job["state"] == "accepted":
        raise ValueError("accepted shot cannot be retried without new plan")
    if not human_approved:
        raise ValueError("human approval required before retry")
    job["attempt"] = int(job.get("attempt", 0)) + 1
    job["state"] = "ready-for-external-provider"
    job["media_receipt"] = None
    return {**queue, "jobs": jobs}


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline contF shot task orchestrator")
    parser.add_argument("command", choices=("plan", "reconcile", "retry", "ingest", "apply"))
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--receipt", type=Path, action="append", default=[])
    parser.add_argument("--approval", type=Path, action="append", default=[])
    parser.add_argument("--shot-id")
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--fps", type=int)
    args = parser.parse_args()
    try:
        project = json.loads(args.project.read_text(encoding="utf-8"))
        if args.approval and (args.command not in ("ingest", "apply") or len(args.approval) != 1):
            raise ValueError("--approval requires ingest/apply and at most one approval")
        approval = json.loads(args.approval[0].read_text(encoding="utf-8")) if args.approval else None
        receipt_errors = []
        queue = json.loads(args.queue.read_text(encoding="utf-8")) if args.queue else None
        if queue is not None and queue.get("project_id") != project["project_id"]:
            queue = None
        defaults = {"width": 640, "height": 360, "fps": 12}
        stored = queue.get("plan_settings", defaults) if queue is not None else defaults
        settings = {}
        for key in defaults:
            explicit = getattr(args, key)
            if queue is not None and explicit is not None and explicit != stored[key]:
                raise ValueError(f"--{key} conflicts with queue plan_settings")
            settings[key] = stored[key] if explicit is None else explicit
        if args.command == "plan":
            result = build_jobs(project, args.root, **settings)
        elif args.command in ("ingest", "apply"):
            if not args.receipt:
                raise ValueError("--receipt required")
            if len(args.receipt) != 1:
                raise ValueError(f"{args.command} requires exactly one --receipt")
            receipt = json.loads(args.receipt[0].read_text(encoding="utf-8"))
            if args.command == "ingest":
                result = ingest(project, receipt, args.root, approval=approval, **settings)
                receipt_errors = result["errors"]
            else:
                if not args.queue:
                    raise ValueError("--queue required for apply")
                previous = queue
                planned = build_jobs(project, args.root, **settings)
                matching = [j for j in planned["jobs"] if j["shot_id"] == receipt["shot_id"]]
                if len(matching) != 1:
                    raise ValueError("receipt shot not found in current plan")
                receipt.setdefault("fingerprint", matching[0]["fingerprint"])
                report = ingest(project, receipt, args.root, approval=approval, **settings)
                receipt_errors = report["errors"]
                result = reconcile(planned, previous, {report["shot_id"]: report})
        else:
            if not args.queue:
                raise ValueError("--queue required")
            if args.command == "reconcile":
                reports = [json.loads(p.read_text(encoding="utf-8")) for p in args.receipt]
                result = reconcile(build_jobs(project, args.root, **settings), queue,
                                   {r["shot_id"]: r for r in reports})
            else:
                if queue is None:
                    raise ValueError("retry requires a queue for the current project")
                if not args.shot_id:
                    raise ValueError("--shot-id required")
                result = prepare_retry(queue, args.shot_id,
                                       human_approved=args.human_approved)
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 2 if receipt_errors else 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

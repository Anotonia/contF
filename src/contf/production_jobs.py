"""Local shot job orchestration: deterministic planning, receipts and selective retry.

Provider execution is deliberately external. No credentials, paid requests or
publication; a provider worker may consume an approved job contract separately.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from contf.production_adapter import REQUIRED_REVIEW, ingest
from contf.shot_pipeline import compile_plan

VERSION = "0.1.0"


def build_jobs(project: dict, root: Path, *, width: int = 640,
               height: int = 360, fps: int = 12) -> dict:
    plan = compile_plan(project, root, width=width, height=height, fps=fps)
    jobs = []
    for source, item in zip(project["shots"], plan["shots"]):
        jobs.append({
            "job_id": item["shot_id"] + "-" + item["cache_key"][:16],
            "shot_id": item["shot_id"],
            "fingerprint": item["cache_key"],
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
            "rights": project["rights"], "jobs": jobs,
            "automatic_provider_execution": False,
            "is_final_video": False}


def _verified_receipt(receipt: dict) -> bool:
    """Only a complete local ingestion report can promote a shot to accepted."""
    return (receipt.get("accepted") is True
            and receipt.get("status") == "accepted"
            and receipt.get("errors") == []
            and isinstance(receipt.get("media_sha256"), str)
            and len(receipt["media_sha256"]) == 64
            and isinstance(receipt.get("reviewer"), str)
            and bool(receipt["reviewer"].strip())
            and isinstance(receipt.get("preflight"), dict)
            and receipt["preflight"].get("passed") is True
            and isinstance(receipt.get("manual_review"), dict)
            and all(receipt["manual_review"].get(k) == "pass" for k in REQUIRED_REVIEW))


def reconcile(queue: dict, previous: dict | None = None,
              receipts: dict | None = None) -> dict:
    """Retain accepted, fingerprint-matched results only; no stale media reuse."""
    previous_jobs = {j["shot_id"]: j for j in (previous or {}).get("jobs", [])}
    receipts = receipts or {}
    jobs = []
    for planned in queue["jobs"]:
        job = dict(planned)
        old = previous_jobs.get(job["shot_id"])
        if old and old.get("fingerprint") == job["fingerprint"]:
            for key in ("state", "attempt", "media_receipt"):
                job[key] = old.get(key, job[key])
        # Previous acceptance is not authoritative without the linked QA report.
        if job["state"] == "accepted" and not _verified_receipt(job.get("media_receipt") or {}):
            job["state"] = "pending-human-review"
        receipt = receipts.get(job["shot_id"])
        if receipt is not None:
            if receipt.get("fingerprint") != job["fingerprint"]:
                job["state"] = "blocked-stale-receipt"
                job["media_receipt"] = None
            else:
                job["media_receipt"] = receipt
                job["state"] = ("accepted" if _verified_receipt(receipt)
                                else "blocked" if receipt.get("errors")
                                else "pending-human-review")
        jobs.append(job)
    return {**queue, "jobs": jobs}


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
    parser.add_argument("command", choices=("plan", "reconcile", "retry", "ingest"))
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--shot-id")
    parser.add_argument("--human-approved", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        project = json.loads(args.project.read_text(encoding="utf-8"))
        if args.command == "plan":
            result = build_jobs(project, args.root)
        elif args.command == "ingest":
            if not args.receipt:
                raise ValueError("--receipt required")
            receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
            result = ingest(project, receipt, args.root)
        else:
            if not args.queue:
                raise ValueError("--queue required")
            queue = json.loads(args.queue.read_text(encoding="utf-8"))
            if args.command == "reconcile":
                result = reconcile(build_jobs(project, args.root), queue)
            else:
                if not args.shot_id:
                    raise ValueError("--shot-id required")
                result = prepare_retry(queue, args.shot_id,
                                       human_approved=args.human_approved)
        output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Local ShotSpec-to-audit storyboard orchestration; no provider execution."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from contf.production_adapter import ingest, receipt_from_report
from contf.production_jobs import audit, build_jobs, reconcile
from contf.shot_pipeline import render_preview, validate_preview_destinations


def run_slice(project: dict, root: Path, out: Path, *, receipts: list[Path] = (),
              approvals: list[Path] = (),
              no_render: bool = False, width: int = 640, height: int = 360,
              fps: int = 12) -> dict:
    settings = dict(width=width, height=height, fps=fps)
    planned = build_jobs(project, root, **settings)
    previous_path = out / "queue.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else None
    if previous and previous.get("project_id") != project["project_id"]:
        previous = None
    revalidation_errors = {}
    for job in (previous or {}).get("jobs", []):
        if job["state"] == "accepted":
            old = job.get("media_receipt") or {}
            checked = ingest(project, receipt_from_report(old), root, approval=old.get("approval"), **settings)
            if not checked["accepted"] or checked["media_sha256"] != old.get("media_sha256"):
                job["state"] = "blocked"
                job["media_receipt"] = checked
                revalidation_errors[job["shot_id"]] = checked["errors"]
    approval_records = {}
    for path in approvals:
        record = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(record, dict) or not isinstance(record.get("shot_id"), str):
            raise ValueError("approval must be an object with shot_id")
        if record["shot_id"] in approval_records:
            raise ValueError("duplicate approval shot_id")
        approval_records[record["shot_id"]] = record
    reports = {}
    ids = {j["shot_id"] for j in planned["jobs"]}
    raw_receipts = {}
    for path in receipts:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("shot_id") not in ids or raw["shot_id"] in raw_receipts:
            raise ValueError("receipt shot_id unknown or duplicated")
        raw_receipts[raw["shot_id"]] = raw
    queued = {j["shot_id"]: j.get("media_receipt") for j in (previous or {}).get("jobs", [])}
    for shot_id in approval_records:
        if shot_id not in raw_receipts:
            if shot_id not in ids or not queued.get(shot_id):
                raise ValueError("approval has no supplied or queued receipt")
            raw_receipts[shot_id] = receipt_from_report(queued[shot_id])
    for shot_id, raw in raw_receipts.items():
        report = ingest(project, raw, root, approval=approval_records.get(shot_id), **settings)
        reports[report["shot_id"]] = report
    queue = reconcile(planned, previous, reports)
    summary = audit(queue)
    preview = copy.deepcopy(project)
    for shot, job in zip(preview["shots"], queue["jobs"]):
        if job["state"] == "accepted":
            receipt = job["media_receipt"]
            shot["source_media"] = receipt["media_path"]
            shot["source_rights"] = "owned" if receipt.get("source_rights") == "owned" else "licensed"
            shot["review_status"] = "accepted"
    evidence = [*reports.values(), *(j.get("media_receipt") or {} for j in queue["jobs"])]
    media_paths = [r["media_path"] for r in evidence if r.get("media_sha256") and r.get("media_path")]
    validate_preview_destinations(project, root, out / "preview.mp4", media_paths=media_paths)
    validate_preview_destinations(preview, root, out / "preview.mp4")
    out.mkdir(parents=True, exist_ok=True)
    for name, data in (("queue.json", queue), ("audit.json", summary)):
        (out / name).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    result = {"queue": str(out / "queue.json"), "audit": summary,
              "rejected_receipts": queue["rejected_receipts"],
              "errors": [e for shot_id, errors in revalidation_errors.items() if shot_id not in reports for e in errors]
                        + [e for r in reports.values() for e in r["errors"]]}
    if not no_render:
        result["render"] = render_preview(preview, root, out / "preview.mp4", out / "cache", **settings)
    return result

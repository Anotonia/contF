"""Local ShotSpec-to-audit storyboard orchestration; no provider execution."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from contf.production_adapter import ingest
from contf.production_jobs import audit, build_jobs, reconcile
from contf.shot_pipeline import render_preview, validate_preview_destinations


def run_slice(project: dict, root: Path, out: Path, *, receipts: list[Path] = (),
              no_render: bool = False, width: int = 640, height: int = 360,
              fps: int = 12) -> dict:
    settings = dict(width=width, height=height, fps=fps)
    planned = build_jobs(project, root, **settings)
    previous_path = out / "queue.json"
    previous = json.loads(previous_path.read_text(encoding="utf-8")) if previous_path.exists() else None
    if previous and previous.get("project_id") != project["project_id"]:
        previous = None
    for job in (previous or {}).get("jobs", []):
        if job["state"] == "accepted":
            old = job.get("media_receipt") or {}
            checked = ingest(project, old, root, **settings)
            if checked["errors"] or checked["media_sha256"] != old.get("media_sha256"):
                job["state"] = "blocked"
    reports = {}
    ids = {j["shot_id"] for j in planned["jobs"]}
    for path in receipts:
        raw = json.loads(path.read_text(encoding="utf-8"))
        report = ingest(project, raw, root, **settings)
        if report["shot_id"] not in ids or report["shot_id"] in reports:
            raise ValueError("receipt shot_id unknown or duplicated")
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
              "errors": [e for r in reports.values() for e in r["errors"]]}
    if not no_render:
        result["render"] = render_preview(preview, root, out / "preview.mp4", out / "cache", **settings)
    return result

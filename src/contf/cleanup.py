"""Validate optional reference-cleanup metadata; never process or upload media."""

from __future__ import annotations

import math
from typing import Any, Mapping


RIGHTS = {"unknown", "owned", "licensed", "public-domain"}
TOOLS = {"watermarkout", "vidproc", "media-io", "reclip-api", "none"}


def validate_cleanup_manifest(doc: Mapping[str, Any]) -> list[str]:
    """Return human-readable errors for a contF v0.1.0 cleanup preflight."""
    errors: list[str] = []
    if doc.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    if not isinstance(doc.get("reference_id"), str) or not doc["reference_id"].strip():
        errors.append("reference_id is required")

    source = doc.get("source_file")
    if not isinstance(source, dict):
        return errors + ["source_file must be an object"]
    duration = source.get("duration_seconds")
    if not _finite(duration) or duration <= 0:
        errors.append("source duration must be positive and finite")
    if not isinstance(source.get("name"), str) or not source["name"].strip():
        errors.append("source_file.name is required")

    rights = doc.get("rights")
    if not isinstance(rights, dict) or not _in_enum(rights.get("status"), RIGHTS):
        errors.append("rights.status is missing or invalid")
        rights = {}
    if not isinstance(rights.get("attested"), bool):
        errors.append("rights.attested must be boolean")

    processor = doc.get("processor")
    if not isinstance(processor, dict) or not _in_enum(processor.get("tool_id"), TOOLS):
        errors.append("processor.tool_id is missing or invalid")
        processor = {}
    state = processor.get("execution_status")
    if not _in_enum(state, {"not-run", "completed", "failed"}):
        errors.append("processor.execution_status is invalid")
    authorized = rights.get("status") in RIGHTS - {"unknown"} and rights.get("attested") is True
    if state == "completed" and not authorized:
        errors.append("completed cleanup requires verified rights attestation")
    output_name = processor.get("output_file_name")
    if state == "completed" and (not isinstance(output_name, str) or not output_name.strip()):
        errors.append("completed cleanup requires output_file_name")
    if state == "not-run" and output_name is not None:
        errors.append("not-run cleanup cannot claim an output file")

    regions = doc.get("regions")
    if not isinstance(regions, list):
        return errors + ["regions must be an array"]
    for idx, region in enumerate(regions):
        if not isinstance(region, dict):
            errors.append(f"regions[{idx}] must be an object")
            continue
        vals = [region.get(k) for k in ("x_pct", "y_pct", "width_pct", "height_pct", "start_s", "end_s")]
        if not all(_finite(v) for v in vals):
            errors.append(f"regions[{idx}] contains non-finite or missing numbers")
            continue
        x, y, w, h, start, end = vals
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > 100.00001 or y + h > 100.00001:
            errors.append(f"regions[{idx}] exceeds video frame")
        if start < 0 or end <= start or (_finite(duration) and end > duration + 0.001):
            errors.append(f"regions[{idx}] has invalid time range")
    return errors


def _in_enum(value: Any, options: set[str]) -> bool:
    return isinstance(value, str) and value in options


def _finite(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False

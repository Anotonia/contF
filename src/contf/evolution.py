"""Small, conservative analytics kernel.

All input is owner-authorized observation data. This module never calls a
network API, changes an experiment, or promotes a skill.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Selection:
    observation: dict[str, Any] | None
    note: str


def observation_at_age(
    observations: list[dict[str, Any]],
    experiment_id: str,
    variant_id: str,
    target_hours: float = 72.0,
    tolerance_hours: float = 12.0,
) -> Selection:
    """Closest age-matched observation, never nearest arbitrary lifetime data."""
    candidates = [
        row for row in observations
        if row.get("experiment_id") == experiment_id
        and row.get("variant_id") == variant_id
        and isinstance(row.get("age_hours"), (int, float))
        and abs(float(row["age_hours"]) - target_hours) <= tolerance_hours
    ]
    if not candidates:
        return Selection(None, f"No observation within {tolerance_hours:g}h of {target_hours:g}h")
    chosen = min(
        candidates,
        key=lambda row: (
            abs(float(row["age_hours"]) - target_hours),
            str(row.get("observed_at", "")),
        ),
    )
    return Selection(chosen, f"Observed at {chosen['age_hours']}h (target {target_hours:g}h)")


def numeric_metric(row: dict[str, Any], field: str) -> float | None:
    value = row.get("metrics", {}).get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def ratio_per_thousand(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round(numerator * 1000.0 / denominator, 3)


def describe_variant(
    variant: dict[str, Any],
    selection: Selection,
    fmt: str,
) -> dict[str, Any]:
    base = {"variant_id": variant["id"], "change": variant.get("change", ""),
            "selected_age_hours": None, "status": "missing-observation",
            "metrics": {}, "proxies": {}, "warnings": [selection.note]}
    row = selection.observation
    if row is None:
        return base
    warnings: list[str] = []
    if row.get("format") != fmt:
        warnings.append("Format mismatch: observation excluded")
        base["warnings"] = warnings
        return base
    raw = row.get("metrics", {})
    if not isinstance(raw, dict):
        warnings.append("Invalid metrics object")
        base["warnings"] = warnings
        return base
    fields = (
        ("engaged_views", "views", "shown_in_feed", "stayed_to_watch_pct",
         "avg_view_duration_s", "avg_view_percentage", "subscribers_gained")
        if fmt == "short" else
        ("views", "impressions", "ctr_pct", "watch_minutes",
         "avg_view_duration_s", "avg_view_percentage", "subscribers_gained")
    )
    metrics = {field: numeric_metric(row, field) for field in fields}
    if fmt == "short":
        denominator = metrics.get("engaged_views")
        if denominator is None:
            warnings.append("Shorts engaged_views unavailable; raw views are not equivalent")
    else:
        denominator = metrics.get("views")
    subs_per_1k = ratio_per_thousand(metrics.get("subscribers_gained"), denominator)
    if subs_per_1k is not None:
        warnings.append("Video-scoped subscribers may omit subscriptions from other surfaces")
    if row.get("source") not in ("youtube_analytics_api", "youtube_studio_export"):
        warnings.append("Manual or synthetic source: not verified channel analytics")
    base.update({
        "status": "observed",
        "selected_age_hours": row["age_hours"],
        "source": row.get("source"),
        "metrics": metrics,
        "proxies": {"subscribers_gained_per_1k_qualified_views": subs_per_1k},
        "warnings": warnings,
    })
    return base


def review(
    experiments: list[dict[str, Any]],
    observations: list[dict[str, Any]],
    *,
    target_hours: float = 72.0,
    tolerance_hours: float = 12.0,
    min_comparable_variants: int = 5,
) -> dict[str, Any]:
    """Generate read-only descriptive review. Never auto-declare a causal winner."""
    if target_hours < 0 or tolerance_hours < 0 or min_comparable_variants < 2:
        raise ValueError("Invalid review configuration")
    out = {"schema_version": "0.1.0", "review_target_hours": target_hours,
           "experiments": [], "global_warnings": [
               "This is observational descriptive analysis, not causal proof.",
               "No skill promotion, publishing or spending is performed.",
           ]}
    for experiment in experiments:
        fmt = experiment.get("format")
        if fmt not in ("short", "long"):
            raise ValueError(f"Unsupported format for {experiment.get('id')}: {fmt}")
        variants = []
        for variant in experiment.get("variants", []):
            selection = observation_at_age(
                observations, experiment["id"], variant["id"],
                target_hours, tolerance_hours)
            variants.append(describe_variant(variant, selection, fmt))
        observed = [v for v in variants if v["status"] == "observed"]
        primary = "engaged_views" if fmt == "short" else "watch_minutes"
        eligible = [v for v in observed if v["metrics"].get(primary) is not None]
        if len(eligible) < min_comparable_variants:
            decision = "insufficient-data"
            leader = None
            caveat = (
                f"{len(eligible)} comparable variants with {primary}; "
                f"needs at least {min_comparable_variants} for an exploratory ranking. "
                "This threshold is a conservative operational gate, not statistical significance."
            )
        else:
            decision = "human-review"
            leader = max(eligible, key=lambda v: v["metrics"][primary])["variant_id"]
            caveat = (
                f"Descriptive {primary} leader only. Exposure, timing, audience and "
                "other confounders require review; not a causal winner."
            )
        out["experiments"].append({
            "experiment_id": experiment["id"], "channel": experiment.get("channel"),
            "format": fmt, "hypothesis": experiment.get("hypothesis"),
            "primary_metric": primary, "comparable_count": len(eligible),
            "decision": decision, "descriptive_leader": leader,
            "caveat": caveat, "variants": variants,
        })
    return out

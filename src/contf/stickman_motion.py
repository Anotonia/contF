"""Provider-neutral deterministic stickman motion contract (no network or paid models).

The renderer owns geometry; the agent proposes timed actions. This module validates
the handoff and samples simple 2-bone poses as an independently testable baseline.
"""
from __future__ import annotations

import hashlib
import json
import math

SCHEMA = "contf.stickman.motion.v0.1"
ACTIONS = {"idle", "walk", "reach", "point", "react", "speak"}
EMOTIONS = {"neutral", "happy", "worried", "surprised", "confident"}
JOINTS = ("hip", "shoulder", "elbow", "wrist", "knee", "ankle")


def validate(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("schema_version") != SCHEMA:
        raise ValueError("unsupported motion schema")
    if not isinstance(spec.get("shot_id"), str) or not spec["shot_id"]:
        raise ValueError("shot_id required")
    duration = spec.get("duration_s")
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("finite positive duration_s required")
    actors = spec.get("actors")
    if not isinstance(actors, list) or not actors:
        raise ValueError("nonempty actors required")
    ids = set()
    for actor in actors:
        aid = actor.get("character_id") if isinstance(actor, dict) else None
        if not isinstance(aid, str) or not aid or aid in ids:
            raise ValueError("character IDs must be unique nonempty strings")
        ids.add(aid)
        actions = actor.get("actions")
        if not isinstance(actions, list) or not actions:
            raise ValueError("actor actions required")
        for action in actions:
            if not isinstance(action, dict) or action.get("type") not in ACTIONS:
                raise ValueError("unknown action")
            start, end = action.get("start_s"), action.get("end_s")
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in (start, end)):
                raise ValueError("action timing must be finite numbers")
            if not 0 <= start < end <= duration:
                raise ValueError("action outside shot timeline")
            if action.get("emotion", "neutral") not in EMOTIONS:
                raise ValueError("unknown emotion")
            if action["type"] == "reach":
                target = action.get("target")
                if not isinstance(target, dict) or set(target) != {"x", "y"} or any(
                    isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in target.values()
                ):
                    raise ValueError("reach requires finite x/y target")
    return spec


def fingerprint(spec: dict) -> str:
    validate(spec)
    return hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def two_bone_ik(origin: tuple[float, float], target: tuple[float, float], upper: float, lower: float, bend: int = 1):
    """Return elbow and wrist. Clamp unreachable targets without NaNs."""
    if upper <= 0 or lower <= 0 or bend not in (-1, 1):
        raise ValueError("invalid limb")
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    distance = math.hypot(dx, dy)
    angle = math.atan2(dy, dx) if distance else 0.0
    effective = min(max(distance, abs(upper - lower) + 1e-9), upper + lower - 1e-9)
    cosine = max(-1.0, min(1.0, (upper * upper + effective * effective - lower * lower) / (2 * upper * effective)))
    elbow_angle = angle + bend * math.acos(cosine)
    elbow = (origin[0] + upper * math.cos(elbow_angle), origin[1] + upper * math.sin(elbow_angle))
    wrist = (origin[0] + effective * math.cos(angle), origin[1] + effective * math.sin(angle))
    return elbow, wrist


def sample(spec: dict, time_s: float) -> dict:
    """Frame-independent actor targets; actual rendering is deliberately external."""
    validate(spec)
    if not math.isfinite(time_s) or not 0 <= time_s <= spec["duration_s"]:
        raise ValueError("time outside shot")
    result = {}
    for actor in spec["actors"]:
        active = [a for a in actor["actions"] if a["start_s"] <= time_s < a["end_s"]]
        # Explicit ordering: later actions override earlier actions.
        action = active[-1] if active else {"type": "idle", "emotion": "neutral"}
        phase = (time_s - action["start_s"]) / (action["end_s"] - action["start_s"]) if active else 0.0
        eased = phase * phase * (3 - 2 * phase)
        result[actor["character_id"]] = {
            "action": action["type"],
            "emotion": action.get("emotion", "neutral"),
            "phase": round(eased, 6),
            "target": action.get("target"),
        }
    return result

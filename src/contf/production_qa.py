"""Fail-closed local media preflight for *candidate* animated footage.

This does not judge visual quality or authorize publication. FFprobe metadata
can verify streams and duration, not identity continuity, lip sync or acting.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path

from contf.shot_pipeline import MEDIA_INPUT_OPTIONS, validate_media_container


def probe(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("candidate media missing")
    validate_media_container(path)
    if not shutil.which("ffprobe"):
        raise RuntimeError("ffprobe is required for candidate preflight")
    p = subprocess.run(
        ["ffprobe", "-v", "error", *MEDIA_INPUT_OPTIONS, "-show_entries",
         "stream=index,codec_type,width,height,avg_frame_rate,duration:stream_disposition=attached_pic",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=False, timeout=30,
    )
    if p.returncode:
        raise RuntimeError("ffprobe failed: " + p.stderr[-500:])
    return json.loads(p.stdout)


def _video_duration(path: Path, stream: dict) -> float:
    try:
        duration = float(stream.get("duration", "nan"))
    except (TypeError, ValueError):
        duration = math.nan
    if math.isfinite(duration) and duration > 0:
        return duration
    if "index" not in stream:
        raise ValueError("video duration cannot be established")
    result = subprocess.run(
        ["ffprobe", "-v", "error", *MEDIA_INPUT_OPTIONS,
         "-select_streams", str(stream["index"]), "-show_packets", "-show_entries",
         "packet=pts_time,dts_time,duration_time", "-of", "json", str(path)],
        capture_output=True, text=True, check=False, timeout=30,
    )
    if result.returncode:
        raise RuntimeError("ffprobe video packets failed: " + result.stderr[-500:])
    starts, ends = [], []
    for packet in json.loads(result.stdout).get("packets", []):
        try:
            start = float(packet.get("pts_time", packet.get("dts_time", "nan")))
            length = float(packet.get("duration_time", 0))
        except (TypeError, ValueError):
            continue
        if math.isfinite(start) and math.isfinite(length) and length >= 0:
            starts.append(start)
            ends.append(start + length)
    if not starts or max(ends) <= min(starts):
        raise ValueError("video duration cannot be established")
    return max(ends) - min(starts)


def inspect(path: Path, *, min_seconds: float = 15, max_seconds: float = 25) -> dict:
    result = {"candidate": str(path), "passed": False, "errors": [], "duration_s": None,
              "manual_gates": {
                  "character_identity": "pending",
                  "costume_and_prop_continuity": "pending",
                  "actual_character_motion": "pending",
                  "dialogue_intelligibility": "pending",
                  "lip_sync": "pending",
                  "shot_transitions": "pending",
                  "rights_and_originality": "pending",
              }, "is_final_video": False}
    try:
        info = probe(path)
        streams = info.get("streams", [])
        video = [s for s in streams if s.get("codec_type") == "video"
                 and not s.get("disposition", {}).get("attached_pic")]
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        if not video:
            result["errors"].append("video stream missing")
        if len(video) > 1:
            result["errors"].append("multiple video streams are not supported")
        if not audio:
            result["errors"].append("audio stream missing")
        if video and (video[0].get("width", 0) < 640 or video[0].get("height", 0) < 360):
            result["errors"].append("video resolution below 640x360")
        result["video_stream_count"] = len(video)
        result["audio_stream_count"] = len(audio)
        if video:
            duration = _video_duration(path, video[0])
            result["duration_s"] = duration
            if not min_seconds <= duration <= max_seconds:
                result["errors"].append("duration outside candidate window")
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError,
            subprocess.TimeoutExpired) as exc:
        result["errors"].append(str(exc))
    result["passed"] = not result["errors"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline candidate motion-footage preflight")
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(args.candidate)
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

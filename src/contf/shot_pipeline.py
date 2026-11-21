"""Offline, rights-gated and reproducible shot-level storyboard preview.

This is a *preview compiler*, not a text-to-video model. Missing footage
renders as explicit storyboard cards. Nothing is uploaded or published.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.2.0"
RENDER_VERSION = "storyboard-3"
MEDIA_EXTENSIONS = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}
MEDIA_INPUT_OPTIONS = ["-protocol_whitelist", "file", "-format_whitelist", "mov,matroska,webm"]
BEATS = {"hook", "setup", "conflict", "escalation", "reaction", "reversal", "payoff", "loop"}
COLORS = {
    "hook": "0x264653", "setup": "0x26547C", "conflict": "0x9B2226",
    "escalation": "0xAE2012", "reaction": "0x5E548E", "reversal": "0x7F5539",
    "payoff": "0x386641", "loop": "0x264653",
}


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_media_container(path: Path) -> None:
    if path.suffix.lower() not in MEDIA_EXTENSIONS or path.resolve().suffix.lower() not in MEDIA_EXTENSIONS:
        raise ValueError("media must be a plain container: mp4, mov, m4v, mkv or webm")


def _media_path(root: Path, name: str) -> Path:
    """Only local files inside the explicit media root; reject path traversal."""
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("source_media must be a nonempty relative path")
    root = root.resolve()
    path = (root / name).resolve()
    if path == root or root not in path.parents:
        raise ValueError("source_media escapes media root")
    if not path.is_file():
        raise ValueError("source_media does not exist: " + name)
    validate_media_container(root / name)
    return path


def validate_preview_destinations(project: dict, root: Path, output: Path,
                                  *, media_paths: list[str] | None = None) -> None:
    output = output.resolve()
    destinations = (output, output.with_suffix(".manifest.json"))
    names = [s["source_media"] for s in project["shots"] if s.get("source_media") is not None]
    names.extend(name for name in (media_paths or []) if (root / name).is_file())
    for name in names:
        source = _media_path(root, name)
        for destination in destinations:
            if destination.resolve() == source or (destination.exists() and destination.samefile(source)):
                raise ValueError("preview or manifest would overwrite source media")


def validate(project: Any, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(project, dict):
        return ["project must be an object"]
    if project.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be " + SCHEMA_VERSION)
    if not isinstance(project.get("project_id"), str) or not project["project_id"].strip():
        errors.append("project_id is required")
    if project.get("rights") != "owned-original":
        errors.append("project rights must be owned-original for this local pilot")
    if project.get("approval_status") not in ("draft", "human-approved"):
        errors.append("approval_status must be draft or human-approved")
    shots = project.get("shots")
    if not isinstance(shots, list) or not shots:
        return errors + ["shots must be a nonempty list"]
    ids: set[str] = set()
    for index, shot in enumerate(shots):
        prefix = f"shots[{index}]"
        if not isinstance(shot, dict):
            errors.append(prefix + " must be an object")
            continue
        sid = shot.get("shot_id")
        if not isinstance(sid, str) or not sid.strip() or "/" in sid or "\\" in sid:
            errors.append(prefix + ".shot_id invalid")
        elif sid in ids:
            errors.append(prefix + ".shot_id duplicate")
        else:
            ids.add(sid)
        if shot.get("beat") not in BEATS:
            errors.append(prefix + ".beat invalid")
        duration = shot.get("duration_s")
        if not _number(duration) or not 0 < duration <= 90:
            errors.append(prefix + ".duration_s must be 0..90 seconds")
        for field in ("title", "action", "dialogue"):
            if not isinstance(shot.get(field), str):
                errors.append(prefix + "." + field + " must be a string")
        if shot.get("review_status") not in ("pending", "accepted", "rejected"):
            errors.append(prefix + ".review_status invalid")
        name = shot.get("source_media")
        if name is not None:
            if shot.get("source_rights") not in ("owned", "licensed"):
                errors.append(prefix + ".source_rights missing/invalid")
            try:
                _media_path(root, name)
            except (ValueError, OSError) as exc:
                errors.append(prefix + ": " + str(exc))
    return errors


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compile_plan(project: dict[str, Any], root: Path, *, width: int = 640,
                 height: int = 360, fps: int = 12) -> dict[str, Any]:
    errors = validate(project, root)
    if errors:
        raise ValueError("; ".join(errors))
    if width < 160 or height < 90 or width % 2 or height % 2 or not 1 <= fps <= 60:
        raise ValueError("width/height must be even >=160x90; fps 1..60")
    cursor = 0.0
    shots = []
    for shot in project["shots"]:
        source = shot.get("source_media")
        media_hash = _file_hash(_media_path(root, source)) if source is not None else None
        signature = {
            "render_version": RENDER_VERSION, "width": width, "height": height, "fps": fps,
            "shot": shot, "source_sha256": media_hash,
        }
        digest = hashlib.sha256(json.dumps(signature, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        duration = float(shot["duration_s"])
        shots.append({
            "shot_id": shot["shot_id"], "beat": shot["beat"],
            "start_s": round(cursor, 4), "end_s": round(cursor + duration, 4),
            "duration_s": duration, "cache_key": digest,
            "kind": "owned-footage-preview" if source else "storyboard-card",
            "review_status": shot["review_status"],
        })
        cursor += duration
    return {
        "schema_version": SCHEMA_VERSION, "project_id": project["project_id"],
        "output_type": "silent-storyboard-preview", "duration_s": round(cursor, 4),
        "width": width, "height": height, "fps": fps, "shots": shots,
        "unapproved_shot_count": sum(s["review_status"] != "accepted" for s in shots),
        "is_final_video": False,
    }


def _command(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError("ffmpeg failed: " + result.stderr[-2500:])


def _render_shot(shot: dict[str, Any], root: Path, destination: Path,
                 width: int, height: int, fps: int) -> None:
    # A fixed filename in an isolated directory is used for drawtext.
    # No user text or media path is interpolated into a shell command.
    with tempfile.TemporaryDirectory(prefix="contf-shot-") as tmp:
        caption_file = Path(tmp) / "caption.txt"
        lines = [
            f"SHOT {shot['shot_id']}  /  {shot['beat'].upper()}",
            shot["title"], shot["action"], shot["dialogue"],
            "STORYBOARD PREVIEW - NOT FINAL",
        ]
        caption_file.write_text(
            "\n".join(textwrap.fill(line, width=36) for line in lines if line),
            encoding="utf-8",
        )
        path = str(caption_file)
        # TemporaryDirectory paths are controlled, no external shell.
        if ":" in path or "'" in path or "\\" in path:
            raise ValueError("unsupported temporary path for FFmpeg drawtext")
        video_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"fps={fps},"
            f"drawtext=textfile='{path}':expansion=none:fontsize=20:fontcolor=white:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:box=1:"
            f"boxcolor=black@0.75:boxborderw=10"
        )
        duration = str(shot["duration_s"])
        if shot.get("source_media"):
            input_args = [*MEDIA_INPUT_OPTIONS, "-stream_loop", "-1", "-i",
                          str(_media_path(root, shot["source_media"]))]
        else:
            input_args = [
                "-f", "lavfi", "-i",
                f"color=c={COLORS[shot['beat']]}:s={width}x{height}:r={fps}",
            ]
        _command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            *input_args, "-map", "0:V:0", "-t", duration, "-vf", video_filter,
            "-an", "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-r", str(fps), str(destination),
        ])


def render_preview(project: dict[str, Any], root: Path, output: Path, cache: Path,
                   *, width: int = 640, height: int = 360, fps: int = 12) -> dict[str, Any]:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is not installed")
    plan = compile_plan(project, root, width=width, height=height, fps=fps)
    validate_preview_destinations(project, root, output)
    output = output.resolve()
    cache = cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    actions = []
    with tempfile.TemporaryDirectory(prefix="contf-concat-") as tmp:
        paths: list[Path] = []
        for shot, item in zip(project["shots"], plan["shots"]):
            clip = cache / (item["cache_key"] + ".mp4")
            if clip.exists() and clip.stat().st_size > 0:
                action = "reused"
            else:
                pending = cache / (item["cache_key"] + ".partial.mp4")
                try:
                    _render_shot(shot, root, pending, width, height, fps)
                    pending.replace(clip)
                finally:
                    pending.unlink(missing_ok=True)
                action = "rendered"
            paths.append(clip)
            actions.append({"shot_id": item["shot_id"], "action": action, "cache_key": item["cache_key"]})
        manifest = Path(tmp) / "concat.txt"
        # Concat list is generated from controlled cache paths, not video metadata.
        if any("\n" in str(p) or "'" in str(p) for p in paths):
            raise ValueError("unsupported quote/newline in cache directory")
        manifest.write_text(
            "".join(f"file '{path}'\n" for path in paths), encoding="utf-8"
        )
        temp_output = Path(tmp) / "preview.mp4"
        _command([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-protocol_whitelist", "file", "-f", "concat", "-safe", "0", "-i", str(manifest),
            "-c", "copy", "-movflags", "+faststart", str(temp_output),
        ])
        shutil.copyfile(temp_output, output)
    report = {**plan, "output_file": str(output), "shot_actions": actions,
              "rendered_count": sum(x["action"] == "rendered" for x in actions),
              "reused_count": sum(x["action"] == "reused" for x in actions)}
    output.with_suffix(".manifest.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="contF offline editable storyboard compiler")
    parser.add_argument("command", choices=("validate", "plan", "render"))
    parser.add_argument("project", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="explicit rights-cleared local footage root")
    parser.add_argument("--output", type=Path, default=Path("preview.mp4"))
    parser.add_argument("--cache", type=Path, default=Path(".contf-shot-cache"))
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args(argv)
    project = json.loads(args.project.read_text(encoding="utf-8"))
    try:
        if args.command == "validate":
            result: Any = {"valid": not (errors := validate(project, args.root)), "errors": errors}
        elif args.command == "plan":
            result = compile_plan(project, args.root, width=args.width,
                                  height=args.height, fps=args.fps)
        else:
            result = render_preview(project, args.root, args.output, args.cache,
                                    width=args.width, height=args.height, fps=args.fps)
    except (ValueError, RuntimeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not isinstance(result, dict) or result.get("valid", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI for reviewing exported or synthetic contF observations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .evolution import review


def load_rows(path: str) -> list[dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(not isinstance(x, dict) for x in data):
        raise ValueError(f"{path}: expected an array of objects")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(prog="contf")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("review", help="Read-only experiment review")
    run.add_argument("--experiments", required=True)
    run.add_argument("--observations", required=True)
    run.add_argument("--target-hours", type=float, default=72.0)
    run.add_argument("--tolerance-hours", type=float, default=12.0)
    run.add_argument("--min-comparable", type=int, default=5)
    run.add_argument("--json", action="store_true", help="Machine-readable output")
    slice_cmd = sub.add_parser("slice", help="Offline shot queue, audit and storyboard preview")
    slice_cmd.add_argument("project", type=Path)
    slice_cmd.add_argument("--root", type=Path, default=Path("."))
    slice_cmd.add_argument("--out", type=Path, required=True)
    slice_cmd.add_argument("--receipt", type=Path, action="append", default=[])
    slice_cmd.add_argument("--approval", type=Path, action="append", default=[])
    slice_cmd.add_argument("--no-render", action="store_true")
    slice_cmd.add_argument("--width", type=int, default=640)
    slice_cmd.add_argument("--height", type=int, default=360)
    slice_cmd.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()
    if args.command == "slice":
        from .slice import run_slice
        try:
            result = run_slice(json.loads(args.project.read_text(encoding="utf-8")),
                               args.root, args.out, receipts=args.receipt, approvals=args.approval,
                               no_render=args.no_render, width=args.width,
                               height=args.height, fps=args.fps)
        except (ValueError, OSError, RuntimeError, KeyError, TypeError) as exc:
            print(json.dumps({"error": str(exc)}))
            return 2
        print(json.dumps(result, indent=2))
        return 2 if result["errors"] else 0
    if args.command == "review":
        result = review(
            load_rows(args.experiments), load_rows(args.observations),
            target_hours=args.target_hours,
            tolerance_hours=args.tolerance_hours,
            min_comparable_variants=args.min_comparable,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            for item in result["experiments"]:
                print(f"{item['experiment_id']}: {item['decision']} "
                      f"({item['comparable_count']} comparable; {item['primary_metric']})")
                for variant in item["variants"]:
                    val = variant["metrics"].get(item["primary_metric"])
                    print(f"  {variant['variant_id']}: {val if val is not None else 'missing'}")
                print(f"  NOTE: {item['caveat']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

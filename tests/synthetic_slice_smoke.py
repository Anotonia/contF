"""Run the documented SYNTHETIC sample with the installed contf entry point."""
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys

from contf.production_adapter import APPROVAL_VERSION, REQUIRED_REVIEW, RECEIPT_VERSION
from contf.production_jobs import build_jobs


def main():
    root = Path(sys.argv[1]).resolve()
    root.mkdir(parents=True, exist_ok=True)
    sample = Path(__file__).resolve().parents[1] / "data/examples/maya_ethan_original_animatic.json"
    shutil.copyfile(sample, root / "project.json")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "testsrc=size=640x360:rate=12",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
                    "-t", "12", "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", str(root / "SYNTHETIC.mp4")], check=True)
    project = json.loads((root / "project.json").read_text())
    settings = dict(width=320, height=180, fps=8)
    receipt = {"receipt_version": RECEIPT_VERSION, "shot_id": "S01",
               "fingerprint": build_jobs(project, root, **settings)["jobs"][0]["fingerprint"],
               "source_rights": "owned", "producer": "SYNTHETIC local ffmpeg",
               "model_version": "testsrc-sine-1", "media_path": "SYNTHETIC.mp4",
               "paid_generation": False,
               "cost": {"amount": 3, "currency": "USD", "source": "SYNTHETIC billing fixture"}}
    (root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    approval = {"approval_version": APPROVAL_VERSION, "shot_id": receipt["shot_id"],
                "fingerprint": receipt["fingerprint"],
                "media_sha256": hashlib.sha256((root / "SYNTHETIC.mp4").read_bytes()).hexdigest(),
                "reviewer": "SYNTHETIC independent human reviewer",
                "manual_review": {key: "pass" for key in REQUIRED_REVIEW}}
    (root / "approval.json").write_text(json.dumps(approval, indent=2) + "\n")
    command = ["contf", "slice", str(root / "project.json"), "--root", str(root),
               "--out", str(root / "out"), "--width", "320", "--height", "180", "--fps", "8"]
    for index in range(2):
        extra = ["--receipt", str(root / "receipt.json"), "--approval", str(root / "approval.json")] if index == 0 else []
        report = json.loads(subprocess.check_output(command + extra, text=True))
        (root / f"run-{index + 1}.json").write_text(json.dumps(report, indent=2) + "\n")
        totals = report["audit"]["totals"]
        assert totals["counts_by_state"] == {"accepted": 1, "awaiting-human-approval": 15}, totals
        assert totals["known_cost_sum"] == 3 and totals["unknown_cost_count"] == 0, totals
        assert totals["not_produced_count"] == 15, totals
        assert totals["cost_per_accepted_minute"] == 15.0, totals
        assert not report["audit"]["published"] and not report["audit"]["is_final_video"]
        queue = json.loads((root / "out/queue.json").read_text())
        assert queue["jobs"][0]["media_receipt"]["approval"] == approval
        assert report["render"]["rendered_count"] == (16 if index == 0 else 0), report
        assert report["render"]["reused_count"] == (0 if index == 0 else 16), report
        print(f"Run {index + 1}: rendered={report['render']['rendered_count']} reused={report['render']['reused_count']}")
    assert (root / "out/preview.mp4").stat().st_size > 0
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()

"""SYNTHETIC offline slice integration, including real generated media."""
import contextlib
import copy
import io
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.cli import main
from contf.production_adapter import REQUIRED_REVIEW
from contf.production_jobs import build_jobs
from contf.slice import run_slice
from test_production_jobs import approval_record, project


class SliceTests(unittest.TestCase):
    def test_obsolete_accepted_receipts_do_not_report_revalidation_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            (root / "SYNTHETIC.mp4").write_bytes(b"SYNTHETIC media")
            raw = {"receipt_version": "0.2.0", "shot_id": "S01",
                   "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                   "producer": "SYNTHETIC producer", "model_version": "SYNTHETIC-1",
                   "source_rights": "owned", "media_path": "SYNTHETIC.mp4"}
            receipt_path = root / "receipt.json"
            receipt_path.write_text(json.dumps(raw))
            approval_path = root / "approval.json"
            approval_path.write_text(json.dumps(approval_record(raw, hashlib.sha256(b"SYNTHETIC media").hexdigest())))
            for change in ("caption", "remove"):
                with self.subTest(change=change), patch("contf.production_adapter.inspect", return_value={"passed": True, "errors": []}):
                    out = root / change
                    accepted = run_slice(spec, root, out, receipts=[receipt_path], approvals=[approval_path], no_render=True)
                    self.assertEqual(accepted["audit"]["shots"][0]["state"], "accepted")
                    changed = copy.deepcopy(spec)
                    if change == "caption":
                        changed["shots"][0]["dialogue"] = "SYNTHETIC edited caption"
                    else:
                        changed["shots"].pop(0)
                    result = run_slice(changed, root, out, no_render=True)
                    self.assertEqual(result["errors"], [])
                    self.assertTrue(all(shot["state"] != "accepted" for shot in result["audit"]["shots"]))
                    self.assertTrue(all(job["media_receipt"] is None for job in json.loads((out / "queue.json").read_text())["jobs"]))

    def test_approval_only_cannot_normalize_blocked_producer_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            (root / "SYNTHETIC.mp4").write_bytes(b"SYNTHETIC media")
            raw = {"receipt_version": "0.2.0", "shot_id": "S01",
                   "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                   "producer": "SYNTHETIC producer", "model_version": "SYNTHETIC-1",
                   "source_rights": "owned", "media_path": "SYNTHETIC.mp4"}
            receipt_path = root / "receipt.json"
            approval_path = root / "approval.json"
            approval_path.write_text(json.dumps(approval_record(raw, hashlib.sha256(b"SYNTHETIC media").hexdigest())))
            invalid_fields = (
                {"reviewer": "SYNTHETIC reviewer", "manual_review": {gate: "pass" for gate in REQUIRED_REVIEW}},
                {"receipt_version": "0.1.0"},
                {"cost": {"amount": -1, "currency": "USD", "source": "SYNTHETIC billing"}},
            )
            with patch("contf.production_adapter.inspect", return_value={"passed": True, "errors": []}):
                for index, fields in enumerate(invalid_fields):
                    with self.subTest(fields=fields):
                        out = root / str(index)
                        receipt_path.write_text(json.dumps({**raw, **fields}))
                        blocked = run_slice(spec, root, out, receipts=[receipt_path], no_render=True)
                        self.assertTrue(blocked["errors"])
                        self.assertEqual(blocked["audit"]["shots"][0]["state"], "blocked")
                        previous = (out / "queue.json").read_bytes()
                        with self.assertRaisesRegex(ValueError, "corrected producer receipt"):
                            run_slice(spec, root, out, approvals=[approval_path], no_render=True)
                        self.assertEqual((out / "queue.json").read_bytes(), previous)
                        receipt_path.write_text(json.dumps(raw))
                        corrected = run_slice(spec, root, out, receipts=[receipt_path], approvals=[approval_path], no_render=True)
                        self.assertEqual(corrected["errors"], [])
                        self.assertEqual(corrected["audit"]["shots"][0]["state"], "accepted")

    def test_approval_files_require_receipts_and_reject_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            approval_path = root / "SYNTHETIC-approval.json"
            approval_path.write_text(json.dumps({"shot_id": "S01"}))
            for approvals, message in (([approval_path], "no supplied or queued receipt"),
                                       ([approval_path, approval_path], "duplicate approval")):
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    run_slice(spec, root, root / "out", approvals=approvals, no_render=True)
                self.assertFalse((root / "out").exists())
            project_path = root / "SYNTHETIC-project.json"
            project_path.write_text(json.dumps(spec))
            argv = ["contf", "slice", str(project_path), "--root", str(root),
                    "--out", str(root / "out"), "--approval", str(approval_path), "--no-render"]
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 2)
            self.assertIn("no supplied or queued receipt", output.getvalue())

    def test_separate_approval_for_queued_pending_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            (root / "SYNTHETIC.mp4").write_bytes(b"SYNTHETIC media")
            raw = {"receipt_version": "0.2.0", "shot_id": "S01",
                   "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                   "producer": "SYNTHETIC producer", "model_version": "SYNTHETIC-1",
                   "source_rights": "owned", "media_path": "SYNTHETIC.mp4",
                   "paid_generation": True, "human_spend_approval": True}
            receipt_path = root / "receipt.json"
            receipt_path.write_text(json.dumps(raw))
            approval_path = root / "approval.json"
            approval_path.write_text(json.dumps(approval_record(raw, hashlib.sha256(b"SYNTHETIC media").hexdigest())))
            with patch("contf.production_adapter.inspect", return_value={"passed": True, "errors": []}):
                pending = run_slice(spec, root, root / "out", receipts=[receipt_path], no_render=True)
                self.assertEqual(pending["audit"]["shots"][0]["state"], "pending-human-review")
                accepted = run_slice(spec, root, root / "out", approvals=[approval_path], no_render=True)
                self.assertEqual(accepted["audit"]["shots"][0]["state"], "accepted")
                reused = run_slice(spec, root, root / "out", no_render=True)
                self.assertEqual(reused["audit"], accepted["audit"])
                self.assertEqual(reused["errors"], [])

    def test_slice_rejects_preview_source_before_writing_queue_or_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "out"
            out.mkdir()
            media = out / "preview.mp4"
            media.write_bytes(b"SYNTHETIC source media")
            audit_path = out / "audit.json"
            audit_path.write_text("SYNTHETIC existing audit")
            spec = project()
            spec["shots"][0].update(source_media="out/preview.mp4", source_rights="owned")
            with self.assertRaisesRegex(ValueError, "overwrite source"):
                run_slice(spec, root, out)
            self.assertFalse((out / "queue.json").exists())
            self.assertEqual(audit_path.read_text(), "SYNTHETIC existing audit")
            spec["shots"][0]["source_media"] = None
            receipt = {"receipt_version": "0.2.0", "shot_id": "S01",
                       "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                       "producer": "SYNTHETIC", "model_version": "SYNTHETIC-1",
                       "media_path": "out/preview.mp4", "source_rights": "owned"}
            path = root / "receipt.json"
            approval_path = root / "approval.json"
            approval = approval_record(receipt, hashlib.sha256(media.read_bytes()).hexdigest())
            path.write_text(json.dumps(receipt))
            with patch("contf.production_adapter.inspect", return_value={"passed": True, "errors": []}):
                for gate_state in ("pass", "pending"):
                    approval["manual_review"] = {k: gate_state for k in REQUIRED_REVIEW}
                    approval_path.write_text(json.dumps(approval))
                    with self.assertRaisesRegex(ValueError, "overwrite source"):
                        run_slice(spec, root, out, receipts=[path], approvals=[approval_path])
            self.assertFalse((out / "queue.json").exists())
            self.assertEqual(audit_path.read_text(), "SYNTHETIC existing audit")
            self.assertEqual(media.read_bytes(), b"SYNTHETIC source media")

    def test_invalid_cli_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "SYNTHETIC.json"
            path.write_text("{}")
            with patch.object(sys, "argv", ["contf", "slice", str(path), "--out", str(root)]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main(), 2)

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
    def test_real_slice_acceptance_reuse_stale_and_null_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = project()
            spec["shots"][0]["duration_s"] = 12
            spec["shots"][1]["duration_s"] = 0.6
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                            "testsrc=size=640x360:rate=12", "-f", "lavfi", "-i",
                            "sine=frequency=440:sample_rate=44100", "-t", "12",
                            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt",
                            "yuv420p", "-c:a", "aac", str(root / "SYNTHETIC.mp4")], check=True)
            receipt = {"receipt_version": "0.2.0", "shot_id": "S01",
                       "fingerprint": build_jobs(spec, root)["jobs"][0]["fingerprint"],
                       "producer": "SYNTHETIC", "model_version": "ffmpeg-testsrc",
                       "media_path": "SYNTHETIC.mp4", "source_rights": "owned",
                       "cost": {"amount": 3, "currency": "USD", "source": "SYNTHETIC billing"}}
            path = root / "receipt.json"
            path.write_text(json.dumps(receipt))
            approval_path = root / "approval.json"
            approval_path.write_text(json.dumps(approval_record(receipt, hashlib.sha256((root / "SYNTHETIC.mp4").read_bytes()).hexdigest())))
            spec_path = root / "project.json"
            spec_path.write_text(json.dumps(spec))
            argv = ["contf", "slice", str(spec_path), "--root", str(root),
                    "--out", str(root / "out"), "--receipt", str(path), "--approval", str(approval_path)]
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as stream:
                self.assertEqual(main(), 0)
            first = json.loads(stream.getvalue())
            totals = first["audit"]["totals"]
            self.assertEqual(totals["counts_by_state"], {"accepted": 1, "awaiting-human-approval": 1})
            self.assertEqual(totals["known_cost_sum"], 3)
            self.assertEqual(totals["unknown_cost_count"], 0)
            self.assertEqual(totals["not_produced_count"], 1)
            self.assertEqual(totals["cost_per_accepted_minute"], 15.0)
            self.assertEqual(first["render"]["rendered_count"], 2)
            self.assertGreater((root / "out" / "preview.mp4").stat().st_size, 0)
            second = run_slice(spec, root, root / "out")
            self.assertEqual(second["render"]["reused_count"], 2)
            self.assertEqual(second["audit"], first["audit"])
            stale_receipt = {**receipt, "fingerprint": "SYNTHETIC-stale"}
            path.write_text(json.dumps(stale_receipt))
            retained = run_slice(spec, root, root / "out", receipts=[path], no_render=True)
            self.assertTrue(retained["errors"])
            self.assertEqual(retained["audit"], first["audit"])
            self.assertEqual(retained["rejected_receipts"][0]["receipt"]["fingerprint"], "SYNTHETIC-stale")
            self.assertEqual(json.loads((root / "out/queue.json").read_text())["jobs"][0]["state"], "accepted")
            foreign = copy.deepcopy(spec)
            foreign["project_id"] = "SYNTHETIC-other-project"
            foreign_empty = run_slice(foreign, root, root / "out", no_render=True)
            self.assertEqual(foreign_empty["audit"]["totals"]["counts_by_state"],
                             {"awaiting-human-approval": 2})
            path.write_text(json.dumps(receipt))
            foreign_result = run_slice(foreign, root, root / "out", receipts=[path], no_render=True)
            self.assertTrue(foreign_result["errors"])
            self.assertNotEqual(foreign_result["audit"]["shots"][0]["state"], "accepted")
            path.write_text(json.dumps(receipt))
            run_slice(spec, root, root / "out", receipts=[path], approvals=[approval_path], no_render=True)
            media = root / "SYNTHETIC.mp4"
            original = media.read_bytes()
            media.write_bytes(original + b"SYNTHETIC changed media")
            changed = run_slice(spec, root, root / "out", no_render=True)
            self.assertEqual(changed["audit"]["shots"][0]["state"], "blocked")
            changed_receipt = json.loads((root / "out/queue.json").read_text())["jobs"][0]["media_receipt"]
            self.assertIn("approval media_sha256 mismatch", changed_receipt["errors"])
            self.assertTrue(changed_receipt["preflight"]["passed"])
            media.write_bytes(original)
            receipt.pop("cost")
            path.write_text(json.dumps(receipt))
            missing = run_slice(spec, root, root / "out", receipts=[path], approvals=[approval_path], no_render=True)
            self.assertIsNone(missing["audit"]["shots"][0]["cost"])
            self.assertEqual(missing["audit"]["totals"]["unknown_cost_count"], 1)
            self.assertEqual(missing["audit"]["totals"]["not_produced_count"], 1)
            self.assertIsNone(missing["audit"]["totals"]["cost_per_accepted_minute"])
            receipt["fingerprint"] = "stale"
            path.write_text(json.dumps(receipt))
            stale = run_slice(spec, root, root / "out", receipts=[path], no_render=True)
            self.assertTrue(stale["errors"])
            self.assertEqual(stale["audit"]["shots"][0]["state"], "accepted")

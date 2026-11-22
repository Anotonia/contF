"""SYNTHETIC-only provider receipt ingestion tests."""
import sys
import copy
import hashlib
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_adapter import REQUIRED_REVIEW, ingest, main
from contf.production_jobs import build_jobs
from test_production_jobs import approval_record, project


class ProductionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "shot.mp4").write_bytes(b"SYNTHETIC MEDIA")
        self.project = project()
        self.project["shots"][0]["duration_s"] = 20
        self.receipt = {"receipt_version": "0.2.0", "shot_id": "S01",
                        "source_rights": "owned", "producer": "local-fixture",
                        "model_version": "synthetic-1", "media_path": "shot.mp4",
                        "paid_generation": False}
        self.ok = {"passed": True, "errors": [], "duration_s": 20}
        self.receipt["fingerprint"] = build_jobs(self.project, self.root)["jobs"][0]["fingerprint"]

    def test_fingerprint_required_and_current(self):
        for fingerprint in (None, "stale"):
            self.receipt["fingerprint"] = fingerprint
            with patch("contf.production_adapter.inspect", return_value=self.ok):
                report = ingest(self.project, self.receipt, self.root)
            self.assertFalse(report["accepted"])
            self.assertIn("fingerprint missing or does not match current shot plan", report["errors"])

    def test_cost_missing_is_null_and_invalid_cost_blocks(self):
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            self.assertIsNone(ingest(self.project, self.receipt, self.root)["cost"])
            self.receipt["cost"] = {"amount": -1, "currency": "USD", "source": "SYNTHETIC"}
            self.assertTrue(ingest(self.project, self.receipt, self.root)["errors"])

    def test_pending_not_auto_accepted(self):
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
        self.assertEqual(result["status"], "pending-human-review")
        self.assertFalse(result["accepted"])
        self.assertIsNotNone(result["media_sha256"])

    def test_missing_rights_fail_closed(self):
        self.receipt.pop("source_rights")
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
        self.assertEqual(result["status"], "blocked")

    def test_path_escape_rejected(self):
        self.receipt["media_path"] = "../shot.mp4"
        result = ingest(self.project, self.receipt, self.root)
        self.assertFalse(result["accepted"])
        self.assertIsNone(result["media_sha256"])

    def test_playlist_receipt_rejected_before_preflight(self):
        for suffix in (".m3u8", ".txt", ".ffconcat", ".m3u"):
            path = self.root / ("SYNTHETIC" + suffix)
            path.write_text("file '../outside.mp4'\n")
            self.receipt["media_path"] = path.name
            with patch("contf.production_adapter.inspect") as preflight:
                result = ingest(self.project, self.receipt, self.root)
                preflight.assert_not_called()
            self.assertFalse(result["accepted"])
            self.assertTrue(any("plain container" in e for e in result["errors"]))

    def test_paid_generation_requires_approval(self):
        self.receipt["paid_generation"] = True
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
        self.assertIn("paid generation without documented human approval", result["errors"])

    def test_producer_cannot_self_approve(self):
        self.receipt["manual_review"] = {k: "pass" for k in REQUIRED_REVIEW}
        self.receipt["reviewer"] = "SYNTHETIC reviewer"
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["status"], "blocked")
        self.assertIn("approval fields belong in a separate approval record", result["errors"])
        self.assertIsNone(result["reviewer"])
        self.assertTrue(all(value == "pending" for value in result["manual_review"].values()))

    def test_valid_separate_approval_accepts(self):
        approval = approval_record(self.receipt, hashlib.sha256(b"SYNTHETIC MEDIA").hexdigest())
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root, approval=approval)
        self.assertTrue(result["accepted"])
        self.assertEqual(result["approval"], approval)
        self.assertEqual(result["reviewer"], approval["reviewer"])
        self.assertEqual(result["manual_review"], approval["manual_review"])

    def test_invalid_approval_blocks(self):
        valid = approval_record(self.receipt, hashlib.sha256(b"SYNTHETIC MEDIA").hexdigest())
        mutations = [(key, value) for key, value in (
            ("approval_version", "SYNTHETIC-wrong"), ("shot_id", "S02"),
            ("fingerprint", "SYNTHETIC-stale"), ("media_sha256", "b" * 64),
            ("reviewer", "  LOCAL-FIXTURE  "), ("reviewer", None),
            ("reviewer", " loCAL- fixTURE "),
            ("reviewer", "  "), ("reviewer", 123), ("manual_review", []),
            ("manual_review", {}))]
        for key, value in mutations:
            with self.subTest(key=key, value=value):
                approval = {**valid, key: value}
                with patch("contf.production_adapter.inspect", return_value=self.ok):
                    result = ingest(self.project, self.receipt, self.root, approval=approval)
                self.assertFalse(result["accepted"])
                self.assertEqual(result["status"], "blocked")
                self.assertIsNone(result["approval"])
        for approval in ([], "SYNTHETIC", 1):
            with self.subTest(approval=approval), patch("contf.production_adapter.inspect", return_value=self.ok):
                self.assertEqual(ingest(self.project, self.receipt, self.root, approval=approval)["status"], "blocked")
        approval = copy.deepcopy(valid)
        del approval["reviewer"]
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            self.assertEqual(ingest(self.project, self.receipt, self.root, approval=approval)["status"], "blocked")

    def test_each_gate_must_pass(self):
        for gate in REQUIRED_REVIEW:
            for state in ("pending", "fail", "invalid", None):
                with self.subTest(gate=gate, state=state):
                    approval = approval_record(self.receipt, hashlib.sha256(b"SYNTHETIC MEDIA").hexdigest())
                    approval["manual_review"][gate] = state
                    with patch("contf.production_adapter.inspect", return_value=self.ok):
                        report = ingest(self.project, self.receipt, self.root, approval=approval)
                    self.assertFalse(report["accepted"])
                    self.assertEqual(report["status"], "pending-human-review" if state in ("pending", "fail") else "blocked")

    def test_legacy_receipt_requires_reissue(self):
        self.receipt["receipt_version"] = "0.1.0"
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            report = ingest(self.project, self.receipt, self.root)
        self.assertIn("receipt_version invalid", report["errors"])

    def test_approval_fields_forbidden_even_with_valid_separate_approval(self):
        approval = approval_record(self.receipt, hashlib.sha256(b"SYNTHETIC MEDIA").hexdigest())
        for field in ("reviewer", "manual_review"):
            with self.subTest(field=field), patch("contf.production_adapter.inspect", return_value=self.ok):
                report = ingest(self.project, {**self.receipt, field: None}, self.root, approval=approval)
                self.assertEqual(report["status"], "blocked")
                self.assertIn("approval fields belong in a separate approval record", report["errors"])

    def test_adapter_cli_loads_separate_approval_and_returns_errors(self):
        project_path = self.root / "SYNTHETIC-project.json"
        receipt_path = self.root / "receipt.json"
        approval_path = self.root / "approval.json"
        project_path.write_text(json.dumps(self.project))
        receipt_path.write_text(json.dumps(self.receipt))
        approval = approval_record(self.receipt, hashlib.sha256(b"SYNTHETIC MEDIA").hexdigest())
        argv = ["adapter", str(project_path), str(receipt_path), "--root", str(self.root)]
        cases = (([], None, 0, "pending-human-review"),
                 (["--approval", str(approval_path)], approval, 0, "accepted"),
                 (["--approval", str(approval_path)], {**approval, "media_sha256": "b" * 64}, 2, "blocked"))
        for extra, record, code, status in cases:
            with self.subTest(status=status):
                approval_path.write_text(json.dumps(record))
                with patch("contf.production_adapter.inspect", return_value=self.ok), patch.object(sys, "argv", argv + extra):
                    with contextlib.redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(main(), code)
                self.assertEqual(json.loads(output.getvalue())["status"], status)


if __name__ == "__main__":
    unittest.main()

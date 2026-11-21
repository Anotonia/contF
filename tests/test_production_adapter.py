"""SYNTHETIC-only provider receipt ingestion tests."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_adapter import REQUIRED_REVIEW, ingest
from contf.production_jobs import build_jobs
from test_production_jobs import project


class ProductionAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "shot.mp4").write_bytes(b"SYNTHETIC MEDIA")
        self.project = project()
        self.project['shots'][0]['duration_s'] = 20
        self.receipt = {"receipt_version": "0.1.0", "shot_id": "S01",
                        "source_rights": "owned", "producer": "local-fixture",
                        "model_version": "synthetic-1", "media_path": "shot.mp4",
                        "paid_generation": False,
                        "manual_review": {k: "pending" for k in REQUIRED_REVIEW}}
        self.ok = {"passed": True, "errors": [], "duration_s": 20}
        self.receipt['fingerprint'] = build_jobs(self.project, self.root)['jobs'][0]['fingerprint']

    def test_fingerprint_required_and_current(self):
        for fingerprint in (None, 'stale'):
            self.receipt['fingerprint'] = fingerprint
            with patch('contf.production_adapter.inspect', return_value=self.ok):
                report = ingest(self.project, self.receipt, self.root)
            self.assertFalse(report['accepted'])
            self.assertIn('fingerprint missing or does not match current shot plan', report['errors'])

    def test_cost_missing_is_null_and_invalid_cost_blocks(self):
        with patch('contf.production_adapter.inspect', return_value=self.ok):
            self.assertIsNone(ingest(self.project, self.receipt, self.root)['cost'])
            self.receipt['cost'] = {'amount': -1, 'currency': 'USD', 'source': 'SYNTHETIC'}
            self.assertTrue(ingest(self.project, self.receipt, self.root)['errors'])

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

    def test_paid_generation_requires_approval(self):
        self.receipt["paid_generation"] = True
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
        self.assertIn("paid generation without documented human approval", result["errors"])

    def test_manual_pass_requires_named_reviewer(self):
        self.receipt["manual_review"] = {k: "pass" for k in REQUIRED_REVIEW}
        with patch("contf.production_adapter.inspect", return_value=self.ok):
            result = ingest(self.project, self.receipt, self.root)
            self.assertFalse(result["accepted"])
            self.receipt["reviewer"] = "human-qa"
            result = ingest(self.project, self.receipt, self.root)
        self.assertTrue(result["accepted"])


if __name__ == "__main__":
    unittest.main()

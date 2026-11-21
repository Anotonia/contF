"""SYNTHETIC offline production job lifecycle tests."""
import copy
import json
from unittest.mock import patch
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_jobs import build_jobs, reconcile, prepare_retry, main
from contf.production_adapter import REQUIRED_REVIEW


def project():
    return {"schema_version": "0.2.0", "project_id": "SYNTHETIC-job-test",
            "rights": "owned-original", "approval_status": "draft", "shots": [
                {"shot_id": "S01", "beat": "hook", "duration_s": 10,
                 "title": "Start", "action": "Maya moves", "dialogue": "Hello",
                 "source_media": None, "review_status": "pending"},
                {"shot_id": "S02", "beat": "payoff", "duration_s": 10,
                 "title": "End", "action": "Ethan reacts", "dialogue": "Bye",
                 "source_media": None, "review_status": "pending"},
            ]}


def verified_receipt(fingerprint):
    return {"fingerprint": fingerprint, "accepted": True, "status": "accepted",
            "errors": [], "media_sha256": "a" * 64, "reviewer": "human-reviewer",
            "preflight": {"passed": True},
            "manual_review": {key: "pass" for key in REQUIRED_REVIEW}}


class ProductionJobTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = project()

    def test_plan_deterministic_and_no_automatic_execution(self):
        a = build_jobs(self.project, self.root)
        self.assertEqual(a, build_jobs(self.project, self.root))
        self.assertFalse(a["automatic_provider_execution"])
        self.assertTrue(all(j["state"] == "awaiting-human-approval" for j in a["jobs"]))

    def test_retry_requires_human_approval(self):
        queue = build_jobs(self.project, self.root)
        with self.assertRaises(ValueError):
            prepare_retry(queue, "S02")
        retried = prepare_retry(queue, "S02", human_approved=True)
        self.assertEqual(retried["jobs"][1]["attempt"], 1)
        self.assertEqual(retried["jobs"][1]["state"], "ready-for-external-provider")
        self.assertEqual(queue["jobs"][1]["attempt"], 0)

    def test_accepted_shot_cannot_be_retried(self):
        queue = build_jobs(self.project, self.root)
        queue["jobs"][0]["state"] = "accepted"
        with self.assertRaises(ValueError):
            prepare_retry(queue, "S01", human_approved=True)

    def test_one_shot_change_invalidates_only_that_shot(self):
        queue = build_jobs(self.project, self.root)
        for job in queue["jobs"]:
            job["state"] = "accepted"
            job["media_receipt"] = verified_receipt(job["fingerprint"])
        modified = copy.deepcopy(self.project)
        modified["shots"][1]["dialogue"] = "Changed!"
        updated = reconcile(build_jobs(modified, self.root), queue)
        self.assertEqual(updated["jobs"][0]["state"], "accepted")
        self.assertEqual(updated["jobs"][1]["state"], "awaiting-human-approval")
        self.assertNotEqual(updated["jobs"][1]["fingerprint"], queue["jobs"][1]["fingerprint"])

    def test_unverified_receipt_cannot_promote_to_accepted(self):
        queue = build_jobs(self.project, self.root)
        receipt = {"fingerprint": queue["jobs"][0]["fingerprint"], "accepted": True}
        updated = reconcile(queue, receipts={"S01": receipt})
        self.assertEqual(updated["jobs"][0]["state"], "pending-human-review")

    def test_verified_receipt_can_promote_to_accepted(self):
        queue = build_jobs(self.project, self.root)
        receipt = verified_receipt(queue["jobs"][0]["fingerprint"])
        updated = reconcile(queue, receipts={"S01": receipt})
        self.assertEqual(updated["jobs"][0]["state"], "accepted")

    def test_restored_acceptance_without_qa_is_downgraded(self):
        queue = build_jobs(self.project, self.root)
        queue["jobs"][0]["state"] = "accepted"
        updated = reconcile(build_jobs(self.project, self.root), queue)
        self.assertEqual(updated["jobs"][0]["state"], "pending-human-review")

    def test_apply_cli_ingests_file_and_preserves_other_shot(self):
        media = self.root / "S02.mp4"
        media.write_bytes(b"SYNTHETIC local media fixture")
        project_file = self.root / "project.json"
        queue_file = self.root / "queue.json"
        receipt_file = self.root / "receipt.json"
        output_file = self.root / "updated.json"
        project_file.write_text(json.dumps(self.project), encoding="utf-8")
        queue = build_jobs(self.project, self.root)
        queue["jobs"][0]["state"] = "accepted"
        queue["jobs"][0]["media_receipt"] = verified_receipt(queue["jobs"][0]["fingerprint"])
        queue_file.write_text(json.dumps(queue), encoding="utf-8")
        receipt = {
            "receipt_version": "0.1.0", "shot_id": "S02",
            "source_rights": "owned", "producer": "SYNTHETIC-local",
            "model_version": "fixture-1", "media_path": "S02.mp4",
            "paid_generation": False,
            "manual_review": {key: "pending" for key in REQUIRED_REVIEW},
        }
        receipt_file.write_text(json.dumps(receipt), encoding="utf-8")
        argv = ["production_jobs", "apply", "--project", str(project_file),
                "--root", str(self.root), "--queue", str(queue_file),
                "--receipt", str(receipt_file), "--output", str(output_file)]
        with patch("contf.production_adapter.inspect",
                   return_value={"passed": True, "errors": [], "duration_s": 10}):
            with patch.object(sys, "argv", argv):
                self.assertEqual(main(), 0)
        result = json.loads(output_file.read_text(encoding="utf-8"))
        self.assertEqual(result["jobs"][0]["state"], "accepted")
        self.assertEqual(result["jobs"][1]["state"], "pending-human-review")
        self.assertEqual(len(result["jobs"][1]["media_receipt"]["media_sha256"]), 64)
        self.assertFalse(result["jobs"][1]["media_receipt"]["accepted"])

    def test_stale_receipt_blocks_acceptance(self):
        queue = build_jobs(self.project, self.root)
        updated = reconcile(queue, receipts={"S01": {"fingerprint": "wrong",
                                                      "accepted": True}})
        self.assertEqual(updated["jobs"][0]["state"], "blocked-stale-receipt")
        self.assertIsNone(updated["jobs"][0]["media_receipt"])


if __name__ == "__main__":
    unittest.main()

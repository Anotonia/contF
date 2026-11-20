"""SYNTHETIC offline production job lifecycle tests."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_jobs import build_jobs, reconcile, prepare_retry
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

    def test_stale_receipt_blocks_acceptance(self):
        queue = build_jobs(self.project, self.root)
        updated = reconcile(queue, receipts={"S01": {"fingerprint": "wrong",
                                                      "accepted": True}})
        self.assertEqual(updated["jobs"][0]["state"], "blocked-stale-receipt")
        self.assertIsNone(updated["jobs"][0]["media_receipt"])


if __name__ == "__main__":
    unittest.main()

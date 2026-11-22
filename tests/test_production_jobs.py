"""SYNTHETIC offline production job lifecycle tests."""
import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from contf.production_jobs import audit, build_jobs, reconcile, prepare_retry, main
from contf.production_adapter import REQUIRED_REVIEW
from contf.shot_pipeline import compile_plan


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
    def test_audit_empty_and_unknown(self):
        empty = audit({"project_id": "SYNTHETIC", "jobs": []})
        self.assertFalse(empty["every_shot_accepted"])
        self.assertIsNone(empty["totals"]["cost_per_accepted_minute"])
        result = audit(build_jobs(project(), Path(".")))
        self.assertEqual(result["totals"]["unknown_cost_count"], 0)
        self.assertEqual(result["totals"]["not_produced_count"], 2)
        self.assertIsNone(result["totals"]["known_cost_sum"])
        self.assertIsNone(result["shots"][0]["cost"])

    def test_audit_partial_production_and_unknown_receipt_cost(self):
        queue = build_jobs(project(), Path("."))
        job = queue["jobs"][0]
        job["state"] = "accepted"
        job["media_receipt"] = {"cost": {"amount": 3, "currency": "USD", "source": "SYNTHETIC"}}
        totals = audit(queue)["totals"]
        self.assertEqual(totals["unknown_cost_count"], 0)
        self.assertEqual(totals["not_produced_count"], 1)
        self.assertEqual(totals["cost_per_accepted_minute"], 18)
        queue["jobs"][1]["media_receipt"] = {}
        totals = audit(queue)["totals"]
        self.assertEqual(totals["unknown_cost_count"], 1)
        self.assertEqual(totals["not_produced_count"], 0)
        self.assertIsNone(totals["cost_per_accepted_minute"])

    def test_audit_known_and_mixed_currency(self):
        queue = build_jobs(project(), Path("."))
        for job in queue["jobs"]:
            job["state"] = "accepted"
            job["media_receipt"] = {"cost": {"amount": 2, "currency": "USD", "source": "SYNTHETIC"}}
        result = audit(queue)
        self.assertTrue(result["every_shot_accepted"])
        self.assertEqual(result["totals"]["known_cost_sum"], 4)
        self.assertEqual(result["totals"]["cost_per_accepted_minute"], 12)
        queue["jobs"][0]["media_receipt"]["cost"]["currency"] = "EUR"
        self.assertIsNone(audit(queue)["totals"]["known_cost_sum"])

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

    def test_custom_settings_cli_preserves_approval_and_rejects_override(self):
        project_file = self.root / "project.json"
        queue_file = self.root / "queue.json"
        receipt_file = self.root / "receipt.json"
        project_file.write_text(json.dumps(self.project))
        base = ["jobs", "plan", "--project", str(project_file), "--root", str(self.root)]
        with patch.object(sys, "argv", base + ["--width", "320", "--height", "180", "--fps", "8"]):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 0)
        queue = json.loads(output.getvalue())
        self.assertEqual(queue["plan_settings"], {"width": 320, "height": 180, "fps": 8})
        queue["jobs"][0]["state"] = "accepted"
        queue["jobs"][0]["media_receipt"] = verified_receipt(queue["jobs"][0]["fingerprint"])
        queue_file.write_text(json.dumps(queue))
        (self.root / "S02.mp4").write_bytes(b"SYNTHETIC media")
        receipt = {
            "receipt_version": "0.1.0", "shot_id": "S02", "source_rights": "owned",
            "producer": "SYNTHETIC", "model_version": "SYNTHETIC-1", "media_path": "S02.mp4",
            "reviewer": "SYNTHETIC reviewer", "manual_review": {k: "pass" for k in REQUIRED_REVIEW},
        }
        args = ["--project", str(project_file), "--root", str(self.root), "--queue", str(queue_file)]
        with patch("contf.production_adapter.inspect", return_value={"passed": True, "errors": []}):
            for supplied in (False, True):
                if supplied:
                    receipt["fingerprint"] = queue["jobs"][1]["fingerprint"]
                receipt_file.write_text(json.dumps(receipt))
                argv = ["jobs", "apply", *args, "--receipt", str(receipt_file)]
                with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(), 0)
                applied = json.loads(output.getvalue())
                self.assertTrue(all(j["state"] == "accepted" for j in applied["jobs"]))
                self.assertEqual(applied["plan_settings"], queue["plan_settings"])
            with patch.object(sys, "argv", ["jobs", "ingest", *args, "--receipt", str(receipt_file)]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(), 0)
            report = json.loads(output.getvalue())
            self.assertTrue(report["accepted"])
            receipt_file.write_text(json.dumps(report))
            with patch.object(sys, "argv", ["jobs", "reconcile", *args, "--receipt", str(receipt_file)]):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(), 0)
            self.assertTrue(all(j["state"] == "accepted" for j in json.loads(output.getvalue())["jobs"]))
        original = queue_file.read_bytes()
        for command in ("plan", "reconcile", "ingest", "apply", "retry"):
            for flag, value in (("--width", "640"), ("--height", "360"), ("--fps", "12")):
                argv = ["jobs", command, *args, flag, value, "--output", str(queue_file)]
                with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                    self.assertEqual(main(), 2)
                self.assertIn("conflicts with queue plan_settings", output.getvalue())
                self.assertEqual(queue_file.read_bytes(), original)

    def test_production_fingerprints_are_project_scoped_but_cache_is_not(self):
        other = copy.deepcopy(self.project)
        other["project_id"] = "SYNTHETIC-other-project"
        self.assertEqual(compile_plan(self.project, self.root)["shots"],
                         compile_plan(other, self.root)["shots"])
        queue = build_jobs(self.project, self.root)
        foreign = build_jobs(other, self.root)
        self.assertNotEqual(queue["jobs"][0]["fingerprint"], foreign["jobs"][0]["fingerprint"])
        foreign["jobs"][0]["state"] = "accepted"
        foreign["jobs"][0]["media_receipt"] = verified_receipt(foreign["jobs"][0]["fingerprint"])
        self.assertEqual(reconcile(queue, foreign)["jobs"][0]["state"], "awaiting-human-approval")
        result = reconcile(queue, receipts={"S01": foreign["jobs"][0]["media_receipt"]})
        self.assertEqual(result["jobs"][0]["state"], "blocked-stale-receipt")

    def test_cli_reconcile_ignores_foreign_queue_settings(self):
        foreign_project = copy.deepcopy(self.project)
        foreign_project["project_id"] = "SYNTHETIC-foreign-project"
        foreign = build_jobs(foreign_project, self.root, width=320, height=180, fps=8)
        foreign["jobs"][1].update(state="accepted", media_receipt=verified_receipt(foreign["jobs"][1]["fingerprint"]))
        project_file = self.root / "project.json"
        queue_file = self.root / "foreign-queue.json"
        receipt_file = self.root / "receipt.json"
        project_file.write_text(json.dumps(self.project))
        queue_file.write_text(json.dumps(foreign))
        for settings, flags in (({}, []), ({"width": 480, "height": 270, "fps": 10},
                                         ["--width", "480", "--height", "270", "--fps", "10"])):
            current = build_jobs(self.project, self.root, **settings)
            receipt = {"shot_id": "S01", **verified_receipt(current["jobs"][0]["fingerprint"])}
            receipt_file.write_text(json.dumps(receipt))
            argv = ["jobs", "reconcile", "--project", str(project_file), "--root", str(self.root),
                    "--queue", str(queue_file), "--receipt", str(receipt_file), *flags]
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["plan_settings"], current["plan_settings"])
            self.assertEqual(result["jobs"][0]["state"], "accepted")
            self.assertEqual(result["jobs"][1]["state"], "awaiting-human-approval")
            self.assertEqual(result["rejected_receipts"], [])
        retry = ["jobs", "retry", "--project", str(project_file), "--root", str(self.root),
                 "--queue", str(queue_file), "--shot-id", "S02", "--human-approved"]
        with patch.object(sys, "argv", retry), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 2)
        self.assertIn("retry requires a queue for the current project", output.getvalue())
        self.assertEqual(json.loads(queue_file.read_text()), foreign)

    def test_stale_incoming_receipt_preserves_current_verified_acceptance(self):
        queue = build_jobs(self.project, self.root)
        previous = copy.deepcopy(queue)
        accepted = verified_receipt(queue["jobs"][0]["fingerprint"])
        previous["jobs"][0].update(state="accepted", media_receipt=accepted)
        stale = verified_receipt("SYNTHETIC-stale")
        result = reconcile(queue, previous, {"S01": stale})
        self.assertEqual(result["jobs"][0]["state"], "accepted")
        self.assertEqual(result["jobs"][0]["media_receipt"], accepted)
        self.assertEqual(result["rejected_receipts"][0]["receipt"], stale)
        previous["jobs"][0]["media_receipt"] = {"accepted": True}
        result = reconcile(queue, previous, {"S01": stale})
        self.assertEqual(result["jobs"][0]["state"], "blocked-stale-receipt")

    def test_cli_reconcile_repeatable_ingest_reports(self):
        queue = build_jobs(self.project, self.root)
        paths = []
        for job in queue["jobs"]:
            path = self.root / (job["shot_id"] + ".json")
            path.write_text(json.dumps({"shot_id": job["shot_id"], **verified_receipt(job["fingerprint"])}))
            paths.extend(["--receipt", str(path)])
        project_path = self.root / "project.json"
        project_path.write_text(json.dumps(self.project))
        queue_path = self.root / "queue.json"
        queue_path.write_text(json.dumps(queue))
        argv = ["jobs", "reconcile", "--project", str(project_path), "--root", str(self.root),
                "--queue", str(queue_path), *paths]
        with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(), 0)
        self.assertTrue(all(j["state"] == "accepted" for j in json.loads(output.getvalue())["jobs"]))

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

    def test_apply_rejects_provided_mismatched_fingerprint(self):
        (self.root / "S01.mp4").write_bytes(b"SYNTHETIC local media fixture")
        project_file = self.root / "project.json"
        queue_file = self.root / "queue.json"
        receipt_file = self.root / "receipt.json"
        project_file.write_text(json.dumps(self.project), encoding="utf-8")
        queue_file.write_text(json.dumps(build_jobs(self.project, self.root)), encoding="utf-8")
        receipt = {
            "receipt_version": "0.1.0", "shot_id": "S01", "fingerprint": "stale",
            "source_rights": "owned", "producer": "SYNTHETIC-local",
            "model_version": "fixture-1", "media_path": "S01.mp4",
            "reviewer": "SYNTHETIC reviewer", "accepted": True,
            "manual_review": {key: "pass" for key in REQUIRED_REVIEW},
        }
        receipt_file.write_text(json.dumps(receipt), encoding="utf-8")
        argv = ["production_jobs", "apply", "--project", str(project_file),
                "--root", str(self.root), "--queue", str(queue_file),
                "--receipt", str(receipt_file)]
        with patch("contf.production_adapter.inspect",
                   return_value={"passed": True, "errors": [], "duration_s": 10}):
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["jobs"][0]["state"], "blocked-stale-receipt")
        self.assertIsNone(result["jobs"][0]["media_receipt"])

    def test_apply_and_ingest_require_exactly_one_receipt(self):
        project_file = self.root / "project.json"
        project_file.write_text(json.dumps(self.project), encoding="utf-8")
        for command in ("apply", "ingest"):
            argv = ["production_jobs", command, "--project", str(project_file),
                    "--root", str(self.root), "--receipt", "unused.json",
                    "--receipt", "also-unused.json"]
            with patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(main(), 2)
            self.assertIn("requires exactly one --receipt", output.getvalue())


if __name__ == "__main__":
    unittest.main()

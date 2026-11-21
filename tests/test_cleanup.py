import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contf.cleanup import validate_cleanup_manifest


BASE = {
    "schema_version": "0.1.0",
    "reference_id": "SYNTHETIC-REF-1",
    "source_url": None,
    "captured_at": "2026-11-10T00:00:00Z",
    "source_file": {"name": "synthetic.mp4", "duration_seconds": 20},
    "rights": {"status": "owned", "attested": True, "evidence": "SYNTHETIC"},
    "processor": {"tool_id": "watermarkout", "execution_status": "not-run", "output_file_name": None},
    "regions": [{"x_pct": 75, "y_pct": 5, "width_pct": 20, "height_pct": 10, "start_s": 1, "end_s": 9}],
    "human_review": {"status": "pending", "notes": None},
}


class CleanupManifestTests(unittest.TestCase):
    def test_synthetic_preflight(self):
        self.assertEqual(validate_cleanup_manifest(BASE), [])

    def test_rights_gate(self):
        value = copy.deepcopy(BASE)
        value["rights"] = {"status": "unknown", "attested": False, "evidence": None}
        value["processor"] = {"tool_id": "watermarkout", "execution_status": "completed", "output_file_name": "clean.mp4"}
        self.assertIn("completed cleanup requires verified rights attestation", validate_cleanup_manifest(value))

    def test_frame_and_time_bounds(self):
        value = copy.deepcopy(BASE)
        value["regions"][0].update({"x_pct": 90, "width_pct": 20, "end_s": 21})
        self.assertEqual(len(validate_cleanup_manifest(value)), 2)

    def test_no_false_output(self):
        value = copy.deepcopy(BASE)
        value["processor"]["output_file_name"] = "invented.mp4"
        self.assertIn("not-run cleanup cannot claim an output file", validate_cleanup_manifest(value))

    def test_invalid_enum_types_return_errors(self):
        for field, key, error in (
            ("rights", "status", "rights.status is missing or invalid"),
            ("processor", "tool_id", "processor.tool_id is missing or invalid"),
            ("processor", "execution_status", "processor.execution_status is invalid"),
        ):
            with self.subTest(field=field, key=key):
                value = copy.deepcopy(BASE)
                value[field][key] = []
                self.assertIn(error, validate_cleanup_manifest(value))

    def test_out_of_range_integer_returns_error(self):
        value = copy.deepcopy(BASE)
        value["source_file"]["duration_seconds"] = 10 ** 400
        self.assertIn("source duration must be positive and finite", validate_cleanup_manifest(value))

    def test_completed_cleanup_requires_nonblank_output_name(self):
        for name in (42, "   "):
            with self.subTest(name=name):
                value = copy.deepcopy(BASE)
                value["processor"].update(execution_status="completed", output_file_name=name)
                self.assertIn("completed cleanup requires output_file_name", validate_cleanup_manifest(value))

    def test_provenance_and_human_review_are_required(self):
        value = copy.deepcopy(BASE)
        del value["captured_at"]
        del value["human_review"]
        errors = validate_cleanup_manifest(value)
        self.assertIn("captured_at must be an ISO timestamp with a timezone", errors)
        self.assertIn("human_review.status is missing or invalid", errors)

    def test_invalid_provenance_and_review_notes(self):
        value = copy.deepcopy(BASE)
        value["captured_at"] = "2026-11-10T00:00:00"
        value["human_review"]["notes"] = 1
        errors = validate_cleanup_manifest(value)
        self.assertIn("captured_at must be an ISO timestamp with a timezone", errors)
        self.assertIn("human_review.notes must be a string or null", errors)


if __name__ == "__main__":
    unittest.main()

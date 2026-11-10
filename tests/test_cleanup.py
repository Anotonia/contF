import copy
import unittest

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


if __name__ == "__main__":
    unittest.main()

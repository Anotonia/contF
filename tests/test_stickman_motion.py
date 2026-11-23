"""SYNTHETIC offline contract tests; no generated film or real media claimed."""
import copy
import math
import unittest

from contf.stickman_motion import SCHEMA, fingerprint, sample, two_bone_ik, validate


def fixture():
    return {
        "schema_version": SCHEMA, "shot_id": "S03", "duration_s": 3.2,
        "actors": [
            {"character_id": "ethan", "actions": [
                {"type": "reach", "start_s": 0.4, "end_s": 2.4,
                 "emotion": "confident", "target": {"x": 0.75, "y": 0.42}},
                {"type": "react", "start_s": 2.4, "end_s": 3.2, "emotion": "surprised"},
            ]}
        ],
    }


class MotionTests(unittest.TestCase):
    def test_deterministic_fingerprint_and_sampling(self):
        spec = fixture()
        self.assertEqual(fingerprint(spec), fingerprint(copy.deepcopy(spec)))
        self.assertEqual(sample(spec, 1.4), sample(spec, 1.4))
        self.assertEqual(sample(spec, 1.4)["ethan"]["action"], "reach")

    def test_single_shot_change_invalidates_fingerprint(self):
        a, b = fixture(), fixture()
        b["actors"][0]["actions"][0]["target"]["x"] = 0.8
        self.assertNotEqual(fingerprint(a), fingerprint(b))

    def test_reject_invalid_and_nonfinite_timing(self):
        for duration in [0, -1, float("nan"), float("inf"), True]:
            spec = fixture()
            spec["duration_s"] = duration
            with self.assertRaises(ValueError):
                validate(spec)

    def test_reject_bad_target_and_unknown_action(self):
        spec = fixture()
        spec["actors"][0]["actions"][0]["target"]["x"] = float("nan")
        with self.assertRaises(ValueError):
            validate(spec)
        spec = fixture()
        spec["actors"][0]["actions"][0]["type"] = "teleport"
        with self.assertRaises(ValueError):
            validate(spec)

    def test_ik_reachable_and_unreachable(self):
        origin = (0.0, 0.0)
        for target in [(1.0, 0.5), (100.0, 0.0), (0.0, 0.0)]:
            elbow, wrist = two_bone_ik(origin, target, 1.0, 1.0)
            self.assertAlmostEqual(math.dist(origin, elbow), 1.0, places=6)
            self.assertLessEqual(math.dist(origin, wrist), 2.0)
            self.assertTrue(all(math.isfinite(v) for v in (*elbow, *wrist)))

    def test_no_overlap_action_is_idle(self):
        self.assertEqual(sample(fixture(), 0.1)["ethan"]["action"], "idle")


if __name__ == "__main__":
    unittest.main()

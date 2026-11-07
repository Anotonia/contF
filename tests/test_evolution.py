"""Synthetic contract tests; no network access or credentials."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from contf.evolution import observation_at_age, ratio_per_thousand, review  # noqa: E402


class EvolutionTests(unittest.TestCase):
    def test_selects_matching_age_not_latest_lifetime(self):
        rows = [
            {"experiment_id": "e", "variant_id": "a", "age_hours": 500},
            {"experiment_id": "e", "variant_id": "a", "age_hours": 71},
            {"experiment_id": "e", "variant_id": "a", "age_hours": 75},
        ]
        self.assertEqual(observation_at_age(rows, "e", "a").observation["age_hours"], 71)

    def test_missing_is_not_zero(self):
        self.assertIsNone(ratio_per_thousand(None, 100))
        self.assertIsNone(ratio_per_thousand(0, None))
        self.assertIsNone(ratio_per_thousand(1, 0))
        self.assertEqual(ratio_per_thousand(2, 400), 5.0)

    def test_small_sample_never_promotes(self):
        exp = [{"id": "e", "channel": "demo", "format": "short",
                "hypothesis": "x", "variants": [{"id": "a"}, {"id": "b"}]}]
        rows = [
            {"experiment_id": "e", "variant_id": name, "format": "short",
             "age_hours": 72, "source": "synthetic",
             "metrics": {"engaged_views": count}}
            for name, count in [("a", 100), ("b", 200)]
        ]
        result = review(exp, rows)
        item = result["experiments"][0]
        self.assertEqual(item["decision"], "insufficient-data")
        self.assertIsNone(item["descriptive_leader"])
        self.assertEqual(item["comparable_count"], 2)

    def test_format_mismatch_excluded(self):
        exp = [{"id": "e", "format": "short", "variants": [{"id": "a"}]}]
        rows = [{"experiment_id": "e", "variant_id": "a", "format": "long",
                 "age_hours": 72, "metrics": {"engaged_views": 99}}]
        item = review(exp, rows)["experiments"][0]
        self.assertEqual(item["comparable_count"], 0)

    def test_invalid_config_rejected(self):
        with self.assertRaises(ValueError):
            review([], [], target_hours=-1)


if __name__ == "__main__":
    unittest.main()

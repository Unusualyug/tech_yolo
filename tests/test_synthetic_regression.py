"""Unit test for the seeded 68.1% synthetic ordering regression.

This is the only place where the 1,000-case 68.1% synthetic result is
generated. It validates an ordering invariant and can fail under a broken
selector; it is not an empirical experiment.
"""
from __future__ import annotations

import unittest

try:
    from tests.synthetic_regression import run_audit
except ModuleNotFoundError:  # unittest discovery with tests as top-level dir
    from synthetic_regression import run_audit  # type: ignore


class SyntheticRegressionUnitTest(unittest.TestCase):
    def test_seeded_synthetic_unit_test_can_fail_and_has_expected_invariant(self):
        result = run_audit()
        self.assertEqual("unit_test_artifact", result["evidence_type"])
        self.assertEqual("tests/test_synthetic_regression.py", result["source"])
        self.assertEqual(681, result["legacy_drop_count"])
        self.assertEqual(0, result["updated_drop_count"])

        def broken_selector(objects, alerts, limit):
            return sorted(objects, key=lambda obj: -float(obj["confidence"]))[:limit]

        fixture = [
            {"name": "person", "confidence": 0.20, "distance": 1.0},
            {"name": "chair", "confidence": 0.99, "distance": 1.0},
        ]
        with self.assertRaises(AssertionError):
            selected = broken_selector(fixture, {"person"}, 1)
            self.assertEqual("person", selected[0]["name"])


if __name__ == "__main__":
    unittest.main()

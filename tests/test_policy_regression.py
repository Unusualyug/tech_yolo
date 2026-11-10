"""Deterministic policy regression checks; synthetic fixtures only."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trinexis_core import (  # noqa: E402
    control_request_status,
    legacy_select_speech_objects,
    select_speech_objects,
)

FIXTURE = [
    {"name": "keys", "confidence": 0.20, "distance": 1.0},
    {"name": "chair", "confidence": 0.99, "distance": 1.0},
    {"name": "table", "confidence": 0.98, "distance": 1.0},
]


class AlertPolicyRegressionTests(unittest.TestCase):
    def test_alert_first_keeps_designated_object_before_shortlist_truncation(self):
        selected = select_speech_objects(FIXTURE, {"keys"}, 2)
        self.assertEqual("keys", selected[0]["name"])

    def test_confidence_first_mutation_can_drop_designated_object(self):
        selected = legacy_select_speech_objects(FIXTURE, {"keys"}, 2)
        self.assertNotIn("keys", [item["name"] for item in selected])

    def test_regression_check_can_fail_on_a_broken_ranking(self):
        def broken_selector(objects, alerts, limit):
            return sorted(objects, key=lambda obj: -float(obj["confidence"]))[:limit]

        with self.assertRaises(AssertionError):
            selected = broken_selector(FIXTURE, {"keys"}, 2)
            self.assertEqual("keys", selected[0]["name"])

    def test_control_request_status_distinguishes_401_and_403(self):
        self.assertEqual((True, 200, "Allowed"), control_request_status("", {}))
        result = control_request_status("secret", {}, method="POST")
        self.assertEqual(401, result[1])
        result = control_request_status(
            "secret",
            {"Authorization": "Basic abc"},
            method="POST",
        )
        self.assertEqual(403, result[1])
        result = control_request_status(
            "secret",
            {"X-API-Token": "secret"},
            read_only=True,
            method="POST",
        )
        self.assertEqual(403, result[1])
        result = control_request_status(
            "secret",
            {"Authorization": "Bearer secret"},
            method="POST",
        )
        self.assertEqual((True, 200, "Allowed"), result)

    def test_read_only_does_not_block_get_in_helper(self):
        self.assertEqual(
            (True, 200, "Allowed"),
            control_request_status("", {}, read_only=True, method="GET"),
        )


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trinexis_core import (  # noqa: E402
    ALLOWED_MODELS,
    camera_config,
    legacy_select_speech_objects,
    normalize_model_name,
    rate_per_second,
    relative_distance_index,
    select_speech_objects,
    single_client_check,
    time_decay_factor,
    validate_control_request,
)


class CorePolicyTests(unittest.TestCase):
    def test_camera_config_defaults(self):
        cfg = camera_config({})
        self.assertEqual(cfg, {"index": 1, "backend": "AUTO"})

    def test_camera_config_custom_environment(self):
        cfg = camera_config(
            {"TRINEXIS_CAMERA_INDEX": "0", "TRINEXIS_CAMERA_BACKEND": "v4l2"}
        )
        self.assertEqual(cfg, {"index": 0, "backend": "V4L2"})

    def test_camera_config_rejects_unknown_backend(self):
        with self.assertRaises(ValueError):
            camera_config({"TRINEXIS_CAMERA_BACKEND": "UNKNOWN"})

    def test_normalize_model_name_accepts_allowlist(self):
        for name in ALLOWED_MODELS:
            self.assertEqual(normalize_model_name(name), name)

    def test_normalize_model_name_rejects_arbitrary_path(self):
        with self.assertRaises(ValueError):
            normalize_model_name("../../etc/passwd")

    def test_alert_first_selection_preserves_low_confidence_alert(self):
        objects = [
            {"name": "cup", "confidence": 0.91, "distance": 10.0},
            {"name": "chair", "confidence": 0.82, "distance": 20.0},
            {"name": "person", "confidence": 0.21, "distance": 50.0},
        ]
        selected = select_speech_objects(objects, {"person"}, 2)
        self.assertEqual([o["name"] for o in selected][0], "person")

    def test_legacy_selection_reproduces_alert_drop(self):
        objects = [
            {"name": "cup", "confidence": 0.91, "distance": 10.0},
            {"name": "chair", "confidence": 0.82, "distance": 20.0},
            {"name": "person", "confidence": 0.21, "distance": 50.0},
        ]
        selected = legacy_select_speech_objects(objects, {"person"}, 2)
        self.assertNotIn("person", [o["name"] for o in selected])

    def test_time_decay_factor_is_half_at_one_half_life(self):
        self.assertAlmostEqual(time_decay_factor(60.0, 60.0), 0.5)

    def test_time_decay_factor_is_frame_rate_independent(self):
        single = time_decay_factor(4.0, 2.0)
        split = time_decay_factor(1.0, 2.0) * time_decay_factor(3.0, 2.0)
        self.assertAlmostEqual(single, split)

    def test_relative_distance_index_has_no_negative_denominator(self):
        self.assertGreater(relative_distance_index(0), 0)
        self.assertEqual(relative_distance_index(0), 60.0 * 360.0)

    def test_rate_per_second_counts_recent_events_only(self):
        rate = rate_per_second([9.0, 9.5, 1.0], now=10.0, window_s=5.0)
        self.assertAlmostEqual(rate, 2.0 / 5.0)

    def test_validate_control_request_allows_when_token_unset(self):
        self.assertTrue(validate_control_request("", {}))

    def test_validate_control_request_requires_matching_token(self):
        self.assertTrue(
            validate_control_request("secret", {"X-API-Token": "secret"})
        )
        self.assertTrue(
            validate_control_request(
                "secret", {"Authorization": "Bearer secret"}
            )
        )
        self.assertFalse(validate_control_request("secret", {}))

    def test_single_client_check_reclaims_stale_session(self):
        allowed, active, seen = single_client_check(
            "old-client", "new-client", last_seen=0.0, now=120.0, timeout_s=60.0
        )
        self.assertTrue(allowed)
        self.assertEqual(active, "new-client")
        self.assertEqual(seen, 120.0)


if __name__ == "__main__":
    unittest.main()

"""Real Flask test-client route tests for all 23 maintained endpoints.

Camera, detector, NumPy, and TTS imports are mocked with ``unittest.mock`` by
``route_test_support``. These tests verify HTTP behavior, not model accuracy,
runtime latency, speech quality, or user benefit.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest import mock

from route_test_support import (
    ROOT,
    load_app,
    new_client,
    reset_state,
    route_inventory,
)

# One status test is generated for every declared route in app23.py.
ROUTE_CASES = [
    {"path": "/", "method": "GET", "mimetype": "text/html"},
    {"path": "/video_feed", "method": "GET", "mimetype": "multipart/x-mixed-replace"},
    {"path": "/start_detection", "method": "POST", "json": {}, "body_status": "running"},
    {"path": "/stop_detection", "method": "POST", "json": {}, "body_status": "stopped"},
    {"path": "/set_language", "method": "POST", "json": {"language": "Hindi"}, "body_status": "success", "language": "Hindi"},
    {"path": "/set_confidence", "method": "POST", "json": {"threshold": 0.25}, "body_status": "success", "confidence": 0.25},
    {"path": "/set_interval", "method": "POST", "json": {"interval": 2.0}, "body_status": "success", "interval": 2.0},
    {"path": "/set_resolution", "method": "POST", "json": {"resolution": 832}, "body_status": "success", "resolution": 832},
    {"path": "/set_model", "method": "POST", "json": {"model": "yolov8s-worldv2.pt"}, "body_status": "success", "model": "yolov8s-worldv2.pt"},
    {"path": "/toggle_speech", "method": "POST", "json": {}, "body_status": "success", "speech_enabled": False},
    {"path": "/set_speech_cooldown", "method": "POST", "json": {"cooldown": 6.0}, "body_status": "success", "cooldown": 6.0},
    {"path": "/set_max_speak_objects", "method": "POST", "json": {"max_objects": 3}, "body_status": "success", "max_objects": 3},
    {"path": "/set_custom_vocab", "method": "POST", "json": {"words": ["test object"]}, "body_status": "success", "expect_total_classes_gt": 455},
    {"path": "/set_alerts", "method": "POST", "json": {"objects": ["keys"]}, "body_status": "success", "alerts": ["keys"], "total": 1},
    {"path": "/get_languages", "method": "GET", "json_keys": ["current", "indian", "international", "all", "english_fallback_languages", "verified_languages", "support_note"]},
    {"path": "/get_logs", "method": "GET", "json_keys": ["logs", "stats"]},
    {"path": "/clear_logs", "method": "POST", "json": {}, "body_status": "success"},
    {"path": "/snapshot", "method": "GET", "expected_status": 404, "json_keys": ["error"]},
    {"path": "/heatmap", "method": "GET", "expected_status": 404, "json_keys": ["error"]},
    {"path": "/export_logs", "method": "GET", "mimetype": "application/json"},
    {"path": "/get_classes", "method": "GET", "json_keys": ["classes", "total"]},
    {"path": "/get_camera", "method": "GET", "json_keys": ["status", "camera_index", "width", "height"]},
    {"path": "/health", "method": "GET", "json_keys": ["status", "service", "model", "classes", "languages"]},
]

POST_ROUTES = [path for path, method in route_inventory() if method == "POST"]
PAYLOAD_ROUTES = [
    "/set_language",
    "/set_confidence",
    "/set_interval",
    "/set_resolution",
    "/set_model",
    "/set_speech_cooldown",
    "/set_max_speak_objects",
    "/set_custom_vocab",
    "/set_alerts",
]


class RouteStatusTests(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.client = new_client(self.app)

    def test_every_declared_route_has_a_status_case(self):
        declared = route_inventory()
        covered = {(case["path"], case["method"]) for case in ROUTE_CASES}
        self.assertEqual(23, len(declared))
        self.assertEqual(set(declared), covered)
        self.assertEqual(23, len(ROUTE_CASES))

    def _invoke(self, case, headers=None):
        path = case["path"]
        headers = headers or {}
        if case["method"] == "GET":
            return self.client.get(path, headers=headers)
        return self.client.post(path, json=case.get("json", {}), headers=headers)

    def _check_route(self, case):
        if case["path"] == "/video_feed":
            payload = iter([b"--frame\r\nContent-Type: image/jpeg\r\n\r\nJPEG\r\n\r\n"])
            with mock.patch.object(self.app, "generate_feed", return_value=payload):
                response = self._invoke(case)
        else:
            response = self._invoke(case)

        expected = case.get("expected_status", 200)
        self.assertEqual(expected, response.status_code)
        if "mimetype" in case:
            self.assertTrue(response.mimetype.startswith(case["mimetype"]))
        if case["path"] == "/video_feed":
            self.assertTrue(response.is_streamed)
            self.assertIn(b"--frame", b"".join(response.response))
        if case["path"] == "/export_logs":
            self.assertIn(".json", response.headers.get("Content-Disposition", ""))
        if "json_keys" in case or "body_status" in case:
            data = response.get_json()
            self.assertIsInstance(data, dict)
            for key in case.get("json_keys", []):
                self.assertIn(key, data)
            if "body_status" in case:
                self.assertEqual(case["body_status"], data["status"])
        for key in ("language", "confidence", "interval", "resolution", "model", "speech_enabled", "cooldown", "max_objects", "alerts", "total"):
            if key in case:
                self.assertEqual(case[key], response.get_json()[key])
        if "expect_total_classes_gt" in case:
            self.assertGreater(response.get_json()["total_classes"], case["expect_total_classes_gt"])
        if case["path"] == "/get_languages":
            data = response.get_json()
            self.assertEqual([], data["verified_languages"])
            self.assertIn("Amharic", data["english_fallback_languages"])
            self.assertIn("Google Translate", data["support_note"])
        if case["path"] == "/get_logs":
            stats = response.get_json()["stats"]
            for key in ("alert_objects", "alert_manifest_sha256", "latency_log_enabled", "event_log_enabled"):
                self.assertIn(key, stats)


def _make_route_test(case):
    def test(self):
        self._check_route(case)
    return test


for index, route_case in enumerate(ROUTE_CASES, start=1):
    slug = re.sub(r"[^a-z0-9]+", "_", route_case["path"].strip("/").lower()).strip("_") or "root"
    setattr(RouteStatusTests, f"test_route_{index:02d}_{slug}", _make_route_test(route_case))


class InputValidationTests(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.client = new_client(self.app)

    def test_non_object_json_returns_400_on_all_payload_routes(self):
        for path in PAYLOAD_ROUTES:
            with self.subTest(path=path):
                response = self.client.post(path, json=["not", "an", "object"])
                self.assertEqual(400, response.status_code)
                self.assertEqual("error", response.get_json()["status"])

    def test_confidence_invalid_value_and_clamping(self):
        self.assertEqual(400, self.client.post("/set_confidence", json={"threshold": "bad"}).status_code)
        self.assertEqual(0.95, self.client.post("/set_confidence", json={"threshold": 2.0}).get_json()["confidence"])
        self.assertEqual(0.05, self.client.post("/set_confidence", json={"threshold": -1.0}).get_json()["confidence"])

    def test_interval_invalid_value_and_clamping(self):
        self.assertEqual(400, self.client.post("/set_interval", json={"interval": "bad"}).status_code)
        self.assertEqual(10.0, self.client.post("/set_interval", json={"interval": 100.0}).get_json()["interval"])
        self.assertEqual(0.2, self.client.post("/set_interval", json={"interval": -1.0}).get_json()["interval"])

    def test_resolution_invalid_value_and_disallowed_value(self):
        self.assertEqual(400, self.client.post("/set_resolution", json={"resolution": "bad"}).status_code)
        self.assertEqual(640, self.client.post("/set_resolution", json={"resolution": 999}).get_json()["resolution"])
        self.assertEqual(832, self.client.post("/set_resolution", json={"resolution": 832}).get_json()["resolution"])

    def test_model_allowlist_rejects_unknown_model(self):
        response = self.client.post("/set_model", json={"model": "unknown.pt"})
        self.assertEqual(400, response.status_code)
        self.assertIn("Unsupported model", response.get_json()["message"])

    def test_speech_cooldown_invalid_value_and_clamping(self):
        self.assertEqual(400, self.client.post("/set_speech_cooldown", json={"cooldown": "bad"}).status_code)
        self.assertEqual(30.0, self.client.post("/set_speech_cooldown", json={"cooldown": 100.0}).get_json()["cooldown"])
        self.assertEqual(1.0, self.client.post("/set_speech_cooldown", json={"cooldown": -1.0}).get_json()["cooldown"])

    def test_max_speak_objects_invalid_value_and_clamping(self):
        self.assertEqual(400, self.client.post("/set_max_speak_objects", json={"max_objects": "bad"}).status_code)
        self.assertEqual(4, self.client.post("/set_max_speak_objects", json={"max_objects": 100}).get_json()["max_objects"])
        self.assertEqual(1, self.client.post("/set_max_speak_objects", json={"max_objects": -1}).get_json()["max_objects"])

    def test_custom_vocab_rejects_non_list_and_ignores_empty_list(self):
        self.assertEqual(400, self.client.post("/set_custom_vocab", json={"words": "bad"}).status_code)
        before = len(self.app.VOCABULARY)
        response = self.client.post("/set_custom_vocab", json={"words": []})
        self.assertEqual(200, response.status_code)
        self.assertEqual(before, len(self.app.VOCABULARY))

    def test_alerts_non_list_is_coerced_to_empty_and_valid_list_is_sorted(self):
        response = self.client.post("/set_alerts", json={"objects": "keys"})
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.get_json()["alerts"])
        response = self.client.post("/set_alerts", json={"objects": ["phone", "keys", "keys", ""]})
        self.assertEqual(["keys", "phone"], response.get_json()["alerts"])

    def test_invalid_language_falls_back_to_english(self):
        response = self.client.post("/set_language", json={"language": "Not a language"})
        self.assertEqual(200, response.status_code)
        self.assertEqual("English", response.get_json()["language"])


class ControlPolicyRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = load_app()
        self.client = new_client(self.app)

    def test_get_routes_bypass_mutation_token(self):
        self.app.API_TOKEN = "secret"
        self.assertEqual(200, self.client.get("/health").status_code)

    def test_missing_or_wrong_token_returns_401_for_all_post_routes(self):
        self.app.API_TOKEN = "secret"
        for path in POST_ROUTES:
            with self.subTest(path=path, kind="missing"):
                self.assertEqual(401, self.client.post(path, json={}).status_code)
            with self.subTest(path=path, kind="wrong"):
                self.assertEqual(401, self.client.post(path, json={}, headers={"X-API-Token": "wrong"}).status_code)

    def test_valid_x_api_token_allows_all_post_routes(self):
        self.app.API_TOKEN = "secret"
        for path in POST_ROUTES:
            with self.subTest(path=path):
                reset_state(self.app)
                response = self.client.post(path, json={}, headers={"X-API-Token": "secret"})
                self.assertEqual(200, response.status_code)

    def test_valid_bearer_token_allows_control_request(self):
        self.app.API_TOKEN = "secret"
        response = self.client.post("/start_detection", json={}, headers={"Authorization": "Bearer secret"})
        self.assertEqual(200, response.status_code)

    def test_unsupported_authorization_scheme_returns_403(self):
        self.app.API_TOKEN = "secret"
        response = self.client.post("/start_detection", json={}, headers={"Authorization": "Basic abc"})
        self.assertEqual(403, response.status_code)
        self.assertIn("Unsupported authorization scheme", response.get_json()["message"])

    def test_read_only_mode_returns_403_with_valid_token(self):
        self.app.API_TOKEN = "secret"
        self.app.READ_ONLY_MODE = True
        response = self.client.post("/start_detection", json={}, headers={"X-API-Token": "secret"})
        self.assertEqual(403, response.status_code)
        self.assertEqual(200, self.client.get("/health").status_code)

    def test_single_client_conflict_returns_409(self):
        self.app.SINGLE_CLIENT_MODE = True
        first = self.app.app.test_client()
        second = self.app.app.test_client()
        self.assertEqual(200, first.post("/start_detection", json={}).status_code)
        response = second.post("/start_detection", json={})
        self.assertEqual(409, response.status_code)

    def test_predeclared_alert_manifest_freezes_set_alerts(self):
        self.app.ALERT_MANIFEST_OBJECTS = ["keys"]
        self.app.ALERT_MANIFEST_SHA256 = "fixture-sha256"
        self.app.alert_objects = {"keys"}
        response = self.client.post("/set_alerts", json={"objects": ["phone"]})
        self.assertEqual(403, response.status_code)
        self.assertEqual(["keys"], response.get_json()["alerts"])

    def test_ui_documents_english_fallback_and_unchecked_languages(self):
        html = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "static" / "script.js").read_text(encoding="utf-8")
        self.assertIn("Missing templates fall back to English", html)
        self.assertIn("language-support-note", html)
        self.assertIn("data.support_note", script)


if __name__ == "__main__":
    unittest.main()

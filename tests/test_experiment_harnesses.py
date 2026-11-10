"""Software self-checks for empirical harnesses; no measured data shipped."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments import (  # noqa: E402
    alert_replay,
    common,
    detection_eval,
    language_eval,
    latency_benchmark,
    multi_session_replay,
    user_study,
    vocab_confidence_grid,
)


class HarnessSelfCheckTests(unittest.TestCase):
    def test_all_harness_self_checks_are_labelled_software_only(self):
        for module in (
            latency_benchmark,
            detection_eval,
            vocab_confidence_grid,
            alert_replay,
            language_eval,
            multi_session_replay,
            user_study,
        ):
            with self.subTest(module=module.__name__):
                self.assertEqual(common.SELF_CHECK, module.self_check()["status"])

    def test_latency_blank_template_has_no_numbers(self):
        result = latency_benchmark.blank_result()
        self.assertEqual(common.NO_DATA, result["status"])
        self.assertEqual(15, len(result["cells"]))
        self.assertTrue(all(cell["median_ms"] is None for cell in result["cells"]))
        self.assertTrue(all(cell["p95_ms"] is None for cell in result["cells"]))

    def test_latency_rejects_incomplete_real_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "latency.jsonl"
            path.write_text(
                json.dumps({"stage": "capture_ms", "duration_ms": 1.0, "imgsz": 640}) + "\n",
                encoding="utf-8",
            )
            result = latency_benchmark.summarize_log(path, None, min_frames=500)
            self.assertEqual(common.INSUFFICIENT_DATA, result["status"])
            self.assertEqual([], result["summary"])

    def test_detection_blank_template_has_no_metrics(self):
        result = detection_eval.blank_result()
        self.assertEqual(common.NO_DATA, result["status"])
        self.assertEqual(3, len(result["cells"]))
        self.assertTrue(all(cell["map50"] is None for cell in result["cells"]))

    def test_vocabulary_grid_has_twelve_blank_cells(self):
        result = vocab_confidence_grid.blank_result()
        self.assertEqual(common.NO_DATA, result["status"])
        self.assertEqual(12, len(result["cells"]))
        self.assertTrue(all(cell["precision"] is None for cell in result["cells"]))

    def test_alert_replay_blank_template_has_no_delivery_or_delay(self):
        result = alert_replay.blank_result()
        self.assertEqual(common.NO_DATA, result["status"])
        self.assertEqual(4, len(result["cells"]))
        self.assertEqual(
            ["alert_first", "confidence_first", "nearest_first"],
            [cell.get("policy") for cell in result["cells"][:3]],
        )
        self.assertTrue(all(cell.get("mean_alert_to_speech_ms") is None for cell in result["cells"][:3]))
        multi = multi_session_replay.blank_result()
        self.assertEqual(4, len(multi["cells"]))
        self.assertTrue(all(cell["status"] == common.NO_DATA for cell in multi["cells"]))
        study = user_study.blank_result()
        self.assertEqual(3, len(study["cells"]))
        self.assertEqual("nearest_first", study["cells"][2].get("policy"))

    def test_alert_replay_rejects_explicitly_synthetic_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            manifest = folder / "manifest.json"
            detection = folder / "frames.json"
            events = folder / "events.jsonl"
            manifest.write_text(
                json.dumps({"declared_at": "2026-11-10T00:00:00Z", "alert_objects": ["keys"]}),
                encoding="utf-8",
            )
            detection.write_text(
                json.dumps([{
                    "synthetic": True,
                    "timestamp_unix": 1.0,
                    "objects": [{"name": "keys", "confidence": 0.9}],
                }]),
                encoding="utf-8",
            )
            events.write_text("", encoding="utf-8")
            args = SimpleNamespace(
                alert_manifest=str(manifest),
                detection_log=str(detection),
                event_log=str(events),
                limit=2,
                cooldown=4.5,
            )
            result = alert_replay.run_replay(args)
            self.assertEqual(common.INSUFFICIENT_DATA, result["status"])
            self.assertTrue(any("synthetic" in reason for reason in result["reasons"]))

    def test_language_blank_worksheet_has_no_ratings(self):
        result = language_eval.blank_result(["Hindi", "Gujarati", "Bengali", "Tamil", "Spanish"])
        self.assertEqual(common.NO_DATA, result["status"])
        self.assertEqual(5, len(result["cells"]))
        self.assertTrue(all(cell["mean_correctness"] is None for cell in result["cells"]))


if __name__ == "__main__":
    unittest.main()

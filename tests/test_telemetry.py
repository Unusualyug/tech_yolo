"""Software-only checks for the optional latency/event recorder."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trinexis_telemetry import (  # noqa: E402
    LatencyRecorder,
    percentile,
    summarize_latency,
    timed,
)


class TelemetryTests(unittest.TestCase):
    def test_timed_returns_result_and_nonnegative_duration(self):
        result, duration = timed(lambda value: value + 1, 2)
        self.assertEqual(3, result)
        self.assertGreaterEqual(duration, 0.0)

    def test_nearest_rank_percentile(self):
        self.assertEqual(5.0, percentile([1, 2, 3, 4, 5], 0.95))
        self.assertIsNone(percentile([], 0.95))

    def test_summarize_latency_groups_fixture_rows(self):
        rows = [
            {"setting": "fixture", "imgsz": 640, "stage": "infer_ms", "duration_ms": 10},
            {"setting": "fixture", "imgsz": 640, "stage": "infer_ms", "duration_ms": 20},
            {"setting": "fixture", "imgsz": 640, "stage": "infer_ms", "duration_ms": 30},
        ]
        summary = summarize_latency(rows)
        self.assertEqual(1, len(summary))
        self.assertEqual(3, summary[0]["count"])
        self.assertEqual(20, summary[0]["median_ms"])
        self.assertEqual(30, summary[0]["p95_ms"])

    def test_disabled_recorder_writes_nothing(self):
        recorder = LatencyRecorder(None)
        recorder.record("capture_ms", 1.0)
        recorder.event("fixture")
        self.assertFalse(recorder.enabled)

    def test_enabled_recorder_writes_duration_and_event_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            recorder = LatencyRecorder(path, setting="software-test", metadata={"fixture": True})
            recorder.record("capture_ms", 1.0)
            recorder.event("speech_enqueued", language="English")
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(2, len(lines))
            rows = [json.loads(line) for line in lines]
            self.assertEqual("capture_ms", rows[0]["stage"])
            self.assertEqual("speech_enqueued", rows[1]["event"])
            self.assertEqual("software-test", rows[1]["setting"])


if __name__ == "__main__":
    unittest.main()

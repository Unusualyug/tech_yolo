#!/usr/bin/env python3
"""Dependency-free latency instrumentation and summary helpers.

The recorder writes one JSON object per line. It is intentionally optional:
when no ``TRINEXIS_LATENCY_LOG`` path is configured, every call is a no-op.
No empirical measurements are shipped in this repository.
"""
from __future__ import annotations

import json
import statistics
import threading
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

STAGES = (
    "capture_ms",
    "infer_ms",
    "tts_ms",
    "playback_ms",
    "render_ms",
)


def timed(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> tuple[Any, float]:
    """Return ``(result, elapsed_milliseconds)`` for one callable."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, (time.perf_counter() - start) * 1000.0


def percentile(values: Sequence[float], p: float = 0.95) -> float | None:
    """Nearest-rank percentile matching ``sorted(values)[int(p * len(values))]``."""
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    index = min(len(ordered) - 1, int(float(p) * len(ordered)))
    return ordered[index]


def load_latency_records(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSONL latency log; blank lines and malformed rows are skipped."""
    records: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            records.append(row)
    return records


def summarize_latency(
    records: Iterable[Mapping[str, Any]],
    stages: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Group JSONL rows and report count, median, and 95th percentile."""
    allowed = set(stages) if stages is not None else set(STAGES)
    grouped: dict[tuple[Any, ...], list[float]] = defaultdict(list)
    hardware: dict[tuple[Any, ...], str | None] = {}

    for row in records:
        stage = str(row.get("stage", ""))
        if stage not in allowed:
            continue
        try:
            duration = float(row.get("duration_ms"))
        except (TypeError, ValueError):
            continue
        key = (
            str(row.get("setting", "default")),
            row.get("imgsz"),
            row.get("confidence"),
            row.get("vocab_size"),
            stage,
        )
        grouped[key].append(duration)
        hardware.setdefault(key, row.get("hardware_manifest"))

    summary: list[dict[str, Any]] = []
    for key in sorted(grouped, key=lambda item: tuple(str(part) for part in item)):
        values = grouped[key]
        setting, imgsz, confidence, vocab_size, stage = key
        summary.append(
            {
                "setting": setting,
                "imgsz": imgsz,
                "confidence": confidence,
                "vocab_size": vocab_size,
                "stage": stage,
                "hardware_manifest": hardware.get(key),
                "count": len(values),
                "median_ms": statistics.median(values),
                "p95_ms": percentile(values, 0.95),
                "min_ms": min(values),
                "max_ms": max(values),
            }
        )
    return summary


class LatencyRecorder:
    """Append timestamped stage durations to a JSONL file."""

    def __init__(
        self,
        log_path: str | Path | None,
        setting: str = "default",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.setting = str(setting or "default")
        self.metadata = dict(metadata or {})
        self.path = Path(log_path) if log_path else None
        self.enabled = self.path is not None
        self._lock = threading.Lock()
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, row: dict[str, Any]) -> None:
        if not self.enabled or self.path is None:
            return
        row = {
            "timestamp": time.time(),
            "setting": self.setting,
            **self.metadata,
            **row,
        }
        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def record(self, stage: str, duration_ms: float, **fields: Any) -> None:
        self._write({"stage": stage, "duration_ms": float(duration_ms), **fields})

    def event(self, event_type: str, **fields: Any) -> None:
        """Record a non-duration event, such as a speech enqueue/playback."""
        self._write({"event": event_type, **fields})

    def timed(
        self,
        stage: str,
        fn: Callable[..., Any],
        *args: Any,
        _fields: Mapping[str, Any] | None = None,
        **kwargs: Any,
    ) -> tuple[Any, float]:
        result, duration_ms = timed(fn, *args, **kwargs)
        self.record(stage, duration_ms, **(_fields or {}))
        return result, duration_ms

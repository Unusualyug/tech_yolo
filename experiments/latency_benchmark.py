#!/usr/bin/env python3
"""Experiment A: real-hardware latency logging and blank-result reporting.

Usage:
  python3 experiments/latency_benchmark.py --self-check
  python3 experiments/latency_benchmark.py --emit-blank
  python3 experiments/latency_benchmark.py --summarize path/to/latency.jsonl \
      --hardware-manifest experiments/hardware_manifest.json \
      --output experiments/results/latency_results.json

The application writes JSONL when ``TRINEXIS_LATENCY_LOG`` is configured. No
measured value is bundled with this repository; incomplete logs never become a
published result.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments import common
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    import common  # type: ignore

from trinexis_telemetry import STAGES, load_latency_records, percentile, summarize_latency

IMG_SIZES = (416, 640, 832)
MIN_FRAMES = 500


def plan_cells() -> list[dict[str, Any]]:
    """Return one explicitly blank cell per required setting/stage."""
    return [
        common.blank_cell(
            setting="default",
            imgsz=imgsz,
            stage=stage,
            count=None,
            median_ms=None,
            p95_ms=None,
            min_frames_required=MIN_FRAMES,
        )
        for imgsz in IMG_SIZES
        for stage in STAGES
    ]


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "A-latency",
        plan_cells(),
        protocol=(
            "Run the live app with TRINEXIS_LATENCY_LOG set. Declare hardware "
            "and software before collection; collect at least 500 camera "
            "frames per 416/640/832 setting. Report median and p95 for "
            "capture, inference, TTS synthesis, playback, and rendering."
        ),
        hardware_declaration_required=list(common.REQUIRED_HARDWARE_KEYS),
    )


def _capture_counts(records: Sequence[Mapping[str, Any]]) -> Counter:
    counts: Counter = Counter()
    for row in records:
        if row.get("stage") != "capture_ms":
            continue
        try:
            imgsz = int(row["imgsz"])
        except (KeyError, TypeError, ValueError):
            continue
        key = (str(row.get("setting", "default")), imgsz)
        counts[key] += 1
    return counts


def summarize_log(
    log_path: str | Path,
    hardware_manifest: Mapping[str, Any] | None,
    min_frames: int = MIN_FRAMES,
) -> dict[str, Any]:
    """Summarize a real JSONL log, or return INSUFFICIENT DATA with reasons."""
    records = common.assert_real_log(load_latency_records(log_path), "latency log")
    counts = _capture_counts(records)
    reasons: list[str] = []

    if hardware_manifest is None:
        reasons.append("hardware manifest not supplied")
    else:
        missing = common.validate_hardware_manifest(hardware_manifest)
        if missing:
            reasons.append("incomplete hardware manifest: " + ", ".join(missing))

    for setting in sorted({key[0] for key in counts}) or ["default"]:
        for imgsz in IMG_SIZES:
            observed = counts[(setting, imgsz)]
            if observed < min_frames:
                reasons.append(
                    f"{setting}/{imgsz}: {observed} capture frames; "
                    f"requires at least {min_frames}"
                )

    hardware_digest = (
        common.canonical_sha256(hardware_manifest) if hardware_manifest else None
    )
    if reasons:
        return {
            "experiment": "A-latency",
            "status": common.INSUFFICIENT_DATA,
            "warning": "No empirical latency result is reported from incomplete data.",
            "reasons": reasons,
            "hardware_manifest": hardware_manifest,
            "hardware_manifest_sha256": hardware_digest,
            "software_manifest": "requirements.txt",
            "capture_frame_counts": [
                {"setting": setting, "imgsz": imgsz, "count": count}
                for (setting, imgsz), count in sorted(counts.items())
            ],
            "summary": [],
        }

    return {
        "experiment": "A-latency",
        "status": common.MEASURED,
        "warning": "Author must personally verify every number before publication.",
        "hardware_manifest": hardware_manifest,
        "hardware_manifest_sha256": hardware_digest,
        "software_manifest": "requirements.txt",
        "min_frames_per_setting": min_frames,
        "summary": summarize_latency(records),
    }


def self_check() -> dict[str, Any]:
    """Exercise summary arithmetic on a tiny in-memory fixture only."""
    fixture = [
        {"stage": "capture_ms", "duration_ms": value, "setting": "fixture", "imgsz": 640}
        for value in (1.0, 2.0, 3.0, 4.0, 5.0)
    ]
    summary = summarize_latency(fixture)
    assert summary[0]["median_ms"] == 3.0
    assert percentile([1.0, 2.0, 3.0, 4.0, 5.0], 0.95) == 5.0
    assert all(cell["status"] == common.NO_DATA for cell in plan_cells())
    return {"status": common.SELF_CHECK, "scope": "in-memory arithmetic fixture"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-blank", action="store_true")
    group.add_argument("--summarize", metavar="JSONL")
    parser.add_argument("--hardware-manifest", metavar="JSON")
    parser.add_argument("--output", default="experiments/results/latency_results.json")
    parser.add_argument("--min-frames", type=int, default=MIN_FRAMES)
    args = parser.parse_args()

    if args.self_check:
        print(self_check()["status"])
        return 0

    if args.emit_blank:
        path = common.write_json(args.output, blank_result())
        print(f"Wrote blank template: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0

    manifest = None
    if args.hardware_manifest:
        manifest = common.load_json(args.hardware_manifest)
    result = summarize_log(args.summarize, manifest, args.min_frames)
    path = common.write_json(args.output, result)
    print(f"{result['status']}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

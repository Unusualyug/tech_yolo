#!/usr/bin/env python3
"""Experiment C: aggregate 5-10 real sessions under three ordering policies.

The manifest must be declared before collection. Each session needs a real
``/export_logs`` JSON file and a real ``TRINEXIS_EVENT_LOG`` speech-event JSONL
file collected under the same predeclared alert manifest. Explicitly synthetic
rows and incomplete session sets are rejected. This script never substitutes
fixture data for a real session.
"""
from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments import alert_replay, common
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    import alert_replay  # type: ignore
    import common  # type: ignore


def repo_path(value: str | Path) -> Path:
    """Resolve a manifest path against the repository root."""
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def validate_manifest(payload: Mapping[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    """Return validation problems and normalized real-session declarations."""
    problems: list[str] = []
    if not payload.get("declared_at"):
        problems.append("declared_at is required before data collection")
    if not payload.get("alert_manifest"):
        problems.append("alert_manifest path is required")
    sessions = payload.get("sessions")
    if not isinstance(sessions, list):
        problems.append("sessions must be a list")
        return problems, []
    try:
        rows = common.assert_real_log(
            [dict(row) for row in sessions if isinstance(row, dict)],
            "session manifest",
        )
    except ValueError as exc:
        problems.append(str(exc))
        return problems, []
    if not 5 <= len(rows) <= 10:
        problems.append("sessions must contain 5 to 10 real sessions")
    normalized: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=1):
        session_id = str(row.get("session_id", "")).strip()
        detection_log = str(row.get("detection_log", "")).strip()
        event_log = str(row.get("event_log", "")).strip()
        if not session_id:
            problems.append(f"session {index}: session_id is required")
        elif session_id in seen_ids:
            problems.append(f"duplicate session_id: {session_id}")
        seen_ids.add(session_id)
        if not detection_log:
            problems.append(f"session {index}: detection_log is required")
        if not event_log:
            problems.append(f"session {index}: event_log is required")
        normalized.append({
            "session_id": session_id,
            "detection_log": detection_log,
            "event_log": event_log,
        })
    return problems, normalized


def weighted_mean(values: list[tuple[float | None, int]]) -> float | None:
    """Mean of per-session means weighted by their nonzero event counts."""
    usable = [(float(value), count) for value, count in values if value is not None and count > 0]
    total = sum(count for _, count in usable)
    if not total:
        return None
    return sum(value * count for value, count in usable) / total


def aggregate_policy(policy: str, sessions: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate one policy across real session results without inventing data."""
    records = [next(row for row in s["policies"] if row["policy"] == policy) for s in sessions]
    delivered = sum(int(row["alert_objects_delivered"]) for row in records)
    seen = sum(int(row["alert_objects_seen"]) for row in records)
    weights = [(row["mean_alert_to_speech_ms"], int(row["alert_objects_delivered"])) for row in records]
    return {
        "policy": policy,
        "sessions": len(records),
        "frames_replayed": sum(int(row["frames_replayed"]) for row in records),
        "speech_opportunities": sum(int(row["speech_opportunities"]) for row in records),
        "alert_objects_seen": seen,
        "alert_objects_delivered": delivered,
        "delivery_rate": delivered / seen if seen else None,
        "session_weighted_mean_alert_to_speech_ms": weighted_mean(weights),
        "mean_of_session_means_alert_to_speech_ms": (
            statistics.mean(
                float(row["mean_alert_to_speech_ms"])
                for row in records
                if row["mean_alert_to_speech_ms"] is not None
            )
            if any(row["mean_alert_to_speech_ms"] is not None for row in records)
            else None
        ),
    }


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "C-multi-session-replay",
        [
            common.blank_cell(policy=policy, delivery_rate=None, mean_alert_to_speech_ms=None)
            for policy in alert_replay.POLICIES
        ] + [
            common.blank_cell(source="real_speech_event_log", mean_observed_alert_to_speech_ms=None),
        ],
        protocol=(
            "Declare 5-10 real sessions in advance. Collect each with the same "
            "frozen TRINEXIS_ALERT_MANIFEST, real /export_logs detections, and "
            "TRINEXIS_EVENT_LOG speech events. Replay the same session frames "
            "under alert-first, confidence-first, and nearest-object-first "
            "ordering. Report delivery rate and mean alert-to-speech delay "
            "exactly as observed, even if alert-first helps less than hoped."
        ),
    )


def self_check() -> dict[str, Any]:
    """Exercise the blank-template and session-count guards only."""
    blank = blank_result()
    assert blank["status"] == common.NO_DATA
    assert len(blank["cells"]) == 4
    assert all(cell["status"] == common.NO_DATA for cell in blank["cells"])
    good = {
        "declared_at": "BEFORE_COLLECTION",
        "alert_manifest": "experiments/alert_manifest.json",
        "sessions": [
            {
                "session_id": f"slot-{index:02d}",
                "detection_log": f"experiments/results/session{index:02d}_export_logs.json",
                "event_log": f"experiments/results/session{index:02d}_events.jsonl",
            }
            for index in range(1, 6)
        ],
    }
    assert not validate_manifest(good)[0]
    too_few = dict(good)
    too_few["sessions"] = good["sessions"][:4]
    assert any("5 to 10" in problem for problem in validate_manifest(too_few)[0])
    return {"status": common.SELF_CHECK, "scope": "blank-template and manifest guards"}


def run(args: argparse.Namespace) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        payload = common.load_json(repo_path(args.session_manifest))
    except (OSError, ValueError) as exc:
        return {
            "experiment": "C-multi-session-replay",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"session manifest unavailable: {exc}"],
            "sessions": [],
            "policies": [],
        }
    if not isinstance(payload, dict):
        return {
            "experiment": "C-multi-session-replay",
            "status": common.INSUFFICIENT_DATA,
            "reasons": ["session manifest must be a JSON object"],
            "sessions": [],
            "policies": [],
        }
    manifest_problems, sessions = validate_manifest(payload)
    reasons.extend(manifest_problems)
    alert_manifest = repo_path(str(payload.get("alert_manifest", "")))
    if not alert_manifest.exists():
        reasons.append("alert manifest file does not exist")
    session_results: list[dict[str, Any]] = []
    for row in sessions:
        detection_log = repo_path(row["detection_log"])
        event_log = repo_path(row["event_log"])
        if not detection_log.exists():
            reasons.append(f"{row['session_id']}: detection log does not exist")
        if not event_log.exists():
            reasons.append(f"{row['session_id']}: event log does not exist")
        result = alert_replay.run_replay(SimpleNamespace(
            alert_manifest=str(alert_manifest),
            detection_log=str(detection_log),
            event_log=str(event_log),
            limit=args.limit,
            cooldown=args.cooldown,
        ))
        result["session_id"] = row["session_id"]
        session_results.append(result)
        if result["status"] != common.MEASURED:
            reasons.append(
                f"{row['session_id']}: {result['status']}: "
                + "; ".join(result.get("reasons", []))
            )

    measured = [row for row in session_results if row["status"] == common.MEASURED]
    policies = [aggregate_policy(policy, measured) for policy in alert_replay.POLICIES] if measured else []
    observed_weights = [
        (
            row["observed_speech_events"]["mean_observed_alert_to_speech_ms"],
            int(row["observed_speech_events"]["alert_objects_with_enqueue"]),
        )
        for row in measured
    ]
    comparison: dict[str, Any] = {"status": common.NO_DATA}
    if policies:
        by_policy = {row["policy"]: row for row in policies}
        alert = by_policy["alert_first"]
        confidence = by_policy["confidence_first"]
        nearest = by_policy["nearest_first"]
        comparison = {
            "delivery_rate_alert_minus_confidence": (
                alert["delivery_rate"] - confidence["delivery_rate"]
                if alert["delivery_rate"] is not None and confidence["delivery_rate"] is not None
                else None
            ),
            "delivery_rate_alert_minus_nearest": (
                alert["delivery_rate"] - nearest["delivery_rate"]
                if alert["delivery_rate"] is not None and nearest["delivery_rate"] is not None
                else None
            ),
            "session_weighted_mean_delay_alert_minus_confidence_ms": (
                alert["session_weighted_mean_alert_to_speech_ms"]
                - confidence["session_weighted_mean_alert_to_speech_ms"]
                if alert["session_weighted_mean_alert_to_speech_ms"] is not None
                and confidence["session_weighted_mean_alert_to_speech_ms"] is not None
                else None
            ),
            "interpretation": "Observed log-delivery differences only; no user noticing or benefit is inferred.",
        }
    status = common.MEASURED if not reasons and len(measured) == len(sessions) and 5 <= len(measured) <= 10 else common.INSUFFICIENT_DATA
    return {
        "experiment": "C-multi-session-replay",
        "status": status,
        "warning": (
            "Report these values as-is, including a small, zero, or negative alert-first effect."
            if status == common.MEASURED
            else "No aggregate empirical result is reported from incomplete/unmatched sessions."
        ),
        "declared_session_count": len(sessions),
        "measured_session_count": len(measured),
        "alert_manifest": str(alert_manifest.relative_to(ROOT) if alert_manifest.is_relative_to(ROOT) else alert_manifest),
        "reasons": reasons,
        "policies": policies,
        "comparison": comparison,
        "observed_speech_events": {
            "speech_enqueue_events": sum(
                int(row["observed_speech_events"]["speech_enqueue_events"]) for row in measured
            ),
            "alert_objects_with_enqueue": sum(
                int(row["observed_speech_events"]["alert_objects_with_enqueue"]) for row in measured
            ),
            "session_weighted_mean_observed_alert_to_speech_ms": weighted_mean(observed_weights),
        },
        "sessions": session_results,
        "research_question": (
            "Does alert-first narration make users notice a designated object "
            "faster or more often than confidence-first narration?"
        ),
        "user_noticing_status": common.NO_DATA,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-blank", action="store_true")
    group.add_argument("--run", action="store_true")
    parser.add_argument("--session-manifest", default="experiments/session_manifest.json")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--cooldown", type=float, default=4.5)
    parser.add_argument("--output", default="experiments/results/multi_session_replay_results.json")
    args = parser.parse_args()
    if args.self_check:
        print(self_check()["status"])
        return 0
    result = blank_result() if args.emit_blank else run(args)
    path = common.write_json(args.output, result)
    label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    print(f"{result['status']}: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Experiment C: replay real webcam detection logs under three narration policies.

Alert objects must be declared in a manifest before collection. The maintained
app freezes those objects when ``TRINEXIS_ALERT_MANIFEST`` is set and writes
timestamped detection and speech-enqueue events when ``TRINEXIS_EVENT_LOG`` is
set. This script replays the same real frames through alert-first,
confidence-first, and nearest-object-first ordering. It reports delivery/delay
as observed, including negative or disappointing effects, without inventing
data.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments import common
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    import common  # type: ignore

from trinexis_core import (
    legacy_select_speech_objects,
    nearest_select_speech_objects,
    select_speech_objects,
)

POLICIES = ("alert_first", "confidence_first", "nearest_first")


def manifest_digest(manifest: Mapping[str, Any]) -> str:
    objects = sorted({
        str(item).strip()
        for item in manifest.get("alert_objects", [])
        if str(item).strip()
    })
    return common.canonical_sha256(
        {"alert_objects": objects, "declared_at": manifest.get("declared_at")}
    )


def validate_manifest(manifest: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if not manifest.get("declared_at"):
        reasons.append("declared_at is required before data collection")
    objects = manifest.get("alert_objects")
    if not isinstance(objects, list) or not [str(item).strip() for item in objects if str(item).strip()]:
        reasons.append("alert_objects must be a nonempty predeclared list")
    return reasons


def normalize_frames(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and "logs" in payload:
        frames = payload["logs"]
    elif isinstance(payload, list):
        frames = payload
    else:
        raise ValueError("detection log must be a list or an object with a logs key")
    if not isinstance(frames, list):
        raise ValueError("detection log frames must be a list")
    return [dict(frame) for frame in frames if isinstance(frame, dict)]


def first_seen_by_alert(
    frames: Sequence[Mapping[str, Any]],
    alerts: Iterable[str],
) -> dict[str, float]:
    alert_set = set(alerts)
    first_seen: dict[str, float] = {}
    for frame in frames:
        timestamp = common.numeric(frame.get("timestamp_unix"))
        if timestamp is None:
            continue
        for obj in frame.get("objects", []):
            name = str(obj.get("name", ""))
            if name in alert_set and name not in first_seen:
                first_seen[name] = timestamp
    return first_seen


def replay_policy(
    frames: Sequence[Mapping[str, Any]],
    alerts: Iterable[str],
    policy: str,
    limit: int = 2,
    cooldown_s: float = 4.5,
) -> dict[str, Any]:
    """Replay frames through one ordering policy. No result is fabricated."""
    if policy not in POLICIES:
        raise ValueError("policy must be one of " + ", ".join(POLICIES))
    alert_set = set(alerts)
    first_seen = first_seen_by_alert(frames, alert_set)
    delivered: dict[str, float] = {}
    last_speech_time = float("-inf")
    opportunities = 0

    for frame in frames:
        timestamp = common.numeric(frame.get("timestamp_unix"))
        if timestamp is None:
            continue
        if timestamp - last_speech_time < cooldown_s:
            continue
        objects = [dict(obj) for obj in frame.get("objects", []) if isinstance(obj, dict)]
        if not objects:
            continue
        opportunities += 1
        if policy == "alert_first":
            selected = select_speech_objects(objects, alert_set, limit)
        elif policy == "confidence_first":
            selected = legacy_select_speech_objects(objects, alert_set, limit)
        else:
            selected = nearest_select_speech_objects(objects, limit)
        for obj in selected:
            name = str(obj.get("name", ""))
            if name in alert_set and name not in delivered:
                delivered[name] = timestamp
        last_speech_time = timestamp

    delays_ms = [
        (spoken_at - first_seen[name]) * 1000.0
        for name, spoken_at in delivered.items()
        if name in first_seen
    ]
    return {
        "policy": policy,
        "configured_alert_count": len(alert_set),
        "frames_replayed": len(frames),
        "speech_opportunities": opportunities,
        "alert_objects_seen": len(first_seen),
        "alert_objects_delivered": len(delivered),
        "delivery_rate": len(delivered) / len(first_seen) if first_seen else None,
        "mean_alert_to_speech_ms": statistics.mean(delays_ms) if delays_ms else None,
        "median_alert_to_speech_ms": statistics.median(delays_ms) if delays_ms else None,
        "censored_alert_names": sorted(set(first_seen) - set(delivered)),
    }


def observed_event_delays(
    events: Sequence[Mapping[str, Any]],
    frames: Sequence[Mapping[str, Any]],
    alerts: Iterable[str],
    manifest_sha256: str,
) -> dict[str, Any]:
    """Compute first enqueue delay for each predeclared alert from real events."""
    alert_set = set(alerts)
    first_seen = first_seen_by_alert(frames, alert_set)
    first_enqueue: dict[str, float] = {}
    mismatched_hash = False
    speech_events = 0

    for event in sorted(events, key=lambda row: common.numeric(row.get("enqueue_timestamp_unix")) or 0.0):
        if event.get("event") != "speech_enqueued":
            continue
        speech_events += 1
        if event.get("alert_manifest_sha256") != manifest_sha256:
            mismatched_hash = True
        enqueue_time = common.numeric(event.get("enqueue_timestamp_unix"))
        if enqueue_time is None:
            continue
        for name in event.get("matched_alert_names", []):
            name = str(name)
            if name in alert_set and name not in first_enqueue:
                first_enqueue[name] = enqueue_time

    delays_ms = [
        (first_enqueue[name] - first_seen[name]) * 1000.0
        for name in first_enqueue
        if name in first_seen
    ]
    return {
        "speech_enqueue_events": speech_events,
        "alert_objects_with_enqueue": len(first_enqueue),
        "mean_observed_alert_to_speech_ms": statistics.mean(delays_ms) if delays_ms else None,
        "median_observed_alert_to_speech_ms": statistics.median(delays_ms) if delays_ms else None,
        "manifest_hash_mismatch": mismatched_hash,
    }


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "C-alert-replay",
        [
            common.blank_cell(policy="alert_first", alert_objects_delivered=None, mean_alert_to_speech_ms=None),
            common.blank_cell(policy="confidence_first", alert_objects_delivered=None, mean_alert_to_speech_ms=None),
            common.blank_cell(policy="nearest_first", alert_objects_delivered=None, mean_alert_to_speech_ms=None),
            common.blank_cell(source="real_speech_event_log", mean_observed_alert_to_speech_ms=None),
        ],
        protocol=(
            "Choose alert objects in advance and freeze them with "
            "TRINEXIS_ALERT_MANIFEST. Export real /export_logs detections and "
            "TRINEXIS_EVENT_LOG speech-enqueue events. Replay all three "
            "orderings on the same frames; report delivery rate and mean "
            "alert-to-speech delay exactly as observed, even if alert-first "
            "helps less than hoped. Replay measures alert delivery, not "
            "whether a user notices the object; that requires a separate "
            "consented study."
        ),
    )


def self_check() -> dict[str, Any]:
    """Verify that a confidence-first mutation can fail the alert invariant."""
    frames = [{
        "timestamp_unix": 1.0,
        "objects": [
            {"name": "keys", "confidence": 0.20, "distance": 9.0},
            {"name": "chair", "confidence": 0.99, "distance": 1.0},
            {"name": "table", "confidence": 0.98, "distance": 2.0},
        ],
    }]
    alerts = {"keys"}
    alert_first = replay_policy(frames, alerts, "alert_first", cooldown_s=0.0)
    confidence_first = replay_policy(frames, alerts, "confidence_first", cooldown_s=0.0)
    nearest_first = replay_policy(frames, alerts, "nearest_first", cooldown_s=0.0)
    assert alert_first["alert_objects_delivered"] == 1
    assert confidence_first["alert_objects_delivered"] == 0
    assert nearest_first["alert_objects_delivered"] == 0
    assert all(cell["status"] == common.NO_DATA for cell in blank_result()["cells"])
    assert len(POLICIES) == 3
    return {"status": common.SELF_CHECK, "scope": "in-memory replay fixture"}


def run_replay(args: argparse.Namespace) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        manifest = common.load_json(args.alert_manifest)
        frame_payload = common.load_json(args.detection_log)
        events = common.load_jsonl(args.event_log)
    except (OSError, ValueError) as exc:
        return {
            "experiment": "C-alert-replay",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"input unavailable: {exc}"],
            "policies": [],
        }

    reasons.extend(validate_manifest(manifest))
    digest = manifest_digest(manifest)
    alerts = sorted({
        str(item).strip()
        for item in manifest.get("alert_objects", [])
        if str(item).strip()
    })
    try:
        frames = common.assert_real_log(normalize_frames(frame_payload), "detection log")
        events = common.assert_real_log(events, "speech event log")
    except ValueError as exc:
        return {
            "experiment": "C-alert-replay",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"invalid real-log input: {exc}"],
            "policies": [],
        }

    if not frames:
        reasons.append("no real detection frames")
    if not Path(args.event_log).exists():
        reasons.append("speech event log file does not exist")
    if any(frame.get("alert_manifest_sha256") != digest for frame in frames):
        reasons.append("detection frames were not collected under this alert manifest")

    first_seen = first_seen_by_alert(frames, alerts)
    policies = [
        replay_policy(frames, alerts, policy, args.limit, args.cooldown)
        for policy in POLICIES
    ]
    observed = observed_event_delays(events, frames, alerts, digest)
    if observed["manifest_hash_mismatch"]:
        reasons.append("speech events were not collected under this alert manifest")

    status = common.MEASURED if not reasons else common.INSUFFICIENT_DATA
    return {
        "experiment": "C-alert-replay",
        "status": status,
        "warning": (
            "Report the observed values exactly, including a smaller or "
            "negative alert-first effect. Replay does not establish user "
            "noticing or benefit."
            if status == common.MEASURED
            else "No empirical replay result is reported from incomplete/unmatched data."
        ),
        "alert_manifest_sha256": digest,
        "alert_objects": alerts,
        "alert_objects_seen": sorted(first_seen),
        "cooldown_s": args.cooldown,
        "max_speak_objects": args.limit,
        "reasons": reasons,
        "policies": policies,
        "observed_speech_events": observed,
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
    parser.add_argument("--alert-manifest", default="experiments/alert_manifest.json")
    parser.add_argument("--detection-log", default="experiments/results/export_logs.json")
    parser.add_argument("--event-log", default="experiments/results/speech_events.jsonl")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--cooldown", type=float, default=4.5)
    parser.add_argument("--output", default="experiments/results/alert_replay_results.json")
    args = parser.parse_args()

    if args.self_check:
        print(self_check()["status"])
        return 0
    if args.emit_blank:
        path = common.write_json(args.output, blank_result())
        print(f"Wrote blank template: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0
    result = run_replay(args)
    path = common.write_json(args.output, result)
    print(f"{result['status']}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

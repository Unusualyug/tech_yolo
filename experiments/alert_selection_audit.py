#!/usr/bin/env python3
"""Seeded synthetic before/after audit of TRINEXIS alert-speech selection.

This script does not run model inference, open a camera, or use human data. It
generates deterministic detection records to measure a software regression:
whether a configured alert object is omitted from the two-object speech
shortlist. The legacy behavior truncated by confidence before alert-aware
ranking; the updated behavior ranks alerts before truncation.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from trinexis_core import (  # noqa: E402
    legacy_select_speech_objects,
    select_speech_objects,
)

SEED = 20261110
N_CASES = 1000
N_OBJECTS = 6
MAX_SPOKEN = 2
ALERT_NAME = "person"
OUT = ROOT / "paper" / "artifacts" / "alert_selection_audit.json"


def make_case(rng: random.Random) -> list[dict[str, object]]:
    objects = [
        {
            "name": f"object_{i}",
            "confidence": rng.uniform(0.16, 0.95),
            "distance": rng.uniform(20.0, 200.0),
        }
        for i in range(N_OBJECTS - 1)
    ]
    objects.append(
        {
            "name": ALERT_NAME,
            "confidence": rng.uniform(0.16, 0.95),
            "distance": rng.uniform(20.0, 200.0),
        }
    )
    rng.shuffle(objects)
    return objects


def main() -> None:
    rng = random.Random(SEED)
    alerts = {ALERT_NAME}
    legacy_drops = 0
    updated_drops = 0

    for _ in range(N_CASES):
        objects = make_case(rng)
        legacy = legacy_select_speech_objects(objects, alerts, MAX_SPOKEN)
        updated = select_speech_objects(objects, alerts, MAX_SPOKEN)
        if not any(obj["name"] in alerts for obj in legacy):
            legacy_drops += 1
        if not any(obj["name"] in alerts for obj in updated):
            updated_drops += 1

    legacy_rate = legacy_drops / N_CASES
    updated_rate = updated_drops / N_CASES
    result = {
        "experiment": "seeded_synthetic_alert_selection_regression",
        "seed": SEED,
        "cases": N_CASES,
        "objects_per_case": N_OBJECTS,
        "alert_objects_per_case": 1,
        "max_spoken_objects": MAX_SPOKEN,
        "legacy_drop_count": legacy_drops,
        "updated_drop_count": updated_drops,
        "legacy_drop_rate": round(legacy_rate, 4),
        "updated_drop_rate": round(updated_rate, 4),
        "absolute_drop_rate_reduction": round(legacy_rate - updated_rate, 4),
        "relative_drop_rate_reduction": (
            round((legacy_rate - updated_rate) / legacy_rate, 4)
            if legacy_rate
            else None
        ),
        "evidence_type": "deterministic_software_regression_test",
        "disclaimer": (
            "Synthetic detection records only. No model inference, camera "
            "capture, labeled dataset, human participant, or real-world "
            "effectiveness measurement was involved."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

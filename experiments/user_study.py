#!/usr/bin/env python3
"""Experiment E: blank worksheet and guarded summarizer for a user study.

Institutional ethics approval and documented consent are required before any
recruitment or worksheet row with participant data is created. A blank slot
worksheet is not participant data. The summarizer refuses incomplete consent,
missing approval identifiers, fewer than 8 or more than 12 participants, and
nonnumeric outcomes. No benefit or assistive-effectiveness claim is produced.
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments import common
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    import common  # type: ignore

POLICIES = ("alert_first", "confidence_first", "nearest_first")
FIELDS = (
    "participant_slot",
    "participant_id",
    "condition_order",
    "policy",
    "designated_object",
    "trial_started_at",
    "consent_confirmed",
    "ethics_approval_id",
    "noticed",
    "time_to_notice_ms",
    "censored_at_timeout",
    "audio_or_log_reference",
    "notes",
)
BLANK_FIELDS = (
    "participant_id",
    "designated_object",
    "trial_started_at",
    "consent_confirmed",
    "ethics_approval_id",
    "noticed",
    "time_to_notice_ms",
    "censored_at_timeout",
    "audio_or_log_reference",
    "notes",
)


def worksheet_rows(participants: int) -> list[dict[str, str]]:
    """Return a counterbalanced, entirely blank three-condition worksheet."""
    if not 8 <= participants <= 12:
        raise ValueError("participants must be between 8 and 12")
    rotations = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
    rows: list[dict[str, str]] = []
    for slot in range(1, participants + 1):
        rotation = rotations[(slot - 1) % 3]
        for condition_order, policy_index in enumerate(rotation, start=1):
            row = {
                "participant_slot": f"slot-{slot:02d}",
                "condition_order": str(condition_order),
                "policy": POLICIES[policy_index],
            }
            row.update({field: "" for field in BLANK_FIELDS})
            rows.append(row)
    return rows


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "E-user-noticing",
        [
            common.blank_cell(policy=policy, notice_rate=None, median_time_to_notice_ms=None)
            for policy in POLICIES
        ],
        protocol=(
            "Obtain institutional ethics approval and documented consent "
            "before recruitment. Use 8-12 participants in a within-subject "
            "design with alert-first, confidence-first, and nearest-object-first "
            "conditions, a predesignated object, counterbalanced order, and "
            "preregistered notice rate and time-to-notice outcomes. Report "
            "negative or null results as-is. A completed worksheet does not "
            "establish assistive benefit."
        ),
    )


def validate_rows(
    rows: Iterable[Mapping[str, Any]],
) -> tuple[list[str], list[dict[str, Any]]]:
    """Reject any worksheet that lacks real consent, approval, or outcomes."""
    problems: list[str] = []
    cleaned: list[dict[str, Any]] = []
    ethics_ids: set[str] = set()
    participant_ids: set[str] = set()
    per_participant: dict[str, set[str]] = {}
    for line, row in enumerate(rows, start=2):
        item = {field: str(row.get(field, "")).strip() for field in FIELDS}
        cleaned.append(item)
        ethics = item["ethics_approval_id"]
        if not ethics or ethics.upper() in {"NO DATA", "PENDING", "N/A"}:
            problems.append(f"line {line}: ethics_approval_id is required")
        else:
            ethics_ids.add(ethics)
        if item["consent_confirmed"].lower() not in {"1", "true", "yes"}:
            problems.append(f"line {line}: consent_confirmed must be true")
        participant = item["participant_id"]
        if not participant or participant.startswith("slot-"):
            problems.append(f"line {line}: real participant_id is required")
        else:
            participant_ids.add(participant)
        if item["policy"] not in POLICIES:
            problems.append(f"line {line}: unknown policy")
        else:
            per_participant.setdefault(participant, set()).add(item["policy"])
        if item["noticed"] not in {"0", "1"}:
            problems.append(f"line {line}: noticed must be 0 or 1")
        elif item["noticed"] == "1":
            try:
                float(item["time_to_notice_ms"])
            except ValueError:
                problems.append(f"line {line}: time_to_notice_ms must be numeric when noticed=1")
    if len(ethics_ids) != 1:
        problems.append("all rows must use one nonempty institutional ethics approval identifier")
    if not 8 <= len(participant_ids) <= 12:
        problems.append("participant_id count must be between 8 and 12")
    for participant, policies in per_participant.items():
        if policies != set(POLICIES):
            problems.append(f"{participant}: all three within-subject conditions are required")
    return problems, cleaned


def summarize(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    problems, cleaned = validate_rows(rows)
    if problems:
        return {
            "experiment": "E-user-noticing",
            "status": common.INSUFFICIENT_DATA,
            "reasons": problems,
            "policies": [],
        }
    policies: list[dict[str, Any]] = []
    for policy in POLICIES:
        selected = [row for row in cleaned if row["policy"] == policy]
        noticed = [row for row in selected if row["noticed"] == "1"]
        times = [float(row["time_to_notice_ms"]) for row in noticed]
        policies.append({
            "policy": policy,
            "trials": len(selected),
            "noticed_trials": len(noticed),
            "notice_rate": len(noticed) / len(selected) if selected else None,
            "median_time_to_notice_ms": statistics.median(times) if times else None,
        })
    return {
        "experiment": "E-user-noticing",
        "status": common.MEASURED,
        "warning": (
            "Report these observed outcomes as-is, including null or negative "
            "effects. Notice rate and time-to-notice do not establish assistive "
            "benefit, clinical readiness, or deployment success."
        ),
        "participants": len({row["participant_id"] for row in cleaned}),
        "ethics_approval_id": cleaned[0]["ethics_approval_id"],
        "consent_confirmed": True,
        "policies": policies,
        "research_question": (
            "Does alert-first narration make users notice a designated object "
            "faster or more often than confidence-first narration?"
        ),
        "benefit_claim": "NO DATA",
    }


def self_check() -> dict[str, Any]:
    """Exercise blank-worksheet and guard logic; no participant data is used."""
    blank = blank_result()
    assert blank["status"] == common.NO_DATA
    assert len(blank["cells"]) == 3
    rows = worksheet_rows(8)
    assert len(rows) == 24
    assert all(all(row[field] == "" for field in BLANK_FIELDS) for row in rows)
    problems, _ = validate_rows(rows)
    assert problems
    assert "nearest_first" in POLICIES
    return {"status": common.SELF_CHECK, "scope": "blank worksheet and consent/ethics guards"}


def write_worksheet(path: str | Path, participants: int) -> Path:
    target = Path(path)
    if not target.is_absolute():
        target = ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(worksheet_rows(participants))
    return target


def read_worksheet(path: str | Path) -> list[dict[str, str]]:
    target = Path(path)
    if not target.is_absolute():
        target = ROOT / target
    with target.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-worksheet", action="store_true")
    group.add_argument("--emit-blank", action="store_true")
    group.add_argument("--summarize", action="store_true")
    parser.add_argument("--participants", type=int, default=8)
    parser.add_argument("--worksheet", default="experiments/results/user_study_worksheet.csv")
    parser.add_argument("--output", default="experiments/results/user_study_results.json")
    args = parser.parse_args()
    if args.self_check:
        print(self_check()["status"])
        return 0
    if args.emit_worksheet:
        path = write_worksheet(args.worksheet, args.participants)
        label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        print(f"Wrote blank worksheet: {label}")
        return 0
    if args.emit_blank:
        result = blank_result()
    else:
        try:
            rows = read_worksheet(args.worksheet)
        except OSError as exc:
            result = {
                "experiment": "E-user-noticing",
                "status": common.INSUFFICIENT_DATA,
                "reasons": [f"worksheet unavailable: {exc}"],
                "policies": [],
            }
        else:
            result = summarize(rows)
    path = common.write_json(args.output, result)
    label = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    print(f"{result['status']}: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

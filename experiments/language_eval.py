#!/usr/bin/env python3
"""Experiment D: blank worksheet for checked-language speech ratings.

The UI exposes 72 language codes, but none is claimed verified. This script
prepares a 5-10 language x 10 announcement worksheet for native or reliable
bilingual raters using 1-5 correctness/naturalness scores. It reports only
explicitly checked languages and never invents ratings. gTTS uses Google
Translate's speech service; raters should listen to sample audio and the author
should listen to a few languages before reporting anything.
"""
from __future__ import annotations

import argparse
import csv
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

from trinexis_language import announcement_rating_template, summarize_ratings

COLUMNS = (
    "language",
    "announcement_id",
    "source_text",
    "tts_audio_path",
    "rater_role",
    "correctness_1_to_5",
    "naturalness_1_to_5",
    "notes",
)


def parse_languages(value: str) -> list[str]:
    languages = [item.strip() for item in value.split(",") if item.strip()]
    if not 5 <= len(languages) <= 10:
        raise ValueError("sample 5 to 10 languages")
    return languages


def emit_worksheet(languages: Sequence[str], item_count: int, output: str | Path) -> Path:
    rows = announcement_rating_template(languages, item_count)
    target = Path(output)
    if not target.is_absolute():
        target = ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return target


def blank_result(languages: Sequence[str]) -> dict[str, Any]:
    return common.blank_result(
        "D-language-ratings",
        [
            common.blank_cell(
                language=language,
                announcements=10,
                rater_count=None,
                mean_correctness=None,
                mean_naturalness=None,
            )
            for language in languages
        ],
        protocol=(
            "Sample 5-10 languages, recruit native or reliable bilingual "
            "raters, prepare 10 announcements per language, listen to sample "
            "gTTS/Google Translate speech audio, and rate correctness and "
            "naturalness from 1 to 5. Report only checked languages; state "
            "that the remaining 72-language claims are unchecked."
        ),
    )


def summarize_csv(
    ratings_path: str | Path,
    checked_languages: Iterable[str],
    output: str | Path,
) -> dict[str, Any]:
    path = Path(ratings_path)
    checked = sorted({item.strip() for item in checked_languages if item.strip()})
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        return {
            "experiment": "D-language-ratings",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"ratings file unavailable: {exc}"],
            "checked_languages": checked,
            "summary": [],
        }
    rows = common.assert_real_log(rows, "language ratings")
    summary = summarize_ratings(rows, checked)
    result = {
        "experiment": "D-language-ratings",
        "status": common.MEASURED if summary else common.INSUFFICIENT_DATA,
        "warning": (
            "Only explicitly checked languages appear; no translation or "
            "comprehension claim is made for unchecked languages."
            if summary
            else "No completed checked-language ratings were found; no result is invented."
        ),
        "checked_languages": checked,
        "unchecked_language_claim": "The remaining language codes are unchecked.",
        "summary": summary,
    }
    common.write_json(output, result)
    return result


def self_check() -> dict[str, Any]:
    languages = ["Hindi", "Gujarati", "Bengali", "Tamil", "Spanish"]
    rows = announcement_rating_template(languages, 10)
    assert len(rows) == 50
    assert all(row["correctness_1_to_5"] is None for row in rows)
    fixture = [{
        "language": "Hindi",
        "correctness_1_to_5": 4,
        "naturalness_1_to_5": 5,
    }]
    assert summarize_ratings(fixture, {"Hindi"})[0]["language"] == "Hindi"
    assert summarize_ratings(fixture, {"Gujarati"}) == []
    return {"status": common.SELF_CHECK, "scope": "blank worksheet/rater-filter fixture"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-worksheet", action="store_true")
    group.add_argument("--emit-blank", action="store_true")
    group.add_argument("--summarize", action="store_true")
    parser.add_argument(
        "--languages",
        default="Hindi,Gujarati,Bengali,Tamil,Spanish",
        help="Example only: comma-separated 5-10 unchecked language names.",
    )
    parser.add_argument("--announcements", type=int, default=10)
    parser.add_argument("--worksheet", default="experiments/results/language_ratings_template.csv")
    parser.add_argument("--ratings", default="experiments/results/language_ratings.csv")
    parser.add_argument("--checked-languages", default="")
    parser.add_argument("--output", default="experiments/results/language_rating_results.json")
    args = parser.parse_args()

    if args.self_check:
        print(self_check()["status"])
        return 0

    languages = parse_languages(args.languages)
    if args.emit_worksheet:
        path = emit_worksheet(languages, args.announcements, args.worksheet)
        print(f"Wrote blank worksheet: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0
    if args.emit_blank:
        path = common.write_json(args.output, blank_result(languages))
        print(f"Wrote blank template: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0

    checked = [item.strip() for item in args.checked_languages.split(",") if item.strip()]
    if not checked:
        parser.error("--summarize requires --checked-languages; no language is assumed checked")
    result = summarize_csv(args.ratings, checked, args.output)
    target = common.write_json(args.output, result)
    print(f"{result['status']}: {target.relative_to(ROOT) if target.is_relative_to(ROOT) else target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Dependency-free speech-template metadata helpers.

These helpers are pure Python so CI and evaluation scripts can assert the
coverage of the language maps without importing Flask, OpenCV, Ultralytics,
or gTTS. The templates themselves live in ``app23.py``.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


def template_coverage(
    language_codes: Mapping[str, str],
    speech_templates: Mapping[str, str],
    fallback_language: str = "English",
) -> dict[str, Any]:
    """Report translated-template coverage and the documented fallback list."""
    if fallback_language not in language_codes:
        raise ValueError("fallback language must have a language code")
    if fallback_language not in speech_templates:
        raise ValueError("fallback language must have a speech template")
    unsupported = sorted(set(language_codes) - set(speech_templates))
    extras = sorted(set(speech_templates) - set(language_codes))
    return {
        "language_count": len(language_codes),
        "template_count": len(speech_templates),
        "fallback_language": fallback_language,
        "english_fallback_languages": unsupported,
        "unmapped_templates": extras,
        "verified_languages": [],
        "unchecked_language_count": len(language_codes),
        "note": (
            "Fallback is a software behavior, not evidence of translation "
            "quality or listener comprehension."
        ),
    }


def announcement_rating_template(
    languages: Sequence[str],
    item_count: int = 10,
) -> list[dict[str, Any]]:
    """Build a blank rater worksheet with no ratings or translations."""
    if item_count < 1:
        raise ValueError("item_count must be positive")
    return [
        {
            "language": language,
            "announcement_id": f"A{index + 1:02d}",
            "source_text": "",
            "tts_audio_path": "",
            "rater_role": "",
            "correctness_1_to_5": None,
            "naturalness_1_to_5": None,
            "notes": "",
        }
        for language in languages
        for index in range(item_count)
    ]


def summarize_ratings(
    rows: Iterable[Mapping[str, Any]],
    checked_languages: Iterable[str] | None = None,
) -> list[dict[str, Any]]:
    """Summarize completed correctness/naturalness rows by checked language."""
    checked = set(checked_languages) if checked_languages is not None else None
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        language = str(row.get("language", ""))
        if checked is not None and language not in checked:
            continue
        try:
            correctness = float(row["correctness_1_to_5"])
            naturalness = float(row["naturalness_1_to_5"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (1 <= correctness <= 5 and 1 <= naturalness <= 5):
            continue
        groups.setdefault(language, []).append(
            {"correctness": correctness, "naturalness": naturalness}
        )

    output: list[dict[str, Any]] = []
    for language in sorted(groups):
        values = groups[language]
        output.append(
            {
                "language": language,
                "n": len(values),
                "mean_correctness": sum(
                    value["correctness"] for value in values
                ) / len(values),
                "mean_naturalness": sum(
                    value["naturalness"] for value in values
                ) / len(values),
            }
        )
    return output

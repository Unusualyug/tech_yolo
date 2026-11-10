#!/usr/bin/env python3
"""Shared, dependency-free helpers for TRINEXIS empirical protocols.

These helpers intentionally separate *blank templates* and *software
self-checks* from measured results. No result value is invented here.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "experiments" / "results"

NO_DATA = "NO DATA"
INSUFFICIENT_DATA = "INSUFFICIENT DATA"
MEASURED = "MEASURED"
SELF_CHECK = "SOFTWARE SELF-CHECK ONLY"

REQUIRED_HARDWARE_KEYS = (
    "cpu",
    "gpu",
    "ram",
    "os",
    "python_version",
    "requirements_file",
    "camera",
    "microphone_or_audio_output",
    "tts_backend",
    "date_declared",
)
REQUIRED_DATASET_KEYS = (
    "dataset_name",
    "report_split",
    "tuning_split",
    "image_count",
    "annotation_format",
    "frozen_prompt_manifest_sha256",
    "declared_before_predictions",
    "report_split_sha256",
)


def write_json(path: str | Path, data: Any) -> Path:
    """Write formatted JSON under the repository unless the path is absolute."""
    target = Path(path)
    if not target.is_absolute():
        target = ROOT / target
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def load_json(path: str | Path) -> Any:
    """Read a JSON object/array and reject empty files."""
    target = Path(path)
    text = target.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Empty JSON file: {target}")
    return json.loads(text)


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read JSONL rows; blank lines and malformed rows are skipped."""
    target = Path(path)
    rows: list[dict[str, Any]] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def canonical_sha256(data: Mapping[str, Any]) -> str:
    """Return a stable SHA-256 digest for a manifest object."""
    encoded = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def blank_cell(**fields: Any) -> dict[str, Any]:
    """Return one explicitly blank result cell."""
    return {"status": NO_DATA, **fields}


def blank_result(experiment: str, cells: Iterable[Mapping[str, Any]], **metadata: Any) -> dict[str, Any]:
    """Return a blank, citable-only-as-template result document."""
    return {
        "experiment": experiment,
        "status": NO_DATA,
        "warning": "Blank template only. Do not report as empirical evidence.",
        "hardware_manifest": None,
        "software_manifest": "requirements.txt",
        "cells": list(cells),
        **metadata,
    }


def validate_hardware_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Return missing/blank hardware-declaration fields."""
    return [
        key for key in REQUIRED_HARDWARE_KEYS
        if manifest.get(key) in (None, "", [], {})
    ]


def validate_dataset_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Return violations in a predeclared evaluation-split manifest."""
    problems = [
        key for key in REQUIRED_DATASET_KEYS
        if manifest.get(key) in (None, "", [], {})
    ]
    try:
        count = int(manifest.get("image_count"))
    except (TypeError, ValueError):
        problems.append("image_count must be an integer")
    else:
        if not 200 <= count <= 300:
            problems.append("image_count must be between 200 and 300")
    if manifest.get("report_split") == manifest.get("tuning_split"):
        problems.append("report_split must differ from tuning_split")
    if manifest.get("declared_before_predictions") is not True:
        problems.append("declared_before_predictions must be true")
    return problems


def assert_real_log(rows: Iterable[Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    """Reject explicitly synthetic/fixture rows for empirical replay."""
    result: list[dict[str, Any]] = []
    for row in rows:
        if row.get("synthetic") is True or row.get("fixture") is True or row.get("simulated") is True:
            raise ValueError(f"{label} contains synthetic/fixture rows; real logs are required")
        result.append(dict(row))
    return result


def numeric(value: Any) -> float | None:
    """Convert a value to float or return None without inventing a number."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

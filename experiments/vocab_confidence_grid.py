#!/usr/bin/env python3
"""Experiment B grid: frozen vocabulary size x confidence threshold.

The grid is {455, 20, 50, 80 prompts} x {0.15, 0.25, 0.35}. Prompt subsets,
dataset split, and predictions must be declared before evaluation. Missing
predictions stay ``NO DATA``; the script never invents a cell value.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from experiments import common
    from experiments import detection_eval
except ModuleNotFoundError:  # pragma: no cover - direct script execution
    import common  # type: ignore
    import detection_eval  # type: ignore

VOCAB_SIZES = (455, 20, 50, 80)
CONFIDENCES = (0.15, 0.25, 0.35)


def cell_name(vocab_size: int, confidence: float) -> str:
    return f"cell_{vocab_size}_{int(round(confidence * 100)):03d}"


def plan_cells() -> list[dict[str, Any]]:
    return [
        common.blank_cell(
            cell=cell_name(vocab_size, confidence),
            vocab_size=vocab_size,
            confidence=confidence,
            prompt_set_sha256=None,
            precision=None,
            recall=None,
            map50=None,
            speed_median_ms=None,
        )
        for vocab_size in VOCAB_SIZES
        for confidence in CONFIDENCES
    ]


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "B-vocabulary-confidence-grid",
        plan_cells(),
        protocol=(
            "Freeze the 455-prompt vocabulary and 20/50/80-prompt subsets "
            "before generating predictions. Evaluate each of the 12 cells on "
            "the same predeclared 200-300-image report split. Never tune on "
            "the reported images. Report precision, recall, mAP@0.5, and "
            "speed; negative or worse results are reportable as-is."
        ),
        grid={"vocab_sizes": list(VOCAB_SIZES), "confidences": list(CONFIDENCES)},
    )


def self_check() -> dict[str, Any]:
    cells = plan_cells()
    assert len(cells) == 12
    assert all(cell["status"] == common.NO_DATA for cell in cells)
    assert cell_name(455, 0.15) == "cell_455_015"
    assert cell_name(20, 0.35) == "cell_020_035" or cell_name(20, 0.35) == "cell_20_035"
    return {"status": common.SELF_CHECK, "scope": "blank grid structure only"}


def validate_vocab_manifest(manifest: Mapping[str, Any]) -> tuple[dict[int, str], list[str]]:
    """Return per-size prompt-set hashes and any manifest violations."""
    sets = manifest.get("prompt_sets", {})
    hashes: dict[int, str] = {}
    reasons: list[str] = []
    for size in VOCAB_SIZES:
        prompts = sets.get(str(size))
        if not isinstance(prompts, list) or len(prompts) != size:
            reasons.append(f"prompt_sets[{size}] must contain exactly {size} prompts")
            continue
        cleaned = [str(item).strip() for item in prompts if str(item).strip()]
        if len(cleaned) != size or len(set(cleaned)) != size:
            reasons.append(f"prompt_sets[{size}] contains blanks or duplicates")
            continue
        hashes[size] = common.canonical_sha256(
            {"vocab_size": size, "prompts": cleaned}
        )
    if manifest.get("declared_before_predictions") is not True:
        reasons.append("declared_before_predictions must be true")
    return hashes, reasons


def run_grid(args: argparse.Namespace) -> dict[str, Any]:
    try:
        dataset_manifest = common.load_json(args.dataset_manifest)
        vocab_manifest = common.load_json(args.vocab_manifest)
    except (OSError, ValueError) as exc:
        return {
            "experiment": "B-vocabulary-confidence-grid",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"manifest unavailable: {exc}"],
            "cells": plan_cells(),
        }

    reasons = common.validate_dataset_manifest(dataset_manifest)
    vocab_hashes, vocab_reasons = validate_vocab_manifest(vocab_manifest)
    reasons.extend(vocab_reasons)

    cells: list[dict[str, Any]] = []
    predictions_dir = Path(args.predictions_dir) if args.predictions_dir else None
    for vocab_size in VOCAB_SIZES:
        for confidence in CONFIDENCES:
            name = cell_name(vocab_size, confidence)
            base = common.blank_cell(
                cell=name,
                vocab_size=vocab_size,
                confidence=confidence,
                prompt_set_sha256=vocab_hashes.get(vocab_size),
                precision=None,
                recall=None,
                map50=None,
                speed_median_ms=None,
            )
            prediction_path = (
                predictions_dir / f"{name}.json" if predictions_dir is not None else None
            )
            if reasons or prediction_path is None or not prediction_path.exists():
                base["status"] = common.NO_DATA if not reasons else common.INSUFFICIENT_DATA
                base["reasons"] = list(reasons) + (
                    [f"missing predictions: {prediction_path}"] if prediction_path else []
                )
                cells.append(base)
                continue

            eval_args = SimpleNamespace(
                backend="pycocotools",
                ground_truth=args.ground_truth,
                predictions=str(prediction_path),
                weights=None,
                data=None,
                dataset_manifest=args.dataset_manifest,
                latency_log=args.latency_log,
                imgsz=args.imgsz,
                confidence=confidence,
                vocab_size=vocab_size,
                vocab_manifest_sha256=vocab_hashes.get(vocab_size),
            )
            outcome = detection_eval.run_evaluation(eval_args)
            metrics = outcome.get("metrics", {})
            base.update({
                "status": outcome["status"],
                "precision": metrics.get("precision"),
                "recall": metrics.get("recall"),
                "map50": metrics.get("map50"),
                "speed_median_ms": metrics.get("speed_median_ms"),
                "reasons": outcome.get("reasons", []),
                "predictions_sha256": metrics.get("predictions_sha256"),
            })
            cells.append(base)

    measured = all(cell["status"] == common.MEASURED for cell in cells)
    return {
        "experiment": "B-vocabulary-confidence-grid",
        "status": common.MEASURED if measured else common.INSUFFICIENT_DATA,
        "warning": (
            "Report all 12 cells, including negative results; author must verify numbers."
            if measured
            else "One or more cells have no complete measured data; nothing is inferred."
        ),
        "dataset_manifest_sha256": common.canonical_sha256(dataset_manifest),
        "vocab_manifest_sha256": common.canonical_sha256(vocab_manifest),
        "grid": {"vocab_sizes": list(VOCAB_SIZES), "confidences": list(CONFIDENCES)},
        "cells": cells,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-plan", action="store_true")
    group.add_argument("--run", action="store_true")
    parser.add_argument("--dataset-manifest", default="experiments/dataset_manifest.json")
    parser.add_argument("--vocab-manifest", default="experiments/vocab_manifest.json")
    parser.add_argument("--ground-truth")
    parser.add_argument("--predictions-dir")
    parser.add_argument("--latency-log")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--output", default="experiments/results/vocab_confidence_grid.json")
    args = parser.parse_args()

    if args.self_check:
        print(self_check()["status"])
        return 0
    if args.emit_plan:
        path = common.write_json(args.output, blank_result())
        print(f"Wrote blank grid: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0
    result = run_grid(args)
    path = common.write_json(args.output, result)
    print(f"{result['status']}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

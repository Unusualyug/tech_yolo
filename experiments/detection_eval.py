#!/usr/bin/env python3
"""Experiment B: genuine detection evaluation on a predeclared report split.

Two optional adapters are supported:
  * ``pycocotools`` using COCO-format ground truth and predictions;
  * Ultralytics ``val`` using a declared weights file and dataset config.

Without real annotations/predictions/weights, the script emits a blank result
or an ``INSUFFICIENT DATA`` record. It never synthesizes precision, recall,
mAP, or speed.
"""
from __future__ import annotations

import argparse
import hashlib
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

from trinexis_telemetry import load_latency_records


def iou_xywh(box_a: Sequence[float], box_b: Sequence[float]) -> float:
    """IoU for two COCO-style ``[x, y, width, height]`` boxes."""
    ax, ay, aw, ah = [float(value) for value in box_a[:4]]
    bx, by, bw, bh = [float(value) for value in box_b[:4]]
    inter_x1 = max(ax, bx)
    inter_y1 = max(ay, by)
    inter_x2 = min(ax + aw, bx + bw)
    inter_y2 = min(ay + ah, by + bh)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    intersection = inter_w * inter_h
    union = aw * ah + bw * bh - intersection
    return intersection / union if union > 0 else 0.0


def precision_recall_at_iou05(
    ground_truth: Mapping[str, Any],
    predictions: Iterable[Mapping[str, Any]],
    confidence_threshold: float,
) -> dict[str, float | int]:
    """Compute pooled precision/recall at IoU 0.5 and one score threshold.

    This is the explicit PR reporting value. mAP@0.5 is obtained from
    pycocotools or Ultralytics ``val``, not from this helper.
    """
    gts_by_image: dict[Any, list[Mapping[str, Any]]] = {}
    for annotation in ground_truth.get("annotations", []):
        if annotation.get("iscrowd", 0):
            continue
        gts_by_image.setdefault(annotation["image_id"], []).append(annotation)

    eligible = [
        row for row in predictions
        if common.numeric(row.get("score")) is not None
        and float(row["score"]) >= confidence_threshold
    ]
    eligible.sort(key=lambda row: float(row["score"]), reverse=True)

    matched_ids: set[int] = set()
    true_positives = 0
    false_positives = 0

    for prediction in eligible:
        candidates = gts_by_image.get(prediction["image_id"], [])
        best_iou = 0.0
        best_index: int | None = None
        for index, annotation in enumerate(candidates):
            key = id(annotation)
            if key in matched_ids:
                continue
            if annotation.get("category_id") != prediction.get("category_id"):
                continue
            score = iou_xywh(prediction["bbox"], annotation["bbox"])
            if score > best_iou:
                best_iou, best_index = score, key
        if best_iou >= 0.5 and best_index is not None:
            matched_ids.add(best_index)
            true_positives += 1
        else:
            false_positives += 1

    total_gt = sum(len(rows) for rows in gts_by_image.values())
    false_negatives = max(0, total_gt - true_positives)
    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )
    return {
        "precision": precision,
        "recall": recall,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
    }


def pycocotools_map50(ground_truth_path: str | Path, predictions_path: str | Path) -> float | None:
    """Return COCOeval AP at IoU 0.5, or None if the adapter is unavailable."""
    try:
        import numpy as np  # pycocotools requires NumPy
        from pycocotools.coco import COCO
        from pycocotools.cocoeval import COCOeval
    except ModuleNotFoundError:
        return None

    coco_gt = COCO(str(ground_truth_path))
    coco_dt = coco_gt.loadRes(str(predictions_path))
    evaluator = COCOeval(coco_gt, coco_dt, "bbox")
    evaluator.params.iouThrs = np.array([0.5], dtype=float)
    evaluator.evaluate()
    evaluator.accumulate()
    evaluator.summarize()
    return float(evaluator.stats[0])


def ultralytics_val_metrics(
    weights: str,
    data: str,
    imgsz: int,
    confidence: float,
) -> dict[str, Any]:
    """Run Ultralytics ``val`` and extract its own summary metrics."""
    try:
        from ultralytics import YOLO
    except ModuleNotFoundError as exc:
        raise RuntimeError("ultralytics is not installed") from exc

    model = YOLO(weights)
    metrics = model.val(
        data=data,
        imgsz=imgsz,
        conf=confidence,
        verbose=False,
    )
    box = getattr(metrics, "box", None)
    speed = getattr(metrics, "speed", {}) or {}
    return {
        "precision": getattr(box, "mp", None),
        "recall": getattr(box, "mr", None),
        "map50": getattr(box, "map50", None),
        "speed_ms": speed.get("inference"),
    }


def median_inference_ms(log_path: str | Path, imgsz: int, min_frames: int = 500) -> float | None:
    """Return median inference time only when 500+ matching real rows exist."""
    try:
        records = common.assert_real_log(load_latency_records(log_path), "latency log")
    except (OSError, ValueError):
        return None
    values = []
    for row in records:
        if row.get("stage") != "infer_ms" or row.get("imgsz") != imgsz:
            continue
        duration = common.numeric(row.get("duration_ms"))
        if duration is not None:
            values.append(duration)
    if len(values) < min_frames:
        return None
    return statistics.median(values)


def blank_result() -> dict[str, Any]:
    return common.blank_result(
        "B-detection",
        [
            common.blank_cell(
                confidence=confidence,
                precision=None,
                recall=None,
                map50=None,
                speed_median_ms=None,
            )
            for confidence in (0.15, 0.25, 0.35)
        ],
        protocol=(
            "Declare 200-300 labeled COCO/LVIS/own images, a separate tuning "
            "split, frozen prompts, and the report split before generating "
            "predictions. Never tune on the reported images. Use pycocotools "
            "or Ultralytics val for mAP@0.5 and report precision, recall, "
            "and speed. Negative results are reportable."
        ),
    )


def self_check() -> dict[str, Any]:
    """Check IoU arithmetic and blank-template structure; not an experiment."""
    assert iou_xywh([0, 0, 10, 10], [0, 0, 10, 10]) == 1.0
    assert iou_xywh([0, 0, 10, 10], [20, 20, 10, 10]) == 0.0
    fixture_gt = {"annotations": [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10]}]}
    fixture_pred = [{"image_id": 1, "category_id": 1, "bbox": [0, 0, 10, 10], "score": 0.9}]
    pr = precision_recall_at_iou05(fixture_gt, fixture_pred, 0.15)
    assert pr["precision"] == 1.0 and pr["recall"] == 1.0
    cells = blank_result()["cells"]
    assert len(cells) == 3 and all(cell["precision"] is None for cell in cells)
    return {"status": common.SELF_CHECK, "scope": "in-memory IoU/blank-template fixture"}


def _file_sha256(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_evaluation(args: argparse.Namespace) -> dict[str, Any]:
    reasons: list[str] = []
    try:
        dataset_manifest = common.load_json(args.dataset_manifest)
    except (OSError, ValueError) as exc:
        return {
            "experiment": "B-detection",
            "status": common.INSUFFICIENT_DATA,
            "reasons": [f"dataset manifest unavailable: {exc}"],
            "metrics": {},
        }
    problems = common.validate_dataset_manifest(dataset_manifest)
    if problems:
        reasons.extend(problems)

    metrics: dict[str, Any] = {
        "precision": None,
        "recall": None,
        "map50": None,
        "speed_median_ms": None,
    }
    backend = args.backend

    if backend == "pycocotools":
        if not args.ground_truth or not args.predictions:
            reasons.append("pycocotools backend requires --ground-truth and --predictions")
        else:
            try:
                gt = common.load_json(args.ground_truth)
                preds = common.load_json(args.predictions)
                if not isinstance(preds, list):
                    raise ValueError("predictions JSON must be a list")
                pr = precision_recall_at_iou05(gt, preds, args.confidence)
                metrics["precision"] = pr["precision"]
                metrics["recall"] = pr["recall"]
                metrics["true_positives"] = pr["true_positives"]
                metrics["false_positives"] = pr["false_positives"]
                metrics["false_negatives"] = pr["false_negatives"]
                metrics["map50"] = pycocotools_map50(args.ground_truth, args.predictions)
                if metrics["map50"] is None:
                    reasons.append("pycocotools is not installed; mAP@0.5 is unavailable")
                metrics["predictions_sha256"] = _file_sha256(args.predictions)
            except (OSError, ValueError, TypeError) as exc:
                reasons.append(f"COCO input error: {exc}")
    elif backend == "ultralytics":
        if not args.weights or not args.data:
            reasons.append("ultralytics backend requires --weights and --data")
        else:
            try:
                metrics.update(ultralytics_val_metrics(args.weights, args.data, args.imgsz, args.confidence))
                if metrics.get("map50") is None:
                    reasons.append("Ultralytics val did not expose box.map50")
            except Exception as exc:  # external adapter / model / dataset errors
                reasons.append(f"Ultralytics val error: {exc}")

    if args.latency_log:
        metrics["speed_median_ms"] = median_inference_ms(args.latency_log, args.imgsz)
        if metrics["speed_median_ms"] is None:
            reasons.append("speed requires 500+ matching real inference rows")
    else:
        reasons.append("speed requires a real TRINEXIS_LATENCY_LOG JSONL file")

    status = common.MEASURED if not reasons else common.INSUFFICIENT_DATA
    return {
        "experiment": "B-detection",
        "status": status,
        "warning": (
            "Report negative results as-is. Author must verify every value."
            if status == common.MEASURED
            else "No empirical detection result is reported from incomplete data."
        ),
        "backend": backend,
        "confidence": args.confidence,
        "imgsz": args.imgsz,
        "vocab_size": args.vocab_size,
        "vocab_manifest_sha256": args.vocab_manifest_sha256,
        "dataset_manifest": dataset_manifest,
        "dataset_manifest_sha256": common.canonical_sha256(dataset_manifest),
        "reasons": reasons,
        "metrics": metrics,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--emit-blank", action="store_true")
    group.add_argument("--run", action="store_true")
    parser.add_argument("--backend", choices=("pycocotools", "ultralytics"))
    parser.add_argument("--ground-truth")
    parser.add_argument("--predictions")
    parser.add_argument("--weights")
    parser.add_argument("--data")
    parser.add_argument("--dataset-manifest", default="experiments/dataset_manifest.json")
    parser.add_argument("--latency-log")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--confidence", type=float, default=0.15)
    parser.add_argument("--vocab-size", type=int)
    parser.add_argument("--vocab-manifest-sha256")
    parser.add_argument("--output", default="experiments/results/detection_results.json")
    args = parser.parse_args()

    if args.self_check:
        print(self_check()["status"])
        return 0
    if args.emit_blank:
        path = common.write_json(args.output, blank_result())
        print(f"Wrote blank template: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        return 0
    if not args.backend:
        parser.error("--run requires --backend pycocotools|ultralytics")
    result = run_evaluation(args)
    path = common.write_json(args.output, result)
    print(f"{result['status']}: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

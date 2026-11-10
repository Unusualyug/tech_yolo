#!/usr/bin/env python3
"""Pure, dependency-free policy helpers for the updated TRINEXIS backend.

These functions are deliberately isolated from Flask, OpenCV, NumPy, Ultralytics,
and gTTS so that the repository's control policies can be unit-tested without
loading model weights or opening a camera.
"""
from __future__ import annotations

import hmac
import os
from typing import Iterable, Mapping, Sequence

ALLOWED_MODELS = (
    "yolov8s-worldv2.pt",
    "yolov8n.pt",
    "yolo11m.pt",
    "yolo11x.pt",
)

DISTANCE_INDEX_NOTE = (
    "A relative size-based index computed from a heuristic width and focal "
    "constant. It is not calibrated metric distance and has no physical unit."
)


def camera_config(env: Mapping[str, str] | None = None) -> dict[str, object]:
    """Return camera index and backend name from environment variables."""
    source = os.environ if env is None else env
    try:
        index = int(source.get("TRINEXIS_CAMERA_INDEX", "1"))
    except ValueError as exc:
        raise ValueError("TRINEXIS_CAMERA_INDEX must be an integer") from exc
    if index < 0:
        raise ValueError("TRINEXIS_CAMERA_INDEX must be non-negative")
    backend = source.get("TRINEXIS_CAMERA_BACKEND", "AUTO").strip().upper()
    if backend not in {"AUTO", "DSHOW", "MSMF", "V4L2"}:
        raise ValueError(
            "TRINEXIS_CAMERA_BACKEND must be AUTO, DSHOW, MSMF, or V4L2"
        )
    return {"index": index, "backend": backend}


def normalize_model_name(value: object) -> str:
    """Validate a model filename against the checked-in model allowlist."""
    if not isinstance(value, str):
        raise ValueError("Model name must be a string")
    name = value.strip()
    if name not in ALLOWED_MODELS:
        raise ValueError(
            "Unsupported model. Allowed values: " + ", ".join(ALLOWED_MODELS)
        )
    return name


def _rank_key(obj: Mapping[str, object], alerts: Iterable[str]) -> tuple:
    alert_set = set(alerts)
    return (
        0 if obj.get("name") in alert_set else 1,
        -float(obj.get("confidence", 0.0)),
        float(obj.get("distance", 0.0)),
    )


def select_speech_objects(
    objects: Sequence[Mapping[str, object]],
    alerts: Iterable[str],
    limit: int,
) -> list[Mapping[str, object]]:
    """Rank alerts before truncating the spoken shortlist."""
    n = max(0, int(limit))
    return sorted(objects, key=lambda obj: _rank_key(obj, alerts))[:n]


def legacy_select_speech_objects(
    objects: Sequence[Mapping[str, object]],
    alerts: Iterable[str],
    limit: int,
) -> list[Mapping[str, object]]:
    """Reproduce the legacy defect: truncate by confidence, then rerank."""
    n = max(0, int(limit))
    shortlist = sorted(
        objects,
        key=lambda obj: -float(obj.get("confidence", 0.0)),
    )[:n]
    return sorted(shortlist, key=lambda obj: _rank_key(obj, alerts))


def time_decay_factor(elapsed_seconds: float, half_life_s: float) -> float:
    """Frame-rate-independent exponential decay for the heatmap."""
    half_life = float(half_life_s)
    if half_life <= 0:
        raise ValueError("half_life_s must be positive")
    dt = max(0.0, float(elapsed_seconds))
    return 0.5 ** (dt / half_life)


def relative_distance_index(
    width_px: float,
    known_width: float = 60.0,
    focal_length: float = 360.0,
) -> float:
    """Return the non-metric distance index used by the updated overlay."""
    return (float(known_width) * float(focal_length)) / max(float(width_px), 1.0)


def rate_per_second(
    timestamps: Iterable[float],
    now: float,
    window_s: float = 5.0,
) -> float:
    """Compute an event rate over a fixed trailing time window."""
    window = float(window_s)
    if window <= 0:
        raise ValueError("window_s must be positive")
    cutoff = float(now) - window
    count = sum(1 for stamp in timestamps if float(stamp) >= cutoff)
    return count / window


def validate_control_request(api_token: str, headers: Mapping[str, str]) -> bool:
    """Validate an optional API token on mutating control requests.

    Kept for backward compatibility with the existing unit tests and callers.
    New route code should use :func:`control_request_status`, which also
    distinguishes read-only and unsupported-scheme rejections.
    """
    token = str(api_token or "")
    if not token:
        return True
    supplied = headers.get("X-API-Token") or headers.get("Authorization") or ""
    if supplied.startswith("Bearer "):
        supplied = supplied[7:]
    return hmac.compare_digest(str(supplied), token)


def control_request_status(
    api_token: str,
    headers: Mapping[str, str],
    read_only: bool = False,
    method: str = "GET",
) -> tuple[bool, int, str]:
    """Return ``(allowed, status_code, message)`` for one control request.

    ``401`` means the API token is missing or invalid. ``403`` means the
    request is understood but forbidden: either mutations are disabled in
    read-only mode or an unsupported Authorization scheme was supplied. GET
    requests remain readable; deployment code applies this helper only to
    mutating control routes.
    """
    token = str(api_token or "")
    auth = str(headers.get("Authorization") or "")
    explicit = str(headers.get("X-API-Token") or "")

    if token:
        if auth and not auth.startswith("Bearer ") and not explicit:
            return (
                False,
                403,
                "Unsupported authorization scheme; use X-API-Token or Bearer",
            )
        supplied = explicit or auth
        if supplied.startswith("Bearer "):
            supplied = supplied[7:]
        if not hmac.compare_digest(str(supplied), token):
            return False, 401, "Invalid or missing API token"

    if read_only and str(method).upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        return False, 403, "Mutations disabled by read-only mode"
    return True, 200, "Allowed"


def single_client_check(
    active_id: str | None,
    candidate_id: str,
    last_seen: float,
    now: float,
    timeout_s: float = 60.0,
) -> tuple[bool, str, float]:
    """Allow one controlling client, with a timeout for stale sessions."""
    timeout = float(timeout_s)
    if active_id is None or active_id == candidate_id or now - last_seen > timeout:
        return True, candidate_id, now
    return False, active_id, last_seen

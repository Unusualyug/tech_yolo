#!/usr/bin/env python3
"""Check prerequisites and captured evidence for a real TRINEXIS smoke test.

This script never starts Flask, opens a camera, loads a model, synthesizes
speech, creates a screenshot, or invents a detection/sentence example. It only
reports what is present on the machine and verifies user-captured evidence.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trinexis_core import ALLOWED_MODELS  # noqa: E402

CORE_MODULES = ("cv2", "numpy", "ultralytics", "gtts", "flask")
EVAL_MODULES = ("pycocotools",)
REQUIRED_ENV = (
    "TRINEXIS_LATENCY_LOG",
    "TRINEXIS_EVENT_LOG",
    "TRINEXIS_EXPERIMENT_SETTING",
    "TRINEXIS_HARDWARE_MANIFEST",
    "TRINEXIS_ALERT_MANIFEST",
)
MANIFESTS = (
    "experiments/hardware_manifest.json",
    "experiments/alert_manifest.json",
    "experiments/session_manifest.json",
    "experiments/dataset_manifest.json",
    "experiments/vocab_manifest.json",
)
EVIDENCE = {
    "dashboard_screenshot": "experiments/results/dashboard_screenshot.png",
    "spoken_io_example": "experiments/results/spoken_io_example.md",
    "export_logs": "experiments/results/export_logs.json",
    "speech_events": "experiments/results/speech_events.jsonl",
    "latency_log": "experiments/results/latency.jsonl",
}


def check(name: str, ready: bool, details: str, *, required_for_run: bool = True) -> dict[str, Any]:
    return {
        "name": name,
        "ready": bool(ready),
        "required_for_run": required_for_run,
        "details": details,
    }


def check_camera() -> dict[str, Any]:
    devices = sorted(str(path) for path in Path("/dev").glob("video*"))
    return check("camera_device", bool(devices), ", ".join(devices) or "no /dev/video* device")


def check_module(module: str, *, required_for_run: bool = True) -> dict[str, Any]:
    try:
        found = importlib.util.find_spec(module) is not None
    except (ImportError, ValueError) as exc:
        return check(f"module_{module}", False, str(exc), required_for_run=required_for_run)
    return check(
        f"module_{module}",
        found,
        "importable" if found else "not importable in the current Python environment",
        required_for_run=required_for_run,
    )


def check_git_lfs() -> dict[str, Any]:
    git = shutil.which("git")
    if not git:
        return check("git_lfs", False, "git executable not found")
    try:
        proc = subprocess.run(
            [git, "lfs", "version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return check("git_lfs", False, str(exc))
    output = (proc.stdout + proc.stderr).strip()
    return check("git_lfs", proc.returncode == 0, output or "git lfs version returned no output")


def check_weights() -> dict[str, Any]:
    details: list[str] = []
    ready = True
    for name in ALLOWED_MODELS:
        path = ROOT / name
        if not path.exists():
            ready = False
            details.append(f"{name}: missing")
            continue
        with path.open("rb") as handle:
            head = handle.read(200)
        pointer = head.startswith(b"version https://git-lfs.github.com/spec/v1")
        if pointer:
            ready = False
            details.append(f"{name}: unhydrated Git LFS pointer")
        else:
            details.append(f"{name}: present, not a pointer")
    return check("model_weights", ready, "; ".join(details))


def check_environment(env: Mapping[str, str]) -> dict[str, Any]:
    missing = [name for name in REQUIRED_ENV if not env.get(name, "").strip()]
    return check(
        "environment_variables",
        not missing,
        "all five configured" if not missing else "missing: " + ", ".join(missing),
    )


def check_manifests(env: Mapping[str, str]) -> dict[str, Any]:
    problems: list[str] = []
    for rel in MANIFESTS:
        path = ROOT / rel
        if not path.exists():
            problems.append(f"{rel}: missing")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            problems.append(f"{rel}: invalid JSON ({exc})")
            continue
        if rel.endswith("alert_manifest.json"):
            objects = payload.get("alert_objects") if isinstance(payload, dict) else None
            declared = payload.get("declared_at") if isinstance(payload, dict) else None
            if not declared or not isinstance(objects, list) or not [str(item).strip() for item in objects if str(item).strip()]:
                problems.append(f"{rel}: declared_at and nonempty alert_objects are required")
    alert_env = env.get("TRINEXIS_ALERT_MANIFEST", "").strip()
    if alert_env:
        path = Path(alert_env)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            problems.append("TRINEXIS_ALERT_MANIFEST path does not exist")
    return check(
        "manifests",
        not problems,
        "five parseable manifests; alert objects declared" if not problems else "; ".join(problems),
    )


def check_prereqs(env: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = os.environ if env is None else env
    checks = [check_camera()]
    checks.extend(check_module(module) for module in CORE_MODULES)
    checks.extend(check_module(module, required_for_run=False) for module in EVAL_MODULES)
    checks.extend([
        check_git_lfs(),
        check_weights(),
        check_environment(source),
        check_manifests(source),
    ])
    missing_run = [row["name"] for row in checks if row["required_for_run"] and not row["ready"]]
    missing_experiments = [row["name"] for row in checks if not row["ready"]]
    evidence_present = {name: (ROOT / rel).exists() for name, rel in EVIDENCE.items()}
    return {
        "scope": "local prerequisite inspection; no live app was run",
        "run_ready": not missing_run,
        "experiment_ready": not missing_experiments,
        "evidence_complete": all(evidence_present.values()),
        "missing_for_run": missing_run,
        "missing_for_experiments": missing_experiments,
        "evidence_present": evidence_present,
        "checks": checks,
    }


def verify_evidence() -> dict[str, Any]:
    problems: list[str] = []
    for name, rel in EVIDENCE.items():
        if not (ROOT / rel).exists():
            problems.append(f"{name}: missing {rel}")
    screenshot = ROOT / EVIDENCE["dashboard_screenshot"]
    if screenshot.exists() and not screenshot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        problems.append("dashboard_screenshot: not a PNG file")
    example = ROOT / EVIDENCE["spoken_io_example"]
    if example.exists():
        text = example.read_text(encoding="utf-8")
        for heading in ("## Detections in", "## Spoken sentence out", "## Human verification"):
            if heading not in text:
                problems.append(f"spoken_io_example: missing {heading}")
        if "NO DATA" in text:
            problems.append("spoken_io_example: NO DATA placeholders remain")
    detection = ROOT / EVIDENCE["export_logs"]
    if detection.exists():
        try:
            payload = json.loads(detection.read_text(encoding="utf-8"))
        except ValueError as exc:
            problems.append(f"export_logs: invalid JSON ({exc})")
        else:
            frames = payload.get("logs", []) if isinstance(payload, dict) else payload
            if not isinstance(frames, list) or not frames:
                problems.append("export_logs: no detection frames")
            elif any(str(row).lower().find("synthetic") >= 0 for row in frames[:10] if isinstance(row, Mapping)):
                problems.append("export_logs: explicitly synthetic rows are not real evidence")
    events = ROOT / EVIDENCE["speech_events"]
    if events.exists():
        rows = []
        for line in events.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    problems.append("speech_events: malformed JSONL row")
                    break
        if not any(row.get("event") == "speech_enqueued" for row in rows if isinstance(row, dict)):
            problems.append("speech_events: no speech_enqueued event")
        if any(row.get("synthetic") is True or row.get("fixture") is True for row in rows if isinstance(row, dict)):
            problems.append("speech_events: explicitly synthetic rows are not real evidence")
    latency = ROOT / EVIDENCE["latency_log"]
    if latency.exists():
        for line in latency.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    json.loads(line)
                except ValueError:
                    problems.append("latency_log: malformed JSONL row")
                    break
    return {
        "scope": "file-format and provenance checks only; no empirical result is inferred",
        "status": "EVIDENCE OK" if not problems else "EVIDENCE INCOMPLETE",
        "problems": problems,
    }


def instructions() -> str:
    return "\n".join([
        "Hand-run smoke test:",
        "1. python3 scripts/live_smoke_test.py --check-prereqs  (run_ready must be true)",
        "2. Set TRINEXIS_LATENCY_LOG, TRINEXIS_EVENT_LOG, TRINEXIS_EXPERIMENT_SETTING,",
        "   TRINEXIS_HARDWARE_MANIFEST, and TRINEXIS_ALERT_MANIFEST; then python3 app23.py.",
        "3. Save experiments/results/dashboard_screenshot.png, export_logs.json,",
        "   speech_events.jsonl, latency.jsonl, and spoken_io_example.md from one real run.",
        "4. python3 scripts/live_smoke_test.py --verify-evidence",
        "Full checklist: experiments/LIVE_SMOKE_TEST.md",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-check", action="store_true")
    group.add_argument("--check-prereqs", action="store_true")
    group.add_argument("--verify-evidence", action="store_true")
    group.add_argument("--instructions", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        report = check_prereqs({})
        assert "run_ready" in report and "evidence_present" in report
        assert set(EVIDENCE) == set(report["evidence_present"])
        assert "TRINEXIS_EVENT_LOG" in instructions()
        print("SOFTWARE SELF-CHECK ONLY")
        return 0
    if args.check_prereqs:
        report = check_prereqs()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["run_ready"] else 2
    if args.verify_evidence:
        report = verify_evidence()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["status"] == "EVIDENCE OK" else 2
    print(instructions())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Write a machine-readable audit for the repository-fixed TRINEXIS release."""
from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "artifacts" / "updated_repository_audit.json"
SOURCE_BASELINE = "6a0405613171a5ed400a7339c3e0a8f6bb94b26d"
RELEASE_TAG = "v0.3.0-standalone"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def run_tests() -> dict[str, object]:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = proc.stderr + proc.stdout
    match = re.search(r"Ran (\d+) tests", output)
    failures = re.search(r"failures=(\d+)", output)
    errors = re.search(r"errors=(\d+)", output)
    return {
        "command": "python3 -m unittest discover -s tests -v",
        "python_version": platform.python_version(),
        "returncode": proc.returncode,
        "test_count": int(match.group(1)) if match else None,
        "failures": int(failures.group(1)) if failures else 0,
        "errors": int(errors.group(1)) if errors else 0,
        "ok": proc.returncode == 0 and "OK" in output,
    }


def tracked_and_new_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(line for line in proc.stdout.splitlines() if line)


def main() -> None:
    alert = json.loads(
        (ROOT / "paper" / "artifacts" / "alert_selection_audit.json").read_text(
            encoding="utf-8"
        )
    )
    files = tracked_and_new_files()
    artifacts = {}
    for rel in [
        "paper/tech_yolo_updated_research_paper.pdf",
        "paper/tech_yolo_updated_research_paper.docx",
        "paper/tech_yolo_updated_research_paper.md",
        "paper/artifacts/alert_selection_audit.json",
        "paper/artifacts/fig1_system_architecture_updated.svg",
        "paper/artifacts/fig1_system_architecture_updated.pdf",
        "paper/artifacts/fig2_implementation_verification.svg",
        "paper/artifacts/fig2_implementation_verification.pdf",
        "paper/reference_verification.md",
        "weights/download_weights.py",
        "weights/weights_checksums.sha256",
        "zenodo.json",
        "ZENODO.md",
    ]:
        path = ROOT / rel
        if path.exists():
            artifacts[rel] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }

    result = {
        "audit_date": date.today().isoformat(),
        "release_tag": RELEASE_TAG,
        "release_url": f"https://github.com/Unusualyug/tech_yolo/releases/tag/{RELEASE_TAG}",
        "source_baseline_commit": SOURCE_BASELINE,
        "zenodo_doi": None,
        "zenodo_status": "pending author authorization",
        "license": "AGPL-3.0-only",
        "evidence_boundary": (
            "Static and synthetic verification only. No model inference, camera "
            "capture, labeled dataset, hardware timing campaign, distance "
            "calibration, translated-template rating, or human-participant "
            "evaluation was performed."
        ),
        "repository_fixes": [
            "AGPL-3.0 LICENSE, README.md, pinned requirements.txt, CITATION.cff, codemeta.json, .env.example, THIRD_PARTY_LICENSES.md",
            "configurable camera index/backend, host/port, API token, single-client mode, and heatmap half-life",
            "alert-aware speech selection before shortlist truncation",
            "separate capture_fps and inference_fps counters",
            "AVG CONFIDENCE dashboard label",
            "time-based heatmap decay and unitless relative distance index",
            "model allowlist for /set_model",
            "standard-library unit and source-contract tests",
            "weights download script with SHA-256 LFS-pointer manifest",
            "per-reference DOI/publisher verification log",
            "prepared Zenodo metadata; DOI pending author authorization",
            "enlarged PNG plus standalone SVG and vector-PDF figures",
        ],
        "tests": run_tests(),
        "alert_selection_audit": alert,
        "file_count": len(files),
        "files": files,
        "artifact_checksums": artifacts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(json.dumps({
        "release_tag": result["release_tag"],
        "file_count": result["file_count"],
        "tests": result["tests"],
        "alert_selection_audit": {
            "legacy_drop_rate": alert["legacy_drop_rate"],
            "updated_drop_rate": alert["updated_drop_rate"],
        },
    }, indent=2))


if __name__ == "__main__":
    main()

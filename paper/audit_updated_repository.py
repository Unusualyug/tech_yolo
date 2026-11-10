#!/usr/bin/env python3
"""Write a machine-readable audit for the unreleased TRINEXIS fix revision."""
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.synthetic_regression import write_artifact  # noqa: E402

OUT = ROOT / "paper" / "artifacts" / "updated_repository_audit.json"
SOURCE_BASELINE = "6a0405613171a5ed400a7339c3e0a8f6bb94b26d"
PRIOR_RELEASE_TAG = "v0.3.0-standalone"
WORKING_BRANCH = "arena/69777d37-tech-yolo"


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
    alert_path = write_artifact()
    alert = json.loads(alert_path.read_text(encoding="utf-8"))
    summary_path = ROOT / "paper" / "artifacts" / "test_summary.json"
    test_summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else None
    files = tracked_and_new_files()
    artifacts = {}
    for rel in [
        "paper/tech_yolo_updated_research_paper.pdf",
        "paper/tech_yolo_updated_research_paper.docx",
        "paper/tech_yolo_updated_research_paper.md",
        "paper/artifacts/alert_selection_audit.json",
        "paper/artifacts/test_summary.json",
        "paper/artifacts/fig1_system_architecture_updated.svg",
        "paper/artifacts/fig1_system_architecture_updated.pdf",
        "paper/artifacts/fig2_implementation_verification.svg",
        "paper/artifacts/fig2_implementation_verification.pdf",
        "paper/reference_verification.md",
        "paper/venue_guide_notes.md",
        "paper/updated_manuscript_content.py",
        "paper/README.md",
        "FIX_STATUS.md",
        "README.md",
        "CITATION.cff",
        "codemeta.json",
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "THIRD_PARTY_LICENSES.md",
        "requirements-ci.txt",
        ".github/workflows/ci.yml",
        "scripts/report_test_counts.py",
        "scripts/verify_no_fabricated_results.py",
        "tests/test_routes.py",
        "tests/test_synthetic_regression.py",
        "tests/synthetic_regression.py",
        "experiments/README.md",
        "experiments/RESULTS_TEMPLATE.md",
        "experiments/LIVE_SMOKE_TEST.md",
        "experiments/SPOKEN_IO_EXAMPLE.template.md",
        "experiments/USER_STUDY_PROTOCOL.md",
        "experiments/ethics_inquiry_receipt.md",
        "experiments/session_manifest.template.json",
        "experiments/user_study_worksheet.template.csv",
        "experiments/latency_benchmark.py",
        "experiments/detection_eval.py",
        "experiments/vocab_confidence_grid.py",
        "experiments/alert_replay.py",
        "experiments/multi_session_replay.py",
        "experiments/user_study.py",
        "experiments/language_eval.py",
        "scripts/live_smoke_test.py",
        "scripts/check_arxiv_metadata.py",
        "scripts/final_release_checklist.py",
        "trinexis_core.py",
        "trinexis_telemetry.py",
        "trinexis_language.py",
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
        "prior_immutable_release_tag": PRIOR_RELEASE_TAG,
        "prior_release_url": f"https://github.com/Unusualyug/tech_yolo/releases/tag/{PRIOR_RELEASE_TAG}",
        "working_branch": WORKING_BRANCH,
        "unreleased_fixes": True,
        "source_baseline_commit": SOURCE_BASELINE,
        "zenodo_doi": None,
        "zenodo_status": "pending author authorization and final GitHub/Zenodo release",
        "license": "AGPL-3.0-only",
        "submission_ready": False,
        "evidence_boundary": (
            "Static, synthetic, and mocked-route software verification only. "
            "No model inference, camera capture, labeled dataset, hardware "
            "timing campaign, distance calibration, translated-template "
            "rating, or human-participant evaluation was performed. All "
            "empirical result cells are NO DATA. Published numeric context is "
            "cited as non-comparable related work, not as a TRINEXIS measurement."
        ),
        "repository_fixes": [
            "AGPL-3.0 LICENSE, README.md, pinned requirements.txt, CITATION.cff, codemeta.json, .env.example, THIRD_PARTY_LICENSES.md",
            "configurable camera index/backend, host/port, API token, read-only mode, single-client mode, and heatmap half-life",
            "alert-aware speech selection before shortlist truncation and a frozen predeclared alert-manifest mode",
            "separate capture_fps and inference_fps counters",
            "AVG CONFIDENCE dashboard label",
            "time-based heatmap decay and unitless relative distance index",
            "model allowlist for /set_model",
            "real Flask test-client route tests for all 23 routes with unittest.mock",
            "policy/telemetry/language/harness unit tests and a tests/-only synthetic regression",
            "GitHub Actions CI on every push and pull request",
            "optional JSONL latency and speech-event instrumentation",
            "Experiments A-D protocols, blank NO DATA result templates, and manifest templates",
            "nearest-object-first baseline, 5-10 session replay harness, and guarded three-policy user-study worksheet",
            "hand-run live smoke-test checklist, dashboard/spoken-example verifier, and prereq inspector",
            "protocol-only paper reframing, preregistered measurement plan, one limitations paragraph, and Figure 2 untagged-snapshot correction",
            "clearly cited published-context table using verified scale facts from [2], [3], [19]; no external benchmark value entered into TRINEXIS result cells",
            "sandbox-only harness self-check/blank-template transcript; no empirical result, screenshot, spoken example, or DOI created",
            "arXiv/institutional-report guide notes, mechanical metadata check, and final-release gate",
            "early departmental ethics-route inquiry sent with a verifiable Gmail receipt; no approval claimed",
            "all 24 reference rows ticked after direct publisher/official-page recheck",
            "language-fallback metadata/UI and explicit unchecked-language status",
            "weights download script with SHA-256 LFS-pointer manifest",
            "per-reference DOI/publisher verification log",
            "prepared Zenodo metadata; DOI pending author authorization and final release",
            "enlarged PNG plus standalone SVG and vector-PDF figures",
        ],
        "experiment_protocols": [
            "A: 500+ frames at 416/640/832 on declared hardware; median/p95 by stage",
            "B: 200-300 labeled images; precision/recall/mAP@0.5/speed; frozen prompt grid",
            "C: 5-10 real sessions; predeclared alerts; alert-first/confidence-first/nearest-object-first replay",
            "D: 5-10 checked languages x 10 announcements; 1-5 correctness/naturalness ratings",
            "E: optional 8-12 person three-policy user-noticing study pending consent and institutional ethics approval",
        ],
        "tests": run_tests(),
        "test_summary": test_summary,
        "alert_selection_audit": alert,
        "file_count": len(files),
        "files": files,
        "artifact_checksums": artifacts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")
    print(json.dumps({
        "working_branch": result["working_branch"],
        "unreleased_fixes": result["unreleased_fixes"],
        "file_count": result["file_count"],
        "tests": result["tests"],
        "zenodo_doi": result["zenodo_doi"],
        "alert_selection_audit_source": alert["source"],
    }, indent=2))


if __name__ == "__main__":
    main()

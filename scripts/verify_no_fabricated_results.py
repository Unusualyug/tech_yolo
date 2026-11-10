#!/usr/bin/env python3
"""Fail if the repository starts claiming empirical results or a DOI."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "results"
PAPER_MD = ROOT / "paper" / "tech_yolo_updated_research_paper.md"
FIX_STATUS = ROOT / "FIX_STATUS.md"

FORBIDDEN_MD_PATTERNS = (
    r"mAP@0\.5\s*=",
    r"median latency\s*=",
    r"p95 latency\s*=",
    r"user study (?:showed|found|demonstrated)",
    r"users noticed .* faster",
)


def main() -> int:
    errors: list[str] = []

    generated = [
        path for path in RESULTS.glob("*")
        if path.is_file() and path.name != ".gitkeep"
    ]
    for path in generated:
        if path.suffix in {".json", ".csv", ".jsonl"}:
            errors.append(f"unexpected generated result file: {path.relative_to(ROOT)}")

    paper = PAPER_MD.read_text(encoding="utf-8") if PAPER_MD.exists() else ""
    if paper:
        for pattern in FORBIDDEN_MD_PATTERNS:
            if re.search(pattern, paper, flags=re.IGNORECASE):
                errors.append(f"possible empirical claim in manuscript: {pattern}")
        for required in (
            "NO DATA",
            "research question",
            "not submission-ready",
            "Zenodo DOI has not been minted",
            "PUBLISHED CONTEXT (NOT TRINEXIS MEASUREMENTS)",
            "not entered into Table V",
        ):
            if required not in paper:
                errors.append(f"manuscript missing evidence-boundary phrase: {required}")
    else:
        errors.append("rebuilt manuscript Markdown is missing")

    summary_path = ROOT / "paper" / "artifacts" / "test_summary.json"
    if not summary_path.exists():
        errors.append("test_summary.json is missing")
    else:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        expected_counts = {
            "route_tests": 43,
            "policy_tests": 37,
            "source_contract_tests": 13,
            "total_tests": 93,
        }
        for key, expected in expected_counts.items():
            if summary.get(key) != expected:
                errors.append(f"test count {key} is {summary.get(key)!r}, expected {expected}")
        if summary.get("exact_report_phrase") != "43 route tests plus 37 policy tests, run in CI":
            errors.append("test summary exact CI phrase is stale")

    zenodo = json.loads((ROOT / "zenodo.json").read_text(encoding="utf-8"))
    if "DOI pending" not in zenodo.get("notes", ""):
        errors.append("zenodo.json no longer says DOI pending")
    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if re.search(r"^doi:", cff, flags=re.MULTILINE):
        errors.append("CITATION.cff contains a DOI before final release/authorization")
    audit_path = ROOT / "paper" / "artifacts" / "updated_repository_audit.json"
    if audit_path.exists():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if audit.get("zenodo_doi") is not None:
            errors.append("repository audit contains a DOI before authorization")
    if not FIX_STATUS.exists():
        errors.append("FIX_STATUS.md is missing")
    elif "pending" not in FIX_STATUS.read_text(encoding="utf-8").lower():
        errors.append("FIX_STATUS.md does not identify pending empirical work")

    protocol_path = ROOT / "experiments" / "USER_STUDY_PROTOCOL.md"
    if not protocol_path.exists():
        errors.append("experiments/USER_STUDY_PROTOCOL.md is missing")
    else:
        protocol = protocol_path.read_text(encoding="utf-8").lower()
        if "no reply, approval, or waiver is claimed" not in protocol:
            errors.append("user-study protocol no longer says no approval/waiver exists")
        if re.search(r"ethics approval (?:received|granted|obtained)", protocol):
            errors.append("user-study protocol claims institutional ethics approval")

    if errors:
        print("EVIDENCE BOUNDARY CHECK FAILED", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print("EVIDENCE BOUNDARY CHECK OK: no empirical results or DOI claimed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

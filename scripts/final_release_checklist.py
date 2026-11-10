#!/usr/bin/env python3
"""Gate the final v1.0.0 release and Zenodo DOI work.

This script never creates a tag, release, DOI, or remote state. It checks the
ordered preconditions and prints the exact author-only sequence. A DOI is
permanent for the exact archived version, so the final release must come last.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "experiments" / "RESULTS_TEMPLATE.md"
PAPER_MD = ROOT / "paper" / "tech_yolo_updated_research_paper.md"
VENUE = ROOT / "paper" / "venue_guide_notes.md"
REFERENCES = ROOT / "paper" / "reference_verification.md"
ZENODO = ROOT / "zenodo.json"
CITATION = ROOT / "CITATION.cff"
AUDIT = ROOT / "paper" / "artifacts" / "updated_repository_audit.json"
STATUS = ROOT / "FIX_STATUS.md"
EVIDENCE_FILES = (
    ROOT / "experiments/results/dashboard_screenshot.png",
    ROOT / "experiments/results/spoken_io_example.md",
    ROOT / "experiments/results/export_logs.json",
    ROOT / "experiments/results/speech_events.jsonl",
    ROOT / "experiments/results/latency.jsonl",
)


def v1_tag_exists() -> bool:
    try:
        proc = subprocess.run(
            ["git", "tag", "--list", "v1.0.0"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return "v1.0.0" in proc.stdout.splitlines()


def check() -> dict[str, object]:
    blockers: list[str] = []
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, detail: str, blocker: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})
        if not passed and blocker:
            blockers.append(blocker)

    results = RESULTS.read_text(encoding="utf-8") if RESULTS.exists() else ""
    no_data = results.count("NO DATA")
    add("empirical_results_filled", no_data == 0, f"NO DATA cells: {no_data}", "Experiment result cells still contain NO DATA")
    paper = PAPER_MD.read_text(encoding="utf-8") if PAPER_MD.exists() else ""
    add("paper_rewritten", "not submission-ready" not in paper.lower(), "current paper still has status prose", "Paper still says not submission-ready and has not been rewritten around findings")
    add("venue_guide", VENUE.exists(), str(VENUE.relative_to(ROOT)), "Venue guide notes are missing")
    refs = REFERENCES.read_text(encoding="utf-8") if REFERENCES.exists() else ""
    ticked = len(re.findall(r"\|\s*\[x\]\s*\|", refs))
    add("references_ticked", ticked >= 24, f"ticked rows: {ticked}", "Reference verification log is not fully ticked")
    add(
        "live_evidence_files",
        all(path.exists() for path in EVIDENCE_FILES),
        f"present: {sum(path.exists() for path in EVIDENCE_FILES)}/{len(EVIDENCE_FILES)}",
        "Dashboard screenshot and real spoken input/output evidence are incomplete",
    )
    status = STATUS.read_text(encoding="utf-8") if STATUS.exists() else ""
    status_pending = "pending" in status.lower()
    add(
        "status_work_resolved",
        not status_pending,
        f"pending language present: {status_pending}",
        "FIX_STATUS still identifies pending empirical/administrative work",
    )
    zenodo = json.loads(ZENODO.read_text(encoding="utf-8")) if ZENODO.exists() else {}
    add("zenodo_version_final", zenodo.get("version") not in {None, "", "PENDING_FINAL_RELEASE"}, str(zenodo.get("version")), "zenodo.json version is still PENDING_FINAL_RELEASE")
    citation = CITATION.read_text(encoding="utf-8") if CITATION.exists() else ""
    add("citation_doi_absent_before_release", not re.search(r"^doi:", citation, flags=re.MULTILINE), "no DOI key before final release", "CITATION.cff already has a DOI before the final release")
    audit = json.loads(AUDIT.read_text(encoding="utf-8")) if AUDIT.exists() else {}
    add("audit_doi_absent_before_release", audit.get("zenodo_doi") is None, "audit zenodo_doi is null", "Repository audit already contains a DOI")
    add("v1_tag_absent_before_release", not v1_tag_exists(), "v1.0.0 tag not created", "v1.0.0 tag already exists; inspect before doing anything else")
    return {
        "status": "FINAL RELEASE READY" if not blockers else "FINAL RELEASE BLOCKED",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "checks": checks,
        "scope": "local gate only; no tag, release, DOI, or remote action performed",
    }


def instructions() -> str:
    return "\n".join([
        "Final release order (after real results, rewritten paper, and author verification):",
        "1. Freeze code, paper PDF/DOCX/MD, results, manifests, CITATION.cff, README.md,",
        "   codemeta.json, zenodo.json, ZENODO.md, CHANGELOG.md, and RELEASE_NOTES.md.",
        "2. Run 93 tests, all harness self-checks, scripts/verify_no_fabricated_results.py,",
        "   scripts/check_arxiv_metadata.py --check, paper/build_updated_manuscript.py,",
        "   and paper/audit_updated_repository.py. Author verifies every number.",
        "3. git commit and git push origin arena/69777d37-tech-yolo.",
        "4. git tag v1.0.0 && git push origin v1.0.0",
        "5. gh release create v1.0.0 --title 'TRINEXIS v1.0.0' --notes-file RELEASE_NOTES.md",
        "6. Author signs into Zenodo, connects https://github.com/Unusualyug/tech_yolo,",
        "   enables the v1.0.0 repository release, publishes it, and records the DOI.",
        "7. Insert that exact DOI into CITATION.cff, README.md,",
        "   paper/updated_manuscript_content.py, codemeta.json, zenodo.json, ZENODO.md.",
        "   Rebuild PDF/DOCX/MD and the repository audit.",
        "8. Verify the DOI resolves to the exact v1.0.0 release. Do not mint a second DOI.",
        "Author-only clicks: Zenodo GitHub connection, Zenodo publish, arXiv self-submission,",
        "license agreement, and endorsement if required.",
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--instructions", action="store_true")
    group.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.self_check:
        assert "v1.0.0" in instructions()
        assert "FINAL RELEASE BLOCKED" in json.dumps(check())
        print("SOFTWARE SELF-CHECK ONLY")
        return 0
    if args.instructions:
        print(instructions())
        return 0
    report = check()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "FINAL RELEASE READY" else 2


if __name__ == "__main__":
    raise SystemExit(main())

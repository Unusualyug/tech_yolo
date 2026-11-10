#!/usr/bin/env python3
"""Check the current manuscript fields against arXiv metadata requirements.

The official arXiv Submission Guidelines, moderation policy, title/abstract
help, and content-type policy were opened on 2026-11-10; see
``paper/venue_guide_notes.md``. This script checks only local, mechanical
properties. It does not submit the paper, create an arXiv ID, or declare the
manuscript submission-ready.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "paper" / "updated_manuscript_content.py"
NOTES = ROOT / "paper" / "venue_guide_notes.md"
PDF = ROOT / "paper" / "tech_yolo_updated_research_paper.pdf"
ALLOWED_FILENAME = re.compile(r"^[a-zA-Z0-9_+\-.,=]+$")


def string_assignment(name: str) -> str:
    """Read one module-level string assignment without importing dependencies."""
    tree = ast.parse(CONTENT.read_text(encoding="utf-8"), filename=str(CONTENT))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    value = ast.literal_eval(node.value)
                    if not isinstance(value, str):
                        raise ValueError(f"{name} is not a string")
                    return value
    raise KeyError(f"{name} not found in {CONTENT}")


def check() -> dict[str, object]:
    problems: list[str] = []
    title = string_assignment("TITLE")
    abstract = string_assignment("ABSTRACT")
    if not title.strip():
        problems.append("TITLE is empty")
    if title.isupper():
        problems.append("arXiv title field must not be all uppercase")
    if not title.isascii():
        problems.append("arXiv title metadata must be ASCII")
    if not abstract.strip():
        problems.append("ABSTRACT is empty")
    if re.search(r"\babstract\b", abstract, flags=re.IGNORECASE):
        problems.append("arXiv abstract metadata must not include the word 'Abstract'")
    if not abstract.isascii():
        problems.append("arXiv abstract metadata must be ASCII")
    if not PDF.exists():
        problems.append(f"missing PDF: {PDF.relative_to(ROOT)}")
    elif not PDF.read_bytes().startswith(b"%PDF-"):
        problems.append("PDF signature is missing")
    if not ALLOWED_FILENAME.fullmatch(PDF.name):
        problems.append("PDF filename contains characters disallowed by arXiv")
    if not NOTES.exists():
        problems.append(f"missing venue guide notes: {NOTES.relative_to(ROOT)}")
    else:
        notes = NOTES.read_text(encoding="utf-8")
        for required in (
            "https://info.arxiv.org/help/submit/index.html",
            "https://info.arxiv.org/help/moderation/index.html",
            "https://info.arxiv.org/help/prep.html",
            "https://info.arxiv.org/help/policies/content-types.html",
            "Yug G. Lakhani (1)",
            "text-to-text generative AI",
            "not submission-ready",
        ):
            if required not in notes:
                problems.append(f"venue guide notes missing: {required}")
    return {
        "status": "ARXIV METADATA CHECK OK" if not problems else "ARXIV METADATA CHECK FAILED",
        "title_is_ascii": title.isascii(),
        "abstract_is_ascii": abstract.isascii(),
        "abstract_words": len(abstract.split()),
        "pdf_filename": PDF.name,
        "problems": problems,
        "scope": "mechanical metadata check only; no submission or DOI action performed",
    }


def metadata_fields() -> dict[str, str]:
    return {
        "title": string_assignment("TITLE"),
        "authors": "Yug G. Lakhani (1)",
        "affiliations": "((1) Department of Computer Engineering, Gyanmanjari Innovative University, Bhavnagar, India))",
        "abstract": string_assignment("ABSTRACT"),
        "warning": "Paste only after real results, author verification, and final paper rewrite. Current report is not submission-ready.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--metadata", action="store_true")
    args = parser.parse_args()
    if args.metadata:
        print(json.dumps(metadata_fields(), indent=2, ensure_ascii=False))
        return 0
    report = check()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "ARXIV METADATA CHECK OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())

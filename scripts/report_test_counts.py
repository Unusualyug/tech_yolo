#!/usr/bin/env python3
"""Count unittest cases by category and write the paper's CI test summary."""
from __future__ import annotations

import argparse
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "artifacts" / "test_summary.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))


def iter_cases(suite: unittest.TestSuite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from iter_cases(item)
        else:
            yield item


def compute_summary() -> dict[str, object]:
    loader = unittest.TestLoader()
    suite = loader.discover(
        start_dir=str(ROOT / "tests"),
        pattern="test_*.py",
        top_level_dir=str(ROOT / "tests"),
    )
    counts = Counter(type(case).__module__ for case in iter_cases(suite))
    route_tests = counts["test_routes"]
    policy_tests = sum(
        counts[name]
        for name in (
            "test_core",
            "test_policy_regression",
            "test_telemetry",
            "test_language",
            "test_experiment_harnesses",
            "test_synthetic_regression",
        )
    )
    source_contract_tests = counts["test_source_contract"]
    other_tests = sum(
        value for name, value in counts.items()
        if name not in {
            "test_routes",
            "test_core",
            "test_policy_regression",
            "test_telemetry",
            "test_language",
            "test_experiment_harnesses",
            "test_synthetic_regression",
            "test_source_contract",
        }
    )
    phrase = (
        f"{route_tests} route tests plus {policy_tests} policy tests, run in CI"
    )
    return {
        "route_tests": route_tests,
        "policy_tests": policy_tests,
        "source_contract_tests": source_contract_tests,
        "other_tests": other_tests,
        "total_tests": sum(counts.values()),
        "by_module": dict(sorted(counts.items())),
        "ci_workflow": ".github/workflows/ci.yml",
        "exact_report_phrase": phrase,
        "scope": (
            "Flask test-client route tests use mocked camera/detector/TTS imports. "
            "Policy tests are deterministic software checks. No empirical result "
            "is represented by these counts."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Compare the committed summary with the current test inventory.",
    )
    args = parser.parse_args()
    summary = compute_summary()
    if args.check:
        if not OUT.exists():
            print(f"Missing {OUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        committed = json.loads(OUT.read_text(encoding="utf-8"))
        if committed != summary:
            print("Test summary is stale; run scripts/report_test_counts.py", file=sys.stderr)
            print(json.dumps({"committed": committed, "computed": summary}, indent=2), file=sys.stderr)
            return 1
        print(summary["exact_report_phrase"])
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(summary["exact_report_phrase"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Source-map and blank-rating checks; no language quality is claimed."""
from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from trinexis_language import (  # noqa: E402
    announcement_rating_template,
    summarize_ratings,
    template_coverage,
)


def mapping_from_app23(name: str) -> dict[str, str]:
    tree = ast.parse((ROOT / "app23.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing mapping {name}")


class LanguageCoverageTests(unittest.TestCase):
    def test_coverage_reports_ten_english_fallback_languages(self):
        codes = mapping_from_app23("language_code_map")
        templates = mapping_from_app23("speech_prefixes")
        coverage = template_coverage(codes, templates)
        self.assertEqual(72, coverage["language_count"])
        self.assertEqual(62, coverage["template_count"])
        self.assertEqual(10, len(coverage["english_fallback_languages"]))
        self.assertIn("Swahili", coverage["english_fallback_languages"])
        self.assertEqual([], coverage["verified_languages"])
        self.assertEqual(72, coverage["unchecked_language_count"])

    def test_announcement_worksheet_has_ten_blank_items_per_language(self):
        rows = announcement_rating_template(["Hindi", "Gujarati"], 10)
        self.assertEqual(20, len(rows))
        self.assertTrue(all(row["correctness_1_to_5"] is None for row in rows))
        self.assertTrue(all(row["naturalness_1_to_5"] is None for row in rows))

    def test_rating_summary_reports_only_checked_languages(self):
        rows = [
            {"language": "Hindi", "correctness_1_to_5": 4, "naturalness_1_to_5": 5},
            {"language": "Gujarati", "correctness_1_to_5": 3, "naturalness_1_to_5": 4},
        ]
        summary = summarize_ratings(rows, ["Hindi"])
        self.assertEqual(1, len(summary))
        self.assertEqual("Hindi", summary[0]["language"])

    def test_invalid_or_out_of_range_ratings_are_not_counted(self):
        rows = [
            {"language": "Hindi", "correctness_1_to_5": "", "naturalness_1_to_5": 5},
            {"language": "Hindi", "correctness_1_to_5": 6, "naturalness_1_to_5": 5},
        ]
        self.assertEqual([], summarize_ratings(rows, ["Hindi"]))


if __name__ == "__main__":
    unittest.main()

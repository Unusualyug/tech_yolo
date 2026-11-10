import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class SourceContractTests(unittest.TestCase):
    def test_agpl_license_present(self):
        text = read("LICENSE")
        self.assertIn("GNU AFFERO GENERAL PUBLIC LICENSE", text)
        self.assertIn("Version 3, 19 November 2007", text)

    def test_readme_documents_license_weights_and_evidence_boundary(self):
        text = read("README.md")
        self.assertIn("AGPL-3.0-only", text)
        self.assertIn("git lfs pull", text)
        self.assertIn("no real webcam sessions", text.lower())
        self.assertIn("empirical result tables", text.lower())
        self.assertIn("not submission-ready", text.lower())
        self.assertIn("the release contains no annotated dataset", text.lower())
        self.assertIn("human-participant evaluation", text.lower())

    def test_runtime_requirements_are_pinned(self):
        lines = [
            line.strip()
            for line in read("requirements.txt").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertTrue(lines)
        self.assertTrue(all("==" in line for line in lines))

    def test_dashboard_uses_confidence_label_not_accuracy(self):
        html = read("templates/index.html")
        self.assertIn("AVG CONFIDENCE", html)
        self.assertNotIn("ACCURACY", html)

    def test_frontend_has_separate_capture_and_inference_displays(self):
        js = read("static/script.js")
        self.assertIn("CAPTURE FPS", js)
        self.assertIn("INFER/s", js)
        self.assertIn("stats.capture_fps", js)
        self.assertIn("stats.inference_fps", js)

    def test_backend_uses_configurable_camera_and_local_default_host(self):
        text = read("app23.py")
        self.assertIn("TRINEXIS_CAMERA_INDEX", text)
        self.assertIn("TRINEXIS_CAMERA_BACKEND", text)
        self.assertIn("TRINEXIS_HOST", text)
        self.assertIn('"127.0.0.1"', text)
        self.assertIsNone(re.search(r"CAMERA_BACKEND\s*=\s*cv2\.CAP_DSHOW", text))
        self.assertNotIn('host="0.0.0.0"', text)

    def test_backend_uses_repaired_policies(self):
        text = read("app23.py")
        self.assertIn("select_speech_objects", text)
        self.assertIn("time_decay_factor", text)
        self.assertIn("relative_distance_index", text)
        self.assertIn("normalize_model_name", text)
        self.assertIn("TRINEXIS_API_TOKEN", text)
        self.assertIn("single_client_check", text)
        self.assertIn("capture_fps", text)
        self.assertIn("inference_fps", text)

    def test_no_metric_cm_label_remains_in_primary_backend(self):
        text = read("app23.py")
        self.assertNotIn("distance_cm", text)
        self.assertNotIn('}cm"', text)
        self.assertNotIn(" cm\"", text)
        self.assertIn("distance index", text)

    def test_citation_and_codemeta_are_valid(self):
        cff = read("CITATION.cff")
        self.assertIn("cff-version: 1.2.0", cff)
        self.assertIn("AGPL-3.0-only", cff)
        meta = json.loads(read("codemeta.json"))
        self.assertEqual(meta["@type"], "SoftwareSourceCode")
        self.assertEqual(meta["version"], "v0.3.0-standalone")

    def test_alert_selection_audit_exists_and_has_zero_updated_drops(self):
        data = json.loads(read("paper/artifacts/alert_selection_audit.json"))
        self.assertEqual(data["updated_drop_count"], 0)
        self.assertEqual(data["legacy_drop_count"] + data["updated_drop_count"] >= 0, True)
        self.assertGreater(data["absolute_drop_rate_reduction"], 0)
        self.assertEqual(data["evidence_type"], "unit_test_artifact")
        self.assertEqual(data["source"], "tests/test_synthetic_regression.py")
        self.assertFalse((ROOT / "experiments" / "alert_selection_audit.py").exists())

    def test_github_actions_runs_tests_on_every_push(self):
        workflow = read(".github/workflows/ci.yml")
        self.assertIn("push:", workflow)
        self.assertIn("pull_request:", workflow)
        self.assertIn("requirements-ci.txt", workflow)
        self.assertIn("unittest discover -s tests -v", workflow)

    def test_language_fallback_and_evidence_boundary_are_documented(self):
        readme = read("README.md")
        self.assertIn("English fallback", readme)
        self.assertIn("Google Translate", readme)
        self.assertIn("unchecked", readme.lower())
        self.assertIn("not submission-ready", readme.lower())
        status = read("FIX_STATUS.md")
        self.assertIn("pending", status.lower())
        self.assertIn("NO DATA", status)
        venue = read("paper/venue_guide_notes.md")
        self.assertIn("arXiv / institutional report", venue)
        self.assertIn("text-to-text generative AI", venue)
        self.assertIn("Yug G. Lakhani (1)", venue)
        self.assertIn("nearest_select_speech_objects", read("trinexis_core.py"))
        self.assertIn("nearest_first", read("experiments/alert_replay.py"))
        self.assertTrue((ROOT / "experiments/LIVE_SMOKE_TEST.md").is_file())
        self.assertTrue((ROOT / "experiments/SPOKEN_IO_EXAMPLE.template.md").is_file())
        self.assertTrue((ROOT / "experiments/USER_STUDY_PROTOCOL.md").is_file())
        receipt = read("experiments/ethics_inquiry_receipt.md")
        self.assertIn("sent inquiry only", receipt)
        self.assertIn("1a1c4db01f9cbe1f", receipt)
        self.assertIn("No reply, approval, or waiver is claimed", read("experiments/USER_STUDY_PROTOCOL.md"))
        self.assertTrue((ROOT / "scripts/live_smoke_test.py").is_file())
        self.assertTrue((ROOT / "scripts/final_release_checklist.py").is_file())
        manuscript = read("paper/updated_manuscript_content.py")
        self.assertIn("TABLE I-B. PUBLISHED CONTEXT (NOT TRINEXIS MEASUREMENTS)", manuscript)
        self.assertIn("Published numeric context (not TRINEXIS results)", manuscript)
        self.assertIn("not entered into Table V", manuscript)
        built = read("paper/tech_yolo_updated_research_paper.md")
        self.assertIn("TABLE I-B. PUBLISHED CONTEXT (NOT TRINEXIS MEASUREMENTS)", built)
        self.assertIn("not entered into Table V", built)

    def test_zenodo_doi_remains_pending(self):
        zenodo = json.loads(read("zenodo.json"))
        self.assertIn("DOI pending", zenodo["notes"])
        cff = read("CITATION.cff")
        self.assertNotIn("\ndoi:", cff)
        self.assertIn("Zenodo DOI pending", cff)


if __name__ == "__main__":
    unittest.main()

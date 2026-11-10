# Standalone TRINEXIS technical report

The main deliverable is `tech_yolo_updated_research_paper.pdf`. Editable
Markdown and DOCX versions use the same basename. Figures are provided as PNG,
SVG, and standalone vector PDF.

Current working-tree title:

> *TRINEXIS: An Alert-Aware Narration Policy and a Protocol for Measuring Its
> Effect on Alert Delivery*

## Purpose and evidence boundary

This is a **standalone technical report** with empirical protocols and blank
`NO DATA` results. It is framed around an alert-aware narration policy and the
research question *Does alert-first narration make users notice a designated
object faster or more often than confidence-first narration?* The author
selected arXiv/institutional-report formatting; current official submission,
moderation, metadata, and content-type pages were read and recorded in
`venue_guide_notes.md`, and arXiv has no mandatory venue template. The report
is **not submission-ready**: empirical cells remain `NO DATA`, no real-app
screenshot/spoken example exists, no final release or DOI exists, and the
author has not verified final numbers.

It documents the maintained Flask/YOLO-World webcam system, the policy,
real-log instrumentation, 23-route Flask test-client tests, CI, language
fallback, and software checks. It does **not** claim empirical detection
quality, latency, distance calibration, multilingual comprehension, assistive
effectiveness, or user-study results. The 68.1% synthetic figure is generated
only by `tests/test_synthetic_regression.py` as a failable unit-test artifact;
it is not an experiment result.

## Files

| File | Purpose |
|---|---|
| `updated_manuscript_content.py` | Structured manuscript source: title, abstract, Sections I–VII, tables, figures, references, declarations, appendices. |
| `build_updated_manuscript.py` | Renders PDF, DOCX, and Markdown. |
| `make_updated_figures.py` | Produces enlarged PNG/SVG/PDF figures. |
| `audit_updated_repository.py` | Writes a machine-readable file census, test summary, and checksums for the unreleased working tree. |
| `artifacts/alert_selection_audit.json` | `tests/` unit-test artifact for the seeded synthetic alert-ordering regression. |
| `artifacts/test_summary.json` | Route/policy/source-contract test counts and exact CI report phrase. |
| `artifacts/updated_repository_audit.json` | Repository/test/artifact audit. |
| `artifacts/fig1_system_architecture_updated.{png,svg,pdf}` | System architecture. |
| `artifacts/fig2_implementation_verification.{png,svg,pdf}` | Software-verification workflow. |
| `../experiments/README.md`, `../experiments/RESULTS_TEMPLATE.md` | Empirical protocols and blank `NO DATA` result cells. |
| `../experiments/LIVE_SMOKE_TEST.md`, `../experiments/SPOKEN_IO_EXAMPLE.template.md` | Hand-run real-app checklist and blank real detections-in / spoken-sentence-out evidence template. |
| `../experiments/USER_STUDY_PROTOCOL.md`, `../experiments/ethics_inquiry_receipt.md` | Three-policy within-subject protocol, early sent ethics inquiry, and no-approval boundary. |
| `../FIX_STATUS.md` | Six-item critique, publication-blocker triage, implemented fixes, and how to finish. |
| `../weights/download_weights.py` | Git LFS weights fetch and SHA-256 verification. |
| `../weights/weights_checksums.sha256` | Expected SHA-256 object identifiers. |
| `../zenodo.json`, `../ZENODO.md` | Prepared DOI metadata; no DOI minted. |
| `reference_verification.md` | Per-reference DOI/publisher verification log; all 24 rows ticked after recheck. |
| `venue_guide_notes.md` | Current arXiv/institutional-report author-guide notes, metadata fields, AI-tool policy, and declarations. |

## Build from the repository root

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -v
python3 scripts/report_test_counts.py
python3 experiments/alert_replay.py --self-check
python3 experiments/multi_session_replay.py --self-check
python3 experiments/user_study.py --self-check
python3 -m pip install -r paper/requirements-paper.txt
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
python3 paper/audit_updated_repository.py
python3 scripts/check_arxiv_metadata.py --check
python3 scripts/live_smoke_test.py --self-check
python3 scripts/final_release_checklist.py --self-check
python3 scripts/verify_no_fabricated_results.py
```

The builder requires ReportLab, python-docx, Pillow, pypdf, and PyMuPDF; the
pinned versions are in `requirements-paper.txt`. Run
`scripts/report_test_counts.py` before building so the paper's test table uses
the current unittest inventory. The CI workflow runs the same route/policy
tests without installing detector/camera/TTS packages.

## Submission notes

1. Run C first with 5–10 real sessions and frozen alert manifest, then A, B,
   and optionally D/E in the order in `FIX_STATUS.md`. Run E only after
   consent and institutional ethics approval.
2. Add the real dashboard screenshot and one spoken input→output example from
   the hand-run smoke test.
3. The author confirmed no external funding, no competing interests, and
   CRediT roles actually performed; add methodology, investigation, and formal
   analysis only after those experiments happen.
4. The AI-tool disclosure was checked against the current arXiv text-to-text
   generative-AI policy. Recheck only if the venue changes.
5. The current arXiv author pages were read; no official template is required.
   Keep the generic single-column layout and numeric citations.
6. After results, rewrite the title/abstract, Section V/VI, tables, and
   discussion; have the author personally verify every number.
7. Freeze the final `v1.0.0` paper/code, publish the GitHub release, connect
   Zenodo, and mint the DOI with explicit author approval. A DOI is permanent
   for the exact version, so do not mint it from `v0.3.0-standalone` or an
   unreleased working tree. `scripts/final_release_checklist.py --check` gates
   the order.
8. Insert the DOI into `CITATION.cff`, `README.md`, Appendix A, and the paper's
   Data and Code Availability section; rebuild the manuscript and audit.

Until the steps above are complete, the manuscript is not submission-ready.

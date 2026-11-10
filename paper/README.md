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
object faster or more often than confidence-first narration?* The report is
**not submission-ready**: no official venue template, citation style, or
current Guide for Authors was supplied/read.

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
| `../FIX_STATUS.md` | Six-item critique, implemented fixes, and how to finish. |
| `../weights/download_weights.py` | Git LFS weights fetch and SHA-256 verification. |
| `../weights/weights_checksums.sha256` | Expected SHA-256 object identifiers. |
| `../zenodo.json`, `../ZENODO.md` | Prepared DOI metadata; no DOI minted. |
| `reference_verification.md` | Per-reference DOI/publisher verification log. |

## Build from the repository root

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -v
python3 scripts/report_test_counts.py
python3 -m pip install -r paper/requirements-paper.txt
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
python3 paper/audit_updated_repository.py
python3 scripts/verify_no_fabricated_results.py
```

The builder requires ReportLab, python-docx, Pillow, pypdf, and PyMuPDF; the
pinned versions are in `requirements-paper.txt`. Run
`scripts/report_test_counts.py` before building so the paper's test table uses
the current unittest inventory. The CI workflow runs the same route/policy
tests without installing detector/camera/TTS packages.

## Submission notes

1. Complete Experiments A–D on real hardware/data/raters; run optional user
   noticing work only after consent and institutional ethics approval.
2. Add a dashboard screenshot and one spoken input→output example.
3. Verify author declarations, especially funding and competing interests;
   match CRediT to work actually done.
4. Recheck the AI-tool disclosure against the chosen venue's policy.
5. Read the venue's current Guide for Authors and apply its official template
   and citation style.
6. Have the author personally verify every number and declaration.
7. Freeze the final paper/code, create the **final** GitHub release, then mint
   the Zenodo DOI with author authorization. A DOI is permanent for the exact
   version, so do not mint it from `v0.3.0-standalone` or this working tree.
8. Insert that DOI into `CITATION.cff`, `README.md`, and the paper's Data and
   Code Availability section; rebuild the manuscript and audit.

The generic single-column layout and numeric citation style are fallbacks
because no target venue or official template was supplied. Until the steps
above are complete, the manuscript is not journal- or
conference-submission-ready.

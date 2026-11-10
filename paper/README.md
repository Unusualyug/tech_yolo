# Standalone TRINEXIS technical report

The main deliverable is `tech_yolo_updated_research_paper.pdf`. Editable
Markdown and DOCX versions are provided with the same basename. Figures are
provided as PNG, SVG, and standalone vector PDF.

## Purpose and evidence boundary

This is a **standalone technical report** prepared for arXiv or a student
technical-report archive. It describes TRINEXIS directly, not as a revision or
review response. It documents the maintained Flask/YOLO-World webcam system,
its alert-aware speech policy, configuration/security changes, repository
artifacts, figures, and software checks. It does **not** claim empirical
detection quality, latency, distance calibration, multilingual comprehension,
assistive effectiveness, or user-study results.

The 68.1% alert-selection figure is a deterministic synthetic regression
check derived from six records, one alert object, and a two-object shortlist;
under uniform rank, the alert falls outside the top two with probability 4/6
(66.7%). The paper explains that the check validates an ordering invariant,
not real-world detection behavior.

## Files

| File | Purpose |
|---|---|
| `updated_manuscript_content.py` | Structured manuscript source with title, abstract, sections, tables, figures, references, and appendices. |
| `build_updated_manuscript.py` | Renders PDF, DOCX, and Markdown. |
| `make_updated_figures.py` | Produces enlarged PNG/SVG/PDF figures. |
| `audit_updated_repository.py` | Writes a machine-readable file census, test summary, and checksums. |
| `artifacts/alert_selection_audit.json` | Seeded synthetic alert-ordering regression result. |
| `artifacts/updated_repository_audit.json` | Repository/test/artifact audit. |
| `artifacts/fig1_system_architecture_updated.{png,svg,pdf}` | System architecture. |
| `artifacts/fig2_implementation_verification.{png,svg,pdf}` | Software-verification workflow. |
| `../weights/download_weights.py` | Git LFS weights fetch and SHA-256 verification. |
| `../weights/weights_checksums.sha256` | Expected SHA-256 object identifiers. |
| `../zenodo.json`, `../ZENODO.md` | Prepared DOI metadata; no DOI minted. |
| `reference_verification.md` | Per-reference DOI/publisher verification log. |

## Build

```bash
python3 -m pip install -r requirements-paper.txt
python3 make_updated_figures.py
python3 build_updated_manuscript.py
python3 audit_updated_repository.py
```

The builder requires ReportLab, python-docx, Pillow, pypdf, and PyMuPDF; the
pinned versions are in `requirements-paper.txt`.

## Submission notes

1. Verify the author declarations, especially funding and competing interests.
2. Check the AI-tool disclosure against the chosen venue's policy.
3. Read the venue's current Guide for Authors and apply its official template
   and citation style before submission.
4. Mint a Zenodo DOI by author authorization, then replace the GitHub release
   URL with the DOI in the manuscript, `CITATION.cff`, `codemeta.json`, and
   `zenodo.json`. `reference_verification.md` records the reference checks.
5. Run the empirical detection, latency, and user-study protocols only after
   real hardware, labeled data, and ethics approval are available.

The generic single-column layout and numeric citation style are fallbacks
because no target venue or official template was supplied. The current
manuscript is not journal- or conference-submission-ready.

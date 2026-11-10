# Updated TRINEXIS manuscript

The repository-fixed author manuscript is:

- `tech_yolo_updated_research_paper.pdf` — **main deliverable**
- `tech_yolo_updated_research_paper.docx` — editable version
- `tech_yolo_updated_research_paper.md` — plain-text version

The earlier `tech_yolo_final_research_paper.*` files are retained only as the
superseded pre-review author version. Do not submit or email them as the
updated paper.

## What this version fixes

- Removes the page header `TRINEXIS final research paper | tech_yolo` and all
  pre-submission placeholder/checklist language.
- Reframes the paper as a software-focused technical report with one clear
  contribution: alert-aware, language-configured narration in an
  interval-throttled open-vocabulary webcam pipeline.
- Replaces “multilingual” with “language-configured” because the translations
  were not evaluated.
- Corrects the Redmon et al. dataset description, cites the published ECCV
  2024 Grounding DINO version, expands related work, and fixes Table VIII-style
  unlike-resource comparisons.
- Removes “not applicable” training, baseline, ablation, hyperparameter, and
  statistical sections; replaces them with a short scope statement and a
  future-evidence table.
- Moves the source audit into a short implementation-verification appendix and
  cites GitHub release `v0.2.0-updated` instead of a bare commit.
- Corrects CRediT roles and adds an AI-tool disclosure.
- Provides enlarged vector SVG/PDF figures in addition to PNG figures.
- Reports one genuine deterministic software result: a seeded synthetic
  before/after regression audit of alert selection.

## Evidence boundary

No labeled detection dataset, hardware timing campaign, known-distance
calibration, translated-template rating, or consented user study was
conducted. The paper therefore claims **no** mAP, precision, recall, latency,
distance MAE, robustness, multilingual comprehension, assistive
effectiveness, or user-study result. The alert-selection result is a
deterministic software regression result, not a detection or human-participant
finding.

## Author metadata

Yug G. Lakhani — Department of Computer Engineering, Gyanmanjari Innovative
University, Bhavnagar, Gujarat, India — `yglakhani@gmiu.edu.in` — ORCID
`0009-0004-2930-4953`.

The funding and competing-interest statements use neutral wording because the
author did not supply verified declarations. Confirm them, and any required
AI-disclosure policy, before submitting to a target venue. No target journal
or conference was supplied; the current numeric citation style and generic
single-column layout are fallbacks. Read the official current Guide for Authors
and apply the official template before submission.

## Rebuild

```bash
python3 -m pip install -r paper/requirements-paper.txt
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
python3 experiments/alert_selection_audit.py
python3 -m unittest discover -s tests -v
python3 paper/audit_updated_repository.py
```

`build_updated_manuscript.py` reads `updated_manuscript_content.py`, which in
turn reads `artifacts/alert_selection_audit.json`. The figure builder writes
PNG, SVG, and vector-PDF versions of both figures into `artifacts/`.

## Artifacts

| Path | Purpose |
|---|---|
| `artifacts/alert_selection_audit.json` | Seeded synthetic before/after alert-selection result. |
| `artifacts/updated_repository_audit.json` | Release, test, file, and checksum summary. |
| `artifacts/fig1_system_architecture_updated.{png,svg,pdf}` | Updated system figure. |
| `artifacts/fig2_implementation_verification.{png,svg,pdf}` | Updated verification-workflow figure. |
| `artifacts/repository_audit.json` | Frozen source-census baseline from the original commit. |
| `delivery/tech_yolo_final_paper.zip` | Historical supporting archive; not the updated-paper email attachment. |

A Zenodo DOI is pending author authorization. Until then, cite the GitHub
release URL in `CITATION.cff` and the manuscript.

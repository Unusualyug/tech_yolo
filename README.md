# TRINEXIS

**TRINEXIS** is a Flask-based webcam application that combines an
interval-throttled YOLO-World open-vocabulary detector, a browser dashboard,
language-configured speech output, detection logs, a relative distance index,
a time-decayed heatmap, and session telemetry.

> **Status:** repository-fixed author manuscript / technical report. This
> release is suitable for an arXiv preprint, a student technical report, or a
> software-focused paper draft. It is **not** an empirical applied-vision paper:
> no mAP, latency, distance-calibration, robustness, or user-study result is
> claimed. See `paper/tech_yolo_updated_research_paper.pdf`.

## Author

Yug G. Lakhani  
Department of Computer Engineering, Gyanmanjari Innovative University,
Bhavnagar, Gujarat, India  
`yglakhani@gmiu.edu.in` · ORCID `0009-0004-2930-4953`

## What changed in `v0.2.0-updated`

- Added `LICENSE` (GNU **AGPL-3.0-only**), this README, pinned
  `requirements.txt`, `CITATION.cff`, `codemeta.json`, `.env.example`, and
  `THIRD_PARTY_LICENSES.md`.
- Added dependency-free policy helpers in `trinexis_core.py` and
  standard-library tests in `tests/`.
- Repaired alert-aware speech selection so alert objects are ranked **before**
  the spoken shortlist is truncated. A seeded synthetic regression audit in
  `experiments/alert_selection_audit.py` reports the before/after drop rate.
- Replaced the misleading dashboard label `ACCURACY` with `AVG CONFIDENCE`.
- Added separate capture-frame and inference-rate counters.
- Replaced per-frame heatmap decay with time-based exponential decay.
- Replaced the centimetre-labelled distance heuristic with a clearly
  non-metric, relative distance index.
- Made camera index/backend, host, port, optional API token, single-client
  mode, and heatmap half-life configurable.
- Restricted `/set_model` to a checked-in model allowlist.
- Added vector SVG/PDF figures and a rewritten software-focused manuscript.
- Removed the pre-submission note and checklist from the paper, corrected the
  YOLO/Grounding DINO citations, expanded related work, and moved the static
  audit into a short implementation-verification appendix.

## Evidence boundary

The original repository contained no annotated dataset, benchmark log,
training script, pinned dependency manifest, human-participant evaluation, or
calibrated distance measurements. The updated release adds reproducible
software tests and a deterministic before/after policy result, but it still
contains **no empirical detection-quality, latency, distance-MAE, translated
template-rating, or assistive-effectiveness result**. Such results require
new experiments and ethics review before publication.

## Installation

Python 3.11 or newer is recommended. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

The five `*.pt` files are Git Large File Storage pointer files, not hydrated
weights. Install Git LFS and fetch the weights before running inference:

```bash
git lfs install
git lfs pull
```

No model tensor is committed as a raw binary in this checkout. Verify the
upstream license and usage terms of each model before redistribution.

## Configuration

Export variables from your shell (`.env` is not auto-loaded). See
`.env.example`.

| Variable | Default | Purpose |
|---|---|---|
| `TRINEXIS_CAMERA_INDEX` | `1` | OpenCV camera index. |
| `TRINEXIS_CAMERA_BACKEND` | `AUTO` | `AUTO`, `DSHOW`, `MSMF`, or `V4L2`. |
| `TRINEXIS_CAMERA_WIDTH` / `TRINEXIS_CAMERA_HEIGHT` | `1280` / `720` | Requested capture resolution. |
| `TRINEXIS_HOST` | `127.0.0.1` | Bind address; use `0.0.0.0` only behind a trusted reverse proxy. |
| `TRINEXIS_PORT` | `5000` | Flask port. |
| `TRINEXIS_API_TOKEN` | empty | When set, mutating control endpoints require `X-API-Token` or `Authorization: Bearer`. |
| `TRINEXIS_SINGLE_CLIENT` | `1` | Enforce one controlling browser session to avoid shared global-state races. |
| `TRINEXIS_CLIENT_TIMEOUT_S` | `60` | Stale single-client lock timeout. |
| `TRINEXIS_SECRET_KEY` | random | Flask session signing key. Set a stable random value in deployment. |
| `TRINEXIS_HEATMAP_HALF_LIFE_S` | `60` | Heatmap exponential-decay half-life. |

## Run

```bash
python3 app23.py
```

Open `http://127.0.0.1:5000`. `app23.py` is the maintained backend because it
implements every frontend endpoint, including `/set_alerts`. `app.py` is a
frozen legacy variant and is not the deployment target.

Control endpoints are optionally protected with `TRINEXIS_API_TOKEN`. The
browser dashboard does not send a token by default; if you enable one, place
the application behind a reverse proxy or extend the frontend to include the
header. Single-client mode prevents a second browser from mutating the shared
server state while the first session is active.

## Tests and reproducibility

```bash
python3 experiments/alert_selection_audit.py
python3 -m unittest discover -s tests -v
```

The first command writes
`paper/artifacts/alert_selection_audit.json`. The unit tests use only the
Python standard library and do not import Flask, OpenCV, Ultralytics, gTTS,
or model weights.

To rebuild the updated manuscript and its vector figures:

```bash
python3 -m pip install -r paper/requirements-paper.txt
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
```

The updated paper is written to
`paper/tech_yolo_updated_research_paper.{pdf,docx,md}`. The original
`paper/tech_yolo_final_research_paper.*` files are retained as the superseded
pre-review author version.

## Repository layout

| Path | Purpose |
|---|---|
| `app23.py` | Maintained Flask backend. |
| `app.py` | Frozen legacy backend variant. |
| `camera_test.py` | Optional camera probe with configurable backend. |
| `trinexis_core.py` | Dependency-free policy helpers. |
| `templates/`, `static/` | Browser dashboard. |
| `utils/coco.txt` | Auxiliary COCO class-name list; not a dataset. |
| `weights/`, `*.pt` | Git LFS pointers for model weights. |
| `tests/` | Standard-library unit and source-contract tests. |
| `experiments/` | Seeded synthetic alert-selection audit. |
| `paper/` | Updated manuscript, figures, builder, and audit artifacts. |

## License and dependency licenses

This repository is licensed under **GNU AGPL-3.0-only**; see `LICENSE`.
Ultralytics YOLO is AGPL-3.0, so this compatible license was selected for the
derivative work. Principal dependency licenses are summarized in
`THIRD_PARTY_LICENSES.md` and should be verified against the exact installed
distributions before redistribution.

## Citation

Use `CITATION.cff` and `codemeta.json`. The release tag is
`v0.2.0-updated`. A Zenodo DOI is pending author authorization; until then,
cite the GitHub release URL rather than a bare commit hash.

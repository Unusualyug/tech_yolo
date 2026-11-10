# TRINEXIS

**TRINEXIS** is an alert-aware, interval-throttled open-vocabulary webcam
system with language-configured speech output, a browser dashboard, detection
logs, a relative distance index, a time-decayed heatmap, and session telemetry.

> **Status:** standalone technical report. The manuscript is
> `paper/tech_yolo_updated_research_paper.pdf`. It is suitable for arXiv or a
> student technical report. No empirical detection-quality, latency,
> distance-error, translation-rating, robustness, or user-study result is
> claimed.

## Author

Yug G. Lakhani  
Department of Computer Engineering, Gyanmanjari Innovative University,
Bhavnagar, Gujarat, India  
`yglakhani@gmiu.edu.in` · ORCID `0009-0004-2930-4953`

## v0.3.0-standalone

- Manuscript reframed as a standalone technical report with no review-response
  language, no JOSS/SoftwareX venue discussion, and no repeated disclaimer lists.
- New title: *TRINEXIS: An Alert-Aware, Interval-Throttled Open-Vocabulary
  Webcam System with Language-Configured Speech*.
- Shortened abstract; one Scope and Limitations paragraph; short future-work list.
- Alert-selection regression check now states the 4/6 uniform-rank probability
  setup and does not present the synthetic 68.1% figure as empirical evidence.
- All 24 references opened and checked against DOI/publisher/official pages; see `paper/reference_verification.md`.
- Ultralytics' LICENSE file cited directly.
- `weights/download_weights.py` and `weights/weights_checksums.sha256` added.
- `zenodo.json` and `ZENODO.md` added; the Zenodo DOI is still pending author
  authorization.
- Added `LICENSE` (GNU AGPL-3.0-only), pinned `requirements.txt`, `CITATION.cff`,
  `codemeta.json`, `.env.example`, and `THIRD_PARTY_LICENSES.md`.

## Evidence boundary

The release contains no annotated dataset, benchmark log, hardware timing
campaign, known-distance calibration, translated-template rating, or
human-participant evaluation. The synthetic alert-selection result is a
deterministic software regression check, not a detection or user finding.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 weights/download_weights.py --fetch --verify
```

`--fetch` runs `git lfs install` and `git lfs pull`. Use `--verify` to check
already-materialized weights against `weights/weights_checksums.sha256`.
The five `*.pt` files in this checkout are Git LFS pointer files, not hydrated
tensors. Verify upstream model terms before redistribution.

## Configuration

Export variables from your shell (`.env` is not auto-loaded). See
`.env.example`.

| Variable | Default | Purpose |
|---|---|---|
| `TRINEXIS_CAMERA_INDEX` | `1` | OpenCV camera index. |
| `TRINEXIS_CAMERA_BACKEND` | `AUTO` | `AUTO`, `DSHOW`, `MSMF`, or `V4L2`. |
| `TRINEXIS_HOST` | `127.0.0.1` | Bind address; use `0.0.0.0` only behind a trusted reverse proxy. |
| `TRINEXIS_PORT` | `5000` | Flask port. |
| `TRINEXIS_API_TOKEN` | empty | When set, mutating control endpoints require `X-API-Token` or `Authorization: Bearer`. |
| `TRINEXIS_SINGLE_CLIENT` | `1` | Enforce one controlling browser session. |
| `TRINEXIS_HEATMAP_HALF_LIFE_S` | `60` | Adjustable heatmap exponential-decay half-life. |

## Run

```bash
python3 app23.py
```

Open `http://127.0.0.1:5000`. `app23.py` is the maintained backend. `app.py`
is a frozen legacy variant.

## Tests and reproducibility

```bash
python3 experiments/alert_selection_audit.py
python3 -m unittest discover -s tests -v
python3 paper/audit_updated_repository.py
```

To rebuild the manuscript and vector figures:

```bash
python3 -m pip install -r paper/requirements-paper.txt
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
```

## Repository layout

| Path | Purpose |
|---|---|
| `app23.py` | Maintained Flask backend. |
| `trinexis_core.py` | Dependency-free policy helpers. |
| `weights/download_weights.py` | Git LFS fetch and SHA-256 verification. |
| `weights/weights_checksums.sha256` | Expected SHA-256 object identifiers. |
| `tests/`, `experiments/` | Standard-library tests and synthetic regression audit. |
| `paper/` | Standalone manuscript, figures, builder, and audit artifacts. |
| `zenodo.json`, `ZENODO.md` | Prepared DOI metadata and minting instructions. |
| `paper/reference_verification.md` | Per-reference DOI/publisher verification log. |

## License

This repository is **AGPL-3.0-only**; see `LICENSE`. Ultralytics YOLO is
AGPL-3.0 under its official LICENSE file
(`https://github.com/ultralytics/ultralytics/blob/main/LICENSE`), so this
compatible license was selected. Principal dependency licenses are in
`THIRD_PARTY_LICENSES.md`.

## Citation

Use `CITATION.cff` and `codemeta.json`. The release tag is
`v0.3.0-standalone`. A Zenodo DOI is pending author authorization; until then,
cite the GitHub release URL rather than a bare commit hash.

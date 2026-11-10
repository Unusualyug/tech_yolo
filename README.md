# TRINEXIS

**TRINEXIS** is an alert-aware, interval-throttled open-vocabulary webcam
system with language-configured speech output, a browser dashboard, detection
logs, a relative distance index, a time-decayed heatmap, and session telemetry.

> **Status:** standalone technical report with empirical protocols and blank
> `NO DATA` results. The manuscript is
> `paper/tech_yolo_updated_research_paper.pdf`. It is **not submission-ready**:
> no official venue template, current Guide for Authors, or citation style was
> supplied/read. No empirical detection-quality, latency, distance-error,
> translation-rating, robustness, or user-study result is claimed.

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

## Unreleased fix revision (this branch)

- Reframed the paper around an alert-aware narration policy and the question:
  *Does alert-first narration make users notice a designated object faster or
  more often than confidence-first narration?*
- Added Experiments A–D protocols, optional runtime instrumentation, blank
  `NO DATA` result templates, and manifest templates under `experiments/`.
- Added real Flask test-client tests for all 23 routes with mocked
  camera/detector/TTS imports, plus GitHub Actions CI on every push and pull
  request. `paper/artifacts/test_summary.json` reports
  `43 route tests plus 37 policy tests, run in CI`.
- Added English fallback documentation to `/get_languages` and the UI. The 72
  language codes are **unchecked**; the ten languages without a top-level
  template use the English fallback. gTTS uses Google Translate's speech
  service; listen to sample audio and a few languages before any claim.
- See `FIX_STATUS.md` for the six-item critique, what was implemented, and how
  to finish each item. No new release/tag or Zenodo DOI was created for these
  unreleased changes.

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
| `TRINEXIS_API_TOKEN` | empty | When set, mutating control endpoints require `X-API-Token` or `Authorization: Bearer`; missing/invalid returns 401. |
| `TRINEXIS_READ_ONLY` | `0` | When `1`, mutating control endpoints return 403 even with a valid token; GET remains readable. |
| `TRINEXIS_SINGLE_CLIENT` | `1` | Enforce one controlling browser session. |
| `TRINEXIS_HEATMAP_HALF_LIFE_S` | `60` | Adjustable heatmap exponential-decay half-life. |
| `TRINEXIS_LATENCY_LOG` | empty | Optional JSONL timing log; no logging when empty. |
| `TRINEXIS_EVENT_LOG` | empty | Optional JSONL speech enqueue/playback event log. |
| `TRINEXIS_EXPERIMENT_SETTING` | `default` | Setting label written into real logs. |
| `TRINEXIS_HARDWARE_MANIFEST` | empty | Declared hardware/software manifest path or label. |
| `TRINEXIS_ALERT_MANIFEST` | empty | Predeclared alert-object manifest; freezes `/set_alerts`. |

## Run

```bash
python3 app23.py
```

Open `http://127.0.0.1:5000`. `app23.py` is the maintained backend. `app.py`
is a frozen legacy variant.

## Tests and reproducibility

CI installs only `requirements-ci.txt` (Flask); native detector/camera/TTS
imports are mocked for route tests. The workflow runs on every push and pull
request.

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest tests.test_synthetic_regression -v
python3 -m unittest discover -s tests -v
python3 scripts/report_test_counts.py
python3 experiments/latency_benchmark.py --self-check
python3 experiments/detection_eval.py --self-check
python3 experiments/vocab_confidence_grid.py --self-check
python3 experiments/alert_replay.py --self-check
python3 experiments/language_eval.py --self-check
python3 scripts/verify_no_fabricated_results.py
python3 paper/audit_updated_repository.py
```

Empirical protocols, commands, and blank results are in `experiments/README.md`
and `experiments/RESULTS_TEMPLATE.md`. Generated logs/result files are
gitignored. To rebuild the manuscript and vector figures:

```bash
python3 -m pip install -r paper/requirements-paper.txt
python3 scripts/report_test_counts.py
python3 paper/make_updated_figures.py
python3 paper/build_updated_manuscript.py
```

## Repository layout

| Path | Purpose |
|---|---|
| `app23.py` | Maintained Flask backend with optional real-log instrumentation. |
| `trinexis_core.py` | Dependency-free control/narration policy helpers. |
| `trinexis_telemetry.py`, `trinexis_language.py` | Dependency-free latency/event and language-support helpers. |
| `weights/download_weights.py` | Git LFS fetch and SHA-256 verification. |
| `weights/weights_checksums.sha256` | Expected SHA-256 object identifiers. |
| `tests/` | Unit, mutation-sensitive, source-contract, and real Flask route tests. |
| `experiments/` | Empirical protocols, runnable harnesses, and blank `NO DATA` templates. |
| `.github/workflows/ci.yml` | Tests and evidence-boundary checks on every push. |
| `FIX_STATUS.md` | Six-item critique, implemented fixes, and how to finish. |
| `paper/` | Standalone manuscript, figures, builder, and audit artifacts. |
| `zenodo.json`, `ZENODO.md` | Prepared DOI metadata and final-release minting instructions. |
| `paper/reference_verification.md` | Per-reference DOI/publisher verification log. |

## License

This repository is **AGPL-3.0-only**; see `LICENSE`. Ultralytics YOLO is
AGPL-3.0 under its official LICENSE file
(`https://github.com/ultralytics/ultralytics/blob/main/LICENSE`), so this
compatible license was selected. Principal dependency licenses are in
`THIRD_PARTY_LICENSES.md`.

## Citation

Use `CITATION.cff` and `codemeta.json`. The prior immutable release tag is
`v0.3.0-standalone`; the fix revision on this branch is unreleased. A Zenodo
DOI is pending author authorization and the **final** GitHub/Zenodo release.
Do not mint it from the older release or this working tree because a DOI is
permanent for the exact archived version. After minting, insert the DOI into
`CITATION.cff`, this README's Citation section, and the paper's Data and Code
Availability section, then rebuild the manuscript. Until then, cite the GitHub
release URL for the prior release only, not a bare commit hash.

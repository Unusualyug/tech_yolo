# Changelog

## v0.2.0-updated — 2026-11-10

- Added AGPL-3.0 `LICENSE`, root `README.md`, pinned `requirements.txt`,
  `CITATION.cff`, `codemeta.json`, `.env.example`, and a third-party license notice.
- Added dependency-free `trinexis_core.py` policy helpers and standard-library
  unit/source-contract tests.
- Repaired alert selection so alert-aware ranking happens before shortlist truncation.
- Added a seeded synthetic before/after audit of the alert-selection defect.
- Replaced the misleading `ACCURACY` dashboard label with `AVG CONFIDENCE`.
- Separated capture-frame and inference-rate counters.
- Replaced frame-rate-dependent heatmap decay with time-based exponential decay.
- Replaced the centimetre-labelled distance heuristic with a non-metric distance index.
- Made camera index/backend, host, port, API token, single-client mode, and heatmap
  half-life configurable through environment variables.
- Restricted `/set_model` to a checked-in model allowlist.
- Added vector SVG/PDF figures and a software-focused updated manuscript.
- Kept an explicit evidence boundary: no detection, latency, distance-calibration,
  or human-subject results are claimed.

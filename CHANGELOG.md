# Changelog

## Unreleased — protocol-only paper revision on `arena/69777d37-tech-yolo`

- Reframed the deliverable as a complete protocol and software-verification
  report: *TRINEXIS: An Alert-Aware Narration Policy, Preregistered Measurement
  Protocol, and Software Verification*. No external results were borrowed or
  presented as TRINEXIS measurements.
- Replaced the blank-results framing with a preregistered measurement plan,
  collapsed repeated draft/status wording into one limitations paragraph, and
  removed the mutable branch name, working-tree prose, and future-DOI
  insertion instructions from the manuscript.
- Fixed Figure 2: the misleading "Tagged release" box is now an "Untagged
  snapshot" box with an explicit no-final-tag/no-DOI note.
- Kept all empirical values unfilled, no fabricated screenshot or spoken
  example, no `v1.0.0` tag, no release, and no Zenodo DOI.

## Unreleased — evidence-protocol and test revision on `arena/69777d37-tech-yolo`

- Reframed the manuscript around an alert-aware narration policy, a testable
  alert-delivery research question, experiment protocols, and blank `NO DATA`
  results; retitled it *TRINEXIS: An Alert-Aware Narration Policy and a
  Protocol for Measuring Its Effect on Alert Delivery*.
- Added optional real-log instrumentation for capture, inference, TTS
  synthesis, playback, rendering, speech enqueue, and playback events.
- Added Experiments A–D protocols, runnable harnesses, hardware/dataset/
  vocabulary/alert manifest templates, and `experiments/RESULTS_TEMPLATE.md`.
- Moved the seeded 1,000-case 68.1% synthetic check into
  `tests/test_synthetic_regression.py`; removed the old `experiments/` generator.
- Added real Flask test-client tests for all 23 routes, input validation,
  401/403/409 control behavior, mocked detector/camera/TTS imports, and
  `.github/workflows/ci.yml` on every push and pull request.
- Added language-fallback metadata/UI: ten missing templates are disclosed,
  the 72 language codes remain unchecked, and gTTS's Google Translate speech
  service plus sample-listening instructions are documented.
- Added `FIX_STATUS.md`, `scripts/report_test_counts.py`, and
  `scripts/verify_no_fabricated_results.py`.
- Clarified that the final GitHub/Zenodo release must come last and that the
  DOI must then be inserted into `CITATION.cff`, `README.md`, and the paper's
  Data and Code Availability section. No DOI, tag, or release was created.
- Added a nearest-object-first comparison policy, 5–10 real-session replay
  aggregator, guarded three-policy within-subject user-study worksheet, blank
  spoken-I/O template, hand-run live smoke-test description, arXiv metadata
  checker, and final-release gate. These are guardrails, not results.
- Sent the early ethics-route inquiry on 2026-11-10 to the official
  `hod@gmiu.edu.in` address; see `experiments/ethics_inquiry_receipt.md` and
  Gmail message `1a1c4db01f9cbe1f`. No reply, approval, or waiver is claimed.
- Reopened all 24 official DOI/publisher/project pages, ticked every row in
  `paper/reference_verification.md`, and read current arXiv submission,
  moderation, metadata, and content-type pages; see `paper/venue_guide_notes.md`.
  The author selected arXiv/institutional report, which has no mandatory
  official template, and confirmed no external funding, no competing interests,
  and the CRediT roles actually performed. The arXiv-aware AI-tool disclosure
  was written; methodology/investigation/formal analysis remain pending.
- Kept the manuscript **not submission-ready**: no real webcam sessions,
  empirical tables, dashboard screenshot, spoken input→output example,
  consented user study, `v1.0.0` release, DOI, or author verification of final
  numbers exists.

## v0.3.0-standalone — 2026-11-10

- Reframed the manuscript as a standalone technical report with the title
  "TRINEXIS: An Alert-Aware, Interval-Throttled Open-Vocabulary Webcam System
  with Language-Configured Speech".
- Removed review-response language, repeated disclaimer lists, JOSS/SoftwareX
  venue discussion, and the "Implementation Verification" title phrase.
- Replaced the long abstract with a 150–200 word problem/system/result/limitation abstract.
- Moved the 68.1% synthetic result into a short regression-check subsection
  and explained the 4/6 uniform-rank probability setup.
- Reduced the unclaimed-results text to one Scope and Limitations paragraph and
  replaced Table V with a short future-work list.
- Corrected Eq. (3) wording to state that time-based decay avoids a per-frame
  0.995 multiplier; labelled tau = 60 s an adjustable default and restated that
  the distance index is unitless and relative.
- Verified references 11–14, 16, and 18–21 against publisher/DOI pages; added
  pages, article numbers, and authors where needed.
- Cited the Ultralytics LICENSE file directly.
- Added weights/download_weights.py and weights/weights_checksums.sha256.
- Added zenodo.json and ZENODO.md; the Zenodo DOI remains pending author authorization.
- Kept the evidence boundary: no empirical detection, latency, distance,
  translated-template, or user-study result is claimed.

## v0.2.0-updated — 2026-11-10

- Added AGPL-3.0 license, documentation, pinned requirements, deterministic
  tests, configurable camera/security settings, vector figures, and a
  software-focused manuscript.

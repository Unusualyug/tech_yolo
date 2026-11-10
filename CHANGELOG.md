# Changelog

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

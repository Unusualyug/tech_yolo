# Problem list: what was fixed and how to finish

This document answers the six-item critique. **Implemented now** means a real
repository change on `arena/69777d37-tech-yolo`. **How to fix / pending** means
the remaining work that requires hardware, labeled data, language raters,
consented participants, author authorization, or a target venue. No empirical
result has been invented. The rebuilt manuscript keeps all empirical cells at
`NO DATA` and remains **not submission-ready**.

## 1. No empirical results; synthetic test presented as evidence

**Implemented now**

- Added optional real-log instrumentation in `app23.py`: capture, inference,
  TTS synthesis, playback, rendering, and speech-enqueue/playback events.
  Logging is off unless `TRINEXIS_LATENCY_LOG` and `TRINEXIS_EVENT_LOG` are set.
- Added Experiment A/B/C/D harnesses and blank templates under
  `experiments/`: latency, detection/grid, alert replay, and language ratings.
  `experiments/RESULTS_TEMPLATE.md` contains only `NO DATA` result cells.
- Added hardware, dataset, vocabulary, and alert manifest templates. The
  scripts require declared hardware/software, 500+ frames at 416/640/832,
  200–300 labeled images, frozen prompts/report split, and predeclared alerts.
- The seeded 68.1% result is generated only by
  `tests/test_synthetic_regression.py`; the old `experiments/` generator was
  removed. The paper cites the resulting JSON solely as a clearly labelled
  software-verification unit-test artifact, never as an empirical result.
- Rebuilt the paper with a blank empirical-results section and protocols.

**How to fix / pending**

- Run the live app with real camera/model/TTS and complete
  `experiments/hardware_manifest.json`; collect 500+ frames per setting.
- Collect 200–300 labeled images and real predictions; use pycocotools or
  Ultralytics `val`; never tune on the reported images.
- Export real `/export_logs` and speech event logs; run the replay harness.
- Complete the 5–10 language × 10 announcement rating worksheet with native
  or reliable bilingual raters and listen to sample gTTS audio.
- Have the author personally verify every number. Negative results are fine.

## 2. Weak novelty; paper read like a Flask app

**Implemented now**

- Reframed the manuscript around an **alert-aware narration policy** and a
  protocol for its **measured effect on alert delivery**, not around a Flask
  application description.
- Added the exact testable question: *Does alert-first narration make users
  notice a designated object faster or more often than confidence-first
  narration?*
- Separated the measurable part (delivery rate and alert-to-speech delay from
  real logs) from the user-noticing part (requires a consented study).
- Kept the paper as a standalone technical report with a single Scope and
  Limitations paragraph and no superiority, assistive-effectiveness, or
  clinical-readiness claim.

**How to fix / pending**

- Complete Experiment C to measure alert delivery; complete optional
  Experiment E only after consent and institutional ethics approval to answer
  the noticing/benefit part.
- Supply an official venue template, current Guide for Authors, and citation
  style before claiming submission readiness. None was supplied/read.

## 3. The synthetic ordering test could not fail

**Implemented now**

- `tests/test_policy_regression.py` contains a mutation-sensitive check: a
  deliberately broken confidence-first selector fails the alert invariant.
- `experiments/alert_replay.py --self-check` demonstrates that confidence-first
  replay can omit a designated alert while alert-first replay keeps it.
- `experiments/alert_replay.py --run` rejects explicitly synthetic/fixture
  rows and requires real logs plus a predeclared alert-manifest hash.
- The old `experiments/alert_selection_audit.py` generator was removed so the
  synthetic 68.1% check lives only under `tests/`.
- `TRINEXIS_ALERT_MANIFEST` freezes `/set_alerts` at runtime (HTTP 403) so
  alert objects cannot be chosen after seeing the data.

**How to fix / pending**

- Replay real webcam detection logs through both orderings and report delivery
  rate and mean alert-to-speech delay, including negative results.

## 4. No Zenodo DOI

**Implemented now**

- `ZENODO.md`, `zenodo.json`, `CITATION.cff`, `README.md`, and the paper's Data
  and Code Availability section now state that a final GitHub/Zenodo release
  must come **last**, followed by inserting the DOI in all three required
  places.
- Added a machine-readable evidence-boundary check that fails if a DOI appears
  before authorization.
- No DOI was minted and no new immutable release/tag was created.

**How to fix / pending**

1. Finish experiments, paper, code, funding/competing-interest confirmation,
   venue-policy recheck, dashboard screenshot, and spoken input→output example.
2. Create the **final** GitHub release for that exact version.
3. With the author's Zenodo authorization, mint the DOI for that exact release.
4. Insert the DOI into `CITATION.cff`, `README.md`, and the paper's Data and
   Code Availability section; rebuild the manuscript; verify all three.
5. A DOI is permanent for the exact archived version, so do not mint it from
   the older `v0.3.0-standalone` release or from this unreleased working tree.

## 5. Thin tests; only string checks

**Implemented now**

- Added `tests/test_routes.py`: real Flask `test_client` status tests for all
  23 routes, input validation/clamping, non-object JSON rejection, API-token
  401 behavior, unsupported-scheme/read-only 403 behavior, Bearer token,
  single-client 409, frozen alert manifest, and language-support metadata.
- `tests/route_test_support.py` mocks `cv2`, `numpy`, `ultralytics`, `gtts`,
  model loading, and the import-time speech thread with `unittest.mock`.
- Added `.github/workflows/ci.yml`, running on every `push` and
  `pull_request`, with `requirements-ci.txt`, compile checks, unit tests,
  experiment self-checks, and evidence-boundary verification.
- `paper/artifacts/test_summary.json` reports `43 route tests plus 37 policy tests, run in CI`.
  Source-contract tests are counted separately; Flask route tests are reported
  separately from source-text tests.
- Local CI-equivalent validation passed; the GitHub Actions run occurs after
  these changes are pushed.

**How to fix / pending**

- Check the first GitHub Actions run on the pushed branch. Add live-hardware
  integration tests only in a separate environment; CI here intentionally does
  not download weights or open a camera.

## 6. Untested vocabulary, confidence thresholds, and languages

**Implemented now**

- Added the 12-cell `{455, 20, 50, 80 prompts} × {0.15, 0.25, 0.35}` blank
  grid, with mAP@0.5 delegated to pycocotools or Ultralytics `val` and speed
  taken only from 500+ real inference rows.
- Added the 5–10 language × 10 announcement rating worksheet, 1–5
  correctness/naturalness fields, and a summarizer that reports only explicitly
  checked languages.
- `/get_languages` now returns the ten English-template fallback languages,
  an empty `verified_languages` list, and a support note. The UI displays the
  English fallback and states that translations/TTS are unchecked. gTTS is
  documented as using **Google Translate's speech service**, with an
  instruction to listen to sample audio.
- The 72 language-code claim is explicitly unchecked; no multilingual
  comprehension or translation-quality claim is made.

**How to fix / pending**

- Freeze prompt sets and report split before generating predictions; report
  all 12 grid cells including negative results.
- Recruit native or reliable bilingual raters for 5–10 languages and 10
  announcements each; listen to a few languages; report only checked
  languages and say the rest are unchecked.
- Add the 10 missing templates only if a reliable reviewer checks them; the
  current fix documents English fallback instead of inventing translations.

## Local validation performed

- `python3 -m unittest discover -s tests -v`: **93 tests OK**, 0 failures,
  0 errors; `43 route tests plus 37 policy tests, run in CI`, plus 13
  source-contract tests.
- All five experiment harness software self-checks passed; no empirical data
  was produced.
- `scripts/verify_no_fabricated_results.py`: **EVIDENCE BOUNDARY CHECK OK**.
- Rebuilt paper: 12-page PDF, 5 tables, 2 figures, 174-word abstract, and
  citations [1]–[24]. `paper/artifacts/updated_repository_audit.json` records
  99 files, 93 tests, and `zenodo_doi: null`.
- `git diff --check` passed. No new tag, GitHub release, Zenodo DOI, or email
  was created for this unreleased revision.

## Overall status

| Item | Status |
|---|---|
| Instrumentation, protocols, blank results | implemented |
| Real Flask route tests and CI workflow | implemented |
| Paper reframing and language-fallback UI/docs | implemented |
| Final answer with this how-to-fix explanation | this document |
| Empirical A–D results | pending real hardware/data/raters |
| Optional user noticing study | pending consent and institutional ethics approval |
| Dashboard screenshot and spoken input→output example | pending |
| Zenodo DOI | pending author authorization and final release |
| Official venue template / Guide for Authors / citation style | pending; not supplied/read |
| AI-tool disclosure policy recheck | pending |
| Funding / competing-interest author confirmation | pending |
| Author's personal verification of every number | pending |
| Submission-ready | no |

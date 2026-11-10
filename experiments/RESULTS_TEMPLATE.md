# Blank empirical result template

Every result cell is `NO DATA`. Protocol settings (image sizes, prompt counts,
confidence thresholds, number of announcements) are not measured results. Do
not cite this table as evidence. Negative results from real experiments are
reportable, but they must replace a `NO DATA` cell only after the corresponding
real log, manifest, and author verification exist.

## Experiment A — latency

Minimum: 500 camera frames per input-size setting on declared hardware.

| Setting | imgsz | Stage | Frames | Median | p95 |
|---|---:|---|---:|---:|---:|
| study-01 | 416 | capture | NO DATA | NO DATA | NO DATA |
| study-01 | 416 | inference | NO DATA | NO DATA | NO DATA |
| study-01 | 416 | TTS synthesis | NO DATA | NO DATA | NO DATA |
| study-01 | 416 | playback | NO DATA | NO DATA | NO DATA |
| study-01 | 416 | rendering | NO DATA | NO DATA | NO DATA |
| study-01 | 640 | capture | NO DATA | NO DATA | NO DATA |
| study-01 | 640 | inference | NO DATA | NO DATA | NO DATA |
| study-01 | 640 | TTS synthesis | NO DATA | NO DATA | NO DATA |
| study-01 | 640 | playback | NO DATA | NO DATA | NO DATA |
| study-01 | 640 | rendering | NO DATA | NO DATA | NO DATA |
| study-01 | 832 | capture | NO DATA | NO DATA | NO DATA |
| study-01 | 832 | inference | NO DATA | NO DATA | NO DATA |
| study-01 | 832 | TTS synthesis | NO DATA | NO DATA | NO DATA |
| study-01 | 832 | playback | NO DATA | NO DATA | NO DATA |
| study-01 | 832 | rendering | NO DATA | NO DATA | NO DATA |

Hardware/software manifest SHA-256: `NO DATA`.

## Experiment B — detection quality and vocabulary/confidence grid

Dataset: 200–300 labeled images; report split declared separately from any
tuning split; no tuning on reported images. mAP@0.5 must come from
pycocotools or Ultralytics `val`.

| Cell | Prompts | Confidence | Precision | Recall | mAP@0.5 | Speed median |
|---|---:|---:|---:|---:|---:|---:|
| cell_455_015 | 455 | 0.15 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_455_025 | 455 | 0.25 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_455_035 | 455 | 0.35 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_20_015 | 20 | 0.15 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_20_025 | 20 | 0.25 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_20_035 | 20 | 0.35 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_50_015 | 50 | 0.15 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_50_025 | 50 | 0.25 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_50_035 | 50 | 0.35 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_80_015 | 80 | 0.15 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_80_025 | 80 | 0.25 | NO DATA | NO DATA | NO DATA | NO DATA |
| cell_80_035 | 80 | 0.35 | NO DATA | NO DATA | NO DATA | NO DATA |

Frozen prompt-set SHA-256: `NO DATA`. Report-split SHA-256: `NO DATA`.

## Experiment C — replay of real alert deliveries

Alert objects must be chosen in advance. Run **5–10 real sessions** with
`TRINEXIS_EVENT_LOG`, then replay the same frames through three orderings.
Replay measures delivery, not user noticing. Report whatever is observed even
if alert-first helps less than hoped.

| Ordering | Real sessions | Real frames | Alerts seen | Alerts delivered | Delivery rate | Mean alert-to-speech delay | Observed mean delay from event log |
|---|---:|---:|---:|---:|---:|---:|---:|
| Alert-first | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |
| Confidence-first | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |
| Nearest-object-first | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |

Predeclared alert-manifest SHA-256: `NO DATA`. Session-manifest SHA-256:
`NO DATA`. The seeded synthetic 68.1% is a `tests/` unit-test artifact only;
it is not a row in this table.

## Experiment D — checked-language ratings

Sample 5–10 languages and 10 announcements per language. Use native speakers
or reliable bilingual raters; give correctness and naturalness ratings from 1
to 5. Listen to sample gTTS/Google Translate speech audio.

| Checked language | Raters | Announcements | Mean correctness | Mean naturalness |
|---|---:|---:|---:|---:|
| NO DATA | NO DATA | 10 | NO DATA | NO DATA |

Report only checked languages. The remaining 72 language codes are
**unchecked**. The ten languages without a top-level template use the English
template fallback in the UI.

## Experiment E — optional user noticing study

Consent and institutional ethics approval are required before recruitment. No
approval or participant data is claimed. The frozen protocol uses 8–12
participants, all three within-subject conditions, counterbalanced order, and
preregistered notice rate and time-to-notice outcomes.

| Condition | Participants | Designated object | Notice rate | Median time-to-notice |
|---|---:|---|---:|---:|
| Alert-first | NO DATA | NO DATA | NO DATA | NO DATA |
| Confidence-first | NO DATA | NO DATA | NO DATA | NO DATA |
| Nearest-object-first | NO DATA | NO DATA | NO DATA | NO DATA |

## Administrative status

| Item | Status |
|---|---|
| Dashboard screenshot | pending real hand-run smoke test |
| Spoken input→output example | pending real hand-run smoke test; blank template only |
| Flask test-client integration tests | 43 route + 37 policy + 13 source-contract = 93; mocked dependencies |
| Live-app smoke test | pending webcam, hydrated weights, runtime deps, browser/audio |
| Target venue | arXiv / institutional report selected 2026-11-10 |
| Venue author guide / official template | current arXiv pages opened in `paper/venue_guide_notes.md`; no mandatory template |
| AI-tool disclosure policy recheck | done against arXiv text-to-text generative-AI policy |
| Funding / competing-interest author confirmation | confirmed: no external funding; no competing interests |
| CRediT roles actually performed | confirmed: conceptualization, software, writing—original draft |
| Methodology / investigation / formal analysis | pending until actual experiments |
| All 24 references ticked after source recheck | done in `paper/reference_verification.md` |
| Author personal verification of every number | pending |
| Final `v1.0.0` GitHub release | pending; `scripts/final_release_checklist.py --check` is blocked |
| Zenodo connection / DOI | authorized after final results; not connected, no DOI minted |
| Submission-ready | no |

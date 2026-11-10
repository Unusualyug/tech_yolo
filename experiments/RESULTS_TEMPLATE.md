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

Alert objects must be chosen in advance. Replay measures delivery, not user
noticing.

| Ordering | Real frames | Alerts seen | Alerts delivered | Delivery rate | Mean alert-to-speech delay | Observed mean delay from event log |
|---|---:|---:|---:|---:|---:|---:|
| Alert-first | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |
| Confidence-first | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA | NO DATA |

Predeclared alert-manifest SHA-256: `NO DATA`. The seeded synthetic 68.1% is a
`tests/` unit-test artifact only; it is not a row in this table.

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
approval or participant data is claimed.

| Condition | Participants | Designated object | Notice rate | Median time-to-notice |
|---|---:|---|---:|---:|
| Alert-first | NO DATA | NO DATA | NO DATA | NO DATA |
| Confidence-first | NO DATA | NO DATA | NO DATA | NO DATA |

## Administrative status

| Item | Status |
|---|---|
| Dashboard screenshot | pending |
| Spoken input→output example | pending |
| Flask test-client integration tests | implemented, reported separately from source-text tests |
| Venue current Guide for Authors / official template | pending; not supplied/read |
| AI-tool disclosure policy recheck | pending |
| Funding / competing-interest author confirmation | pending |
| Author personal verification of every number | pending |
| Final GitHub release | pending |
| Zenodo DOI | pending author authorization; no DOI minted |
| Submission-ready | no |

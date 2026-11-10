# Hand-run live smoke test (not yet completed)

This is a human-run checklist. The repository's 93 tests use mocked camera,
NumPy, detector, and TTS imports; they do **not** count as a live-app run. No
dashboard screenshot, real detection frame, heard speech sentence, webcam, or
hydrated model weight exists in this sandbox. Do not replace any field with a
synthetic example.

## 1. Check real prerequisites on the machine with the webcam

```bash
python3 -m pip install -r requirements.txt
python3 weights/download_weights.py --fetch --verify
python3 scripts/live_smoke_test.py --check-prereqs
```

`--check-prereqs` must report `run_ready: true`. It checks `/dev/video*`,
runtime modules (`cv2`, `numpy`, `ultralytics`, `gtts`, `flask`,
`pycocotools`), Git LFS, hydrated root `*.pt` files, the five `TRINEXIS_*`
environment variables, and the manifest templates. A report of
`run_ready: false` means the live smoke test cannot honestly be claimed.

## 2. Freeze declarations before starting

Copy and complete `hardware_manifest.template.json`,
`alert_manifest.template.json`, `session_manifest.template.json`,
`dataset_manifest.template.json`, and `vocab_manifest.template.json`. Record the
alert objects (for example, `person` and `knife`) and `declared_at` **before**
capture. Record each manifest SHA-256 in the session notes.

```bash
export TRINEXIS_LATENCY_LOG="$PWD/experiments/results/latency.jsonl"
export TRINEXIS_EVENT_LOG="$PWD/experiments/results/speech_events.jsonl"
export TRINEXIS_EXPERIMENT_SETTING="study-01"
export TRINEXIS_HARDWARE_MANIFEST="$PWD/experiments/hardware_manifest.json"
export TRINEXIS_ALERT_MANIFEST="$PWD/experiments/alert_manifest.json"
python3 app23.py
```

## 3. Human-run actions

1. Open the dashboard in the same machine's browser at the host printed by
   `app23.py` (normally `http://127.0.0.1:5000/`).
2. Start the real camera and confirm that a live frame, detection boxes, and
   the average-confidence display appear. Do not use a static mock image.
3. Present a scene containing at least one predeclared alert object and one
   higher-confidence non-alert object. Allow the speech interval and TTS
   playback to complete.
4. Save an unedited browser screenshot as
   `experiments/results/dashboard_screenshot.png`.
5. Click `/export_logs` and save the real JSON as
   `experiments/results/export_logs.json`.
6. Copy `experiments/SPOKEN_IO_EXAMPLE.template.md` to
   `experiments/results/spoken_io_example.md`. Paste the exact detection JSON
   for that frame and write the exact sentence heard from the app. Fill the
   human-verification fields. Do not leave any `NO DATA` placeholder.
7. Stop the app. Preserve `latency.jsonl` and `speech_events.jsonl` from the
   same run.

## 4. Verify the captured evidence

```bash
python3 scripts/live_smoke_test.py --verify-evidence
```

The verifier checks the PNG signature, the spoken example's required sections,
parseable detection JSON, and at least one real `speech_enqueued` event. It
rejects explicitly synthetic/fixture rows. It does not judge detection quality
or create a result number.

## 5. Continue with Experiment C first

Repeat the real run for **5–10 sessions** using the same frozen alert manifest,
saving each session's `export_logs` and `speech_events.jsonl` separately. Add
them to `experiments/session_manifest.json`, then run:

```bash
python3 experiments/multi_session_replay.py --self-check
python3 experiments/multi_session_replay.py --run \
  --session-manifest experiments/session_manifest.json \
  --output experiments/results/multi_session_replay_results.json
```

Report delivery rate and mean alert-to-speech delay exactly as observed, even
if alert-first helps less than hoped. Then proceed to Experiments A, B, and D
under `experiments/README.md`. Only after all results and author verification
should the paper be rewritten and the final `v1.0.0`/Zenodo DOI steps begin.

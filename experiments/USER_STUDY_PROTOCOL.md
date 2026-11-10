# Experiment E — within-subject user-noticing protocol (not yet run)

**Status:** no recruitment, consent, institutional ethics approval, participants,
trials, notice rate, or time-to-notice result exists. All result cells remain
`NO DATA`. The department was asked early about the ethics route; see the
sent-inquiry receipt below. That inquiry is not approval.

## Prerequisites before any participant is contacted

1. Written institutional ethics approval or a documented formal waiver, with an
   approval identifier. An inquiry email to the department is not approval.
2. A consent form covering the camera feed, audio announcements, what is
   recorded, retention/deletion, withdrawal, and bystander privacy.
3. Freeze the three ordering policies, the predesignated alert objects, the
   trial script, the timeout, and the two outcomes before the first session.
4. A working live app, hydrated weights, real webcam, and audio output. The
   mocked Flask test-client tests do not satisfy this requirement.

## Design

- **Participants:** 8–12 consented adults. Report the exact number actually
  recruited; do not fill unused slots.
- **Design:** within-subject. Every participant experiences all three policies:
  alert-first, confidence-first, and nearest-object-first.
- **Order:** counterbalanced rotation across participants, frozen before the
  first session. `experiments/user_study.py --emit-worksheet` generates the
  blank slots and deterministic rotation.
- **Task:** for each condition, present the same class of scene with one
  predesignated object. Start the trial timer at the same audible/visual cue.
  Ask the participant to indicate when they notice the designated object.
- **Preregistered outcomes:** binary notice within the trial timeout
  (`noticed`) and time-to-notice in milliseconds. Trials with no notice are
  censored at the timeout; they must not be silently converted to a numeric
  detection time.
- **Analysis:** notice rate and median time-to-notice by policy. Report
  whichever effect is observed, including a small, null, or negative
  alert-first effect. Do not infer assistive benefit, clinical readiness, or
  deployment success from these outcomes.

## Blank worksheet

```bash
python3 experiments/user_study.py --self-check
python3 experiments/user_study.py --emit-worksheet --participants 8 \
  --worksheet experiments/results/user_study_worksheet.csv
python3 experiments/user_study.py --summarize \
  --worksheet experiments/results/user_study_worksheet.csv \
  --output experiments/results/user_study_results.json
```

The emitted slots are blank placeholders, not participant data. The summarizer
requires one real ethics-approval identifier, consent on every row, 8–12 unique
real participant IDs, all three conditions per participant, and numeric
time-to-notice for noticed trials. It returns `INSUFFICIENT DATA` otherwise.

## Department inquiry

An early ethics-route inquiry was **sent** on 2026-11-10 from the author's
institutional Gmail account to `hod@gmiu.edu.in`, the HOD address appearing in
official GMIU mail. Gmail message ID `1a1c4db01f9cbe1f`; thread ID
`1a1c4dad79d27fcf`; Message-ID
`<CAC9kwkrSSDv3p2XF5sGyj90QuW3cTSHsb6-LGf=3S-tO70CGLw@mail.gmail.com>`.
It asks which committee, forms, consent, and data-retention documents apply,
and explicitly states that recruitment will not begin before written approval
or a documented formal waiver. No reply, approval, or waiver is claimed. The
author must verify the reply and enter its approval identifier into the real
worksheet before recruitment. See `experiments/ethics_inquiry_receipt.md`.

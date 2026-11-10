# Zenodo DOI instructions

A DOI has **not** been minted. `v0.3.0-standalone` is an older immutable
release; the unreleased working-tree fixes on
`arena/69777d37-tech-yolo` change the paper, tests, instrumentation, and UI.
Do **not** mint a DOI from that older release or from this working tree. A DOI
is permanent for the exact archived version, so the final GitHub/Zenodo release
must come **last**.

## Why this is pending

1. Zenodo requires the author to authorize the GitHub connection; this sandbox
   cannot create a deposit under the author's Zenodo account.
2. Empirical Experiments A–D are blank `NO DATA` protocols until real hardware,
   labeled data, logs, and raters are supplied.
3. Optional user-noticing work requires consent and institutional ethics
   approval first.
4. The dashboard screenshot, spoken input→output example, real 5–10 session
   replay, and author's personal number verification are pending.
5. The author selected arXiv/institutional-report formatting; current official
   arXiv pages were read in `paper/venue_guide_notes.md` and no mandatory
   template exists. AI-tool policy and author funding/competing-interest/
   CRediT decisions were checked and recorded. The author has authorized the
   final DOI sequence but has not connected Zenodo or approved a frozen
   `v1.0.0` archive; the manuscript is **not submission-ready**.

## Exact minting order after all of the above are complete

1. Freeze the final paper, code, metadata, and result files.
2. Create the **final** GitHub release and tag for that exact version; do not
   reuse `v0.3.0-standalone`.
3. Sign in to Zenodo with the author's account and connect
   `https://github.com/Unusualyug/tech_yolo` through Zenodo's GitHub
   integration.
4. Enable and publish the final GitHub release in Zenodo. Zenodo creates the
   deposit and mints the DOI.
5. Insert the resulting DOI in **all required locations**:
   - `CITATION.cff` (`doi` and the preferred-citation URL);
   - `README.md` (Citation section);
   - `paper/updated_manuscript_content.py` → Data and Code Availability, then
     rebuild `paper/tech_yolo_updated_research_paper.{pdf,docx,md}`.
6. Also update `codemeta.json`, `zenodo.json`, and this file's status so the
   metadata does not describe a draft. Verify the DOI resolves to the exact
   final release.
7. Rebuild the manuscript and audit; have the author personally verify every
   number and declaration.

`zenodo.json` contains prepared deposit metadata with
`version: "PENDING_FINAL_RELEASE"` and `notes: "DOI pending..."`.
`scripts/final_release_checklist.py --check` mechanically refuses a release
while empirical data, hand-run evidence, status prose, or final author
verification is unresolved. Until the DOI exists, cite the immutable prior
GitHub release URL [23] for the prior release only; do not claim that the
unreleased fixes are part of that DOI.

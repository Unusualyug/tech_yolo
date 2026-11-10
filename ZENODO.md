# Zenodo DOI instructions

A DOI has **not** been minted yet. Zenodo requires the author to authorize the
GitHub connection; this sandbox cannot create a deposit under the author's
Zenodo account.

1. Sign in to Zenodo with the author's account.
2. Connect `https://github.com/Unusualyug/tech_yolo` through Zenodo's GitHub
   integration and enable the repository.
3. Enable the existing GitHub release `v0.3.0-standalone` in Zenodo (or republish it).
4. Zenodo will create a deposit and mint a DOI.
5. Replace the GitHub release URL in `CITATION.cff`, `codemeta.json`,
   `zenodo.json`, `paper/updated_manuscript_content.py`, and
   `paper/README.md` with the DOI.
6. Rebuild the manuscript and create a new patch release.

`zenodo.json` contains the prepared deposit metadata. Until the DOI exists, the
paper cites the GitHub release URL [23] rather than claiming a DOI.

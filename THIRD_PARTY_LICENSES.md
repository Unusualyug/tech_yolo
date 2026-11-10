# Third-party license notice

This project is licensed under **GNU AGPL-3.0-only**. The following principal
dependencies were checked against their PyPI package metadata or official
repositories on 2026-11-10. Always verify the license of the exact installed
distribution and version before redistribution.

| Component | Version checked | License | Source |
|---|---:|---|---|
| Ultralytics / YOLO | 8.4.208 | AGPL-3.0 | Official LICENSE file: https://github.com/ultralytics/ultralytics/blob/main/LICENSE |
| Flask | 3.1.3 | BSD-3-Clause | PyPI package metadata |
| NumPy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | PyPI package metadata |
| OpenCV (`opencv-python`) | 5.0.0.93 | Apache-2.0 | PyPI package metadata |
| gTTS | 2.5.4 | MIT | PyPI package metadata |
| Pillow | 13.0.0 | MIT-CMU | PyPI package metadata |
| ReportLab | 5.1.0 | BSD | PyPI package metadata |
| python-docx | 1.2.0 | MIT | PyPI package metadata |
| pypdf | 7.0.0 | BSD-3-Clause | PyPI package metadata |
| PyMuPDF | 2.1 | AGPL-3.0 or Artifex commercial license | PyPI package metadata |

Ultralytics states that its AGPL-3.0 license applies to derivative works that
use its code or models. This repository therefore adopts AGPL-3.0-only. See
`LICENSE` for the full license text.

Model weights in `*.pt` files are Git LFS pointers, not redistributed tensor
files in this checkout. Their upstream licenses and terms must be checked
separately before fetching or redistribution. `weights/download_weights.py`
verifies the Git LFS object identifiers as SHA-256 checksums after materialization.

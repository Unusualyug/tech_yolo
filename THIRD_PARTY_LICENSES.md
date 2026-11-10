# Third-party license notice

This project is licensed under **GNU AGPL-3.0-only**. The following principal
dependencies were checked against their PyPI package metadata or official
repositories on 2026-11-10. Always verify the license of the exact installed
distribution and version before redistribution.

| Component | Version checked | License | Notes |
|---|---:|---|---|
| Ultralytics / YOLO | 8.4.208 | AGPL-3.0 | Official Ultralytics repositories state AGPL-3.0 and describe derivative-work source-disclosure requirements. This repository therefore uses AGPL-3.0. |
| Flask | 3.1.3 | BSD-3-Clause | Web framework. |
| NumPy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | Composite license string reported by PyPI metadata. |
| OpenCV (`opencv-python`) | 5.0.0.93 | Apache-2.0 | Camera capture and frame drawing. |
| gTTS | 2.5.4 | MIT | Speech synthesis wrapper; not affiliated with Google. |
| Pillow | 13.0.0 | MIT-CMU | Figure generation. |
| ReportLab | 5.1.0 | BSD | PDF manuscript and vector figure generation. |
| python-docx | 1.2.0 | MIT | DOCX manuscript generation. |
| pypdf | 7.0.0 | BSD-3-Clause | PDF validation. |
| PyMuPDF | 2.1 | AGPL-3.0 or Artifex commercial license | Dual-licensed PDF validation utility. |

Model weights in `*.pt` files are Git LFS pointers, not redistributed tensor
files in this checkout. Their upstream licenses and terms must be checked
separately before fetching or redistribution.

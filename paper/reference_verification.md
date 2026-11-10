# Reference verification log

**Check date:** 2026-11-10  
**Scope:** All 24 references in `paper/updated_manuscript_content.py`.  
**Method:** Each DOI, publisher landing page, or official project page was opened
with `fetch_page`; authors, year, venue, and page/article metadata were checked
against the opened source. Where a DOI resolver failed or an ACM Basic Edition
page hid metadata, the official publisher PDF, IEEE Xplore/Computer Society
page, CVF Open Access page, arXiv record, or official project page was opened
instead. No reference was trusted solely from an unopened citation. No Zenodo
DOI is claimed in the manuscript.

| Ref | Source opened | Metadata confirmed | Notes |
|---|---|---|---|
| [1] | IEEE Xplore `https://ieeexplore.ieee.org/document/7780460/` and CVF PDF | Redmon, Divvala, Girshick, Farhadi; CVPR 2016; pp. 779–788; DOI `10.1109/CVPR.2016.91` | Direct `doi.org` request returned HTTP 500; IEEE Xplore metadata and CVF paper resolved it. PASCAL VOC 2007/2012 and Picasso/People-Art evaluation confirmed in the paper. |
| [2] | Springer chapter `10.1007/978-3-319-10602-1_48` | Lin et al.; ECCV 2014; LNCS 8693; pp. 740–755 | Abstract confirms 328k images, 2.5M instances, 91 object types; the 2014 release contains 80 released categories. |
| [3] | PMLR `https://proceedings.mlr.press/v139/radford21a.html` | Radford et al.; ICML 2021; PMLR 139; pp. 8748–8763 | BibTeX on the page gives full author list, venue, year, and pages. |
| [4] | Springer chapter `10.1007/978-3-031-72970-6_3` | Liu et al.; ECCV 2024; LNCS 15105; pp. 38–55 | Published ECCV 2024 version, not the arXiv preprint. |
| [5] | CVF Open Access CVPR 2024 | Cheng, Song, Ge, Liu, Wang, Shan; CVPR 2024; pp. 16901–16911; DOI `10.1109/CVPR52733.2024.01599` | CVF HTML includes BibTeX and page range. |
| [6] | Ultralytics YOLO-World documentation | `set_classes` / offline-vocabulary workflow | Official documentation page opened. |
| [7] | Flask documentation | Flask 3.1.x; lightweight WSGI framework | Official Pallets documentation opened. |
| [8] | OpenCV 4.13.0 “Getting Started with Videos” | `cv.VideoCapture` camera-index behavior | Official OpenCV tutorial opened. |
| [9] | GitHub `pndurette/gTTS` | gTTS repository description and MIT license link | Official repository opened. |
| [10] | Git LFS `docs/spec.md` | Pointer format, `oid sha256:...`, `size` | Official specification opened. |
| [11] | Springer chapter `10.1007/978-3-031-20080-9_42` | Minderer et al.; ECCV 2022; pp. 728–755 | Title is “Simple Open-Vocabulary Object Detection”; some indexes use the expanded “with Vision Transformers” variant. |
| [12] | IEEE Computer Society CSDL, IEEE Xplore, CVF Open Access | Liunian Harold Li et al.; CVPR 2022; DOI `10.1109/CVPR52688.2022.01069` | Direct `doi.org` request returned HTTP 500. IEEE Computer Society gives pp. 10955–10965; CVF gives pp. 10965–10975. Manuscript uses the IEEE Computer Society proceedings pagination. |
| [13] | Springer chapter `10.1007/978-3-031-20077-9_21` | Zhou et al.; ECCV 2022; LNCS 13669; pp. 350–368 | Detic paper and page range confirmed. |
| [14] | arXiv `2503.07465` | Wang, Liu, Chen, Lin, Han, Ding; submitted 2025; revised 2025; DOI `10.48550/arXiv.2503.07465` | arXiv v2 comments mention ICCV 2025; manuscript cites the arXiv record only. |
| [15] | GitHub `ultralytics/ultralytics` | Official Ultralytics YOLO repository | Repository page opened. |
| [16] | ACM DOI `10.1145/2910674.2935839` and ACM citation metadata | Avila, Wolf, Brock, Henze; PETRA 2016; Article 85; 2 pages | ACM Basic Edition hid some fields; official ACM reference format and citing papers supplied article number and page count. |
| [17] | `https://www.seeingai.com/` | Microsoft Seeing AI official site | The former `microsoft.com/en-us/ai/seeing-ai` URL resolves to the Seeing AI site; manuscript uses the final URL. |
| [18] | ACM DOI `10.1145/3613904.3642211` and ACM citation metadata | Gonzalez Penuela, Collins, Bennett, Azenkot; CHI 2024; Article 901; 21 pages | Official ACM reference format/citing papers supplied article number and page count. |
| [19] | arXiv `2409.16808` | Alqahtani, Cheema, Rodriguez, Toosi; v1 2024; v3 2026; DOI `10.48550/arXiv.2409.16808` | Manuscript notes revision; no project results are borrowed from this benchmark. |
| [20] | ACM DOI `10.1145/3375627.3375820` and ACM PDF | Raji, Gebru, Mitchell, Buolamwini, Lee, Remi Denton; AIES 2020; pp. 145–151 | ACM PDF uses “Remi Denton”; some secondary indexes use “Emily Denton.” Manuscript uses “R. Denton” to match the PDF. |
| [21] | ACM DOI `10.1145/3583135` and ACM citation metadata | Hasan, Guest, Deravi; ACM Computing Surveys 55(13s); Article 286; pp. 1–27; 2023 | Official ACM reference format and journal TOC supplied article number and pages. |
| [22] | GitHub `ultralytics/ultralytics/blob/main/LICENSE` | GNU AGPL-3.0 license text | Direct license file opened and cited. This satisfies the request to cite Ultralytics' license page rather than only the repository. |
| [23] | `https://github.com/Unusualyug/tech_yolo/releases/tag/v0.3.0-standalone` | Project release URL | Verified with `gh release view` after publication. No Zenodo DOI is claimed. |
| [24] | `https://www.gnu.org/licenses/agpl-3.0.txt` and SPDX `AGPL-3.0-only` | GNU AGPL v3.0, 19 November 2007 | FSF HTML page returned HTTP 500; the official plain-text license and SPDX page opened successfully. |

## Resolver and metadata notes

- `doi.org/10.1109/CVPR.2016.91` and `doi.org/10.1109/CVPR52688.2022.01069`
  returned HTTP 500 in this environment. IEEE Xplore, IEEE Computer Society
  CSDL, and CVF Open Access pages were opened instead.
- `www.gnu.org/licenses/agpl-3.0.en.html` returned HTTP 500. The official
  `agpl-3.0.txt` and SPDX `AGPL-3.0-only` pages were opened instead.
- ACM Basic Edition pages sometimes hide author, page, or article metadata;
  official ACM PDFs, ACM reference formats, and publisher citation metadata
  were used for those fields.
- The GLIP page-range discrepancy is recorded above rather than silently
  choosing one source.
- Funding, competing-interest, and AI-tool disclosure statements still require
  author confirmation and a venue-policy check before submission.

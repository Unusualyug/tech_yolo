# Reference verification log

**Check date:** 2026-11-10; full recheck completed 2026-11-10
**Scope:** All 24 references in `paper/updated_manuscript_content.py`.
**Method:** Each DOI, publisher landing page, or official project page was opened
with `fetch_page`; authors, year, venue, and page/article metadata were checked
against the opened source. On the recheck date, all 24 official sources were
opened again, and priority refs [11], [12], [16], [19], [20], and [21] were
opened directly. Where a DOI resolver failed or an ACM Basic Edition page hid
metadata, the official publisher PDF, IEEE Xplore/Computer Society page, CVF
Open Access page, arXiv record, official project page, or publisher citation
metadata was opened instead. No reference was trusted solely from an unopened
citation. No Zenodo DOI is claimed in the manuscript.

| Verified | Ref | Source opened | Metadata confirmed | Notes |
|---|---|---|---|---|
| [x] | [1] | IEEE Xplore `https://ieeexplore.ieee.org/document/7780460/` and CVF PDF | Redmon, Divvala, Girshick, Farhadi; CVPR 2016; pp. 779–788; DOI `10.1109/CVPR.2016.91` | Direct `doi.org` request returned HTTP 500; IEEE Xplore metadata and CVF paper resolved it. PASCAL VOC 2007/2012 and Picasso/People-Art evaluation confirmed in the paper. |
| [x] | [2] | Springer chapter `10.1007/978-3-319-10602-1_48` | Lin et al.; ECCV 2014; LNCS 8693; pp. 740–755 | Abstract confirms 328k images, 2.5M instances, 91 object types; the 2014 release contains 80 released categories. |
| [x] | [3] | PMLR `https://proceedings.mlr.press/v139/radford21a.html` | Radford et al.; ICML 2021; PMLR 139; pp. 8748–8763 | BibTeX on the page gives full author list, venue, year, and pages. |
| [x] | [4] | Springer chapter `10.1007/978-3-031-72970-6_3` | Liu et al.; ECCV 2024; LNCS 15105; pp. 38–55 | Published ECCV 2024 version, not the arXiv preprint. |
| [x] | [5] | CVF Open Access CVPR 2024 | Cheng, Song, Ge, Liu, Wang, Shan; CVPR 2024; pp. 16901–16911; DOI `10.1109/CVPR52733.2024.01599` | CVF HTML includes BibTeX and page range. |
| [x] | [6] | Ultralytics YOLO-World documentation | `set_classes` / offline-vocabulary workflow | Official documentation page opened. |
| [x] | [7] | Flask documentation | Flask 3.1.x; lightweight WSGI framework | Official Pallets documentation opened. |
| [x] | [8] | OpenCV 4.13.0 “Getting Started with Videos” | `cv.VideoCapture` camera-index behavior | Official OpenCV tutorial opened. |
| [x] | [9] | GitHub `pndurette/gTTS` | gTTS repository description and MIT license link | Official repository opened. |
| [x] | [10] | Git LFS `docs/spec.md` | Pointer format, `oid sha256:...`, `size` | Official specification opened. |
| [x] | [11] | Springer chapter `10.1007/978-3-031-20080-9_42` | Minderer et al.; ECCV 2022; pp. 728–755; first online 03 Nov 2022 | Priority recheck: Springer page confirms the short title “Simple Open-Vocabulary Object Detection” and pp. 728–755; some indexes use the expanded “with Vision Transformers” variant. |
| [x] | [12] | IEEE Computer Society CSDL, IEEE Xplore, CVF Open Access | Liunian Harold Li et al.; CVPR 2022; pp. 10955–10965; DOI `10.1109/CVPR52688.2022.01069` | Priority recheck: CSDL confirms authors, year, IEEE pagination, and DOI. Direct `doi.org` request returned HTTP 500. CVF gives pp. 10965–10975; manuscript uses IEEE Computer Society proceedings pagination. |
| [x] | [13] | Springer chapter `10.1007/978-3-031-20077-9_21` | Zhou et al.; ECCV 2022; LNCS 13669; pp. 350–368 | Detic paper and page range confirmed. |
| [x] | [14] | arXiv `2503.07465` | Wang, Liu, Chen, Lin, Han, Ding; submitted 2025; revised 2025; DOI `10.48550/arXiv.2503.07465` | arXiv v2 comments mention ICCV 2025; manuscript cites the arXiv record only. |
| [x] | [15] | GitHub `ultralytics/ultralytics` | Official Ultralytics YOLO repository | Repository page opened. |
| [x] | [16] | ACM DOI `10.1145/2910674.2935839` and ACM citation metadata | Avila, Wolf, Brock, Henze; PETRA 2016; Article 85; 2 pages; published 29 Jun 2016 | Priority recheck: ACM page title/abstract opened; Basic Edition hid some fields, so official ACM citation metadata supplied article number and page count. |
| [x] | [17] | `https://www.seeingai.com/` | Microsoft Seeing AI official site | The former `microsoft.com/en-us/ai/seeing-ai` URL resolves to the Seeing AI site; manuscript uses the final URL. |
| [x] | [18] | ACM DOI `10.1145/3613904.3642211` and ACM citation metadata | Gonzalez Penuela, Collins, Bennett, Azenkot; CHI 2024; Article 901; 21 pages | Official ACM reference format/citing papers supplied article number and page count. |
| [x] | [19] | arXiv `2409.16808` | Alqahtani, Cheema, Rodriguez, Toosi; v1 25 Sep 2024; v3 14 Jul 2026; DOI `10.48550/arXiv.2409.16808` | Priority recheck: arXiv record confirms authors, versions, dates, and arXiv DOI; no project results are borrowed from this benchmark. |
| [x] | [20] | ACM DOI `10.1145/3375627.3375820` and ACM PDF | Raji, Gebru, Mitchell, Buolamwini, Lee, Remi Denton; AIES 2020; pp. 145–151; 7 Feb 2020 | Priority recheck: ACM page title/abstract opened; publisher citation metadata confirms authors, year, venue, and pages. ACM PDF uses “Remi Denton”; some secondary indexes use “Emily Denton.” Manuscript uses “R. Denton” to match the PDF. |
| [x] | [21] | ACM DOI `10.1145/3583135` and ACM citation metadata | Hasan, Guest, Deravi; ACM Computing Surveys 55(13s); Article 286; pp. 1–27; published 13 Jul 2023 | Priority recheck: ACM page title/abstract opened; official ACM reference format and journal TOC supplied article number and pages. |
| [x] | [22] | GitHub `ultralytics/ultralytics/blob/main/LICENSE` | GNU AGPL-3.0 license text | Direct license file opened and cited. This satisfies the request to cite Ultralytics' license page rather than only the repository. |
| [x] | [23] | `https://github.com/Unusualyug/tech_yolo/releases/tag/v0.3.0-standalone` | Project release URL | GitHub release page was opened again on the recheck date; `gh release view` verified publication previously. No Zenodo DOI is claimed. |
| [x] | [24] | `https://www.gnu.org/licenses/agpl-3.0.txt` and SPDX `AGPL-3.0-only` | GNU AGPL v3.0, 19 November 2007 | FSF HTML page returned HTTP 500; the official plain-text license and SPDX page opened successfully. |

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
- All 24 rows are ticked `[x]` after the 2026-11-10 recheck. Priority refs
  [11], [12], [16], [19], [20], and [21] were explicitly re-opened and their
  notes updated above.
- The author selected arXiv/institutional-report formatting on 2026-11-10.
  Current arXiv Submission Guidelines, moderation, metadata, and content-type
  pages were opened and recorded in `paper/venue_guide_notes.md`; arXiv has no
  mandatory venue template, so the generic single-column PDF is retained.
- The author confirmed no external funding, no competing interests, and the
  CRediT roles actually performed. AI-tool disclosure was rechecked against
  arXiv's text-to-text generative-AI policy. Methodology, investigation, and
  formal analysis remain pending until those experiments are actually
  performed; the author must personally verify every number and declaration
  before submission. No Zenodo DOI exists.

#!/usr/bin/env python3
"""Render the structured tech_yolo manuscript to Markdown, PDF, and DOCX.

The content lives in paper/manuscript_content.py. This builder keeps the three
deliverables consistent and uses only the checked-in audit artifacts.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
sys.path.insert(0, str(PAPER))

from manuscript_content import BLOCKS, TITLE  # noqa: E402

MD_PATH = PAPER / "tech_yolo_final_research_paper.md"
PDF_PATH = PAPER / "tech_yolo_final_research_paper.pdf"
DOCX_PATH = PAPER / "tech_yolo_final_research_paper.docx"


def md_escape_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown() -> Path:
    out = []
    for kind, value in BLOCKS:
        if kind == "title":
            out.append(f"# {value}\n")
        elif kind == "authors":
            out.append("**Authors and Affiliations**\n")
            out.append("\n".join(line + "  " for line in value.splitlines()) + "\n")
        elif kind == "meta":
            out.append(f"*{value}*\n")
        elif kind == "abstract":
            out.append(f"## Abstract\n\n{value}\n")
        elif kind == "keywords":
            out.append(f"**Keywords / Index Terms:** {value}\n")
        elif kind == "note":
            out.append(f"> **Pre-submission note.** {value}\n")
        elif kind == "h1":
            out.append(f"## {value}\n")
        elif kind == "h2":
            out.append(f"### {value}\n")
        elif kind == "p":
            out.append(f"{value}\n")
        elif kind == "bullets":
            out.extend(f"- {item}" for item in value)
            out.append("")
        elif kind == "equation":
            out.append(f"> `{value}`\n")
        elif kind == "code":
            out.append("```text\n" + value.rstrip() + "\n```\n")
        elif kind == "table":
            out.append(f"**{value['caption']}**\n")
            rows = value["rows"]
            out.append("| " + " | ".join(md_escape_cell(c) for c in rows[0]) + " |")
            out.append("| " + " | ".join("---" for _ in rows[0]) + " |")
            for row in rows[1:]:
                out.append("| " + " | ".join(md_escape_cell(c) for c in row) + " |")
            out.append("")
        elif kind == "figure":
            rel = (ROOT / value["path"]).relative_to(PAPER).as_posix()
            short = ".".join(value["caption"].split(".")[:2])
            out.append(f"![{short}]({rel})\n")
            out.append(f"*{value['caption']}*\n")
        elif kind == "refs":
            for ref in value:
                out.append(f"{ref}\n")
        elif kind == "pagebreak":
            out.append("---\n")
        else:
            raise ValueError(f"Unknown block type: {kind}")
    MD_PATH.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    return MD_PATH


def render_pdf() -> Path:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    from PIL import Image as PILImage

    base = getSampleStyleSheet()
    S = {
        "title": ParagraphStyle("PaperTitle", parent=base["Title"], fontName="Times-Bold", fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12, textColor=colors.HexColor("#111827")),
        "authors": ParagraphStyle("PaperAuthors", fontName="Times-Roman", fontSize=10.5, leading=14, alignment=TA_CENTER, spaceAfter=10),
        "meta": ParagraphStyle("PaperMeta", fontName="Times-Italic", fontSize=9, leading=12, alignment=TA_CENTER, textColor=colors.HexColor("#4B5563"), spaceAfter=12),
        "h1": ParagraphStyle("PaperH1", fontName="Times-Bold", fontSize=13, leading=16, spaceBefore=14, spaceAfter=7, keepWithNext=True, textColor=colors.HexColor("#111827")),
        "h2": ParagraphStyle("PaperH2", fontName="Times-Bold", fontSize=11, leading=14, spaceBefore=10, spaceAfter=5, keepWithNext=True, textColor=colors.HexColor("#1F2937")),
        "body": ParagraphStyle("PaperBody", fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY, spaceAfter=7),
        "abstract": ParagraphStyle("PaperAbstract", fontName="Times-Roman", fontSize=10, leading=14, alignment=TA_JUSTIFY, leftIndent=18, rightIndent=18, spaceAfter=10),
        "keywords": ParagraphStyle("PaperKeywords", fontName="Times-Roman", fontSize=10, leading=13, spaceAfter=8),
        "note": ParagraphStyle("PaperNote", fontName="Times-Italic", fontSize=9, leading=12, leftIndent=14, rightIndent=14, borderPadding=6, backColor=colors.HexColor("#F3F4F6"), spaceAfter=10, textColor=colors.HexColor("#374151")),
        "bullet": ParagraphStyle("PaperBullet", fontName="Times-Roman", fontSize=10, leading=13.5, leftIndent=18, bulletIndent=6, spaceAfter=4, alignment=TA_JUSTIFY),
        "equation": ParagraphStyle("PaperEquation", fontName="Courier", fontSize=9.5, leading=13, alignment=TA_CENTER, spaceBefore=5, spaceAfter=8),
        "code": ParagraphStyle("PaperCode", fontName="Courier", fontSize=7.6, leading=9.5, leftIndent=10, textColor=colors.HexColor("#111827")),
        "caption": ParagraphStyle("PaperCaption", fontName="Times-Bold", fontSize=8.7, leading=11, spaceBefore=8, spaceAfter=4, alignment=TA_LEFT),
        "figcaption": ParagraphStyle("PaperFigCaption", fontName="Times-Italic", fontSize=9, leading=12, alignment=TA_CENTER, spaceBefore=5, spaceAfter=10),
        "cell": ParagraphStyle("PaperCell", fontName="Times-Roman", fontSize=8, leading=10),
        "cellhead": ParagraphStyle("PaperCellHead", fontName="Times-Bold", fontSize=8, leading=10, textColor=colors.white),
        "ref": ParagraphStyle("PaperRef", fontName="Times-Roman", fontSize=9, leading=12, leftIndent=16, firstLineIndent=-16, spaceAfter=5, alignment=TA_JUSTIFY),
    }

    def para(text: str, style: str = "body", bullet: bool = False) -> Paragraph:
        content = html.escape(str(text)).replace("\n", "<br/>")
        if bullet:
            return Paragraph(content, S[style], bulletText="•")
        return Paragraph(content, S[style])

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=0.82 * inch,
        rightMargin=0.82 * inch,
        topMargin=0.78 * inch,
        bottomMargin=0.78 * inch,
        title=TITLE,
        author="Yug G. Lakhani",
        subject="Application / system research paper for tech_yolo",
    )

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(doc_.leftMargin, 0.45 * inch, "TRINEXIS final research paper | tech_yolo")
        canvas.drawRightString(A4[0] - doc_.rightMargin, 0.45 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    story = []
    for kind, value in BLOCKS:
        if kind == "title":
            story.append(para(value, "title"))
        elif kind == "authors":
            story.append(para(value, "authors"))
        elif kind == "meta":
            story.append(para(value, "meta"))
        elif kind == "abstract":
            story.append(Paragraph("<b>Abstract&#8212;</b> " + html.escape(value), S["abstract"]))
        elif kind == "keywords":
            story.append(Paragraph("<b>Keywords / Index Terms&#8212;</b> " + html.escape(value), S["keywords"]))
        elif kind == "note":
            story.append(para("Pre-submission note. " + value, "note"))
        elif kind == "h1":
            story.append(para(value, "h1"))
        elif kind == "h2":
            story.append(para(value, "h2"))
        elif kind == "p":
            story.append(para(value))
        elif kind == "bullets":
            for item in value:
                story.append(para(item, "bullet", bullet=True))
            story.append(Spacer(1, 4))
        elif kind == "equation":
            story.append(para(value, "equation"))
        elif kind == "code":
            story.append(Preformatted(value, S["code"]))
            story.append(Spacer(1, 8))
        elif kind == "table":
            story.append(para(value["caption"], "caption"))
            rows = value["rows"]
            data = []
            for r_idx, row in enumerate(rows):
                style = "cellhead" if r_idx == 0 else "cell"
                data.append([para(cell, style) for cell in row])
            widths = [w * doc.width for w in value["widths"]]
            table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34445A")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FA")]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2CC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(table)
            story.append(Spacer(1, 8))
        elif kind == "figure":
            path = ROOT / value["path"]
            with PILImage.open(path) as im:
                iw, ih = im.size
            width = doc.width
            height = width * ih / iw
            story.append(Image(str(path), width=width, height=height))
            story.append(para(value["caption"], "figcaption"))
        elif kind == "refs":
            for ref in value:
                story.append(para(ref, "ref"))
        elif kind == "pagebreak":
            story.append(PageBreak())
        else:
            raise ValueError(f"Unknown block type: {kind}")

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return PDF_PATH


def render_docx() -> Path:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.9)
    section.bottom_margin = Inches(0.9)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hr = header.add_run("TRINEXIS final research paper")
    hr.font.name = "Times New Roman"
    hr.font.size = Pt(8)
    hr.font.color.rgb = RGBColor(110, 116, 128)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr = footer.add_run("tech_yolo research paper")
    fr.font.name = "Times New Roman"
    fr.font.size = Pt(8)
    fr.font.color.rgb = RGBColor(110, 116, 128)

    def set_cell_shading(cell, fill: str):
        tc_pr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:fill"), fill)
        tc_pr.append(shd)

    def set_repeat_header(row):
        tr_pr = row._tr.get_or_add_trPr()
        tbl_header = OxmlElement("w:tblHeader")
        tbl_header.set(qn("w:val"), "true")
        tr_pr.append(tbl_header)

    def add_p(text: str, *, bold=False, italic=False, size=10.5, align=None, style=None, space_after=6, color=None, mono=False):
        p = doc.add_paragraph(style=style)
        if align is not None:
            p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        run = p.add_run(str(text))
        run.bold = bold
        run.italic = italic
        run.font.name = "Courier New" if mono else "Times New Roman"
        run.font.size = Pt(size)
        if color:
            run.font.color.rgb = RGBColor(*color)
        return p

    for kind, value in BLOCKS:
        if kind == "title":
            add_p(value, bold=True, size=18, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
        elif kind == "authors":
            add_p("Authors and Affiliations", bold=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
            add_p(value, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
        elif kind == "meta":
            add_p(value, italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10, color=(75, 85, 99))
        elif kind == "abstract":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.right_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(9)
            r = p.add_run("Abstract—")
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r2 = p.add_run(value)
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(10.5)
        elif kind == "keywords":
            p = doc.add_paragraph()
            r = p.add_run("Keywords / Index Terms—")
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            r2 = p.add_run(value)
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(10.5)
        elif kind == "note":
            add_p("Pre-submission note. " + value, italic=True, size=9, space_after=9, color=(55, 65, 81))
        elif kind == "h1":
            p = add_p(value, bold=True, size=13, space_after=5)
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.keep_with_next = True
        elif kind == "h2":
            p = add_p(value, bold=True, size=11, space_after=4)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.keep_with_next = True
        elif kind == "p":
            p = add_p(value)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif kind == "bullets":
            for item in value:
                add_p(item, style="List Bullet", size=10.5, space_after=3)
        elif kind == "equation":
            add_p(value, size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, mono=True, space_after=7)
        elif kind == "code":
            for line in value.splitlines():
                p = add_p(line, size=8, mono=True, space_after=0)
                p.paragraph_format.left_indent = Inches(0.2)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
        elif kind == "table":
            add_p(value["caption"], bold=True, size=9, space_after=3)
            rows = value["rows"]
            table = doc.add_table(rows=1, cols=len(rows[0]))
            table.style = "Table Grid"
            table.autofit = False
            usable = 6.7
            widths = [Inches(w * usable) for w in value["widths"]]
            hdr = table.rows[0]
            set_repeat_header(hdr)
            for j, cell_text in enumerate(rows[0]):
                cell = hdr.cells[j]
                cell.width = widths[j]
                cell.text = ""
                p = cell.paragraphs[0]
                r = p.add_run(str(cell_text))
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
                r.font.color.rgb = RGBColor(255, 255, 255)
                set_cell_shading(cell, "34445A")
            for i, row in enumerate(rows[1:], start=1):
                cells = table.add_row().cells
                for j, cell_text in enumerate(row):
                    cell = cells[j]
                    cell.width = widths[j]
                    cell.text = ""
                    p = cell.paragraphs[0]
                    r = p.add_run(str(cell_text))
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(8.5)
                    if i % 2 == 0:
                        set_cell_shading(cell, "F5F7FA")
            doc.add_paragraph().paragraph_format.space_after = Pt(3)
        elif kind == "figure":
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(str(ROOT / value["path"]), width=Inches(6.5))
            p.paragraph_format.space_after = Pt(3)
            add_p(value["caption"], italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=9)
        elif kind == "refs":
            for ref in value:
                p = add_p(ref, size=9.5, space_after=4)
                p.paragraph_format.left_indent = Inches(0.22)
                p.paragraph_format.first_line_indent = Inches(-0.22)
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        elif kind == "pagebreak":
            doc.add_page_break()
        else:
            raise ValueError(f"Unknown block type: {kind}")

    core = doc.core_properties
    core.title = TITLE
    core.subject = "Application / system research paper for tech_yolo"
    core.author = "Yug G. Lakhani"
    core.keywords = "YOLO-World; Flask; open-vocabulary detection; static audit"
    doc.save(DOCX_PATH)
    return DOCX_PATH


def main() -> None:
    paths = [render_markdown()]
    try:
        paths.append(render_pdf())
    except ImportError as exc:
        print(f"PDF generation skipped (missing dependency: {exc})")
    try:
        paths.append(render_docx())
    except ImportError as exc:
        print(f"DOCX generation skipped (missing dependency: {exc})")
    for path in paths:
        print(f"Wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

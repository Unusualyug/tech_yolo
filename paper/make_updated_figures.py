#!/usr/bin/env python3
"""Generate enlarged PNG, SVG, and vector-PDF figures for the updated paper."""
from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "paper" / "artifacts"
CANVAS_W = 1000
CANVAS_H = 560

FIG1 = {
    "name": "fig1_system_architecture_updated",
    "nodes": [
        {"id": "browser", "x": 30, "y": 60, "w": 180, "h": 90, "label": ["Browser", "dashboard"]},
        {"id": "flask", "x": 250, "y": 60, "w": 180, "h": 90, "label": ["Flask control", "REST + session"]},
        {"id": "camera", "x": 470, "y": 60, "w": 180, "h": 90, "label": ["Configurable", "camera"]},
        {"id": "capture", "x": 690, "y": 60, "w": 180, "h": 90, "label": ["OpenCV", "capture"]},
        {"id": "throttle", "x": 250, "y": 210, "w": 180, "h": 90, "label": ["Interval", "throttle"]},
        {"id": "detector", "x": 470, "y": 210, "w": 180, "h": 90, "label": ["YOLO-World", "text prompts"]},
        {"id": "records", "x": 690, "y": 210, "w": 180, "h": 90, "label": ["Detection", "records"]},
        {"id": "optional", "x": 30, "y": 360, "w": 180, "h": 90, "label": ["Optional face", "hook (absent)"], "muted": True},
        {"id": "selector", "x": 250, "y": 360, "w": 180, "h": 90, "label": ["Alert-aware", "selector"]},
        {"id": "speech", "x": 470, "y": 360, "w": 180, "h": 90, "label": ["Language-", "configured TTS"]},
        {"id": "telemetry", "x": 690, "y": 360, "w": 180, "h": 90, "label": ["Telemetry", "heatmap / logs"]},
    ],
    "edges": [
        ("browser", "flask", "solid"),
        ("flask", "camera", "solid"),
        ("camera", "capture", "solid"),
        ("capture", "throttle", "solid"),
        ("throttle", "detector", "solid"),
        ("detector", "records", "solid"),
        ("records", "selector", "solid"),
        ("selector", "speech", "solid"),
        ("records", "telemetry", "solid"),
        ("optional", "selector", "dashed"),
    ],
    "notes": [
        "Solid arrows: implemented runtime paths. Dashed arrow: optional/unavailable face-recognition hook.",
        "No training, benchmark-evaluation, or human-participant path is shown.",
    ],
}

FIG2 = {
    "name": "fig2_implementation_verification",
    "nodes": [
        {"id": "source", "x": 40, "y": 80, "w": 180, "h": 90, "label": ["Frozen source", "snapshot"]},
        {"id": "fixes", "x": 260, "y": 80, "w": 180, "h": 90, "label": ["Repository", "fixes"]},
        {"id": "core", "x": 480, "y": 80, "w": 180, "h": 90, "label": ["trinexis_core", "pure helpers"]},
        {"id": "tests", "x": 700, "y": 80, "w": 180, "h": 90, "label": ["unittest", "suite"]},
        {"id": "audit", "x": 260, "y": 280, "w": 180, "h": 90, "label": ["Seeded alert", "audit"]},
        {"id": "release", "x": 480, "y": 280, "w": 180, "h": 90, "label": ["Tagged", "release"]},
        {"id": "paper", "x": 700, "y": 280, "w": 180, "h": 90, "label": ["Updated", "manuscript"]},
    ],
    "edges": [
        ("source", "fixes", "solid"),
        ("fixes", "core", "solid"),
        ("core", "tests", "solid"),
        ("core", "audit", "solid"),
        ("audit", "release", "solid"),
        ("release", "paper", "solid"),
        ("tests", "paper", "solid"),
    ],
    "notes": [
        "All verification is static or synthetic: no model inference, camera capture, dataset, or human data.",
        "The tagged release and manuscript are reproducible from checked-in scripts and metadata.",
    ],
}


def _node_map(spec):
    return {node["id"]: node for node in spec["nodes"]}


def _center_topleft(node):
    return node["x"] + node["w"] / 2, node["y"] + node["h"] / 2


def _border_topleft(node, toward):
    cx, cy = _center_topleft(node)
    dx, dy = toward[0] - cx, toward[1] - cy
    if dx == 0 and dy == 0:
        return cx, cy
    tx = (node["w"] / 2) / abs(dx) if dx else float("inf")
    ty = (node["h"] / 2) / abs(dy) if dy else float("inf")
    t = min(tx, ty)
    return cx + dx * t, cy + dy * t


def _edge_points_topleft(src, dst):
    sc = _center_topleft(src)
    dc = _center_topleft(dst)
    return _border_topleft(src, dc), _border_topleft(dst, sc)


def _canvas_center(node):
    cx, cy = _center_topleft(node)
    return cx, CANVAS_H - cy


def _canvas_border(node, toward_canvas):
    # Convert the canvas target back to top-left coordinates for border math.
    toward_topleft = (toward_canvas[0], CANVAS_H - toward_canvas[1])
    x, y = _border_topleft(node, toward_topleft)
    return x, CANVAS_H - y


def _canvas_edge_points(src, dst):
    sc = _canvas_center(src)
    dc = _canvas_center(dst)
    return _canvas_border(src, dc), _canvas_border(dst, sc)


def draw_spec_canvas(c, spec):
    """Draw a figure on a reportlab canvas already sized to 1000 x 560."""
    from reportlab.lib import colors

    nodes = _node_map(spec)
    c.saveState()
    c.setLineWidth(1.8)
    for src_id, dst_id, style in spec["edges"]:
        src, dst = nodes[src_id], nodes[dst_id]
        (x1, y1), (x2, y2) = _canvas_edge_points(src, dst)
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setDash(4, 4) if style == "dashed" else c.setDash()
        c.line(x1, y1, x2, y2)
        c.setDash()
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 11
        left = (x2 - size * math.cos(angle - 0.5), y2 - size * math.sin(angle - 0.5))
        right = (x2 - size * math.cos(angle + 0.5), y2 - size * math.sin(angle + 0.5))
        path = c.beginPath()
        path.moveTo(x2, y2)
        path.lineTo(left[0], left[1])
        path.lineTo(right[0], right[1])
        path.close()
        c.setFillColor(colors.HexColor("#334155"))
        c.drawPath(path, stroke=0, fill=1)

    for node in spec["nodes"]:
        x, y, w, h = node["x"], node["y"], node["w"], node["h"]
        cy = CANVAS_H - y - h
        fill = "#F8FAFC" if node.get("muted") else "#EAF2FF"
        stroke = "#94A3B8" if node.get("muted") else "#2563EB"
        c.setFillColor(colors.HexColor(fill))
        c.setStrokeColor(colors.HexColor(stroke))
        c.setLineWidth(1.5)
        c.roundRect(x, cy, w, h, 10, stroke=1, fill=1)
        c.setFillColor(colors.HexColor("#0F172A"))
        c.setFont("Helvetica-Bold", 19)
        lines = node["label"]
        line_h = 24
        start = CANVAS_H - (y + h / 2) + (len(lines) - 1) * line_h / 2
        for i, line in enumerate(lines):
            c.drawCentredString(x + w / 2, start - i * line_h, line)

    c.setFillColor(colors.HexColor("#475569"))
    c.setFont("Helvetica", 14)
    for i, note in enumerate(spec["notes"]):
        c.drawString(30, 70 - i * 22, note)
    c.restoreState()


def write_svg(spec, path: Path) -> None:
    nodes = _node_map(spec)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}">',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,6 L9,3 z" fill="#334155"/></marker></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" fill="white"/>',
    ]
    for src_id, dst_id, style in spec["edges"]:
        (x1, y1), (x2, y2) = _edge_points_topleft(nodes[src_id], nodes[dst_id])
        dash = ' stroke-dasharray="6 5"' if style == "dashed" else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#334155" stroke-width="2" marker-end="url(#arrow)"{dash}/>'
        )
    for node in spec["nodes"]:
        x, y, w, h = node["x"], node["y"], node["w"], node["h"]
        fill = "#F8FAFC" if node.get("muted") else "#EAF2FF"
        stroke = "#94A3B8" if node.get("muted") else "#2563EB"
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        )
        cx, cy = _center_topleft(node)
        lines = node["label"]
        line_h = 24
        start = cy - (len(lines) - 1) * line_h / 2 + 6
        text = "".join(
            f'<tspan x="{cx:.1f}" dy="{0 if i == 0 else line_h}">{escape(line)}</tspan>'
            for i, line in enumerate(lines)
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{start:.1f}" text-anchor="middle" '
            f'font-family="DejaVu Sans, Arial, sans-serif" font-size="19" '
            f'font-weight="bold" fill="#0F172A">{text}</text>'
        )
    for i, note in enumerate(spec["notes"]):
        parts.append(
            f'<text x="30" y="{CANVAS_H - 70 + i * 22}" '
            f'font-family="DejaVu Sans, Arial, sans-serif" font-size="14" '
            f'fill="#475569">{escape(note)}</text>'
        )
    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_png(spec, path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    scale = 1.6
    im = Image.new("RGB", (int(CANVAS_W * scale), int(CANVAS_H * scale)), "white")
    draw = ImageDraw.Draw(im)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    note_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    font = ImageFont.truetype(font_path, int(19 * scale))
    note_font = ImageFont.truetype(note_path, int(14 * scale))
    nodes = _node_map(spec)

    def sc(pt):
        return pt[0] * scale, pt[1] * scale

    for src_id, dst_id, style in spec["edges"]:
        p1, p2 = _edge_points_topleft(nodes[src_id], nodes[dst_id])
        a, b = sc(p1), sc(p2)
        color = "#334155"
        width = max(2, int(2 * scale))
        if style == "dashed":
            dist = math.hypot(b[0] - a[0], b[1] - a[1])
            dash, gap = 8 * scale, 6 * scale
            pos = 0.0
            while pos < dist:
                end = min(pos + dash, dist)
                u1 = pos / dist
                u2 = end / dist
                draw.line(
                    [a[0] + (b[0] - a[0]) * u1, a[1] + (b[1] - a[1]) * u1,
                     a[0] + (b[0] - a[0]) * u2, a[1] + (b[1] - a[1]) * u2],
                    fill=color, width=width,
                )
                pos += dash + gap
        else:
            draw.line([a, b], fill=color, width=width)
        angle = math.atan2(b[1] - a[1], b[0] - a[0])
        size = 11 * scale
        left = (b[0] - size * math.cos(angle - 0.5), b[1] - size * math.sin(angle - 0.5))
        right = (b[0] - size * math.cos(angle + 0.5), b[1] - size * math.sin(angle + 0.5))
        draw.polygon([b, left, right], fill=color)

    for node in spec["nodes"]:
        x, y, w, h = (node[k] * scale for k in ("x", "y", "w", "h"))
        fill = "#F8FAFC" if node.get("muted") else "#EAF2FF"
        stroke = "#94A3B8" if node.get("muted") else "#2563EB"
        draw.rounded_rectangle(
            [x, y, x + w, y + h], radius=10 * scale,
            fill=fill, outline=stroke, width=max(1, int(1.5 * scale)),
        )
        cx, cy = _center_topleft(node)
        draw.text(
            sc((cx, cy)), "\n".join(node["label"]), font=font,
            fill="#0F172A", anchor="mm", align="center", spacing=4 * scale,
        )

    for i, note in enumerate(spec["notes"]):
        draw.text(
            (30 * scale, (CANVAS_H - 70 + i * 22) * scale),
            note, font=note_font, fill="#475569",
        )
    im.save(path, dpi=(300, 300))


def write_vector_pdf(spec, path: Path) -> None:
    from reportlab.pdfgen import canvas

    c = canvas.Canvas(str(path), pagesize=(CANVAS_W, CANVAS_H))
    c.setTitle(spec["name"])
    c.setAuthor("Yug G. Lakhani")
    draw_spec_canvas(c, spec)
    c.showPage()
    c.save()


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    for spec in (FIG1, FIG2):
        stem = ART / spec["name"]
        write_png(spec, stem.with_suffix(".png"))
        write_svg(spec, stem.with_suffix(".svg"))
        write_vector_pdf(spec, stem.with_suffix(".pdf"))
        print(f"Wrote {stem.name}.png, .svg, .pdf")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create high-resolution figures for the tech_yolo system paper using Pillow."""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/artifacts"
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

COLORS = {
    "bg": "#FFFFFF",
    "ink": "#1A2230",
    "muted": "#5A6678",
    "blue": "#DCEBFF",
    "blue_edge": "#3676C9",
    "teal": "#DDF4EF",
    "teal_edge": "#178A76",
    "purple": "#EBE3FF",
    "purple_edge": "#7651C7",
    "orange": "#FFF0D8",
    "orange_edge": "#D58117",
    "gray": "#EDF1F5",
    "gray_edge": "#758394",
    "red": "#FDE8E8",
    "red_edge": "#C74747",
    "arrow": "#34445A",
}


def font(size: int, bold: bool = False, mono: bool = False):
    return ImageFont.truetype(MONO if mono else (BOLD if bold else FONT), size)


def wrap(text: str, fnt, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        cur = ""
        for w in words:
            test = f"{cur} {w}".strip()
            if draw.textlength(test, font=fnt) <= max_width:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def box(draw, rect, title, body, fill, edge, title_size=34, body_size=27, dashed=False):
    x1, y1, x2, y2 = rect
    width = 4
    if dashed:
        # Pillow has no dashed rounded_rectangle; draw a dashed outline manually.
        draw.rounded_rectangle(rect, radius=22, fill=fill, outline=None)
        dash, gap = 18, 12
        # top/bottom
        for x in range(x1 + 20, x2 - 20, dash + gap):
            draw.line((x, y1, min(x + dash, x2 - 20), y1), fill=edge, width=width)
            draw.line((x, y2, min(x + dash, x2 - 20), y2), fill=edge, width=width)
        for y in range(y1 + 20, y2 - 20, dash + gap):
            draw.line((x1, y, x1, min(y + dash, y2 - 20)), fill=edge, width=width)
            draw.line((x2, y, x2, min(y + dash, y2 - 20)), fill=edge, width=width)
    else:
        draw.rounded_rectangle(rect, radius=22, fill=fill, outline=edge, width=width)
    tf = font(title_size, bold=True)
    bf = font(body_size)
    draw.text((x1 + 26, y1 + 20), title, font=tf, fill=COLORS["ink"])
    lines = wrap(body, bf, x2 - x1 - 52, draw)
    y = y1 + 20 + title_size + 14
    for line in lines:
        draw.text((x1 + 26, y), line, font=bf, fill=COLORS["muted"])
        y += body_size + 9


def arrow(draw, start, end, label=None, color=None, width=6, bidirectional=False, dashed=False):
    color = color or COLORS["arrow"]
    x1, y1 = start
    x2, y2 = end
    if dashed:
        import math
        length = ((x2-x1)**2 + (y2-y1)**2) ** 0.5
        dash, gap = 16, 10
        ux, uy = (x2-x1)/length, (y2-y1)/length
        d = 0.0
        while d < length:
            a = min(d + dash, length)
            draw.line((x1+ux*d, y1+uy*d, x1+ux*a, y1+uy*a), fill=color, width=width)
            d += dash + gap
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    # arrowhead
    import math
    angle = math.atan2(y2-y1, x2-x1)
    size = 20
    p1 = (x2 - size*math.cos(angle-0.5), y2 - size*math.sin(angle-0.5))
    p2 = (x2 - size*math.cos(angle+0.5), y2 - size*math.sin(angle+0.5))
    draw.polygon([end, p1, p2], fill=color)
    if bidirectional:
        angle2 = math.atan2(y1-y2, x1-x2)
        p1 = (x1 - size*math.cos(angle2-0.5), y1 - size*math.sin(angle2-0.5))
        p2 = (x1 - size*math.cos(angle2+0.5), y1 - size*math.sin(angle2+0.5))
        draw.polygon([start, p1, p2], fill=color)
    if label:
        lf = font(23, bold=True)
        mx, my = (x1+x2)/2, (y1+y2)/2
        bbox = draw.textbbox((0,0), label, font=lf)
        lw, lh = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.rounded_rectangle((mx-lw/2-12, my-lh/2-8, mx+lw/2+12, my+lh/2+8), radius=8, fill=COLORS["bg"])
        draw.text((mx-lw/2, my-lh/2-2), label, font=lf, fill=COLORS["ink"])


def make_architecture() -> Path:
    W, H = 3000, 1780
    img = Image.new("RGB", (W, H), COLORS["bg"])
    d = ImageDraw.Draw(img)
    d.text((90, 40), "TRINEXIS: verified runtime and control flow", font=font(46, bold=True), fill=COLORS["ink"])
    d.text((90, 102), "Static reconstruction from app23.py, static/script.js and templates/index.html at commit 6a04056", font=font(26), fill=COLORS["muted"])

    # top boxes
    box(d, (90, 190, 790, 430), "Browser client", "index.html | script.js | style.css\nControl widgets, MJPEG view, logs and charts", COLORS["blue"], COLORS["blue_edge"])
    box(d, (1080, 190, 1990, 430), "Flask application: app23.py", "23 HTTP routes; shared global state\nControl, telemetry, camera and health endpoints", COLORS["teal"], COLORS["teal_edge"])
    box(d, (2240, 190, 2910, 430), "Configuration state", "running flag | model | prompt list\nlanguage | thresholds | alerts | cooldown\ncontrols detector, speech and stream", COLORS["gray"], COLORS["gray_edge"])

    arrow(d, (790, 300), (1080, 300), "REST", bidirectional=True)
    arrow(d, (1990, 310), (2240, 310), "updates")

    # middle boxes
    box(d, (90, 650, 690, 890), "USB webcam / OpenCV", "index 1 | CAP_DSHOW\n1280 x 720 requested | buffer size 1", COLORS["blue"], COLORS["blue_edge"])
    box(d, (830, 650, 1470, 890), "Frame generator", "MJPEG multipart/x-mixed-replace\nJPEG quality 85 | capture FPS counter", COLORS["teal"], COLORS["teal_edge"])
    box(d, (1620, 650, 2340, 890), "YOLOv8s-WorldV2", "set_classes(455 unique prompts)\nimgsz 640 | conf 0.15 | IoU 0.5\nmax_det 100 | 1.5 s throttling", COLORS["purple"], COLORS["purple_edge"])
    box(d, (2490, 650, 2910, 890), "Annotation", "Boxes and labels\nDistance heuristic\nHeatmap, logs and stats", COLORS["gray"], COLORS["gray_edge"])

    arrow(d, (690, 770), (830, 770), "frames")
    arrow(d, (1470, 770), (1620, 770), "if running")
    arrow(d, (2340, 770), (2490, 770), "detections")
    arrow(d, (1535, 430), (1150, 650), "start / stop", dashed=True)

    # prompt box above detector
    box(d, (1620, 470, 2340, 610), "Prompt vocabulary", "455 unique texts | /set_custom_vocab", COLORS["purple"], COLORS["purple_edge"], title_size=27, body_size=22)
    arrow(d, (1980, 610), (1980, 650), None, color=COLORS["purple_edge"], width=5)

    # bottom boxes
    box(d, (90, 1110, 690, 1400), "Optional face recognition", "modules.faces.FaceRecognizer\nABSENT from repository\nImport exception disables feature", COLORS["red"], COLORS["red_edge"], dashed=True)
    box(d, (830, 1110, 1630, 1400), "Speech selection and TTS", "Top 2 by confidence | 4.5 s cooldown\nAlert-aware rerank inside shortlist\ngTTS: 72 language codes, 62 templates", COLORS["orange"], COLORS["orange_edge"])
    box(d, (1780, 1110, 2910, 1400), "User-facing outputs", "MJPEG stream | dashboard statistics\nJSON logs | snapshots | detection heatmap\nTemporary MP3 announcements", COLORS["gray"], COLORS["gray_edge"])

    arrow(d, (390, 890), (390, 1110), "optional", color=COLORS["red_edge"], width=5, dashed=True)
    arrow(d, (1980, 890), (1230, 1110), "scene text", color=COLORS["orange_edge"], width=5)
    arrow(d, (2700, 890), (2345, 1110), "annotated frames", color=COLORS["gray_edge"], width=5)
    arrow(d, (1630, 1255), (1780, 1255), "audio", color=COLORS["orange_edge"])
    arrow(d, (690, 1255), (830, 1255), "greeting", color=COLORS["red_edge"], width=5, dashed=True)

    d.text((90, 1490), "Solid arrows: implemented runtime paths. Dashed arrows: configuration or unavailable optional path. No training or benchmark-evaluation path is present.", font=font(26), fill=COLORS["muted"])
    d.line((90, 1545, 2910, 1545), fill="#C9D2DD", width=3)
    d.text((90, 1585), "Note: inference runs at most once per 1.5 s when detection is enabled; the displayed FPS counts captured stream frames, not detector inferences.", font=font(27), fill=COLORS["ink"])
    d.text((90, 1650), "The optional face-recognition import target and materialized model weights are not present in the analyzed source snapshot.", font=font(27), fill=COLORS["ink"])

    path = OUT / "fig1_system_architecture.png"
    img.save(path, "PNG", dpi=(300, 300), optimize=True)
    return path


def make_audit_flow() -> Path:
    W, H = 2800, 850
    img = Image.new("RGB", (W, H), COLORS["bg"])
    d = ImageDraw.Draw(img)
    d.text((80, 40), "Static audit workflow", font=font(46, bold=True), fill=COLORS["ink"])
    d.text((80, 102), "Deterministic, no model execution, no webcam capture, no human-participant data", font=font(26), fill=COLORS["muted"])

    specs = [
        ((70, 250, 610, 590), "1. Freeze snapshot", "commit 6a04056\n22 tracked source files\nSHA-256 of source artifacts", COLORS["blue"], COLORS["blue_edge"]),
        ((760, 250, 1300, 590), "2. Parse source", "Python ast on 3 .py files\nExtract routes and literal constants\nSyntax pass/fail", COLORS["teal"], COLORS["teal_edge"]),
        ((1450, 250, 1990, 590), "3. Cross-check", "16 frontend endpoint literals\napp23.py vs app.py coverage\nLFS pointers and missing files", COLORS["purple"], COLORS["purple_edge"]),
        ((2140, 250, 2730, 590), "4. Emit evidence", "repository_audit.json\nCounts, routes, checks\nManuscript tables", COLORS["gray"], COLORS["gray_edge"]),
    ]
    for spec in specs:
        rect, title, body, fill, edge = spec
        box(d, rect, title, body, fill, edge, title_size=32, body_size=26)
    arrow(d, (610, 420), (760, 420), width=7)
    arrow(d, (1300, 420), (1450, 420), width=7)
    arrow(d, (1990, 420), (2140, 420), width=7)
    d.text((80, 690), "Output: exact counts for the frozen snapshot. No accuracy, mean average precision, latency, confidence interval, or statistical significance is inferred.", font=font(27), fill=COLORS["ink"])
    path = OUT / "fig2_static_audit_workflow.png"
    img.save(path, "PNG", dpi=(300, 300), optimize=True)
    return path


if __name__ == "__main__":
    for p in (make_architecture(), make_audit_flow()):
        print(p.relative_to(ROOT))

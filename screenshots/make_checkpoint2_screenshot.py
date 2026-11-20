"""
Generate screenshots/checkpoint2_loan_picker.png
Renders a faithful mockup of the MudraMitra Checkpoint-2 UI at ₹25 lakh,
showing: Tarun Plus card, Stand-Up India card, and the conflict note.
Run: python screenshots/make_checkpoint2_screenshot.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

OUT = Path(__file__).resolve().parent / "checkpoint2_loan_picker.png"
W = 980
FONT_DIR = Path("C:/Windows/Fonts")


def ttf(name, size):
    p = FONT_DIR / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


FONT_TITLE  = ttf("calibrib.ttf",  22)
FONT_BODY   = ttf("calibri.ttf",   16)
FONT_SMALL  = ttf("calibri.ttf",   13)
FONT_BADGE  = ttf("calibrib.ttf",  17)
FONT_BRAND  = ttf("calibrib.ttf",  26)
FONT_SUB    = ttf("calibri.ttf",   13)
FONT_H2     = ttf("calibrib.ttf",  19)
FONT_TABLE  = ttf("calibri.ttf",   14)
FONT_TABLEH = ttf("calibrib.ttf",  14)

BG        = (11,  18,  32)
PANEL     = (21,  31,  48)
BORDER    = (38,  52,  73)
TEXT_MAIN = (232, 238, 248)
TEXT_DIM  = (145, 164, 189)
BRAND_BLU = (57, 137, 213)
GREEN     = (30, 142,  62)
AMBER     = (249, 171,   0)
ORANGE    = (227, 116,   0)
PURPLE    = (147,  52, 230)
CONFLICT  = (245, 201, 122)
CONF_BG   = (31,  21,  16)
CONF_BDR  = (122, 60,   0)
SLIDER_BG = (38,  52,  73)
SLIDER_FG = (57, 137, 213)
WHITE     = (255, 255, 255)


def rounded_rect(draw, xy, radius, fill, outline=None, outline_width=2):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                            fill=fill, outline=outline, width=outline_width)


def wrap_text(draw, text, font, max_width, fill, x, y, line_height=22):
    """Simple word-wrap."""
    words = text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            line = test
        else:
            if line:
                draw.text((x, y), line, font=font, fill=fill)
                y += line_height
            line = word
    if line:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------

H = 1050
img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)


# ---------------------------------------------------------------------------
# Brand header
# ---------------------------------------------------------------------------

icon_x, icon_y = 32, 24
rounded_rect(draw, (icon_x, icon_y, icon_x+46, icon_y+46),
             radius=12, fill=(36, 90, 145))
draw.text((icon_x + 11, icon_y + 8), "💰", font=ttf("seguiemj.ttf", 22) if
          (FONT_DIR / "seguiemj.ttf").exists() else FONT_TITLE,
          fill=WHITE)

draw.text((icon_x + 56, icon_y + 2),  "MudraMitra",         font=FONT_BRAND, fill=TEXT_MAIN)
draw.text((icon_x + 57, icon_y + 32), "AI Loan Assistant · Checkpoint 2",
          font=FONT_SUB, fill=TEXT_DIM)
draw.line([(32, 85), (W - 32, 85)], fill=BORDER, width=1)


# ---------------------------------------------------------------------------
# Loan picker panel
# ---------------------------------------------------------------------------

PX, PY = 32, 102
PW = W - 64

rounded_rect(draw, (PX, PY, PX + PW, PY + 850),
             radius=16, fill=PANEL, outline=BORDER)

draw.text((PX + 18, PY + 14),
          "🎚️  Loan Amount Picker — find your scheme",
          font=FONT_TITLE, fill=TEXT_MAIN)

draw.text((PX + 18, PY + 44),
          "Drag the slider to your required loan amount and the matching scheme highlights automatically.",
          font=FONT_SMALL, fill=TEXT_DIM)

# --- Slider bar ---
SX, SY = PX + 18, PY + 76
SW = PW - 36
SH = 8
AMOUNT = 25_00_000
MAX_AMOUNT = 1_00_00_000
ratio = AMOUNT / MAX_AMOUNT

rounded_rect(draw, (SX, SY, SX + SW, SY + SH),
             radius=4, fill=SLIDER_BG)
fill_w = int(SW * ratio)
rounded_rect(draw, (SX, SY, SX + fill_w, SY + SH),
             radius=4, fill=SLIDER_FG)
# thumb
thumb_x = SX + fill_w
draw.ellipse((thumb_x - 10, SY - 6, thumb_x + 10, SY + SH + 6),
             fill=SLIDER_FG, outline=WHITE, width=2)

# selected label
draw.text((PX + 18, SY + 20), "Selected:  ₹25.0 L   ·   ₹25,00,000",
          font=FONT_BADGE, fill=TEXT_MAIN)


# --- Tarun Plus card ---
CY = PY + 118
CX = PX + 18
CW = PW - 36

rounded_rect(draw, (CX, CY, CX + CW, CY + 68),
             radius=14,
             fill=(227 // 8 + 20, 116 // 8 + 20, 0 // 8 + 20),
             outline=ORANGE, outline_width=2)
draw.text((CX + 14, CY + 10), "🏆",   font=FONT_TITLE, fill=ORANGE)
draw.text((CX + 50, CY + 10), "PMMY — Tarun Plus",
          font=FONT_BADGE, fill=ORANGE)
draw.text((CX + 50, CY + 36),
          "₹10 lakh – ₹20 lakh — only for borrowers who have repaid a Tarun loan.",
          font=FONT_SMALL, fill=TEXT_DIM)


# --- Stand-Up India card ---
CY2 = CY + 82
rounded_rect(draw, (CX, CY2, CX + CW, CY2 + 68),
             radius=14,
             fill=(147 // 8 + 10, 52 // 8 + 10, 230 // 8 + 20),
             outline=PURPLE, outline_width=2)
draw.text((CX + 14, CY2 + 10), "🏛️",  font=FONT_TITLE, fill=PURPLE)
draw.text((CX + 50, CY2 + 10), "Stand-Up India also applies",
          font=FONT_BADGE, fill=PURPLE)
draw.text((CX + 50, CY2 + 36),
          "₹10 lakh – ₹1 crore — for SC/ST & women entrepreneurs (greenfield).",
          font=FONT_SMALL, fill=TEXT_DIM)


# --- Conflict box ---
CY3 = CY2 + 82
rounded_rect(draw, (CX, CY3, CX + CW, CY3 + 108),
             radius=12, fill=CONF_BG, outline=CONF_BDR, outline_width=1)

conflict_lines = [
    "⚠️  Document Disagreement",
    "An older version of the Stand-Up India FAQ states the margin money requirement",
    "was up to 25% of project cost.  Following Union Budget 2021-22, this was",
    "reduced to up to 15% (with at least 10% own contribution).",
    "If your lender quotes 25%, ask them to apply the updated 2021-22 scheme terms.",
]
cy = CY3 + 12
draw.text((CX + 14, cy), conflict_lines[0], font=FONT_BADGE, fill=CONFLICT)
cy += 24
for line in conflict_lines[1:]:
    draw.text((CX + 14, cy), line, font=FONT_SMALL, fill=CONFLICT)
    cy += 18


# --- Quick reference table ---
TY = CY3 + 122
draw.text((CX, TY), "Quick reference — all scheme bands:", font=FONT_H2, fill=TEXT_MAIN)
TY += 26

BANDS = [
    ("🌱 Shishu",         "₹0 – ₹50K",          "PMMY / MUDRA",    None),
    ("🌿 Kishor",         "₹50K – ₹5L",          "PMMY / MUDRA",    None),
    ("🌳 Tarun",          "₹5L – ₹10L",          "PMMY / MUDRA",    None),
    ("🏆 Tarun Plus",     "₹10L – ₹20L",         "PMMY / MUDRA",    ORANGE),
    ("🏛️ Stand-Up India", "₹10L – ₹1Cr",         "SC/ST · Women",   PURPLE),
]

COL_W = [220, 180, 180]
ROW_H = 28

# header
hx = CX
rounded_rect(draw, (CX, TY, CX + CW, TY + ROW_H),
             radius=0, fill=(24, 40, 64))
for i, hdr in enumerate(["Scheme", "Amount Range", "Target"]):
    draw.text((hx + 8, TY + 7), hdr, font=FONT_TABLEH, fill=(169, 200, 240))
    hx += COL_W[i]

TY += ROW_H

for name, amts, target, highlight in BANDS:
    active = highlight is not None
    row_fill = (28, 42, 58) if active else (17, 26, 40)
    rounded_rect(draw, (CX, TY, CX + CW, TY + ROW_H),
                 radius=0, fill=row_fill)
    rx = CX
    for i, cell in enumerate([name, amts, target]):
        col_fill = highlight if (active and highlight) else TEXT_MAIN
        draw.text((rx + 8, TY + 7), cell, font=FONT_TABLE, fill=col_fill)
        rx += COL_W[i]
    TY += ROW_H


# ---------------------------------------------------------------------------
# Mode bar at top-right
# ---------------------------------------------------------------------------

MODE_X = W - 260
MODE_Y = 95
rounded_rect(draw, (MODE_X, MODE_Y, MODE_X + 220, MODE_Y + 30),
             radius=8, fill=(20, 30, 46), outline=BORDER)
draw.text((MODE_X + 10, MODE_Y + 7),
          "Mode:  💬 RAG (fast, cited)",
          font=FONT_SMALL, fill=TEXT_DIM)

# ---------------------------------------------------------------------------
# Footer note
# ---------------------------------------------------------------------------

draw.text((32, H - 26),
          "MudraMitra · Checkpoint 2  |  Sources: PMMY FAQ · Stand-Up India FAQ",
          font=FONT_SMALL, fill=TEXT_DIM)


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

img.save(str(OUT), format="PNG")
print(f"Saved: {OUT}")

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import qrcode

# Color definitions matching the website palette
COLOR_BG = (245, 245, 245)       # #f5f5f5
COLOR_INK = (26, 26, 26)         # #1a1a1a
COLOR_SUB = (58, 58, 58)         # #3a3a3a
COLOR_MUTED = (107, 107, 107)    # #6b6b6b
COLOR_FAINT = (140, 140, 140)    # #8c8c8c
COLOR_LINE = (217, 217, 217)     # #d9d9d9
COLOR_CARD = (255, 255, 255)     # #ffffff
COLOR_ACCENT = (31, 58, 107)     # #1f3a6b

FONT_FILE = "Quicksand.ttf"

def get_font(size, weight=700):
    f = ImageFont.truetype(FONT_FILE, size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f

# 1. Prepare flattened S1b image (puppet waving)
print("Processing S1b base image...")
LO, HI, TARGET = 175, 226, 245
lut = np.array([v if v < LO else (LO + (v - LO) * (TARGET - LO) / (HI - LO) if v < HI else TARGET) for v in range(256)]).round().astype(np.uint8)

s1b_raw = Image.open("keyframes/S1b.png").convert("RGB")
s1b_flat = Image.fromarray(lut[np.array(s1b_raw)])

# Generate crisp QR code for https://ioannisbekas.github.io/
def make_qr_badge(box_size=14, border=2, target_size=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border
    )
    qr.add_data("https://ioannisbekas.github.io/")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color=COLOR_INK, back_color=COLOR_CARD).convert("RGB")
    if target_size:
        qr_img = qr_img.resize(target_size, Image.Resampling.NEAREST)
    return qr_img

output_dir = "card_output"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# DESIGN 1: Widescreen Hero Card (2752 x 1536 px - Matches Screenshot 1)
# -------------------------------------------------------------
print("Rendering Design 1: Widescreen Hero Edition (2752 x 1536)...")
hero_card = s1b_flat.copy()
draw = ImageDraw.Draw(hero_card)

# Top wordmark "ioannis."
draw.text((100, 75), "ioannis.", fill=COLOR_INK, font=get_font(48, 700))

# Hero headline
draw.text((1520, 360), "Hi,", fill=COLOR_INK, font=get_font(44, 600))
draw.text((1520, 430), "From raw chaos", fill=COLOR_INK, font=get_font(84, 700))
draw.text((1520, 525), "to decision-grade AI.", fill=COLOR_INK, font=get_font(84, 700))

# Subtitle paragraph
sub_lines = [
    "Production LLM pipelines, predictive systems and analytics",
    "that hold up under scrutiny, for research institutes and",
    "global organisations."
]
y_sub = 660
for line in sub_lines:
    draw.text((1520, y_sub), line, fill=COLOR_SUB, font=get_font(34, 500))
    y_sub += 48

# Name and title
draw.text((1520, 850), "Ioannis Bekas", fill=COLOR_INK, font=get_font(58, 700))
draw.text((1520, 925), "Applied AI Engineer & Quantitative Data Scientist", fill=COLOR_MUTED, font=get_font(32, 600))
name_w = draw.textlength("Applied AI Engineer & Quantitative Data Scientist ", font=get_font(32, 600))
draw.text((1520 + int(name_w), 925), "(7 years)", fill=COLOR_FAINT, font=get_font(30, 500))

# Tech Stack line
draw.text((1520, 975), "Python · PyTorch · LLMs & RAG · SQL · Databricks · Power BI · AWS · Azure · GCP", fill=COLOR_FAINT, font=get_font(25, 600))

# Embed QR code badge at bottom right
qr_w = 340
qr_img = make_qr_badge(box_size=10, border=1).resize((qr_w, qr_w), Image.Resampling.NEAREST)

# Draw a clean rounded card container for the QR code and contact info
card_x, card_y, card_w, card_h = 1520, 1050, 1100, 390
draw.rounded_rectangle([card_x, card_y, card_x + card_w, card_y + card_h], radius=24, fill=COLOR_CARD, outline=COLOR_LINE, width=2)

# Paste QR code
hero_card.paste(qr_img, (card_x + 30, card_y + 25))

# Text next to QR code
q_tx = card_x + 405
draw.text((q_tx, card_y + 40), "EXPLORE PORTFOLIO", fill=COLOR_ACCENT, font=get_font(26, 700))
draw.text((q_tx, card_y + 80), "Scan for live interactive mascot,", fill=COLOR_INK, font=get_font(30, 600))
draw.text((q_tx, card_y + 120), "case studies & code repositories", fill=COLOR_INK, font=get_font(30, 600))

draw.line([(q_tx, card_y + 180), (card_x + card_w - 40, card_y + 180)], fill=COLOR_LINE, width=1)

draw.text((q_tx, card_y + 205), "Website:", fill=COLOR_MUTED, font=get_font(24, 600))
draw.text((q_tx + 120, card_y + 205), "ioannisbekas.github.io", fill=COLOR_INK, font=get_font(26, 700))

draw.text((q_tx, card_y + 250), "Email:", fill=COLOR_MUTED, font=get_font(24, 600))
draw.text((q_tx + 120, card_y + 250), "bekas.ioannis.1996@gmail.com", fill=COLOR_INK, font=get_font(26, 600))

draw.text((q_tx, card_y + 295), "LinkedIn:", fill=COLOR_MUTED, font=get_font(24, 600))
draw.text((q_tx + 120, card_y + 295), "linkedin.com/in/ioannisbekas", fill=COLOR_INK, font=get_font(26, 600))

hero_path = os.path.join(output_dir, "card_hero_widescreen.png")
hero_card.save(hero_path, dpi=(300, 300))
print(f"Saved: {hero_path}")

# -------------------------------------------------------------
# DESIGN 2: Standard US Business Card (3.5\" x 2\" @ 600 DPI = 2100 x 1200 px)
# -------------------------------------------------------------
print("Rendering Design 2: Standard Business Card Front (2100 x 1200 @ 600 DPI)...")
card_front = Image.new("RGB", (2100, 1200), COLOR_BG)

# Crop puppet from s1b_flat and scale to fit height 1200
# In s1b_flat, puppet is in x=[0, 1250], y=[0, 1536]
# Let's crop x=[0, 1280], y=[0, 1536]
puppet_crop = s1b_flat.crop((0, 0, 1280, 1536))
# Scale so height is 1200 px (ratio 1200 / 1536 = 0.78125)
target_w = int(1280 * (1200 / 1536))
puppet_scaled = puppet_crop.resize((target_w, 1200), Image.Resampling.LANCZOS)
card_front.paste(puppet_scaled, (0, 0))

draw = ImageDraw.Draw(card_front)

# Brand mark
draw.text((950, 75), "ioannis.", fill=COLOR_INK, font=get_font(46, 700))

# Headline
draw.text((950, 160), "From raw chaos", fill=COLOR_INK, font=get_font(64, 700))
draw.text((950, 235), "to decision-grade AI.", fill=COLOR_INK, font=get_font(64, 700))

# Name and title
draw.text((950, 355), "Ioannis Bekas", fill=COLOR_INK, font=get_font(52, 700))
draw.text((950, 420), "Applied AI Engineer & Quantitative Data Scientist", fill=COLOR_MUTED, font=get_font(28, 600))

# Core Stack pill line
draw.text((950, 465), "Python · PyTorch · LLMs & RAG · Databricks · Power BI · Cloud", fill=COLOR_FAINT, font=get_font(23, 600))

# QR Code Badge container on the right side
qr_w = 480
qr_badge_w = 1050
qr_badge_h = 560
bx, by = 950, 530

draw.rounded_rectangle([bx, by, bx + qr_badge_w, by + qr_badge_h], radius=22, fill=COLOR_CARD, outline=COLOR_LINE, width=2)

# QR Code inside badge
qr_size = 460
qr_clean = make_qr_badge(box_size=14, border=1).resize((qr_size, qr_size), Image.Resampling.NEAREST)
card_front.paste(qr_clean, (bx + 45, by + 50))

# Details inside QR badge
qtx = bx + 550
draw.text((qtx, by + 65), "PORTFOLIO & CODE", fill=COLOR_ACCENT, font=get_font(24, 700))
draw.text((qtx, by + 105), "Scan to see live puppet,", fill=COLOR_INK, font=get_font(28, 600))
draw.text((qtx, by + 145), "models & UN case studies", fill=COLOR_INK, font=get_font(28, 600))

draw.line([(qtx, by + 215), (bx + qr_badge_w - 45, by + 215)], fill=COLOR_LINE, width=1)

draw.text((qtx, by + 245), "Web", fill=COLOR_MUTED, font=get_font(21, 600))
draw.text((qtx + 75, by + 245), "ioannisbekas.github.io", fill=COLOR_INK, font=get_font(25, 700))

draw.text((qtx, by + 300), "Email", fill=COLOR_MUTED, font=get_font(21, 600))
draw.text((qtx + 75, by + 300), "bekas.ioannis.1996@gmail.com", fill=COLOR_INK, font=get_font(24, 600))

draw.text((qtx, by + 355), "In", fill=COLOR_MUTED, font=get_font(21, 600))
draw.text((qtx + 75, by + 355), "linkedin.com/in/ioannisbekas", fill=COLOR_INK, font=get_font(24, 600))

draw.text((qtx, by + 410), "Loc", fill=COLOR_MUTED, font=get_font(21, 600))
draw.text((qtx + 75, by + 410), "Zurich · Geneva · Remote Worldwide", fill=COLOR_SUB, font=get_font(23, 500))

front_path = os.path.join(output_dir, "card_standard_front.png")
card_front.save(front_path, dpi=(600, 600))
print(f"Saved: {front_path}")

# -------------------------------------------------------------
# DESIGN 3: Premium Double-Sided Set (Front & Back @ 600 DPI)
# -------------------------------------------------------------
print("Rendering Design 3: Minimalist Front + Dedicated QR Back...")
# Side A: Hero Front
front_a = Image.new("RGB", (2100, 1200), COLOR_BG)
# Put puppet slightly larger on left
puppet_crop_a = s1b_flat.crop((0, 0, 1300, 1536))
p_scale_a = puppet_crop_a.resize((int(1300 * (1200 / 1536)), 1200), Image.Resampling.LANCZOS)
front_a.paste(p_scale_a, (40, 0))

draw_fa = ImageDraw.Draw(front_a)
draw_fa.text((1050, 180), "ioannis.", fill=COLOR_INK, font=get_font(60, 700))
draw_fa.text((1050, 310), "From raw chaos", fill=COLOR_INK, font=get_font(76, 700))
draw_fa.text((1050, 400), "to decision-grade AI.", fill=COLOR_INK, font=get_font(76, 700))

draw_fa.text((1050, 560), "Production LLM pipelines, predictive systems", fill=COLOR_SUB, font=get_font(34, 500))
draw_fa.text((1050, 610), "and analytics that hold up under scrutiny.", fill=COLOR_SUB, font=get_font(34, 500))

draw_fa.line([(1050, 720), (1980, 720)], fill=COLOR_LINE, width=2)

draw_fa.text((1050, 760), "Ioannis Bekas", fill=COLOR_INK, font=get_font(64, 700))
draw_fa.text((1050, 845), "Applied AI Engineer & Quantitative Data Scientist", fill=COLOR_MUTED, font=get_font(32, 600))
draw_fa.text((1050, 905), "Python · PyTorch · LLMs · SQL · Databricks · Power BI · Cloud", fill=COLOR_FAINT, font=get_font(25, 600))

front_a_path = os.path.join(output_dir, "card_doublesided_front.png")
front_a.save(front_a_path, dpi=(600, 600))
print(f"Saved: {front_a_path}")

# Side B: Networking Back with Large QR Code
back_b = Image.new("RGB", (2100, 1200), COLOR_BG)
draw_b = ImageDraw.Draw(back_b)

# Center-left white card for QR Code
b_qr_card_x, b_qr_card_y = 140, 160
b_qr_card_w, b_qr_card_h = 760, 880
draw_b.rounded_rectangle([b_qr_card_x, b_qr_card_y, b_qr_card_x + b_qr_card_w, b_qr_card_y + b_qr_card_h], radius=28, fill=COLOR_CARD, outline=COLOR_LINE, width=2)

qr_large = make_qr_badge(box_size=18, border=1).resize((620, 620), Image.Resampling.NEAREST)
back_b.paste(qr_large, (b_qr_card_x + 70, b_qr_card_y + 70))

draw_b.text((b_qr_card_x + 190, b_qr_card_y + 730), "SCAN TO EXPLORE", fill=COLOR_ACCENT, font=get_font(26, 700))
draw_b.text((b_qr_card_x + 160, b_qr_card_y + 780), "ioannisbekas.github.io", fill=COLOR_INK, font=get_font(32, 700))

# Right side: Full Contact and Credentials
rx = 1020
draw_b.text((rx, 180), "ioannis.", fill=COLOR_INK, font=get_font(56, 700))
draw_b.text((rx, 260), "Ioannis Bekas", fill=COLOR_INK, font=get_font(60, 700))
draw_b.text((rx, 335), "Applied AI Engineer & Quantitative Data Scientist", fill=COLOR_MUTED, font=get_font(30, 600))

draw_b.line([(rx, 415), (1960, 415)], fill=COLOR_LINE, width=2)

items = [
    ("Portfolio", "ioannisbekas.github.io"),
    ("Email", "bekas.ioannis.1996@gmail.com"),
    ("LinkedIn", "linkedin.com/in/ioannisbekas"),
    ("GitHub", "github.com/IoannisBekas"),
    ("Focus", "UN Early Warning AI · Climate Evidence · LLMs"),
    ("Location", "Greece · Switzerland · Remote Worldwide")
]

iy = 450
for label, val in items:
    draw_b.text((rx, iy), label, fill=COLOR_MUTED, font=get_font(25, 600))
    draw_b.text((rx + 160, iy), val, fill=COLOR_INK, font=get_font(27, 600 if label != "Portfolio" else 700))
    iy += 68

back_b_path = os.path.join(output_dir, "card_doublesided_back.png")
back_b.save(back_b_path, dpi=(600, 600))
print(f"Saved: {back_b_path}")

print("All card designs rendered successfully!")

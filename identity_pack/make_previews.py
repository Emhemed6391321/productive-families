#!/usr/bin/env python3
"""Comparison sheets + safe-zone guide + identity board (previews only; the deliverables are the single files)."""
from PIL import Image, ImageDraw
from pack_lib import *

LBL = lambda s: font(600, s)

def label(d, xy, text, size=26, fill=(60, 60, 60)):
    d.text(xy, text, font=LBL(size), fill=fill, anchor="la")

def templates_preview():
    tw, th, g = 540, 720, 36
    sheet = Image.new("RGB", (3 * tw + 4 * g, 2 * (th + 60) + g), (232, 228, 220))
    d = ImageDraw.Draw(sheet)
    for i in range(6):
        im = Image.open(f"Templates/Template-{i+1:02d}.png").resize((tw, th), Image.LANCZOS)
        x, y = g + (i % 3) * (tw + g), g + (i // 3) * (th + 60)
        sheet.paste(im, (x, y))
        label(d, (x, y + th + 12), f"Template-{i+1:02d}")
    sheet.save("Previews/Templates-Preview.png")

def covers_preview():
    cw, ch, g = 820, 462, 36
    sheet = Image.new("RGB", (2 * cw + 3 * g, 3 * (ch + 60) + g), (232, 228, 220))
    d = ImageDraw.Draw(sheet)
    for i in range(5):
        im = Image.open(f"Covers/Cover-{i+1:02d}.png").resize((cw, ch), Image.LANCZOS)
        x, y = g + (i % 2) * (cw + g), g + (i // 2) * (ch + 60)
        sheet.paste(im, (x, y))
        label(d, (x, y + ch + 12), f"Cover-{i+1:02d}")
    sheet.save("Previews/Covers-Preview.png")

def safe_guide():
    im = Image.open("Covers/Cover-05.png").convert("RGBA")
    W, H = im.size
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle((0, 0, W, 150), fill=(0, 0, 0, 120)); d.rectangle((0, 774, W, H), fill=(0, 0, 0, 120))
    d.rectangle((0, 150, W, 774), outline=(255, 60, 60, 255), width=6)
    d.rectangle((0, 0, W - 1, H - 1), outline=(60, 140, 255, 255), width=6)
    d.ellipse((60, 560, 360, 860), outline=(255, 200, 0, 255), width=5)
    out = Image.alpha_composite(im, ov).convert("RGB")
    dd = ImageDraw.Draw(out)
    dd.text((24, 24), "mobile 640x360 = full cover (blue)", font=LBL(34), fill=(60, 140, 255))
    dd.text((24, 160), "desktop 820x312 = centre band only (red)", font=LBL(34), fill=(255, 90, 90))
    dd.text((70, 700), "profile photo area", font=LBL(30), fill=(255, 200, 0))
    out.resize((W // 2, H // 2), Image.LANCZOS).save("Previews/Cover-Safe-Zone-Guide.png")

def board():
    W, H = 1600, 1270
    img = Image.new("RGB", (W, H), (246, 240, 229))
    d = ImageDraw.Draw(img)
    label(d, (60, 40), "Visual identity - extracted from the reference designs", 40, GREEN)
    sw = [("Authority teal", TEAL), ("Title green", GREEN), ("Deep green", GREEN_DK), ("Gold", GOLD), ("Bronze panel", BRONZE),
          ("Gold light (dark grounds)", GOLD_LT), ("Paper light", PAPER_A), ("Paper dark", PAPER_B)]
    for i, (n, c) in enumerate(sw):
        x, y = 60 + (i % 4) * 380, 130 + (i // 4) * 250
        d.rounded_rectangle((x, y, x + 340, y + 150), 24, fill=c, outline=(200, 190, 170), width=2)
        label(d, (x, y + 160), n, 26)
        label(d, (x, y + 194), "#%02X%02X%02X" % c, 24, (110, 100, 80))
    label(d, (60, 640), "Font: IBM Plex Sans Arabic  (400 / 500 / 600 / 700)", 30, GREEN)
    for i, w in enumerate((400, 500, 600, 700)):
        d.text((1540, 710 + i * 78), "تنسيقية طرابلس ب - %d" % w, font=font(w, 56), fill=GREEN, anchor="ra", direction="rtl", language="ar")
    label(d, (60, 700), "Title 96-128 px / body 44-58 px", 24, (110, 100, 80))
    label(d, (60, 740), "Highlight word = gold (#AF893B)", 24, (110, 100, 80))
    label(d, (60, 780), "Divider = gold line + diamond", 24, (110, 100, 80))
    diamond_divider(img, 330, 860, half=200)
    o = asset("ornament"); paste(img, o.resize((40, round(40 * o.size[1] / o.size[0]))), 60, 890)
    paste(img, fit_w(asset("rakb_gold"), 260), 60, 1010 - 50)
    paste(img, fit_w(asset("rakb_green"), 160), 360, 1000)
    paste(img, fit_w(asset("hajj_green"), 120), 560, 1000)
    gb = Image.new("RGB", (160, 160), TEAL); paste(gb, fit_w(asset("hajj_white"), 120), 20, 20); img.paste(gb, (720, 990))
    img.save("Previews/Identity-Board.png")

if __name__ == "__main__":
    templates_preview(); covers_preview(); safe_guide(); board(); print("previews ok")

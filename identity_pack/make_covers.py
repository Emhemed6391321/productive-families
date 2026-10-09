#!/usr/bin/env python3
"""Five Facebook cover proposals for "تنسيقية طرابلس ب" -> Covers/Cover-0N.png

Canvas 1640x924 (= 2 x 820x462, 16:9).  Facebook shows the whole 16:9 on mobile (640x360) and the
centre 820x312 band on desktop, so every key element sits inside the centre 1640x624 band
(y 150..774).  Only the real name and the two original logos are used - no dates, numbers or slogans."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pack_lib import *

CW, CH = 1640, 924
BAND = (150, 774)                       # desktop-safe vertical band
NAME_W = lambda size: font(700, size).getlength("تنسيقية طرابلس ب", direction="rtl", language="ar")

def row(img, cy, size, col, left_logo, right_logo, gap=70, lh=250, rh=215):
    """name in the centre, Rakb al-Abrar logo on the left, authority logo on the right (as in footers)."""
    tw = NAME_W(size)
    L = asset(left_logo[0]); Rr = asset(right_logo[0])
    lw = round(L.size[0] * lh / L.size[1]); rw = round(Rr.size[0] * rh / Rr.size[1])
    total = lw + gap + tw + gap + rw
    x0 = (CW - total) / 2
    logo(img, left_logo[0], x0, cy - lh / 2, h=lh, rgb=left_logo[1])
    name_text(img, x0 + lw + gap + tw / 2, cy, size, col)
    logo(img, right_logo[0], x0 + lw + gap + tw + gap, cy - rh / 2, h=rh, rgb=right_logo[1])
    return x0, total

# ------------------------------------------------------------------ 1 official / elegant
def c1():
    img = paper(CW, CH)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(CH, 0, CH, .35, .9), R=130)
    frame(img, 30, GOLD, 4, 11, corner=0.8)
    d = ImageDraw.Draw(img)
    cy = 440
    x0, total = row(img, cy, 100, GREEN, ("rakb_gold", None), ("hajj_green", None), gap=90, lh=215, rh=185)
    d = ImageDraw.Draw(img)
    tw = NAME_W(100)
    for x in (CW / 2 - tw / 2 - 45, CW / 2 + tw / 2 + 45):             # slim gold stems between name and logos
        d.line((x, cy - 70, x, cy + 70), fill=GOLD, width=3)
    diamond_divider(img, CW / 2, cy + 110, half=300, gap=40, size=16)
    return img

# ------------------------------------------------------------------ 2 majestic / Haram skyline
def c2():
    img = gradient(CW, CH, [(0, (0, 92, 78)), (.6, (2, 52, 38)), (1, GREEN_DK)], 90)
    g, m = glow(CW, CH, CW / 2, 330, 900, 380, (14, 128, 108), .55)
    img = over(img, (14, 128, 108), m)
    img = add_lattice(img, GOLD_LT, 30, ramp=vramp(CH, 0, CH * .6, 1, .2), R=130)
    sk = sky_layer(CW, 0.95, tint=GOLD_LT, blur=1.4)
    paste(img, sk, 0, CH - sk.size[1] + 120)
    d = ImageDraw.Draw(img)
    star8(d, CW / 2, 215, 52, outline=GOLD, width=3)
    star8(d, CW / 2, 215, 30, outline=GOLD, width=2, rot=-math.pi / 2 + math.pi / 8)
    d.ellipse((CW / 2 - 6, 209, CW / 2 + 6, 221), fill=GOLD)
    name_text(img, CW / 2, 372, 112, GOLD_LT)
    diamond_divider(img, CW / 2, 452, half=300, gap=36, col=GOLD)
    logo(img, "rakb_gold", 130, 262, h=210)
    logo(img, "hajj_white", CW - 130 - 190, 268, h=190)
    return img

# ------------------------------------------------------------------ 3 gradient + original ornaments
def c3():
    img = gradient(CW, CH, [(0, (0, 98, 84)), (.5, (3, 62, 38)), (1, (96, 70, 36))], 18)
    g, m = glow(CW, CH, CW * .95, CH * 1.0, 720, 520, BRONZE, .6)
    img = over(img, BRONZE, m)
    sf = star_field(CW, CH, 230, GOLD_LT + (46,), 2)
    apply_alpha(img, sf, 1.0)
    box = (330, 232, CW - 330, CH - 232)
    soft_shadow(img, box, 70, alpha=120, blur=28, off=14, rgb=(0, 20, 10))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle(box, 70, fill=(2, 40, 28, 205))
    ld.rounded_rectangle(box, 70, outline=GOLD_LT + (255,), width=3)
    ld.rounded_rectangle((box[0] + 16, box[1] + 16, box[2] - 16, box[3] - 16), 56, outline=GOLD + (200,), width=1)
    img.paste(lay, (0, 0), lay)
    name_text(img, CW / 2, 440, 92, CREAM)
    diamond_divider(img, CW / 2, 520, half=250, gap=34, col=GOLD_LT)
    ornament_pair(img, CW / 2, 440, NAME_W(92) + 130, col=GOLD_LT, h=70)
    logo(img, "rakb_gold", 80, 352, h=200, rgb=GOLD_LT)
    logo(img, "hajj_white", CW - 90 - 176, 358, h=176)
    return img

# ------------------------------------------------------------------ 4 modern: photo + geometry
def c4():
    img = gradient(CW, CH, [(0, (253, 249, 242)), (1, (243, 236, 223))], 90)
    panel = gradient(940, CH, [(0, (0, 92, 78)), (1, (2, 44, 30))], 70)
    ph_h = 560
    ph = sky_photo(ph_h, 940).filter(ImageFilter.GaussianBlur(0.9))
    duo = ImageOps.colorize(ImageOps.autocontrast(ph.convert("L"), cutoff=1), black=(1, 30, 21),
                            mid=(40, 84, 62), white=(214, 196, 150))
    duo = Image.blend(duo, gradient(940, ph_h, [(0, (0, 92, 78)), (1, (2, 44, 30))], 70), 0.28)
    fade = Image.fromarray((np.clip(np.arange(ph_h) / 220, 0, 1)[:, None].repeat(940, 1) * 255).astype("uint8"))
    panel.paste(duo, (0, CH - ph_h), fade)
    lay = Image.new("RGB", img.size)
    lay.paste(panel, (0, 0))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([(0, 0), (800, 0), (560, CH), (0, CH)], fill=255)
    img.paste(lay, (0, 0), m.filter(ImageFilter.GaussianBlur(0.8)))
    d = ImageDraw.Draw(img)
    d.line((800, 0, 560, CH), fill=GOLD, width=6)                 # gold seam
    d.line((830, 0, 590, CH), fill=GOLD, width=2)
    lay2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay2)
    for r in (150, 215, 280):                                      # rings behind the name
        ld.ellipse((1180 - r, 462 - r, 1180 + r, 462 + r), outline=GOLD + (60,), width=3)
    img.paste(lay2, (0, 0), lay2)
    name_text(img, 1175, 400, 104, GREEN)
    diamond_divider(img, 1175, 478, half=250, gap=34)
    logo(img, "rakb_green", 1040, 520, h=150)
    logo(img, "hajj_green", 1290, 524, h=140)
    d = ImageDraw.Draw(img)
    d.line((1240, 530, 1240, 668), fill=GOLD, width=3)
    return img

# ------------------------------------------------------------------ 5 minimal / calm
def c5():
    img = paper(CW, CH)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for i, r in enumerate(range(330, 1000, 110)):
        ld.ellipse((CW / 2 - r, 462 - r, CW / 2 + r, 462 + r), outline=GOLD + (max(14, 70 - i * 9),), width=2)
    img.paste(lay, (0, 0), lay)
    logo(img, "rakb_gold", CW / 2 - 170, 200, w=340)
    name_text(img, CW / 2, 585, 92, GREEN)
    diamond_divider(img, CW / 2, 660, half=210, gap=30)
    return img

COVERS = [c1, c2, c3, c4, c5]

def main():
    for i, fn in enumerate(COVERS, 1):
        fn().convert("RGB").save(f"Covers/Cover-{i:02d}.png", optimize=True)
        print("cover", i, flush=True)

if __name__ == "__main__":
    main()

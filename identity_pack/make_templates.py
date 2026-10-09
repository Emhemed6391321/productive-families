#!/usr/bin/env python3
"""Six empty, fully designed templates (no text) for Tripoli-B.  Output: Templates/Template-0N.png
(1080x1440, the size of the reference cards) and Templates/1080x1350/Template-0N.png (4:5 feed size).
Empty zones are left for: title (T), detail text (B) and an optional signature / name (S)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pack_lib import *

W = 1080

def footer_logos(img, dark=False, y_off=152, rk=96, hj=82):
    Wd, H = img.size
    if dark:
        logo(img, "rakb_gold", 70, H - y_off - 4, w=rk, rgb=GOLD_LT)
        logo(img, "hajj_white", Wd - 70 - hj, H - y_off, w=hj)
    else:
        logo(img, "rakb_green", 70, H - y_off - 4, w=rk)
        logo(img, "hajj_green", Wd - 70 - hj, H - y_off, w=hj)

# --------------------------------------------------------------------------- 1 light
def t1(H):
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 46, ramp=vramp(H, H * .3, H * .95, .1, 1))
    paste(img, sky_layer(W, 0.8), 0, H - 510)
    ornament_pair(img, W / 2, 285, 860)                  # flank the title zone (as in refs 2 & 4)
    diamond_divider(img, W / 2, 440)                     # title | body
    footer_logos(img)
    return img

# --------------------------------------------------------------------------- 2 dark
def t2(H):
    img = gradient(W, H, [(0, TEAL), (.55, (2, 54, 42)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, H * .22, 560, 420, (12, 120, 100), .5)
    img = over(img, (12, 120, 100), m)
    img = add_lattice(img, GOLD_LT, 42)
    paste(img, sky_layer(W, 0.8, tint=GOLD_LT, blur=1.1), 0, H - 520)
    frame(img, 46, GOLD, 4, 14)
    d = ImageDraw.Draw(img)
    star8(d, W / 2, 168, 66, outline=GOLD, width=3)
    star8(d, W / 2, 168, 38, outline=GOLD, width=2, rot=-math.pi / 2 + math.pi / 8)
    d.ellipse((W / 2 - 7, 161, W / 2 + 7, 175), fill=GOLD)
    diamond_divider(img, W / 2, 560, col=GOLD)
    footer_logos(img, dark=True, y_off=176)
    return img

# --------------------------------------------------------------------------- 3 gradient
def t3(H):
    img = gradient(W, H, [(0, (0, 98, 84)), (.5, (3, 62, 38)), (1, (2, 38, 24))], 62)
    g, m = glow(W, H, 40, H - 60, 760, 640, BRONZE, .65)
    img = over(img, BRONZE, m)
    g, m = glow(W, H, W * .9, 60, 520, 380, (20, 140, 118), .45)
    img = over(img, (20, 140, 118), m)
    arcs = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(arcs)
    for r in range(260, 1100, 130):
        ad.ellipse((W * .92 - r, -80 - r, W * .92 + r, -80 + r), outline=GOLD_LT + (60,), width=3)
    img.paste(arcs, (0, 0), arcs)
    box = (64, 520, W - 64, H - 250)
    soft_shadow(img, box, 60, alpha=110, blur=26, off=14, rgb=(0, 20, 10))
    card = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(box, 60, fill=CREAM + (244,))
    cd.rounded_rectangle((box[0] + 20, box[1] + 20, box[2] - 20, box[3] - 20), 44, outline=GOLD + (200,), width=2)
    img.paste(card, (0, 0), card)
    ornament_pair(img, W / 2, 330, 640, col=GOLD_LT, h=96)
    footer_logos(img, dark=True, y_off=176)
    return img

# --------------------------------------------------------------------------- 4 photo
def t4(H):
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, H * .45, H, .0, 1))
    ph_h = 860
    plate = sky_photo(ph_h, W).filter(ImageFilter.GaussianBlur(1.8))
    duo = ImageOps.colorize(ImageOps.autocontrast(plate.convert("L"), cutoff=1),
                            black=(1, 28, 19), mid=(46, 86, 64), white=(214, 196, 150))
    scrim = gradient(W, ph_h, [(0, (1, 46, 34)), (.55, (2, 52, 36)), (1, (4, 61, 31))], 90)
    sc_a = Image.fromarray((vramp(ph_h, 0, ph_h * .85, .90, .30)[:, None].repeat(W, 1) * 255).astype("uint8"))
    duo = Image.composite(scrim, duo, sc_a)
    mask = Image.fromarray((np.clip((ph_h - np.arange(ph_h)) / 260, 0, 1)[:, None].repeat(W, 1) * 255).astype("uint8"))
    img.paste(duo, (0, 0), mask)
    d = ImageDraw.Draw(img)
    ornament_pair(img, W / 2, 285, 860, col=GOLD_LT)
    diamond_divider(img, W / 2, 470, col=GOLD_LT)
    footer_logos(img)
    return img

# --------------------------------------------------------------------------- 5 geometric
def t5(H):
    img = paper(W, H, warm=True)
    sf = star_field(W, H, 180, GOLD + (70,), 2)
    apply_alpha(img, sf, 0.9)
    frame(img, 50, GOLD, 5, 16)
    # calm inner field for the text
    box = (118, 520, W - 118, H - 330)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle(box, 40, fill=PAPER_A + (232,))
    img.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 40, outline=GOLD, width=3)
    d.rounded_rectangle((box[0] + 14, box[1] + 14, box[2] - 14, box[3] - 14), 28, outline=GOLD, width=1)
    # crown medallion above the title zone
    star8(d, W / 2, 168, 70, fill=GOLD)
    star8(d, W / 2, 168, 46, fill=PAPER_A, rot=-math.pi / 2 + math.pi / 8)
    star8(d, W / 2, 168, 22, fill=GOLD)
    diamond_divider(img, W / 2, 468)
    # logos centred at the bottom, either side of a gold stem (signature space between)
    by = H - 300
    d.line((W / 2, by + 8, W / 2, by + 112), fill=GOLD, width=3)
    logo(img, "rakb_green", W / 2 - 40 - 120, by, w=120)
    logo(img, "hajj_green", W / 2 + 40, by + 4, w=96)
    return img

# --------------------------------------------------------------------------- 6 modern
def t6(H):
    img = gradient(W, H, [(0, (253, 249, 242)), (1, (243, 236, 223))], 90)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    for r, a in ((330, 90), (410, 55), (490, 30)):                 # rings, top-left
        ld.ellipse((60 - r, 150 - r, 60 + r, 150 + r), outline=GOLD + (a,), width=3)
    for i in range(9):                                              # dot grid, mid-left
        for j in range(6):
            x, y = 90 + i * 34, 620 + j * 34
            ld.ellipse((x - 3, y - 3, x + 3, y + 3), fill=GOLD + (120,))
    img.paste(lay, (0, 0), lay)
    # teal tab with the authority logo (top right) and Rakb logo (top left)
    tab = (W - 330, -70, W + 70, 240)
    soft_shadow(img, tab, 70, alpha=70, blur=20, off=10, rgb=(0, 40, 30))
    tg = gradient(W, H, [(0, (0, 98, 84)), (1, (3, 56, 36))], 40)
    tm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(tm).rounded_rectangle(tab, 70, fill=255)
    img.paste(tg, (0, 0), tm)
    logo(img, "hajj_white", W - 250, 62, w=118)
    logo(img, "rakb_green", 80, 66, w=170)
    d = ImageDraw.Draw(img)
    # right-hand accent bar that carries the text block
    d.rounded_rectangle((W - 74, 330, W - 66, H - 520), 4, fill=GOLD)
    d.polygon([(W - 70, 300), (W - 56, 318), (W - 70, 336), (W - 84, 318)], fill=GOLD)
    # photo card
    box = (70, H - 430, W - 70, H - 150)
    soft_shadow(img, box, 54, alpha=80, blur=22, off=12)
    ph = sky_photo(box[3] - box[1], box[2] - box[0])
    ph = ImageOps.colorize(ImageOps.autocontrast(ph.convert("L"), cutoff=1), black=(20, 40, 30), mid=(120, 105, 75),
                           white=(244, 234, 214))
    pm = Image.new("L", img.size, 0)
    ImageDraw.Draw(pm).rounded_rectangle(box, 54, fill=255)
    layer = Image.new("RGB", img.size)
    layer.paste(ph, (box[0], box[1]))
    img.paste(layer, (0, 0), pm)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 54, outline=GOLD, width=4)
    for k in range(3):
        d.ellipse((W / 2 - 40 + k * 40 - 5, H - 98 - 5, W / 2 - 40 + k * 40 + 5, H - 98 + 5), fill=GOLD)
    return img

TEMPLATES = [t1, t2, t3, t4, t5, t6]

def main():
    for i, fn in enumerate(TEMPLATES, 1):
        for H, folder in ((1440, "Templates"), (1350, "Templates/1080x1350")):
            fn(H).convert("RGB").save(f"{folder}/Template-{i:02d}.png", optimize=True)
        print("template", i, flush=True)

if __name__ == "__main__":
    main()

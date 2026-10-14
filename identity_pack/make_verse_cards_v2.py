#!/usr/bin/env python3
"""Four different 1 x 1 m layouts for Quran 2:197 (verse text verbatim, no Rakb al-Abrar logo).
    python3 make_verse_cards_v2.py preview | print"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pack_lib import *
from make_rollup import smooth
from make_verse_card import LINES, REF, qfont, DW      # imports the verbatim-text assertion too

def fit_verse(S, maxw, maxh, maxsz=76, ls=1.62):
    P = lambda v: int(round(v * S)); sz = maxsz
    while True:
        f = qfont(P(sz))
        if max(f.getlength(t, direction="rtl", language="ar") for t, _ in LINES) <= P(maxw) and len(LINES) * P(sz * ls) <= P(maxh): return f, P(sz * ls), sz
        sz -= 1

def draw_verse(img, S, cx, top, maxw, maxh, base, hi, maxsz=76, ls=1.62, shadow=None):
    d = ImageDraw.Draw(img); f, lh, sz = fit_verse(S, maxw, maxh, maxsz, ls)
    tot = lh * len(LINES); y = int(top * S + (maxh * S - tot) / 2) + lh // 2
    for t, c in LINES:
        if shadow: d.text((cx + shadow[0], y + shadow[1]), t, font=f, fill=shadow[2], anchor="mm", direction="rtl", language="ar")
        d.text((cx, y), t, font=f, fill=hi if c == "o" else base, anchor="mm", direction="rtl", language="ar"); y += lh
    return y - lh // 2

def ref_pill(img, S, cx, y, fill, line, txt, size=40, h=68):
    P = lambda v: int(round(v * S)); d = ImageDraw.Draw(img)
    rf = font(700, P(size)); rw = rf.getlength(REF, direction="rtl", language="ar") + P(84)
    d.rounded_rectangle((cx - rw / 2, P(y), cx + rw / 2, P(y + h)), P(h / 2), fill=fill, outline=line, width=max(2, P(3)))
    d.text((cx, P(y + h / 2)), REF, font=rf, fill=txt, anchor="mm", direction="rtl", language="ar")

def footer(img, S, y, name_col, logo_name, rgb=None, w=84, x_off=110):
    P = lambda v: int(round(v * S)); W = img.size[0]; d = ImageDraw.Draw(img)
    d.text((W // 2, P(y)), "تنسيقية حجاج طرابلس ب", font=font(700, P(34)), fill=name_col, anchor="mm", direction="rtl", language="ar")
    paste(img, smooth(asset(logo_name), P(w), S), W - P(x_off) - P(w), P(y) - P(w * .52))

def crown(img, S, cx, cy, r, fill, inner):
    P = lambda v: int(round(v * S)); d = ImageDraw.Draw(img)
    star8(d, cx, P(cy), P(r), fill=fill); star8(d, cx, P(cy), P(r * .64), fill=inner, rot=-math.pi / 2 + math.pi / 8); star8(d, cx, P(cy), P(r * .3), fill=fill)

# ---------------------------------------------------------------- A : deep emerald, gold lattice, cream verse
def build_a(S):
    P = lambda v: int(round(v * S)); W = H = P(DW)
    img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, H * .42, P(640), P(520), (12, 120, 100), .45); img = over(img, (12, 120, 100), m)
    img = add_lattice(img, GOLD_LT, 36, R=P(105))
    paste(img, sky_layer(W, 0.9, tint=GOLD_LT, blur=1.1), 0, P(850))
    frame(img, P(34), GOLD, max(3, P(4)), P(14))
    cx = W // 2; ornament_pair(img, cx, P(118), P(800), col=GOLD_LT, h=P(80)); crown(img, S, cx, 118, 46, GOLD, TEAL)
    y = draw_verse(img, S, cx, 205, 930, 640, CREAM, GOLD_LT, shadow=(0, P(2), (0, 25, 15)))
    ref_pill(img, S, cx, 878, GOLD, GOLD_LT, GREEN_DK)
    footer(img, S, 1012, CREAM, "hajj_white", w=80)
    return img

# ---------------------------------------------------------------- B : cream, dome-shaped emerald panel
def build_b(S):
    P = lambda v: int(round(v * S)); W = H = P(DW)
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1), R=P(110))
    paste(img, sky_layer(W, 0.6), 0, P(900))
    cx = W // 2; box = (P(95), P(70), P(DW - 95), P(900)); rad = P(330)
    soft_shadow(img, box, rad, alpha=90, blur=P(26), off=P(14), rgb=(0, 20, 12))
    pg = add_lattice(gradient(W, H, [(0, (0, 98, 84)), (1, (3, 56, 36))], 70), GOLD_LT, 26, R=P(95))
    mk = Image.new("L", img.size, 0); md = ImageDraw.Draw(mk)
    md.rounded_rectangle(box, rad, fill=255); md.rectangle((box[0], box[1] + rad, box[2], box[3]), fill=0); md.rounded_rectangle((box[0], box[1] + rad, box[2], box[3]), P(34), fill=255)
    img.paste(pg, (0, 0), mk)
    d = ImageDraw.Draw(img)
    for off, col, wd in ((0, GOLD, 6), (P(18), GOLD_LT, 2)):
        d.rounded_rectangle((box[0] + off, box[1] + off, box[2] - off, box[3] - off), rad - off if off else rad, outline=col, width=max(2, P(wd)))
    crown(img, S, cx, 128, 50, GOLD_LT, (3, 56, 36))
    draw_verse(img, S, cx, 215, 700, 620, CREAM, GOLD_LT, maxsz=62)
    ref_pill(img, S, cx, 915, GREEN, GOLD, GOLD_LT)
    footer(img, S, 1030, GREEN, "hajj_green", w=70, x_off=120)
    return img

# ---------------------------------------------------------------- C : photo band (duotone Mecca) + cream text field + green footer bar
def build_c(S):
    P = lambda v: int(round(v * S)); W = H = P(DW)
    img = paper(W, H); img = add_lattice(img, (205, 183, 140), 36, ramp=vramp(H, P(400), H, 0, 1), R=P(110))
    ph_h = P(350); plate = sky_photo(ph_h, W).filter(ImageFilter.GaussianBlur(1.2 * S))
    duo = ImageOps.colorize(ImageOps.autocontrast(plate.convert("L"), cutoff=1), black=(1, 28, 19), mid=(36, 84, 62), white=(214, 196, 150))
    scrim = gradient(W, ph_h, [(0, (1, 46, 34)), (1, (3, 60, 38))], 90)
    import numpy as np
    sa = Image.fromarray((vramp(ph_h, 0, ph_h, .78, .28)[:, None].repeat(W, 1) * 255).astype("uint8")); duo = Image.composite(scrim, duo, sa)
    msk = Image.fromarray((np.clip((ph_h - np.arange(ph_h)) / P(120), 0, 1)[:, None].repeat(W, 1) * 255).astype("uint8"))
    img.paste(duo, (0, 0), msk)
    d = ImageDraw.Draw(img); cx = W // 2
    d.rectangle((0, ph_h - P(8), W, ph_h - P(2)), fill=GOLD)
    crown(img, S, cx, 175, 56, GOLD_LT, (3, 56, 36))
    # verse on cream, right accent bar like the earlier cards
    d.rounded_rectangle((W - P(70), P(430), W - P(62), P(930)), P(4), fill=GOLD)
    d.polygon([(W - P(66), P(398)), (W - P(52), P(416)), (W - P(66), P(434)), (W - P(80), P(416))], fill=GOLD)
    draw_verse(img, S, cx - P(14), 385, 900, 560, GREEN, (160, 118, 40), maxsz=76)
    bar = (0, P(960), W, H); d.rectangle(bar, fill=GREEN_DK); d.rectangle((0, P(960), W, P(966)), fill=GOLD)
    d.text((P(DW) - P(130) - P(70) - P(40), P(1020)), REF, font=font(700, P(36)), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    d.text((P(70), P(1020)), "تنسيقية حجاج طرابلس ب", font=font(700, P(34)), fill=CREAM, anchor="lm", direction="rtl", language="ar")
    paste(img, smooth(asset("hajj_white"), P(74), S), W - P(100) - P(74) + P(30), P(1020) - P(40))
    return img

# ---------------------------------------------------------------- D : cream card on emerald pattern, star corners
def build_d(S):
    P = lambda v: int(round(v * S)); W = H = P(DW)
    img = gradient(W, H, [(0, (0, 98, 84)), (.5, (3, 62, 38)), (1, (2, 38, 24))], 62)
    g, m = glow(W, H, 40, H - 60, P(760), P(640), BRONZE, .55); img = over(img, BRONZE, m)
    img = add_lattice(img, GOLD_LT, 44, R=P(100))
    cx = W // 2; box = (P(80), P(80), P(DW - 80), P(DW - 80))
    soft_shadow(img, box, P(60), alpha=130, blur=P(30), off=P(16), rgb=(0, 16, 10))
    card = Image.new("RGBA", img.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle(box, P(60), fill=CREAM + (246,)); img.paste(card, (0, 0), card)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((box[0] + P(20), box[1] + P(20), box[2] - P(20), box[3] - P(20)), P(44), outline=GOLD, width=max(2, P(3)))
    d.rounded_rectangle((box[0] + P(32), box[1] + P(32), box[2] - P(32), box[3] - P(32)), P(34), outline=GOLD_LT, width=max(1, P(1.5)))
    for (x, y) in ((box[0] + P(20), box[1] + P(20)), (box[2] - P(20), box[1] + P(20)), (box[0] + P(20), box[3] - P(20)), (box[2] - P(20), box[3] - P(20))):
        star8(d, x, y, P(26), fill=GOLD); star8(d, x, y, P(13), fill=CREAM, rot=-math.pi / 2 + math.pi / 8)
    paste(img, sky_layer(W, 0.5), 0, P(830))
    d = ImageDraw.Draw(img)
    ornament_pair(img, cx, P(165), P(640), col=GOLD, h=P(70)); crown(img, S, cx, 165, 40, GOLD, CREAM)
    draw_verse(img, S, cx, 235, 790, 560, GREEN, (160, 118, 40), maxsz=68)
    ref_pill(img, S, cx, 810, GREEN, GOLD, GOLD_LT, size=36, h=62)
    footer(img, S, 930, GREEN, "hajj_green", w=66, x_off=170)
    return img

BUILDS = [("1-emerald", build_a), ("2-dome", build_b), ("3-photo-band", build_c), ("4-card-on-pattern", build_d)]
if __name__ == "__main__":
    os.makedirs("VerseCard", exist_ok=True)
    if (sys.argv[1] if len(sys.argv) > 1 else "preview") == "preview":
        for i, (n, fn) in enumerate(BUILDS, 1): fn(1.0).convert("RGB").save(f"VerseCard/v2-preview-{i}.png")
        print("ok")
    else:
        S = 3937 / DW
        for i, (n, fn) in enumerate(BUILDS, 1):
            im = fn(S).convert("RGB")
            im.save(f"VerseCard/VerseCard-{n}-100x100cm.pdf", resolution=100.0); im.save(f"VerseCard/VerseCard-{n}-100x100cm-100dpi.png", dpi=(100, 100)); print(n, im.size, flush=True)

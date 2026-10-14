#!/usr/bin/env python3
"""Six welcome-to-pilgrims templates in different sizes / shapes (no Rakb logo):
 1 square 1080x1080 (emerald medallion)   2 story 1080x1920 (tall arch)   3 landscape 1920x1080 (split photo)
 4 portrait 1080x1350 (cream frame)       5 A4 2480x3508 (print poster)   6 cover 1640x624 (Facebook cover)"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pack_lib import *
from make_rollup import smooth

NAME, PHONE, PLACE = "تنسيقية حجاج طرابلس ب", "0934455422", "طرابلس - زناتة"
GREETING, HERO, SUB = "أهلًا وسهلًا", "بحجاج بيت الله الحرام", f"{NAME} ترحّب بكم"
_LG = Image.open("assets/coordination_logo.jpg").convert("RGB")

def T(d, x, y, text, size, fill, w=700, maxw=900, anchor="mm"):
    f = font(w, int(size))
    while f.getlength(text, direction="rtl", language="ar") > maxw: f = font(w, f.size - 2)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar")

def emerald(W, H, glow_xy=None):
    img = gradient(W, H, [(0, (0, 98, 84)), (.5, (3, 62, 38)), (1, (2, 38, 24))], 62)
    gx, gy = glow_xy or (W * .2, H * .9)
    g, m = glow(W, H, gx, gy, W * .7, H * .6, BRONZE, .5); img = over(img, BRONZE, m)
    return add_lattice(img, GOLD_LT, 40, R=max(90, int(min(W, H) * .1)))

def cream(W, H):
    img = paper(W, H, warm=True); return add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1), R=max(90, int(min(W, H) * .1)))

def medallion(img, cx, cy, R, ring_col=GOLD, back=CREAM, rings=True, shadow=True):
    d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((cx - R - 14, cy - R, cx + R + 14, cy + R + 28), fill=(0, 0, 0, 100))
        sh = sh.filter(ImageFilter.GaussianBlur(R * .06)); img.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(img)
    if rings:
        for rr, col, wd in ((R + R * .16, ring_col, 3), (R + R * .08, GOLD_LT, 2)): d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=max(2, int(wd * R / 150)))
        for k in range(8):
            a = math.radians(-90 + k * 45 + 22.5); star8(d, cx + (R + R * .16) * math.cos(a), cy + (R + R * .16) * math.sin(a), R * .055, fill=ring_col)
    d.ellipse((cx - R - R * .05, cy - R - R * .05, cx + R + R * .05, cy + R + R * .05), fill=back, outline=ring_col, width=max(3, int(R * .035)))
    c = min(_LG.size) / 2; lg = _LG.crop((int(_LG.size[0] / 2 - c * .985), int(_LG.size[1] / 2 - c * .985), int(_LG.size[0] / 2 + c * .985), int(_LG.size[1] / 2 + c * .985))).resize((int(2 * R), int(2 * R)), Image.LANCZOS)
    mk = Image.new("L", lg.size, 0); ImageDraw.Draw(mk).ellipse((0, 0, lg.size[0] - 1, lg.size[1] - 1), fill=255); img.paste(lg, (int(cx - R), int(cy - R)), mk)

def duo_photo(w, h, blur=2.0, scrim_a=(.62, .15)):
    plate = sky_photo(h, w).filter(ImageFilter.GaussianBlur(blur))
    duo = ImageOps.colorize(ImageOps.autocontrast(plate.convert("L"), cutoff=1), black=(1, 30, 20), mid=(34, 92, 68), white=(226, 205, 150))
    scrim = gradient(w, h, [(0, (1, 44, 32)), (.5, (2, 56, 38)), (1, (3, 60, 36))], 90)
    sa = Image.fromarray((vramp(h, 0, h, *scrim_a)[:, None].repeat(w, 1) * 255).astype("uint8")); return Image.composite(scrim, duo, sa)

def pill(img, box, left_txt, num, right_txt, fill=GREEN, line=GOLD, ink=GOLD_LT, num_ink=CREAM, size=None):
    h = box[3] - box[1]; soft_shadow(img, box, h // 2, alpha=60, blur=10, off=5); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, h // 2, fill=fill, outline=line, width=max(2, h // 26)); cy = (box[1] + box[3]) / 2; fs = size or h * .5
    d.text((box[2] - h * .5, cy), "للتواصل", font=font(600, int(fs * .56)), fill=ink, anchor="rm", direction="rtl", language="ar")
    d.text(((box[0] + box[2]) / 2 - h * .15, cy + 1), num, font=font(700, int(fs)), fill=num_ink, anchor="mm")
    d.text((box[0] + h * .5, cy), right_txt, font=font(600, int(fs * .56)), fill=ink, anchor="lm", direction="rtl", language="ar")

def arch_mask(size, box, rad):
    mk = Image.new("L", size, 0); md = ImageDraw.Draw(mk)
    md.ellipse((box[0], box[1], box[2], box[1] + 2 * rad), fill=255); md.rectangle((box[0], box[1] + rad, box[2], box[3]), fill=255); md.rectangle((0, box[3] + 1, size[0], size[1]), fill=0); return mk

def arch(img, box, blur=2.0):
    rad = (box[2] - box[0]) // 2; w, h = box[2] - box[0], box[3] - box[1]
    soft_shadow(img, box, rad, alpha=100, blur=24, off=14, rgb=(0, 20, 12))
    layer = Image.new("RGB", img.size); layer.paste(duo_photo(w, h, blur), (box[0], box[1])); img.paste(layer, (0, 0), arch_mask(img.size, box, rad))
    d = ImageDraw.Draw(img)
    for off, col, wd in ((0, GOLD, 6), (16, GOLD_LT, 2)):
        b = (box[0] + off, box[1] + off, box[2] - off, box[3]); d.arc((b[0], b[1], b[2], b[1] + (b[2] - b[0])), 180, 360, fill=col, width=wd)
        d.line((b[0], b[1] + (b[2] - b[0]) // 2, b[0], b[3]), fill=col, width=wd); d.line((b[2], b[1] + (b[2] - b[0]) // 2, b[2], b[3]), fill=col, width=wd)
    d.line((box[0], box[3], box[2], box[3]), fill=GOLD, width=6)

def crown(d, cx, cy, r, fill, inner):
    star8(d, cx, cy, r, fill=fill); star8(d, cx, cy, r * .64, fill=inner, rot=-math.pi / 2 + math.pi / 8); star8(d, cx, cy, r * .3, fill=fill)

# ---------------------------------------------------------------- 1 square, emerald medallion
def t1():
    W = H = 1080; img = emerald(W, H); frame(img, 34, GOLD, 3, 12); cx = W // 2
    medallion(img, cx, 360, 235, back=(3, 56, 36)); d = ImageDraw.Draw(img)
    T(d, cx, 700, GREETING, 52, GOLD_LT, 700, 600); T(d, cx, 805, HERO, 100, CREAM, 700, 930); T(d, cx, 900, SUB, 42, GOLD_LT, 600, 900)
    pill(img, (160, 960, W - 160, 1032), "", PHONE, PLACE, fill=(2, 36, 22), line=GOLD, ink=GOLD_LT, num_ink=CREAM, size=40)
    return img

# ---------------------------------------------------------------- 2 story, tall arch (safe zones respected)
def t2():
    W, H = 1080, 1920; img = cream(W, H); cx = W // 2
    paste(img, sky_layer(W, 0.4), 0, 1735)
    arch(img, (80, 215, W - 80, 1010)); d = ImageDraw.Draw(img); crown(d, cx, 365, 62, GOLD_LT, (3, 56, 36))
    medallion(img, cx, 1010, 165); d = ImageDraw.Draw(img)
    T(d, cx, 1235, GREETING, 56, GOLD, 700, 600); diamond_divider(img, cx, 1285, half=260, gap=30, col=GOLD, width=3, size=11)
    T(d, cx, 1385, "بحجاج بيت", 116, GREEN, 700, 900); T(d, cx, 1505, "الله الحرام", 116, GREEN, 700, 900)
    T(d, cx, 1592, SUB, 42, BRONZE, 600, 900)
    pill(img, (110, 1650, W - 110, 1724), "", PHONE, PLACE, size=44)
    return img

# ---------------------------------------------------------------- 3 landscape, split with photo
def t3():
    W, H = 1920, 1080; img = cream(W, H)
    pw = 800; layer = Image.new("RGB", img.size); layer.paste(duo_photo(pw, H, 2.0, (.5, .3)), (0, 0))
    mk = Image.new("L", img.size, 0); md = ImageDraw.Draw(mk); md.rectangle((0, 0, pw, H), fill=255)
    soft_shadow(img, (0, 0, pw, H), 20, alpha=90, blur=26, off=0, rgb=(0, 20, 12)); img.paste(layer, (0, 0), mk); d = ImageDraw.Draw(img)
    d.rectangle((pw, 0, pw + 8, H), fill=GOLD); crown(d, 400, 120, 52, GOLD_LT, (3, 56, 36))
    medallion(img, pw + 4, H // 2, 170); d = ImageDraw.Draw(img); cx = 1400
    T(d, cx, 250, GREETING, 66, GOLD, 700, 700); diamond_divider(img, cx, 310, half=280, gap=30, col=GOLD, width=3, size=11)
    T(d, cx, 440, "بحجاج بيت الله", 140, GREEN, 700, 780); T(d, cx, 600, "الحرام", 170, GREEN, 700, 780)
    T(d, cx, 740, SUB, 50, BRONZE, 600, 780)
    pill(img, (990, 860, 1830, 950), "", PHONE, PLACE, size=52)
    paste(img, smooth(asset("hajj_green"), 90, 1), W - 90 - 90, 60)
    return img

# ---------------------------------------------------------------- 4 portrait 4:5, cream frame
def t4():
    W, H = 1080, 1350; img = cream(W, H); paste(img, sky_layer(W, 0.5), 0, 1020); frame(img, 40, GOLD, 4, 14); cx = W // 2
    ornament_pair(img, cx, 150, 760, col=GOLD, h=86); d = ImageDraw.Draw(img); crown(d, cx, 150, 44, GOLD, PAPER_A)
    medallion(img, cx, 430, 190); d = ImageDraw.Draw(img)
    T(d, cx, 760, GREETING, 130, GOLD, 700, 760); diamond_divider(img, cx, 840, half=250, gap=30, col=GOLD, width=3, size=11)
    T(d, cx, 940, HERO, 92, GREEN, 700, 920); T(d, cx, 1030, SUB, 42, BRONZE, 600, 900)
    pill(img, (130, 1130, W - 130, 1206), "", PHONE, PLACE, size=44)
    return img

# ---------------------------------------------------------------- 5 A4 print poster (design 1080 x 1527, rendered x2.296)
def t5():
    s = 2480 / 1080; Wd, Hd = 1080, 1527; img = emerald(Wd, Hd, (Wd * .5, Hd * .15)); d = ImageDraw.Draw(img); cx = Wd // 2
    # cream lower field with a scalloped top edge
    d.rectangle((0, 660, Wd, Hd), fill=(250, 241, 228)); img.paste(add_lattice(Image.new("RGB", (Wd, Hd - 660), (250, 241, 228)), (205, 183, 140), 30, R=100), (0, 660))
    paste(img, sky_layer(Wd, 0.55), 0, 1240); d = ImageDraw.Draw(img)
    d.rectangle((0, 654, Wd, 666), fill=GOLD); frame(img, 30, GOLD, 3, 12); d = ImageDraw.Draw(img)
    ornament_pair(img, cx, 130, 760, col=GOLD_LT, h=80); crown(d, cx, 130, 44, GOLD_LT, (3, 56, 36))
    medallion(img, cx, 430, 215, back=(3, 56, 36)); d = ImageDraw.Draw(img)
    T(d, cx, 850, GREETING, 70, GOLD, 700, 700); diamond_divider(img, cx, 912, half=270, gap=30, col=GOLD, width=3, size=12)
    T(d, cx, 1030, "بحجاج بيت الله", 130, GREEN, 700, 940); T(d, cx, 1150, "الحرام", 130, GREEN, 700, 940); T(d, cx, 1250, SUB, 46, BRONZE, 600, 900)
    pill(img, (150, 1330, Wd - 150, 1412), "", PHONE, PLACE, size=48)
    return img.resize((2480, 3508), Image.LANCZOS)

# ---------------------------------------------------------------- 6 Facebook cover 1640 x 624
def t6():
    W, H = 1640, 624; img = emerald(W, H, (W * .3, H)); frame(img, 22, GOLD, 3, 10, stars=False); d = ImageDraw.Draw(img)
    paste(img, sky_layer(W, 0.8, tint=GOLD_LT, blur=1.0), 0, 430); d = ImageDraw.Draw(img)
    medallion(img, 1230, 312, 205, back=(3, 56, 36)); d = ImageDraw.Draw(img)
    T(d, 560, 150, GREETING, 56, GOLD_LT, 700, 640); T(d, 560, 270, HERO, 92, CREAM, 700, 840); T(d, 560, 375, SUB, 40, GOLD_LT, 600, 800)
    pill(img, (170, 440, 950, 510), "", PHONE, PLACE, fill=(2, 36, 22), size=40)
    return img

BUILDS = [("1-square-1080", t1), ("2-story-1080x1920", t2), ("3-landscape-1920x1080", t3), ("4-portrait-1080x1350", t4), ("5-A4-print-2480x3508", t5), ("6-cover-1640x624", t6)]
if __name__ == "__main__":
    os.makedirs("Welcome/Set", exist_ok=True)
    for n, fn in BUILDS:
        im = fn().convert("RGB"); im.save(f"Welcome/Set/Welcome-{n}.png", optimize=True); print(n, im.size, flush=True)

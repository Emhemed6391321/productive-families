#!/usr/bin/env python3
"""Location cards v2: four NEW layouts, new office photo, big scannable QR (-> the map pin), phone number slot.
Set PHONE below (or env PHONE="09x xxx xxxx") and re-run:  python3 make_location_v2.py"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageChops
from pack_lib import *
import map_lib as ml
import real_map as rm
import make_location as L1

W, H = 1080, 1440
PHONE = os.environ.get("PHONE", "093-4455422")           # <- placeholder until the real number is supplied
L1.PHOTO = "mapdata/shop_photo2.jpg"
LM = L1.LM[:3]                                            # three nearest landmarks
NAME, AREA, NOTE = L1.NAME, L1.AREA, L1.NOTE
QR_CAP = "امسح الرمز للوصول إلى المقر"
QR_SUB = "يفتح موقع المقر على الخريطة مباشرة"

def phone_icon(img, cx, cy, s, col):
    d = ImageDraw.Draw(img)
    w, h = s * .56, s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(s * .14), outline=col, width=max(3, int(s * .08)))
    d.line((cx - w * .18, cy + h * .34, cx + w * .18, cy + h * .34), fill=col, width=max(3, int(s * .08)))

def phone_bar(img, box, dark=False):
    d = ImageDraw.Draw(img)
    fill, txt, ring = ((3, 60, 44), GOLD_LT, GOLD) if dark else (GREEN, CREAM, GOLD)
    if not dark:
        soft_shadow(img, box, (box[3] - box[1]) // 2, alpha=60, blur=10, off=5)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, (box[3] - box[1]) // 2, fill=fill, outline=ring, width=2)
    cy = (box[1] + box[3]) / 2
    phone_icon(img, box[2] - 56, cy, 40, txt)
    d = ImageDraw.Draw(img)
    d.text((box[2] - 100, cy), "للتواصل", font=font(600, 26), fill=ring if not dark else GOLD, anchor="rm", direction="rtl", language="ar")
    d.text((box[0] + 36, cy + 1), PHONE, font=font(700, 44), fill=txt, anchor="lm")

def big_qr(img, x, y, size, dark=False, cap=True, ring=True):
    """QR on a white plate with a generous quiet zone + gold ring; x,y = top-left of the plate."""
    pad = 22
    box = (x, y, x + size + 2 * pad, y + size + 2 * pad)
    soft_shadow(img, box, 30, alpha=80, blur=14, off=7, rgb=(0, 20, 12) if dark else (90, 70, 30))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 30, fill=(255, 255, 255), outline=GOLD, width=4)
    q = L1.qr_img(size, fg=(4, 40, 24), bg=(255, 255, 255))
    img.paste(q, (x + pad, y + pad))
    # corner brackets
    for cx, cy, sx, sy in ((box[0], box[1], 1, 1), (box[2], box[1], -1, 1), (box[0], box[3], 1, -1), (box[2], box[3], -1, -1)):
        d.line((cx - sx * 10, cy - sy * 10, cx + sx * 40, cy - sy * 10), fill=GOLD, width=6)
        d.line((cx - sx * 10, cy - sy * 10, cx - sx * 10, cy + sy * 40), fill=GOLD, width=6)
    return box

def tag(img, x, y, n, text, dark=False, side="left", size=26, wrap=False):
    f = font(700, size)
    d = ImageDraw.Draw(img)
    if wrap and " " in text:
        words = text.split(" "); k = len(words) // 2 or 1
        lines = [" ".join(words[:k]), " ".join(words[k:])]
    else:
        lines = [text]
    tw = max(f.getlength(t, direction="rtl", language="ar") for t in lines)
    w = tw + 70; h = 48 if len(lines) == 1 else 74
    x0 = x + 26 if side == "right" else x - 26 - w
    box = (x0, y - h / 2, x0 + w, y + h / 2)
    d.rounded_rectangle(box, 24, fill=(255, 252, 244) if not dark else (3, 52, 38), outline=GOLD if not dark else GOLD_LT, width=2)
    for i, t in enumerate(lines):
        yy = y + 1 + (i - (len(lines) - 1) / 2) * (size + 6)
        d.text((box[2] - 18, yy), t, font=f, fill=GREEN if not dark else CREAM, anchor="rm", direction="rtl", language="ar")
    ml.badge(d, x, y, n, GOLD if not dark else GOLD_LT, WHITE if not dark else GREEN_DK, font(700, 24), r=22)

def flat_map(img, box, pal, dark=False, labels=True, r=40):
    mw, mh = box[2] - box[0], box[3] - box[1]
    win = rm.window_for([l["pos"] for l in LM], pad=26, aspect=mw / mh)
    mp, to = rm.flat(win, mw, pal)
    mp = mp.crop((0, 0, mw, mh))
    soft_shadow(img, box, r, alpha=70, blur=16, off=9, rgb=(0, 20, 12) if dark else (90, 70, 30))
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(mp, (box[0], box[1])); img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, r, outline=GOLD if not dark else GOLD_LT, width=4)
    hx, hy = to(rm.PIN); hx += box[0]; hy += box[1]
    for n, l in enumerate(LM, 1):
        px, py = to(l["pos"]); px += box[0]; py += box[1]
        if labels:
            side = "left" if px > (box[0] + box[2]) / 2 else "right"
            f = font(700, 24); w = f.getlength(l["name"], direction="rtl", language="ar") + 70
            x0 = px + 26 if side == "right" else px - 26 - w
            # keep clear of the pin + its callout (x: hx-340..hx+60, y: hy-110..hy+70)
            wrap = x0 < hx + 60 and x0 + w > hx - 340 and abs(py - hy) < 110
            tag(img, px, py, n, l["name"], dark, side=side, size=24, wrap=wrap)
        else:
            ml.badge(d, px, py, n, GOLD, WHITE, font(700, 24), r=22)
    return hx, hy

# ------------------------------------------------------------------ V1: map hero + photo + big QR
def v1():
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, H * .3, H, .1, 1))
    L1.header(img)
    box = (60, 190, W - 60, 760)
    hx, hy = flat_map(img, box, L1.FLAT_LIGHT)
    ml.pin(img, hx, hy + 6, 44, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    L1.callout(img, hx, hy + 44, "مقر التنسيقية", side="left")
    # photo + QR
    py = 782
    L1.rounded_paste(img, L1.photo(440, 350, focus=(0, .12, 1, .86)), (60, py, 500, py + 350), 36)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, py + 288, 490, py + 340), 20, fill=(2, 36, 22))
    d.text((280, py + 314), "واجهة المقر", font=font(700, 28), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    panel = (526, py, W - 60, py + 350)
    bc.shadowed_round(img, panel, 36, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=55)
    qs = 206
    qb = big_qr(img, (panel[0] + panel[2]) // 2 - (qs + 44) // 2, py + 14, qs)
    d = ImageDraw.Draw(img)
    d.text(((panel[0] + panel[2]) / 2, qb[3] + 26), QR_CAP, font=font(700, 27), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text(((panel[0] + panel[2]) / 2, qb[3] + 58), QR_SUB, font=font(500, 20), fill=GOLD, anchor="mm", direction="rtl", language="ar")
    phone_bar(img, (60, 1146, W - 60, 1226))
    d.text((W - 60, 1262), AREA, font=font(600, 26), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.text((60, 1262), NOTE, font=font(500, 20), fill=(140, 128, 104), anchor="lm", direction="rtl", language="ar")
    logo(img, "rakb_green", (W - 84) // 2, 1296, w=84)
    return img

# ------------------------------------------------------------------ V2: dark, QR is the hero
def v2():
    img = gradient(W, H, [(0, TEAL), (.45, (2, 52, 40)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, 760, 760, 520, (14, 128, 108), .5); img = over(img, (14, 128, 108), m)
    img = add_lattice(img, GOLD_LT, 30)
    frame(img, 34, GOLD, 3, 12, corner=0.9)
    L1.header(img, dark=True, y=56)
    box = (70, 218, W - 70, 770)
    hx, hy = flat_map(img, box, L1.FLAT_DARK, dark=True, r=36)
    ml.pin(img, hx, hy + 6, 40, GOLD, ring=GREEN_DK, logo=asset("hajj_logo_white"), glow_rgb=GOLD_LT)
    # circular office photo overlapping the map corner
    cx, cy, r = 190, 1062, 112
    ph = L1.photo(2 * r, 2 * r, focus=(0, .22, 1, .84))
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    layer = Image.new("RGB", img.size); layer.paste(ph, (cx - r, cy - r)); img.paste(layer, (0, 0), mk)
    d = ImageDraw.Draw(img); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD_LT, width=6)
    qs = 250
    qb = big_qr(img, W - 70 - (qs + 44) - 40, 800, qs, dark=True)
    d = ImageDraw.Draw(img)
    d.text(((qb[0] + qb[2]) / 2 - 360, 880), QR_CAP, font=font(700, 34), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar") if False else None
    xr = qb[0] - 40
    d.text((xr, 842), QR_CAP, font=font(700, 36), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    d.text((xr, 888), QR_SUB, font=font(500, 22), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    d.text((xr, 950), AREA, font=font(600, 24), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    d.text((xr, 990), NOTE, font=font(500, 20), fill=(150, 190, 168), anchor="rm", direction="rtl", language="ar")
    phone_bar(img, (110, 1196, W - 110, 1278), dark=True)
    logo(img, "rakb_gold", (W - 80) // 2, 1298, w=80, rgb=GOLD_LT)
    return img

# ------------------------------------------------------------------ V3: arch photo + map side by side
def v3():
    img = paper(W, H, warm=True)
    img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, H * .3, H, .1, 1))
    L1.header(img)
    top, bot = 196, 800
    # arch photo (right)
    ax0, ax1 = 560, W - 60
    arch = (ax0, top, ax1, bot)
    ph = L1.photo(ax1 - ax0, bot - top, focus=(0, .1, 1, .88))
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle(arch, (ax1 - ax0) // 2, fill=255)
    ImageDraw.Draw(m).rectangle((ax0, top + (ax1 - ax0) // 2, ax1, bot), fill=0)
    ImageDraw.Draw(m).rounded_rectangle((ax0, top + 200, ax1, bot), 36, fill=255)
    soft_shadow(img, arch, 40, alpha=70, blur=16, off=9)
    layer = Image.new("RGB", img.size); layer.paste(ph, (ax0, top)); img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((ax0 + 10, bot - 64, ax1 - 10, bot - 10), 22, fill=(2, 36, 22))
    d.text(((ax0 + ax1) / 2, bot - 37), "واجهة المقر", font=font(700, 28), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    # map (left)
    mb = (60, top, 530, bot)
    hx, hy = flat_map(img, mb, L1.FLAT_LIGHT, labels=False, r=40)
    ml.pin(img, hx, hy + 6, 40, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    L1.callout(img, hx, hy + 44, "المقر", side="right" if hx < 300 else "left")
    # legend + QR panel
    panel = (60, 824, W - 60, 1196)
    bc.shadowed_round(img, panel, 36, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=55)
    L1.legend(img, panel, size=27, row=58, lms=LM, dist_x=420)
    qs = 230
    big_qr(img, panel[0] + 34, panel[1] + 34, qs - 20)
    d = ImageDraw.Draw(img)
    d.text((panel[0] + 24 + (qs + 36) / 2 - 4, panel[1] + 28 + qs + 78), QR_CAP, font=font(700, 22), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((panel[2] - 26, panel[3] - 30), AREA, font=font(600, 24), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    phone_bar(img, (60, 1220, W - 60, 1300))
    d.text((W / 2, 1330), NOTE, font=font(500, 20), fill=(140, 128, 104), anchor="mm", direction="rtl", language="ar")
    logo(img, "rakb_green", (W - 70) // 2, 1352, w=70)
    return img

# ------------------------------------------------------------------ V4: ticket style with 3-D map
def v4():
    img = paper(W, H)
    # teal top band
    band = gradient(W, 520, [(0, (0, 98, 84)), (1, (3, 60, 38))], 70)
    img.paste(band, (0, 0))
    ov = add_lattice(Image.new("RGB", (W, 520), (0, 0, 0)), GOLD_LT, 0, R=100)
    d = ImageDraw.Draw(img)
    layerp = star_field(W, 520, 200, GOLD_LT + (40,), 2); img.paste(layerp, (0, 0), layerp)
    d = ImageDraw.Draw(img)
    logo(img, "rakb_gold", 56, 44, w=120, rgb=GOLD_LT)
    logo(img, "hajj_logo_white", W - 56 - 88, 40, w=88)
    d.text((W / 2, 70), "موقع المقر", font=font(700, 38), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    d.text((W / 2, 124), NAME, font=font(700, 54), fill=CREAM, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W / 2, 168, half=280, gap=24, col=GOLD_LT, width=2, size=9)
    # photo overlapping the band
    pb = (90, 200, W - 90, 640)
    soft_shadow(img, pb, 44, alpha=100, blur=20, off=12, rgb=(0, 20, 12))
    L1.rounded_paste(img, L1.photo(900, 440, focus=(0, .12, 1, .86)), pb, 44, border=CREAM, bw=6)
    # 3-D map card
    mb = (60, 664, W - 60, 1048)
    win = rm.window_for([l["pos"] for l in LM], pad=44)
    m3, proj = rm.iso(win, 960, L1.ISO_LIGHT, squash=.40, inset=.12)
    hx0, hy0 = proj(rm.PIN, 0)
    cw, ch = mb[2] - mb[0], mb[3] - mb[1]
    cx0 = 0; cy0 = int(min(max(hy0 - ch * .5, 0), max(0, m3.size[1] - ch)))
    crop = m3.crop((cx0, cy0, cx0 + cw, cy0 + ch))
    soft_shadow(img, mb, 40, alpha=70, blur=14, off=8)
    bgp = Image.new("RGBA", crop.size, (236, 227, 208, 255)); bgp.alpha_composite(crop)
    mm = Image.new("L", img.size, 0); ImageDraw.Draw(mm).rounded_rectangle(mb, 40, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(bgp.convert("RGB"), (mb[0], mb[1])); img.paste(layer, (0, 0), mm)
    d = ImageDraw.Draw(img); d.rounded_rectangle(mb, 40, outline=GOLD, width=4)
    hx, hy = hx0 - cx0 + mb[0], hy0 - cy0 + mb[1]
    for n, l in enumerate(LM, 1):
        px, py = proj(l["pos"], 0); px = px - cx0 + mb[0]; py = py - cy0 + mb[1]
        py = min(max(py, mb[1] + 40), mb[3] - 40); px = min(max(px, mb[0] + 40), mb[2] - 40)
        side = "left" if px > W / 2 else "right"
        f = font(700, 22); w = f.getlength(l["name"], direction="rtl", language="ar") + 70
        x0 = px + 26 if side == "right" else px - 26 - w
        if x0 < hx + 60 and x0 + w > hx - 300 and abs(py - hy) < 90:
            py = hy - 120 if py <= hy else hy + 90
        tag(img, px, py, n, l["name"], False, side=side, size=22)
    ml.pin(img, hx, hy - 18, 42, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    # ticket (QR + info) with perforation
    tk = (60, 1072, W - 60, 1330)
    bc.shadowed_round(img, tk, 40, CREAM, GOLD, 3, blur=14, off=7, alpha=60)
    d = ImageDraw.Draw(img)
    px_ = tk[0] + 318
    for yy in range(tk[1] + 24, tk[3] - 24, 18):
        d.line((px_, yy, px_, yy + 9), fill=GOLD, width=3)
    for yy in (tk[1], tk[3]):
        d.ellipse((px_ - 16, yy - 16, px_ + 16, yy + 16), fill=(243, 234, 219))
    qs = 186
    big_qr(img, tk[0] + 26, tk[1] + 18, qs)
    xr = tk[2] - 30
    d = ImageDraw.Draw(img)
    d.text((xr, tk[1] + 44), QR_CAP, font=font(700, 34), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.text((xr, tk[1] + 88), QR_SUB, font=font(500, 22), fill=GOLD, anchor="rm", direction="rtl", language="ar")
    d.text((xr, tk[1] + 128), AREA, font=font(600, 24), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    phone_bar(img, (tk[0] + 346, tk[3] - 82, tk[2] - 24, tk[3] - 20))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1356), NOTE, font=font(500, 20), fill=(140, 128, 104), anchor="mm", direction="rtl", language="ar")
    return img

CARDS = [v1, v2, v3, v4]
if __name__ == "__main__":
    os.makedirs("Location", exist_ok=True)
    for i, fn in enumerate(CARDS, 1):
        fn().convert("RGB").save(f"Location/Location-v2-{i}.png", optimize=True); print("v2", i, flush=True)

#!/usr/bin/env python3
"""Location cards v5 (1080 x 1620): new facade photo, 3-D map in all four, coordination logo, route explanation, phone, QR. No Rakb logo.
Route text: office is right after the Zenata (New) traffic light, ~50 m on the left, directly next to Jotun Paints."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pack_lib import *
import make_location as L1
import make_location_v2 as V
import real_map as rm
import map_lib as ml
from make_welcome_set import medallion, crown

W, H = 1080, 1620
PHONE = "0934455422"
SEM = "سيمافور زناتة الجديدة"
NEXT_TO = "جوتن للطلاء"
DIST = "50 م"
ISLAND = "جزيرة الفرناج"
L1.PHOTO = "mapdata/shop_photo4.jpg"
_photo = L1.photo
def photo(w, h, focus=None):
    if w <= 300: focus = (0, .50, 1, .84)
    elif w / h > 1.1: focus = (0, .44, 1, .82)
    else: focus = (0, .04, 1, .90)
    return _photo(w, h, focus)

def iso_map(img, box, dark=False, labels=True, r=40, pin_col=None):
    cw, ch = box[2] - box[0], box[3] - box[1]
    win = rm.window_for([l["pos"] for l in V.LM], pad=44)
    m3, proj = rm.iso(win, max(960, cw), L1.ISO_DARK if dark else L1.ISO_LIGHT, squash=.40, inset=.12)
    hx0, hy0 = proj(rm.PIN, 0)
    cx0 = int(min(max(hx0 - cw * .5, 0), max(0, m3.size[0] - cw))); cy0 = int(min(max(hy0 - ch * .55, 0), max(0, m3.size[1] - ch)))
    crop = Image.new("RGBA", (cw, ch), (2, 32, 24, 255) if dark else (236, 227, 208, 255)); crop.alpha_composite(m3.crop((cx0, cy0, cx0 + cw, cy0 + ch)))
    soft_shadow(img, box, r, alpha=70, blur=16, off=9, rgb=(0, 20, 12) if dark else (90, 70, 30))
    mm = Image.new("L", img.size, 0); ImageDraw.Draw(mm).rounded_rectangle(box, r, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(crop.convert("RGB"), (box[0], box[1])); img.paste(layer, (0, 0), mm)
    ImageDraw.Draw(img).rounded_rectangle(box, r, outline=GOLD_LT if dark else GOLD, width=4)
    hx, hy = hx0 - cx0 + box[0], hy0 - cy0 + box[1]
    placed = []
    for n, l in enumerate(V.LM, 1):
        px, py = proj(l["pos"], 0); px = min(max(px - cx0 + box[0], box[0] + 40), box[2] - 40); py = min(max(py - cy0 + box[1], box[1] + 40), box[3] - 40)
        if labels and cw > 600:
            side = "left" if px > (box[0] + box[2]) / 2 else "right"
            f = font(700, 22); w = f.getlength(l["name"], direction="rtl", language="ar") + 70
            x0 = px + 26 if side == "right" else px - 26 - w
            if x0 < hx + 60 and x0 + w > hx - 300 and abs(py - hy) < 130: py = hy + 120
            for (a0, a1, ay) in placed:
                if x0 < a1 and x0 + w > a0 and abs(py - ay) < 58: py = min(ay + 62, box[3] - 40) if ay + 62 <= box[3] - 40 else max(ay - 62, box[1] + 40)
            placed.append((x0, x0 + w, py))
            V.tag(img, px, py, n, l["name"], dark, side=side, size=22)
        else:
            ml.badge(ImageDraw.Draw(img), px, py, n, GOLD_LT if dark else GOLD, GREEN_DK if dark else WHITE, font(700, 22), r=20)
    ml.pin(img, hx, hy - 14, 40, pin_col or (GOLD if dark else TEAL), ring=GREEN_DK if dark else CREAM, logo=asset("hajj_logo_white"))
    return hx, hy

def route_panel(img, box, dark=False):
    x0, y0, x1, y1 = box; w = x1 - x0
    if dark:
        ImageDraw.Draw(img).rounded_rectangle(box, 34, fill=(3, 52, 38), outline=GOLD, width=3); txt, acc, road = CREAM, GOLD_LT, (200, 178, 120)
    else:
        V.bc.shadowed_round(img, box, 34, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=55); txt, acc, road = GREEN, GOLD, (150, 138, 110)
    d = ImageDraw.Draw(img)
    cw = 250; d.rounded_rectangle((x1 - 28 - cw, y0 + 16, x1 - 28, y0 + 62), 23, fill=GOLD)
    d.text((x1 - 28 - cw / 2, y0 + 39), "طريق الوصول", font=font(700, 28), fill=(2, 36, 22), anchor="mm", direction="rtl", language="ar")
    ry = y0 + 150; xa, xb, xc = x1 - 110, (x0 + x1) // 2 + 30, x0 + 120
    d.line((xc, ry, xa, ry), fill=road, width=10)
    for xx in range(int(xc) + 40, int(xa) - 30, 46): d.line((xx, ry, xx + 22, ry), fill=(250, 245, 230), width=3)
    d.polygon([(xc - 26, ry), (xc + 4, ry - 16), (xc + 4, ry + 16)], fill=road)
    # traffic light
    d.rounded_rectangle((xa - 17, ry - 34, xa + 17, ry + 34), 10, fill=(30, 30, 30), outline=(235, 235, 235), width=2)
    for k, col in enumerate(((220, 50, 40), (245, 180, 30), (50, 190, 90))): d.ellipse((xa - 8, ry - 24 + k * 22 - 7 + 3, xa + 8, ry - 24 + k * 22 + 9 + 3), fill=col)
    d.ellipse((xc - 34, ry - 28, xc + 22, ry + 28), outline=acc, width=5); d.ellipse((xc - 17, ry - 11, xc + 5, ry + 11), fill=(4, 60, 44) if dark else (236, 227, 208), outline=acc, width=3)
    d.text((xa, y0 + 98), SEM, font=font(700, 23), fill=txt, anchor="mm", direction="rtl", language="ar")
    d.text((xc - 6, y0 + 98), ISLAND, font=font(700, 23), fill=txt, anchor="mm", direction="rtl", language="ar")
    mx = (xa + xb) / 2; d.rounded_rectangle((mx - 52, ry - 46, mx + 52, ry - 8), 19, fill=acc)
    d.text((mx, ry - 27), DIST, font=font(700, 24), fill=(2, 36, 22), anchor="mm", direction="rtl", language="ar")
    d.line((xb, ry + 6, xb, ry + 28), fill=acc, width=5)
    ml.pin(img, xb, ry + 70, 30, TEAL if not dark else GOLD, ring=CREAM if not dark else (3, 52, 38), logo=asset("hajj_logo_white"))
    d = ImageDraw.Draw(img)
    d.text((xb - 40, ry + 44), "المقر على يسارك، بجانب جوتن مباشرة", font=font(700, 23), fill=acc if dark else TEAL, anchor="rm", direction="rtl", language="ar")
    d.text(((x0 + x1) / 2, y1 - 52), f"المقر بعد {SEM} بنحو {DIST.replace('م', 'متر')} على اليسار", font=font(600, 25), fill=txt, anchor="mm", direction="rtl", language="ar")
    d.text(((x0 + x1) / 2, y1 - 20), f"باتجاه {ISLAND}، بجانب {NEXT_TO} مباشرة", font=font(600, 25), fill=txt, anchor="mm", direction="rtl", language="ar")

def contact(img, box, dark=False): V.phone_bar(img, box, dark)

def title(img, y, dark=False, size=50):
    d = ImageDraw.Draw(img)
    d.text((W // 2, y), "موقع المقر", font=font(700, 34), fill=GOLD_LT if dark else GOLD, anchor="mm", direction="rtl", language="ar")
    d.text((W // 2, y + 60), "تنسيقية حجاج طرابلس ب", font=font(700, size), fill=CREAM if dark else GREEN, anchor="mm", direction="rtl", language="ar")

# ---------------------------------------------------------------- N1 photo-first (arch bottom) + logo medallion
def n1():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    box = (60, 40, W - 60, 640); ph = L1.photo(box[2] - box[0], box[3] - box[1])
    soft_shadow(img, box, 60, alpha=100, blur=22, off=12, rgb=(0, 20, 12))
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rounded_rectangle(box, 60, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(ph, (box[0], box[1])); img.paste(layer, (0, 0), mk)
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, 60, outline=GOLD, width=5)
    d.rounded_rectangle((box[0] + 24, box[3] - 74, box[0] + 250, box[3] - 22), 24, fill=(2, 36, 22)); d.text((box[0] + 137, box[3] - 48), "واجهة المقر", font=font(700, 27), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    medallion(img, W - 170, 705, 100, shadow=True); d = ImageDraw.Draw(img)
    d.text((W - 170 - 130, 677), "تنسيقية حجاج", font=font(700, 36), fill=GREEN, anchor="rm", direction="rtl", language="ar"); d.text((W - 170 - 130, 727), "طرابلس ب", font=font(700, 36), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    mb = (60, 830, W - 60, 1190); iso_map(img, mb)
    route_panel(img, (60, 1210, W - 60, 1520))
    contact(img, (60, 1535, W - 60, 1605))
    return img

# ---------------------------------------------------------------- N2 dark emerald, big map, round photo inset
def n2():
    img = gradient(W, H, [(0, TEAL), (.5, (2, 52, 40)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, H * .35, 700, 600, (12, 120, 100), .45); img = over(img, (12, 120, 100), m); img = add_lattice(img, GOLD_LT, 30)
    frame(img, 30, GOLD, 3, 12); cx = W // 2
    medallion(img, cx, 150, 95, back=(3, 56, 36)); title(img, 292, dark=True, size=54)
    mb = (60, 400, W - 60, 960); iso_map(img, mb, dark=True)
    cxp, cyp, rp = 215, 930, 125
    pm = L1.photo(2 * rp, 2 * rp); mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).ellipse((cxp - rp, cyp - rp, cxp + rp, cyp + rp), fill=255)
    lay = Image.new("RGB", img.size); lay.paste(pm, (cxp - rp, cyp - rp)); img.paste(lay, (0, 0), mk); d = ImageDraw.Draw(img); d.ellipse((cxp - rp, cyp - rp, cxp + rp, cyp + rp), outline=GOLD_LT, width=6)
    d.text((cxp + rp + 30, 1040), "واجهة المقر", font=font(700, 28), fill=GOLD_LT, anchor="lm", direction="rtl", language="ar") if False else None
    route_panel(img, (60, 1090, W - 60, 1400), dark=True)
    contact(img, (110, 1430, W - 110, 1510), dark=True)
    return img

# ---------------------------------------------------------------- N3 arch photo + tall map side by side, QR
def n3():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    ornament_pair(img, cx, 100, 780, col=GOLD, h=76); title(img, 76, size=48) if False else None
    d = ImageDraw.Draw(img); crown(d, cx, 100, 42, GOLD, PAPER_A)
    d.text((cx, 190), "تنسيقية حجاج طرابلس ب", font=font(700, 56), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    top, bot = 250, 880; ax0, ax1 = 530, W - 60; arch = (ax0, top, ax1, bot)
    ph = L1.photo(ax1 - ax0, bot - top); m = Image.new("L", img.size, 0); md = ImageDraw.Draw(m); md.rounded_rectangle(arch, (ax1 - ax0) // 2, fill=255); md.rectangle((ax0, top + (ax1 - ax0) // 2, ax1, bot), fill=0); md.rounded_rectangle((ax0, top + 220, ax1, bot), 36, fill=255)
    soft_shadow(img, arch, 40, alpha=70, blur=16, off=9); lay = Image.new("RGB", img.size); lay.paste(ph, (ax0, top)); img.paste(lay, (0, 0), m)
    d = ImageDraw.Draw(img); d.rounded_rectangle((ax0 + 10, bot - 64, ax1 - 10, bot - 10), 22, fill=(2, 36, 22)); d.text(((ax0 + ax1) / 2, bot - 37), "واجهة المقر", font=font(700, 28), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    iso_map(img, (60, top, 500, bot), labels=False)
    medallion(img, 280, bot + 5, 78, shadow=True)
    route_panel(img, (60, 960, W - 60, 1270))
    q = V.big_qr(img, 70, 1300, 190); d = ImageDraw.Draw(img)
    d.text((q[2] + 26, 1350), "امسح الرمز للوصول إلى المقر", font=font(700, 30), fill=GREEN, anchor="lm", direction="rtl", language="ar")
    d.text((q[2] + 26, 1396), "يفتح موقع المقر على الخريطة", font=font(500, 22), fill=GOLD, anchor="lm", direction="rtl", language="ar")
    contact(img, (60, 1530, W - 60, 1600))
    return img

# ---------------------------------------------------------------- N4 ticket: teal band + photo overlap
def n4():
    img = paper(W, H); cx = W // 2
    band = gradient(W, 560, [(0, (0, 98, 84)), (1, (3, 60, 38))], 70); img.paste(band, (0, 0))
    lp = star_field(W, 560, 200, GOLD_LT + (40,), 2); img.paste(lp, (0, 0), lp)
    medallion(img, 140, 118, 78, back=(3, 56, 36), shadow=False); d = ImageDraw.Draw(img)
    d.text((W - 60, 84), "موقع المقر", font=font(700, 34), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    d.text((W - 60, 142), "تنسيقية حجاج طرابلس ب", font=font(700, 52), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    pb = (90, 230, W - 90, 700); soft_shadow(img, pb, 44, alpha=100, blur=20, off=12, rgb=(0, 20, 12)); L1.rounded_paste(img, L1.photo(900, 470), pb, 44, border=CREAM, bw=6)
    d = ImageDraw.Draw(img); d.rounded_rectangle((pb[0] + 24, pb[3] - 72, pb[0] + 250, pb[3] - 20), 24, fill=(2, 36, 22)); d.text((pb[0] + 137, pb[3] - 46), "واجهة المقر", font=font(700, 27), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    iso_map(img, (60, 725, W - 60, 1085))
    route_panel(img, (60, 1105, W - 60, 1415))
    tk = (60, 1430, W - 60, 1600); V.bc.shadowed_round(img, tk, 36, CREAM, GOLD, 3, blur=14, off=7, alpha=60)
    q = V.big_qr(img, tk[0] + 22, tk[1] + 10, 110); d = ImageDraw.Draw(img)
    d.text((tk[2] - 28, tk[1] + 38), "امسح الرمز للوصول إلى المقر", font=font(700, 28), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    V.phone_bar(img, (q[2] + 24, tk[1] + 80, tk[2] - 20, tk[3] - 18))
    return img

BUILDS = [("1", n1), ("2", n2), ("3", n3), ("4", n4)]
if __name__ == "__main__":
    os.makedirs("Location", exist_ok=True)
    for n, fn in BUILDS: fn().convert("RGB").save(f"Location/Location-v5-{n}.png", optimize=True); print(n, flush=True)

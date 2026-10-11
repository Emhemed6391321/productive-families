#!/usr/bin/env python3
"""Four concept cards announcing where the Tripoli-B coordination office is (1080x1440).
Real street geometry + landmark names come from the supplied Google-Maps screenshot
(pin 32.859620, 13.235758); distances are approximate (read from the screenshot's scale bar)."""
import math, os
import qrcode
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from pack_lib import *
import map_lib as ml
import real_map as rm

W, H = 1080, 1440
MAPS_URL = "https://maps.app.goo.gl/1JSxPQokT7d6L9g86"
PHOTO = "mapdata/shop_photo.jpg"
NAME = "تنسيقية حجاج طرابلس ب"
AREA = "زناتة الجديدة - قرب طريق زناتة"
NOTE = "المسافات تقريبية"
# numbered landmarks, nearest first
LM = sorted([l for l in rm.LANDMARKS if l["name"] != "بيتزا السمعة"], key=lambda l: rm.distance_m(l["pos"]))
for l in LM:
    l["dist"] = int(round(rm.distance_m(l["pos"]) / 10.0) * 10)

ISO_LIGHT = dict(road=(200, 190, 170), edge=(178, 166, 144), roadline=(243, 236, 221), major=(238, 216, 164), block=(232, 222, 204),
                 park=(188, 206, 160), wall=(226, 215, 196), roof=(251, 247, 238), roof_edge=(208, 196, 174),
                 hq_wall=(176, 132, 54), hq_roof=(208, 164, 70), shadow=(110, 95, 70, 95))
ISO_DARK = dict(road=(3, 28, 21), edge=(2, 21, 15), roadline=(16, 76, 58), major=(160, 128, 62), block=(5, 38, 29),
                park=(8, 58, 40), wall=(10, 66, 51), roof=(26, 102, 80), roof_edge=(52, 140, 108),
                hq_wall=(170, 128, 56), hq_roof=GOLD_LT, shadow=(0, 0, 0, 120))
FLAT_LIGHT = dict(block=(238, 229, 211), tint=(7, 7, 7), edge=(224, 212, 190), road=(255, 252, 244), major=(236, 214, 160))
FLAT_DARK = dict(block=(4, 40, 30), tint=(3, 6, 5), edge=(2, 28, 20), road=(12, 82, 63), major=(178, 144, 72))

def qr_img(size, fg=GREEN, bg=CREAM):
    q = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10)
    q.add_data(MAPS_URL); q.make(fit=True)
    return q.make_image(fill_color=fg, back_color=bg).convert("RGB").resize((size, size), Image.NEAREST)

def qr_plate(img, x, y, size, caption=None, dark=False):
    pad = 14
    box = (x, y, x + size + 2 * pad, y + size + 2 * pad)
    bc.shadowed_round(img, box, 24, CREAM, GOLD, 2, blur=10, off=5, alpha=55)
    img.paste(qr_img(size), (x + pad, y + pad))
    if caption:
        ImageDraw.Draw(img).text(((box[0] + box[2]) / 2, box[3] + 22), caption, font=font(600, 24), fill=CREAM if dark else GREEN,
                                 anchor="mm", direction="rtl", language="ar")

def photo(w, h, focus=(0.0, .12, 1.0, .80)):
    im = Image.open(PHOTO).convert("RGB")
    x0, y0, x1, y1 = [int(v) for v in (focus[0] * im.size[0], focus[1] * im.size[1], focus[2] * im.size[0], focus[3] * im.size[1])]
    im = im.crop((x0, y0, x1, y1))
    s = max(w / im.size[0], h / im.size[1])
    im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    cx, cy = (im.size[0] - w) // 2, (im.size[1] - h) // 2
    im = im.crop((cx, cy, cx + w, cy + h))
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Contrast(im).enhance(1.08); im = ImageEnhance.Color(im).enhance(1.12); im = ImageEnhance.Brightness(im).enhance(1.04)
    return im.filter(ImageFilter.UnsharpMask(1.2, 60, 2))

def rounded_paste(img, im, box, r, border=GOLD, bw=4):
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(im.convert("RGB"), (box[0], box[1]))
    img.paste(layer, (0, 0), m)
    if border:
        ImageDraw.Draw(img).rounded_rectangle(box, r, outline=border, width=bw)

def header(img, dark=False, y=36):
    d = ImageDraw.Draw(img)
    logo(img, "rakb_gold" if dark else "rakb_green", 56, y + 8, w=130, rgb=GOLD_LT if dark else None)
    logo(img, "hajj_logo_white", W - 56 - 92, y, w=92, rgb=None if dark else GREEN)
    d.text((W / 2, y + 26), "موقع المقر", font=font(700, 40), fill=GOLD_LT if dark else GOLD, anchor="mm", direction="rtl", language="ar")
    d.text((W / 2, y + 82), NAME, font=font(700, 58), fill=CREAM if dark else GREEN, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W / 2, y + 138, half=300, gap=26, col=GOLD, width=2, size=9)

def legend(img, box, dark=False, size=30, row=62, dist=True, dist_x=None, lms=None):
    lms = lms or LM
    d = ImageDraw.Draw(img)
    x1 = box[2] - 26; y = box[1] + 22
    for i, l in enumerate(lms, 1):
        ml.badge(d, x1 - 24, y + row / 2, i, GOLD if not dark else GOLD_LT, WHITE if not dark else GREEN_DK, font(700, 28), r=23)
        d.text((x1 - 66, y + row / 2), l["name"], font=font(600, size), fill=GREEN if not dark else CREAM, anchor="rm", direction="rtl", language="ar")
        if dist:
            d.text(((dist_x if dist_x else box[0] + 26), y + row / 2), f"نحو {l['dist']} م", font=font(600, size - 6), fill=GOLD if not dark else GOLD_LT, anchor="lm", direction="rtl", language="ar")
        y += row

def callout(img, x, y, text, dark=False, side="right"):
    """bubble beside the roof (x, y = roof point); side right = bubble to the right with a tail pointing left"""
    f = font(700, 32)
    tw = f.getlength(text, direction="rtl", language="ar")
    bx = x + 70 if side == "right" else x - 70 - (tw + 64)
    box = (bx, y - 120, bx + tw + 64, y - 62)
    soft_shadow(img, box, 29, alpha=90, blur=10, off=6, rgb=(0, 20, 12))
    d = ImageDraw.Draw(img)
    fill = GOLD if dark else TEAL
    d.rounded_rectangle(box, 29, fill=fill, outline=CREAM, width=3)
    if side == "right":
        d.polygon([(box[0] + 2, box[3] - 14), (box[0] + 2, box[3] - 36), (box[0] - 22, box[3] - 8)], fill=fill)
    else:
        d.polygon([(box[2] - 2, box[3] - 14), (box[2] - 2, box[3] - 36), (box[2] + 22, box[3] - 8)], fill=fill)
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 1), text, font=f, fill=CREAM if not dark else GREEN_DK, anchor="mm", direction="rtl", language="ar")

def iso_scene(img, pal, ox, oy, width, dark):
    win = rm.window_for([l["pos"] for l in LM], pad=70)
    m3, proj = rm.iso(win, width, pal, squash=.44, inset=.17)
    fade = Image.fromarray((np.clip(np.arange(m3.size[1]) / 70, 0, 1)[:, None].repeat(m3.size[0], 1) * 255).astype("uint8"))
    a = ImageChops.multiply(m3.getchannel("A"), fade)
    m3.putalpha(a)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); lay.paste(m3, (ox, oy), m3)
    d = ImageDraw.Draw(lay)
    for n, l in enumerate(LM, 1):
        px, py = proj(l["pos"], 0); px += ox; py += oy
        d.line((px, py, px, py - 54), fill=GOLD_LT if dark else GOLD, width=3)
        ml.badge(d, px, py - 76, n, GOLD_LT if dark else GOLD, GREEN_DK if dark else WHITE, font(700, 28), r=24)
    img.paste(lay, (0, 0), lay)
    hx, hy = proj(rm.PIN, 0); hx += ox; hy += oy
    return hx, hy, m3.size

import numpy as np
from PIL import ImageChops

# ------------------------------------------------------------------------------------ 1: 3D, light
def card1():
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, H * .3, H, .1, 1))
    header(img)
    hx, hy, sz = iso_scene(img, ISO_LIGHT, 20, 180, 1040, dark=False)
    ml.pin(img, hx, hy - 30, 46, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    callout(img, hx, hy + 40, "مقر التنسيقية", side="left")
    panel = (60, 884, W - 60, 1262)
    bc.shadowed_round(img, panel, 40, CREAM, (222, 204, 168), 2, blur=14, off=7, alpha=60)
    legend(img, panel, size=30, row=62, dist_x=300)
    qr_plate(img, 84, panel[1] + 30, 150, None)
    d = ImageDraw.Draw(img)
    d.text((84 + 82, panel[1] + 30 + 150 + 28 + 26), "امسح للوصول", font=font(600, 24), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((W / 2, 1288), AREA, font=font(600, 28), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((W / 2, 1326), NOTE, font=font(500, 20), fill=(140, 128, 104), anchor="mm", direction="rtl", language="ar")
    logo(img, "rakb_green", (W - 100) // 2, 1346, w=100)
    return img

# ------------------------------------------------------------------------------------ 2: flat map + route + photo
def card2():
    img = paper(W, H, warm=True)
    img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, H * .3, H, .1, 1))
    header(img)
    mw, mh = 960, 640
    L = LM[:4]
    win = rm.window_for([l["pos"] for l in L], pad=24, aspect=mw / mh)
    mp, to = rm.flat(win, mw, FLAT_LIGHT)
    mp = mp.crop((0, 0, mw, mh))
    ox, oy = 60, 192
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((ox, oy, ox + mw, oy + mh), 40, fill=255)
    soft_shadow(img, (ox, oy, ox + mw, oy + mh), 40, alpha=80, blur=18, off=10)
    layer = Image.new("RGB", img.size); layer.paste(mp, (ox, oy)); img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((ox, oy, ox + mw, oy + mh), 40, outline=GOLD, width=4)
    for n, l in enumerate(L, 1):
        px, py = to(l["pos"]); ml.badge(d, px + ox, py + oy, n, GOLD, WHITE, font(700, 28), r=24)
    hx, hy = to(rm.PIN); hx += ox; hy += oy
    ml.pin(img, hx, hy + 4, 40, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    callout(img, hx, hy + 40, "مقر التنسيقية", side="left")
    d = ImageDraw.Draw(img)
    cx, cy = ox + 66, oy + 66
    d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=CREAM, outline=GOLD, width=3)
    d.polygon([(cx, cy - 30), (cx + 10, cy + 8), (cx, cy), (cx - 10, cy + 8)], fill=GREEN)
    d.text((cx, cy + 24), "N", font=font(700, 20), fill=GREEN, anchor="mm")
    py0 = 860
    rounded_paste(img, photo(420, 400), (60, py0, 480, py0 + 400), 36)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((70, py0 + 332, 470, py0 + 390), 20, fill=(2, 36, 22))
    d.text((270, py0 + 361), "واجهة المقر", font=font(700, 30), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    panel = (506, py0, W - 60, py0 + 400)
    bc.shadowed_round(img, panel, 36, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=55)
    legend(img, panel, size=24, row=56, lms=L)
    qr_plate(img, 530, py0 + 258, 110, None)
    d = ImageDraw.Draw(img)
    d.text((W - 60 - 28, py0 + 290), AREA, font=font(600, 24), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.text((W - 60 - 28, py0 + 328), "امسح للوصول عبر الخريطة", font=font(600, 22), fill=GOLD, anchor="rm", direction="rtl", language="ar")
    d.text((W - 60 - 28, py0 + 364), NOTE, font=font(500, 18), fill=(140, 128, 104), anchor="rm", direction="rtl", language="ar")
    logo(img, "rakb_green", (W - 100) // 2, 1296, w=100)
    return img

# ------------------------------------------------------------------------------------ 3: dark premium 3D
def card3():
    img = gradient(W, H, [(0, TEAL), (.45, (2, 52, 40)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, 620, 760, 480, (14, 128, 108), .5); img = over(img, (14, 128, 108), m)
    img = add_lattice(img, GOLD_LT, 30)
    frame(img, 34, GOLD, 3, 12, corner=0.9)
    header(img, dark=True, y=56)
    hx, hy, sz = iso_scene(img, ISO_DARK, 20, 200, 1040, dark=True)
    ml.pin(img, hx, hy - 30, 46, GOLD, ring=GREEN_DK, logo=asset("hajj_logo_white"), glow_rgb=GOLD_LT)
    callout(img, hx, hy + 40, "مقر التنسيقية", dark=True, side="left")
    panel = (70, 896, W - 70, 1272)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(panel, 38, fill=(2, 34, 22, 218), outline=GOLD + (255,), width=2)
    img.paste(lay, (0, 0), lay)
    legend(img, panel, dark=True, size=29, row=58, dist_x=290)
    qr_plate(img, 96, panel[1] + 28, 140, "امسح للوصول", dark=True)
    d = ImageDraw.Draw(img)
    d.text((W - 96, 1246), AREA, font=font(600, 24), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    d.text((W / 2, 1296), NOTE, font=font(500, 20), fill=(120, 170, 148), anchor="mm", direction="rtl", language="ar")
    logo(img, "rakb_gold", (W - 100) // 2, 1316, w=100, rgb=GOLD_LT)
    return img

# ------------------------------------------------------------------------------------ 4: modern - photo + mini map
def card4():
    img = gradient(W, H, [(0, (253, 249, 242)), (1, (243, 236, 223))], 90)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for r, a in ((330, 80), (410, 50), (490, 28)):
        ld.ellipse((W - 60 - r, 130 - r, W - 60 + r, 130 + r), outline=GOLD + (a,), width=3)
    img.paste(lay, (0, 0), lay)
    ph = (60, 40, W - 60, 440)
    rounded_paste(img, photo(960, 400), ph, 56, border=GOLD, bw=4)
    scrim = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(scrim)
    for k in range(190):
        sd.rectangle((60, 40 + k, W - 60, 41 + k), fill=(2, 36, 22, int(205 * (1 - k / 190))))
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rounded_rectangle(ph, 56, fill=255)
    sc2 = Image.new("RGBA", img.size, (0, 0, 0, 0)); sc2.paste(scrim, (0, 0), mk); img.paste(sc2, (0, 0), sc2)
    d = ImageDraw.Draw(img)
    logo(img, "hajj_logo_white", W - 60 - 40 - 84, 66, w=84)
    d.text((W - 60 - 40 - 84 - 22, 108), NAME, font=font(700, 44), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    d.text((W - 60 - 40 - 84 - 22, 62), "موقع المقر", font=font(600, 28), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    mw, mh = 960, 640
    L = LM[:3]
    win = rm.window_for([l["pos"] for l in L], pad=24, aspect=mw / mh)
    mp, to = rm.flat(win, mw, FLAT_LIGHT)
    ox, oy = 60, 470
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rounded_rectangle((ox, oy, ox + mw, oy + mh), 40, fill=255)
    soft_shadow(img, (ox, oy, ox + mw, oy + mh), 40, alpha=70, blur=14, off=8)
    layer = Image.new("RGB", img.size); layer.paste(mp.crop((0, 0, mw, mh)), (ox, oy)); img.paste(layer, (0, 0), mk)
    d = ImageDraw.Draw(img); d.rounded_rectangle((ox, oy, ox + mw, oy + mh), 40, outline=GOLD, width=3)
    for n, l in enumerate(L, 1):
        px, py = to(l["pos"]); ml.badge(d, px + ox, py + oy, n, GOLD, WHITE, font(700, 26), r=22)
    hx, hy = to(rm.PIN); hx += ox; hy += oy
    ml.pin(img, hx, hy + 4, 38, TEAL, ring=CREAM, logo=asset("hajj_logo_white"), glow_rgb=GOLD)
    callout(img, hx, hy + 40, "مقر التنسيقية", side="left")
    d = ImageDraw.Draw(img)
    # landmark chips (3 rows) + QR
    y0 = 1124
    for i, l in enumerate(L):
        f = font(600, 26)
        chip = (W - 60 - 560, y0 + i * 62, W - 60, y0 + i * 62 + 52)
        d.rounded_rectangle(chip, 26, fill=CREAM, outline=GOLD, width=2)
        ml.badge(d, chip[2] - 28, chip[1] + 26, i + 1, GOLD, WHITE, font(700, 22), r=19)
        d.text((chip[2] - 62, chip[1] + 26), l["name"], font=f, fill=GREEN, anchor="rm", direction="rtl", language="ar")
        d.text((chip[0] + 22, chip[1] + 26), f"نحو {l['dist']} م", font=font(600, 22), fill=GOLD, anchor="lm", direction="rtl", language="ar")
    qr_plate(img, 60, 1124, 128, None)
    d = ImageDraw.Draw(img)
    d.text((60 + 78, 1124 + 128 + 28 + 20), "امسح للوصول", font=font(600, 22), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((W - 60, 1334), AREA + "  -  " + NOTE, font=font(600, 22), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    logo(img, "rakb_green", (W - 84) // 2, 1358, w=70) if False else None
    return img

CARDS = [card1, card2, card3, card4]

if __name__ == "__main__":
    os.makedirs("Location", exist_ok=True)
    for i, fn in enumerate(CARDS, 1):
        fn().convert("RGB").save(f"Location/Location-{i}.png", optimize=True); print("location", i, flush=True)

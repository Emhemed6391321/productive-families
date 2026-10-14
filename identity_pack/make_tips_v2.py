#!/usr/bin/env python3
"""Four more layouts for the heat-warning tips (same text, Tripoli-B identity)."""
import os, math
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np
from pack_lib import *
import make_tips as T
from make_tips import wrap, para, sun, badge, ITEMS, MAIN, SUB, NAME, PHONE, AR
from make_welcome_set import medallion, crown, duo_photo

def txt(d, xy, t, size, fill, w=700, anchor="mm"): d.text(xy, t, font=font(w, size), fill=fill, anchor=anchor, direction="rtl", language="ar")
def footer(img, y, h, dark=True, W=None):
    W = W or img.size[0]; d = ImageDraw.Draw(img)
    d.rectangle((0, y, W, y + h), fill=GREEN_DK); d.rectangle((0, y, W, y + 5), fill=GOLD)
    txt(d, (W - 60, y + h / 2 + 3), NAME, 36, CREAM, anchor="rm"); d.text((60, y + h / 2 + 3), PHONE, font=font(700, 42), fill=GOLD_LT, anchor="lm")

# ------------------------------------------------------------ A  1080x1350 : emerald, numbered rows
def a():
    W, H = 1080, 1350; img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, 260, 700, 420, (12, 120, 100), .5); img = over(img, (12, 120, 100), m); img = add_lattice(img, GOLD_LT, 34)
    paste(img, sky_layer(W, 0.8, tint=GOLD_LT, blur=1.1), 0, 1020); frame(img, 30, GOLD, 3, 12); cx = W // 2
    sun(img, 140, 150, 46); d = ImageDraw.Draw(img)
    txt(d, (cx + 40, 150), T.TITLE1, 96, GOLD_LT); txt(d, (cx + 40, 270), T.TITLE2, 128, CREAM)
    diamond_divider(img, cx, 372, half=320, gap=34, col=GOLD_LT, width=3, size=12); d = ImageDraw.Draw(img)
    txt(d, (cx, 430), SUB, 46, GOLD_LT)
    box = (70, 480, W - 70, 660); d.rounded_rectangle(box, 34, fill=(3, 52, 38), outline=GOLD, width=3); para(d, cx, 535, MAIN, 38, CREAM, 700, 840, 1.5)
    y = 695
    for t, n in ITEMS:
        r = (70, y, W - 70, y + 118); d.rounded_rectangle(r, 30, fill=CREAM, outline=GOLD, width=2)
        badge(d, W - 70 - 62, y + 59, n, 40); para(d, W - 70 - 130, y + 59, t, 30, GREEN, 700, 780, 1.4, anchor="rm") if False else None
        f = font(700, 31); ls = wrap(f, t, 760); yy = y + 59 - (len(ls) - 1) * 21
        for i, l in enumerate(ls): d.text((W - 70 - 125, yy + i * 42), l, font=f, fill=GREEN, anchor="rm", direction="rtl", language="ar")
        y += 138
    medallion(img, cx, 1195, 0) if False else None
    footer(img, 1262, 88); return img

# ------------------------------------------------------------ B  1080x1080 : cream square, sun disc + 2x2 grid
def b():
    W = H = 1080; img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    frame(img, 30, GOLD, 3, 12); g, m = glow(W, H, W / 2, 0, 700, 360, (245, 220, 160), .6); img = over(img, (245, 220, 160), m)
    sun(img, cx, 120, 44); d = ImageDraw.Draw(img)
    txt(d, (cx, 245), T.TITLE1 + " " + T.TITLE2, 82, GREEN, maxw := None) if False else None
    f = font(700, 84); t = T.TITLE1 + " " + T.TITLE2
    d.text((cx, 245), t, font=f, fill=GREEN, anchor="mm", direction="rtl", language="ar")
    txt(d, (cx, 335), SUB, 40, GOLD)
    cells = [(MAIN, "!")] + [(t, n) for t, n in ITEMS]
    cw, ch, g_ = 470, 270, 36; x0 = (W - 2 * cw - g_) // 2; y0 = 410
    for k, (t, n) in enumerate(cells):
        col, row = k % 2, k // 2; bx = x0 + (1 - col) * (cw + g_); by = y0 + row * (ch + g_); box = (bx, by, bx + cw, by + ch)
        if k == 0:
            soft_shadow(img, box, 34, alpha=80, blur=14, off=8, rgb=(0, 20, 12)); d = ImageDraw.Draw(img); d.rounded_rectangle(box, 34, fill=GREEN, outline=GOLD, width=3); fg = CREAM
            d.ellipse((bx + cw // 2 - 34, by - 34, bx + cw // 2 + 34, by + 34), fill=GOLD, outline=CREAM, width=4); txt(d, (bx + cw // 2, by + 2), "!", 52, GREEN)
        else:
            T.card(img, box, 34, accent=False); d = ImageDraw.Draw(img); fg = GREEN; badge(d, bx + cw // 2, by, n, 34)
        para(d, bx + cw // 2, by + ch / 2 - 22 - (len(wrap(font(700, 31), t, cw - 56)) - 1) * 24 + (26 if k == 0 else 6), t, 31, fg, 700, cw - 56, 1.52)
    footer(img, 992, 88); return img

# ------------------------------------------------------------ C  1080x1920 story : photo band + stacked cards
def c():
    W, H = 1080, 1920; img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    ph = 560; layer = Image.new("RGB", img.size); layer.paste(duo_photo(W, ph, 1.2, (.7, .25)), (0, 0))
    mk = Image.fromarray((np.clip((ph - np.arange(H)) / 150, 0, 1)[:, None].repeat(W, 1) * 255).astype("uint8")); img.paste(layer, (0, 0), mk)
    sun(img, 170, 300, 56); d = ImageDraw.Draw(img)
    txt(d, (cx + 60, 210), T.TITLE1, 108, GOLD_LT); txt(d, (cx + 60, 360), T.TITLE2, 150, CREAM)
    d.rectangle((0, ph - 6, W, ph), fill=GOLD); txt(d, (cx, ph + 70), SUB, 52, GOLD)
    diamond_divider(img, cx, ph + 130, half=300, gap=34, col=GOLD, width=3, size=12); d = ImageDraw.Draw(img)
    box = (60, ph + 175, W - 60, ph + 395); soft_shadow(img, box, 36, alpha=90, blur=18, off=10, rgb=(0, 20, 12)); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 36, fill=GREEN, outline=GOLD, width=3); para(d, cx, ph + 245, MAIN, 42, CREAM, 700, 880, 1.55)
    y = ph + 430
    for t, n in ITEMS:
        r = (60, y, W - 60, y + 190); T.card(img, r, 34); d = ImageDraw.Draw(img); badge(d, W - 60 - 80, y + 95, n, 44)
        f = font(700, 40); ls = wrap(f, t, 700); yy = y + 95 - (len(ls) - 1) * 31
        for i, l in enumerate(ls): d.text((W - 60 - 150, yy + i * 62), l, font=f, fill=GREEN, anchor="rm", direction="rtl", language="ar")
        y += 215
    medallion(img, cx, 1745, 70, shadow=True); d = ImageDraw.Draw(img)
    footer(img, 1830, 90); return img

# ------------------------------------------------------------ D  1920x1080 landscape : emerald left, list right
def d_():
    W, H = 1920, 1080; img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1))
    pw = 760; pan = gradient(W, H, [(0, (0, 98, 84)), (1, (3, 56, 36))], 70); pan = add_lattice(pan, GOLD_LT, 30)
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rectangle((W - pw, 0, W, H), fill=255); img.paste(pan, (0, 0), mk); d = ImageDraw.Draw(img)
    d.rectangle((W - pw - 8, 0, W - pw, H), fill=GOLD); cxp = W - pw // 2
    sun(img, cxp, 170, 56); d = ImageDraw.Draw(img)
    txt(d, (cxp, 330), T.TITLE1, 96, GOLD_LT); txt(d, (cxp, 470), T.TITLE2, 150, CREAM)
    diamond_divider(img, cxp, 580, half=270, gap=34, col=GOLD_LT, width=3, size=12); d = ImageDraw.Draw(img)
    para(d, cxp, 660, SUB, 44, GOLD_LT, 700, 640, 1.4)
    medallion(img, cxp, 880, 96, back=(3, 56, 36)); d = ImageDraw.Draw(img)
    # list on the left (reading area)
    L, R = 70, W - pw - 70; items = [(MAIN, "!")] + ITEMS; y = 70; hs = [200, 200, 200, 200]
    for k, ((t, n), h) in enumerate(zip(items, hs)):
        box = (L, y, R, y + h)
        if k == 0:
            soft_shadow(img, box, 34, alpha=80, blur=14, off=8, rgb=(0, 20, 12)); d = ImageDraw.Draw(img); d.rounded_rectangle(box, 34, fill=GREEN, outline=GOLD, width=3); fg = CREAM
            d.ellipse((R - 100, y + h / 2 - 40, R - 20, y + h / 2 + 40), fill=GOLD, outline=CREAM, width=3); txt(d, (R - 60, y + h / 2 + 2), "!", 56, GREEN)
        else:
            T.card(img, box, 34); d = ImageDraw.Draw(img); badge(d, R - 60, y + h / 2, n, 40); fg = GREEN
        f = font(700, 38); ls = wrap(f, t, R - L - 220); yy = y + h / 2 - (len(ls) - 1) * 29
        for i, l in enumerate(ls): d.text((R - 120, yy + i * 58), l, font=f, fill=fg, anchor="rm", direction="rtl", language="ar")
        y += h + 22
    d.text((L + 10, 1030), PHONE, font=font(700, 40), fill=GREEN, anchor="lm"); txt(d, (R, 1030), NAME, 36, GREEN, anchor="rm")
    return img

BUILDS = [("1-emerald-rows-1080x1350", a), ("2-square-grid-1080x1080", b), ("3-story-1080x1920", c), ("4-landscape-1920x1080", d_)]
if __name__ == "__main__":
    for n, fn in BUILDS: fn().convert("RGB").save(f"Tips/Tips-{n}.png", optimize=True); print(n, flush=True)

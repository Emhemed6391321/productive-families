#!/usr/bin/env python3
"""'المستندات المطلوبة' card, two designs (A light / B dark), 1080x1350.
Text comes from the reference card; branding = Tripoli-B identity + Rakb al-Abrar + coordination logo."""
import sys
from PIL import Image, ImageDraw
from pack_lib import *

W, H = 1080, 1350
NAME = "تنسيقية حجاج طرابلس ب"
TITLE = "المستندات المطلوبة"
ITEMS = [
    ("document", "عدد *(2)* وضع عائلي حديث."),
    ("certificate", "عدد *(2)* شهادة ميلاد مفضلة حديثة من السجل المدني."),
    ("passport", "عدد *(2)* صورة جواز سفر ملونة على أن يكون ساري المفعول ولا تقل صلاحيته عن سنة كاملة اعتباراً من *2026/10/1م*، "
                 "كما يطلب منك إحضار جواز السفر وجميع الأوراق والمستندات المرفقة."),
    ("photos", "عدد *(4)* صور خلفية بيضاء زوم الوجه *(%80)*."),
]

# ------------------------------------------------------------------ line icons (supersampled)
def icon(kind, size, col, sw=6):
    k = 4; s = size * k
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = sw * k; c = col + (255,)
    P = lambda x, y: (x * s / 100, y * s / 100)
    if kind == "document":
        d.rounded_rectangle((*P(24, 12), *P(76, 88)), 6 * k, outline=c, width=w)
        for y in (34, 50, 66):
            d.line((*P(36, y), *P(64, y)), fill=c, width=w)
    elif kind == "certificate":
        d.rounded_rectangle((*P(10, 22), *P(90, 74)), 5 * k, outline=c, width=w)
        d.line((*P(22, 38), *P(58, 38)), fill=c, width=w); d.line((*P(22, 52), *P(46, 52)), fill=c, width=w)
        d.ellipse((*P(60, 48), *P(80, 68)), outline=c, width=w)
        d.line((*P(66, 68), *P(63, 86)), fill=c, width=w); d.line((*P(74, 68), *P(77, 86)), fill=c, width=w)
    elif kind == "passport":
        d.rounded_rectangle((*P(14, 16), *P(58, 86)), 5 * k, outline=c, width=w)
        d.rounded_rectangle((*P(42, 10), *P(86, 80)), 5 * k, outline=c, width=w)
        d.ellipse((*P(48, 28), *P(80, 60)), outline=c, width=w - k)
        d.line((*P(64, 28), *P(64, 60)), fill=c, width=w // 2); d.line((*P(48, 44), *P(80, 44)), fill=c, width=w // 2)
    elif kind == "photos":
        for dx, dy in ((10, 18), (38, 8)):
            d.rounded_rectangle((*P(dx, dy), *P(dx + 46, dy + 66)), 5 * k, outline=c, width=w)
            d.ellipse((*P(dx + 15, dy + 14), *P(dx + 31, dy + 30)), fill=c)
            d.pieslice((*P(dx + 7, dy + 36), *P(dx + 39, dy + 72)), 180, 360, fill=c)
    elif kind == "clip":
        d.rounded_rectangle((*P(22, 16), *P(78, 90)), 6 * k, outline=c, width=w)
        d.rounded_rectangle((*P(38, 8), *P(62, 24)), 4 * k, fill=c)
        for y in (42, 56, 70):
            d.line((*P(34, y), *P(66, y)), fill=c, width=w)
    return im.resize((size, size), Image.LANCZOS)

def text_h(t, size, wd, lh=1.5):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    return bc.draw_text(d, wd, 0, 0, t, size, 600, GREEN, "right", lh, measure=True)

def card_heights(size, wd, pad, mn):
    return [max(mn, text_h(t, size, wd) + 2 * pad) for _, t in ITEMS]

# ------------------------------------------------------------------ Design A (light)
def design_a():
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, H * .3, H, .1, 1))
    paste(img, sky_layer(W, 0.45), 0, H - 400)
    # header: Rakb al-Abrar (left) and the coordination logo (right)
    logo(img, "rakb_green", 60, 34, w=150)
    logo(img, "hajj_logo_white", W - 60 - 100, 30, w=100, rgb=GREEN)
    d = ImageDraw.Draw(img)
    diamond_divider(img, W / 2, 112, half=250, gap=0, size=0) if False else None
    d.text((W - 60, 196), NAME, font=font(700, 42), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    ornament_pair(img, W - 60 - 6, 262, 0, h=0) if False else None
    # title pill
    pill = (60, 226, W - 60, 314)
    soft_shadow(img, pill, 46, alpha=70, blur=16, off=8)
    g = gradient(W, H, [(0, (3, 78, 56)), (1, GREEN)], 0)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle(pill, 46, fill=255)
    img.paste(g, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(pill, 46, outline=GOLD, width=3)
    d.text((W / 2 + 20, 270), TITLE, font=font(700, 58), fill=CREAM, anchor="mm", direction="rtl", language="ar")
    d.ellipse((W - 60 - 80 - 12, 270 - 38, W - 60 - 80 + 64, 270 + 38), outline=CREAM, width=3)
    paste(img, icon("clip", 52, CREAM, 5), W - 60 - 80 + 2 - 0, 346 - 26 + 0) if False else None
    ic = icon("clip", 56, CREAM, 5); paste(img, ic, W - 60 - 22 - 56 - 0, 270 - 28)
    # cards
    size, pad = 40, 28
    x0, x1 = 60, W - 60
    tw = (x1 - x0) - 120 - 175
    hs = card_heights(size, tw, pad, 140)
    y = 342
    gap = 22
    for (kind, t), h in zip(ITEMS, hs):
        box = (x0, y, x1, y + h)
        bc.shadowed_round(img, box, 40, CREAM, (222, 204, 168), 2, blur=14, off=7, alpha=55)
        d = ImageDraw.Draw(img)
        tile = (x0 + 14, y + 14, x0 + 14 + 136, y + h - 14)
        d.rounded_rectangle(tile, 30, fill=(4, 70, 44))
        ic = icon(kind, 104, WHITE, 5)
        paste(img, ic, (tile[0] + tile[2]) / 2 - 52, (tile[1] + tile[3]) / 2 - 52)
        cx, cy = x1 - 54, y + h / 2
        d.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=GREEN)
        d.text((cx, cy), str(ITEMS.index((kind, t)) + 1), font=font(700, 42), fill=WHITE, anchor="mm")
        d.line((x1 - 108, y + 30, x1 - 108, y + h - 30), fill=(214, 196, 160), width=3)
        bc.draw_text(d, x1 - 126, x0 + 175, y + (h - text_h(t, size, tw)) / 2, t, size, 600, GREEN, "right", 1.5)
        y += h + gap
    d = ImageDraw.Draw(img)
    d.rectangle((0, H - 22, W, H), fill=GREEN); d.rectangle((0, H - 26, W, H - 22), fill=GOLD)
    return img, y

# ------------------------------------------------------------------ Design B (dark)
def design_b():
    img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, 260, 700, 380, (12, 120, 100), .5)
    img = over(img, (12, 120, 100), m)
    img = add_lattice(img, GOLD_LT, 34)
    paste(img, sky_layer(W, 0.8, tint=GOLD_LT, blur=1.1), 0, H - 480)
    frame(img, 38, GOLD, 3, 12, corner=0.9)
    # header: Rakb al-Abrar | coordination logo, centred pair; name beneath
    logo(img, "rakb_gold", W // 2 - 34 - 140, 56, w=140, rgb=GOLD_LT)
    logo(img, "hajj_logo_white", W // 2 + 34, 50, w=108)
    d = ImageDraw.Draw(img)
    d.line((W / 2, 66, W / 2, 168), fill=GOLD, width=3)
    d.text((W / 2, 212), NAME, font=font(700, 44), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W / 2, 252, half=210, gap=24, col=GOLD, width=2, size=9)
    # title cartouche with the diamond tips
    ct = (150, 280, W - 150, 368)
    d.rounded_rectangle(ct, 44, fill=(2, 36, 22, 255), outline=GOLD, width=3)
    d.rounded_rectangle((ct[0] + 8, ct[1] + 8, ct[2] - 8, ct[3] - 8), 36, outline=GOLD + (), width=1)
    d.text((W / 2, 325), TITLE, font=font(700, 58), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    for cx in (ct[0] - 30, ct[2] + 30):
        d.polygon([(cx, 324 - 22), (cx + 22, 324), (cx, 324 + 22), (cx - 22, 324)], fill=GOLD)
    size, pad = 40, 26
    x0, x1 = 60, W - 60
    tw = (x1 - x0) - 120 - 170
    hs = card_heights(size, tw, pad, 138)
    y, gap = 398, 20
    for n, ((kind, t), h) in enumerate(zip(ITEMS, hs), 1):
        box = (x0, y, x1, y + h)
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle(box, 38, fill=(2, 40, 28, 205), outline=GOLD + (230,), width=2)
        img.paste(lay, (0, 0), lay)
        d = ImageDraw.Draw(img)
        cx, cy = x1 - 62, y + h / 2
        star8(d, cx, cy, 48, fill=GOLD)
        d.text((cx, cy), str(n), font=font(700, 44), fill=GREEN_DK, anchor="mm")
        ix = x0 + 84
        d.ellipse((ix - 62, cy - 62, ix + 62, cy + 62), outline=GOLD, width=3)
        ic = icon(kind, 84, GOLD_LT, 5); paste(img, ic, ix - 42, cy - 42)
        d = ImageDraw.Draw(img)
        bc.draw_text(d, x1 - 128, x0 + 170, y + (h - text_h(t, size, tw)) / 2, t, size, 600, CREAM, "right", 1.5, hl=GOLD_LT)
        y += h + gap
    return img, y

if __name__ == "__main__":
    a, ya = design_a(); b, yb = design_b()
    print("A ends", ya, "B ends", yb)
    a.convert("RGB").save("Requirements/Requirements-A-light.png"); b.convert("RGB").save("Requirements/Requirements-B-dark.png")

#!/usr/bin/env python3
"""Adds the notice text to the supplied 1500x2000 template (template pixels untouched; text is drawn only in the empty
area between the title pill and the skyline).  Three layouts -> Notice/Notice-1..3.png"""
import os
from PIL import Image, ImageDraw
from pack_lib import *

TPL = "mapdata/template_notice.webp"
W, H = 1500, 2000
GREEN_T, BRONZE_T = (5, 64, 32), (147, 106, 52)
AREA = (70, 650, W - 70, 1478)               # safe area inside the empty region

HEAD = "تنويه"
PASS = "يجب على الحاج والمرافق أن يكون جواز سفرهما ساري المفعول إلى *11/2027م* فما فوق."
INTRO = "كما يُطلب منهم تجهيز الأوراق الآتية ابتداءً من الآن، وسيتم التواصل معكم لاحقًا لتحديد موعد التسليم، والذي سيكون *قريبًا جدًا.*"
LEAD = "والأوراق هي:"
ITEMS = [
    "سحب نموذج إقرار من الحاج بعدم أدائه فريضة الحج سابقًا (مع استثناء المرافق)، على أن يكون *ملوّنًا*، مع تعبئته وتصديقه من محرر عقود.",
    "الرقم الوطني (أصلي) *2026م*.",
    "الوضع العائلي (أصلي) *2026م*.",
    "صورة ملوّنة لجواز السفر.",
    "صورة شخصية بخلفية بيضاء، العدد *(2)*، بنظام الزووم (الوجه بارز).",
]

def th(d, t, size, wd, w=600, lh=1.5):
    return bc.draw_text(d, wd, 0, 0, t, size, w, GREEN_T, "right", lh, measure=True)

def txt(d, x0, x1, y, t, size, w=600, col=GREEN_T, align="right", lh=1.5, hl=BRONZE_T):
    return bc.draw_text(d, x1, x0, y, t, size, w, col, align, lh, hl=hl)

def heading(img, y, size=84):
    d = ImageDraw.Draw(img)
    d.text((W / 2, y), HEAD, font=font(700, size), fill=GREEN_T, anchor="mm", direction="rtl", language="ar")
    for sx in (-1, 1):
        d.line((W / 2 + sx * 100, y, W / 2 + sx * 330, y), fill=BRONZE_T, width=3)
        cx = W / 2 + sx * 348
        d.polygon([(cx, y - 13), (cx + 13, y), (cx, y + 13), (cx - 13, y)], fill=BRONZE_T)

def bullet(d, cx, cy, kind, n, r=22):
    if kind == "num":
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN_T)
        d.text((cx, cy + 1), str(n), font=font(700, 26), fill=(255, 255, 255), anchor="mm")
    elif kind == "dia":
        d.polygon([(cx, cy - 11), (cx + 11, cy), (cx, cy + 11), (cx - 11, cy)], fill=BRONZE_T)

# --------------------------------------------------------------------------- layout A
def layout_a(img, s):
    d = ImageDraw.Draw(img); x0, x1 = AREA[0], AREA[2]
    y = AREA[1] + 10
    heading(img, y + 30, int(min(84, 70 * s))); y += 82
    # passport notice: cream card with gold frame
    pw = x1 - x0
    ph = th(d, PASS, int(40 * s), pw - 80, 700, 1.45) + 40
    box = (x0, y, x1, y + ph)
    bc.shadowed_round(img, box, 40, (255, 252, 244), BRONZE_T, 3, blur=12, off=6, alpha=45); d = ImageDraw.Draw(img)
    d.rounded_rectangle((box[0] + 9, box[1] + 9, box[2] - 9, box[3] - 9), 32, outline=(222, 204, 168), width=2)
    txt(d, box[0] + 40, box[2] - 40, y + 20, PASS, int(40 * s), 700, GREEN_T, "center", 1.45); y += ph + 20
    y += txt(d, x0 + 30, x1 - 30, y, INTRO, int(33 * s), 600, GREEN_T, "center", 1.55) + 14
    d.text((x1 - 30, y + 28), LEAD, font=font(700, int(38 * s)), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar"); y += 62
    for t in ITEMS:
        h = th(d, t, int(33 * s), x1 - x0 - 150, 600, 1.45)
        bullet(d, x1 - 40, y + 25, "dia", 0)
        txt(d, x0 + 20, x1 - 80, y, t, int(33 * s), 600, GREEN_T, "right", 1.45)
        y += h + 12
    return y

# --------------------------------------------------------------------------- layout B
def layout_b(img, s):
    d = ImageDraw.Draw(img); x0, x1 = AREA[0], AREA[2]
    y = AREA[1] + 8
    heading(img, y + 30, int(min(84, 70 * s))); y += 80
    ph = th(d, PASS, int(38 * s), x1 - x0 - 160, 700, 1.5) + 54
    box = (x0, y, x1, y + ph)
    soft_shadow(img, box, 36, alpha=70, blur=14, off=7); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 36, fill=GREEN_T, outline=BRONZE_T, width=3)
    d.ellipse((x1 - 90, y + ph / 2 - 34, x1 - 22, y + ph / 2 + 34), outline=(226, 196, 132), width=4)
    d.text((x1 - 56, y + ph / 2 + 2), "!", font=font(700, 44), fill=(226, 196, 132), anchor="mm")
    txt(d, x0 + 36, x1 - 110, y + 27, PASS, int(38 * s), 700, (255, 252, 244), "right", 1.5, hl=(236, 208, 148)); y += ph + 26
    # list card
    items_h = sum(th(d, t, int(32 * s), x1 - x0 - 190, 600, 1.45) + 14 for t in ITEMS)
    ih = th(d, INTRO, int(32 * s), x1 - x0 - 100, 600, 1.55)
    ch = ih + 22 + 56 + items_h + 40
    box = (x0, y, x1, y + ch)
    bc.shadowed_round(img, box, 36, (255, 252, 244), (222, 204, 168), 2, blur=12, off=6, alpha=45); d = ImageDraw.Draw(img)
    yy = y + 20
    yy += txt(d, x0 + 50, x1 - 50, yy, INTRO, int(32 * s), 600, GREEN_T, "right", 1.55) + 14
    d.text((x1 - 50, yy + 26), LEAD, font=font(700, int(36 * s)), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar"); yy += 58
    for n, t in enumerate(ITEMS, 1):
        h = th(d, t, int(32 * s), x1 - x0 - 190, 600, 1.45)
        bullet(d, x1 - 74, yy + 24, "num", n)
        txt(d, x0 + 40, x1 - 120, yy, t, int(32 * s), 600, GREEN_T, "right", 1.45)
        yy += h + 14
    return y + ch

# --------------------------------------------------------------------------- layout C
def layout_c(img, s):
    d = ImageDraw.Draw(img); x0, x1 = AREA[0], AREA[2]
    y = AREA[1] + 8
    heading(img, y + 30, int(min(84, 70 * s))); y += 80
    # passport notice: capsule with gold double frame and medallion
    pw = x1 - x0 - 60
    ph = th(d, PASS, int(37 * s), pw - 260, 700, 1.5) + 50
    box = (x0 + 30, y, x1 - 30, y + ph)
    soft_shadow(img, box, int(ph / 2), alpha=60, blur=14, off=7); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, int(ph / 2), fill=(255, 252, 244), outline=BRONZE_T, width=4)
    d.rounded_rectangle((box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10), int(ph / 2) - 10, outline=(222, 204, 168), width=2)
    cx, cy = box[2] - 100, y + ph / 2
    d.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), fill=GREEN_T, outline=BRONZE_T, width=3)
    star8(d, cx, cy, 30, fill=(226, 196, 132)); star8(d, cx, cy, 13, fill=GREEN_T, rot=-math.pi / 2 + math.pi / 8)
    txt(d, box[0] + 50, box[2] - 190, y + 25, PASS, int(37 * s), 700, GREEN_T, "right", 1.5); y += ph + 24
    y += txt(d, x0 + 30, x1 - 30, y, INTRO, int(32 * s), 600, GREEN_T, "center", 1.55) + 12
    d.text((W / 2, y + 26), LEAD, font=font(700, int(38 * s)), fill=BRONZE_T, anchor="mm", direction="rtl", language="ar"); y += 62
    # items as a 2-column grid of cards (RTL: item 1 on the right)
    colw = (x1 - x0 - 24) // 2
    rows = [(0, 1), (2, 3), (4,)]
    for r in rows:
        wd = [(colw if len(r) > 1 else (x1 - x0)) - 120 for _ in r]
        hs = [th(d, ITEMS[i], int(30 * s), w_, 600, 1.4) for i, w_ in zip(r, wd)]
        rh = max(max(hs) + 34, 76)
        for k, i in enumerate(r):
            xr = x1 - k * (colw + 24)
            bx = (xr - colw, y, xr, y + rh) if len(r) > 1 else (x0, y, x1, y + rh)
            bc.shadowed_round(img, bx, 26, (255, 252, 244), (222, 204, 168), 2, blur=8, off=4, alpha=40); d = ImageDraw.Draw(img)
            bullet(d, bx[2] - 40, (bx[1] + bx[3]) / 2, "num", i + 1, 22)
            ty = y + (rh - hs[k]) / 2
            txt(d, bx[0] + 22, bx[2] - 80, ty, ITEMS[i], int(30 * s), 600, GREEN_T, "right", 1.4)
        y += rh + 14
    return y

LAYOUTS = [layout_a, layout_b, layout_c]

def fit(fn, s0=1.6):
    s = s0
    while s > 0.6:
        im = Image.open(TPL).convert("RGB")
        end = fn(im, s)
        if end <= AREA[3]:
            return im, s, end
        s -= 0.02
    return im, s, end

if __name__ == "__main__":
    os.makedirs("Notice", exist_ok=True)
    for i, fn in enumerate(LAYOUTS, 1):
        im, s, end = fit(fn)
        im.save(f"Notice/Notice-{i}.png", optimize=True); print(i, "scale", round(s, 2), "ends", round(end))

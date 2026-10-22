#!/usr/bin/env python3
"""Medical-examination place card (3 layouts, 1080x1350): enter the lottery number at tripoli-b.ly/medical-place."""
import math, os
import qrcode
from PIL import Image, ImageDraw
from pack_lib import *
from make_welcome_set import medallion, crown

W, H = 1080, 1350
URL = "https://tripoli-b.ly/medical-place"; SHOW = "tripoli-b.ly/medical-place"
TXT = "لمعرفة مكان الكشف الطبي لك ولمرافقك، ادخل على الرابط التالي واكتب رقم القرعة:"
STEPS = [("افتح الرابط", "من هاتفك أو حاسوبك"), ("اكتب رقم القرعة", "الخاص بك أو بمرافقك"), ("اعرف مكان الكشف", "مكان العيادة المخصصة لك")]
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
NAME, PHONE = "تنسيقية حجاج طرابلس ب", "0934455422"

def qr(size, fg, bg):
    q = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10); q.add_data(URL); q.make(fit=True)
    return q.make_image(fill_color=fg, back_color=bg).convert("RGB").resize((size, size), Image.NEAREST)
def wrap(f, text, maxw):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t, direction="rtl", language="ar") <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def para(d, cx, y, text, size, fill, w=600, maxw=880, lh=1.55):
    f = font(w, size); ls = wrap(f, text, maxw)
    for i, l in enumerate(ls): d.text((cx, y + i * size * lh), l, font=f, fill=fill, anchor="mm", direction="rtl", language="ar")
    return y + len(ls) * size * lh
def med_cross(d, cx, cy, r, fill, bg=None, ring=None):
    if bg: d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bg, outline=ring, width=4)
    a, b = r * .52, r * .17
    d.rounded_rectangle((cx - b, cy - a, cx + b, cy + a), int(b * .5), fill=fill); d.rounded_rectangle((cx - a, cy - b, cx + a, cy + b), int(b * .5), fill=fill)
def pin_icon(d, cx, cy, s, fill, hole):
    d.ellipse((cx - s, cy - s * 1.3, cx + s, cy + s * .7), fill=fill); d.polygon([(cx - s * .8, cy + s * .25), (cx + s * .8, cy + s * .25), (cx, cy + s * 1.7)], fill=fill); d.ellipse((cx - s * .42, cy - s * .7, cx + s * .42, cy + s * .14), fill=hole)
def link_pill(img, cy, dark=False, w=860):
    d = ImageDraw.Draw(img); box = (W // 2 - w // 2, cy - 48, W // 2 + w // 2, cy + 48)
    soft_shadow(img, box, 48, alpha=70, blur=12, off=6); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 48, fill=CREAM if dark else GREEN, outline=GOLD, width=3)
    f = ImageFont_latin(46); d.text((W // 2, cy + 2), SHOW, font=f, fill=GREEN if dark else GOLD_LT, anchor="mm")
def ImageFont_latin(sz):
    from PIL import ImageFont; return ImageFont.truetype("fonts/IBMPlexSansArabic-700.ttf", sz) if os.path.exists("fonts/IBMPlexSansArabic-700.ttf") else font(700, sz)
def footer(img, dark=False):
    d = ImageDraw.Draw(img); d.rectangle((0, H - 78, W, H), fill=GREEN_DK); d.rectangle((0, H - 78, W, H - 73), fill=GOLD)
    d.text((W - 60, H - 38), NAME, font=font(700, 32), fill=CREAM, anchor="rm", direction="rtl", language="ar"); d.text((60, H - 38), PHONE, font=font(700, 36), fill=GOLD_LT, anchor="lm")

# ---- A: cream, medallion + QR hero
def a():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); frame(img, 26, GOLD, 3, 12); cx = W // 2
    paste(img, sky_layer(W, .45), 0, 1050)
    medallion(img, 150, 150, 70, shadow=False); d = ImageDraw.Draw(img)
    d.text((W - 70, 120), "الهيئة العامة لشؤون الحج والعمرة", font=font(600, 28), fill=GREEN, anchor="rm", direction="rtl", language="ar"); d.text((W - 70, 166), NAME, font=font(700, 44), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    med_cross(d, cx, 330, 80, WHITE, GREEN, GOLD)
    d.text((cx, 470), "الكشف الطبي", font=font(700, 118), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((cx, 570), "اعرف مكان عيادتك بنقرة واحدة", font=font(700, 48), fill=GOLD, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, cx, 625, half=300, gap=30, col=GOLD, width=3, size=11); d = ImageDraw.Draw(img)
    para(d, cx, 700, TXT, 38, (70, 60, 40), 600, 900)
    q = qr(250, (4, 40, 24), (255, 255, 255)); qb = (W - 70 - 290, 810, W - 70, 1100); soft_shadow(img, qb, 30, alpha=80, blur=14, off=7); d = ImageDraw.Draw(img)
    d.rounded_rectangle(qb, 30, fill=WHITE, outline=GOLD, width=4); img.paste(q, (qb[0] + 20, qb[1] + 20))
    d.text((qb[0] - 40, 880), "امسح الرمز", font=font(700, 42), fill=GREEN, anchor="rm", direction="rtl", language="ar"); d.text((qb[0] - 40, 935), "أو افتح الرابط أدناه", font=font(500, 30), fill=GOLD, anchor="rm", direction="rtl", language="ar")
    link_pill(img, 1180); footer(img); return img

# ---- B: emerald with 3 steps
def b():
    img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90); g, m = glow(W, H, W / 2, 300, 700, 420, (12, 120, 100), .5); img = over(img, (12, 120, 100), m); img = add_lattice(img, GOLD_LT, 32)
    frame(img, 26, GOLD, 3, 12); cx = W // 2; d = ImageDraw.Draw(img)
    medallion(img, cx, 170, 90, back=(3, 56, 36), shadow=True); d = ImageDraw.Draw(img)
    d.text((cx, 340), "الكشف الطبي", font=font(700, 100), fill=CREAM, anchor="mm", direction="rtl", language="ar")
    d.text((cx, 425), "لك ولمرافقك", font=font(700, 52), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    para(d, cx, 520, TXT, 36, CREAM, 600, 900)
    y = 610
    for i, (t, s) in enumerate(STEPS):
        r = (70, y, W - 70, y + 120); d.rounded_rectangle(r, 34, fill=CREAM, outline=GOLD, width=3)
        d.ellipse((W - 70 - 110, y + 15, W - 70 - 20, y + 105), fill=GREEN, outline=GOLD, width=4); d.text((W - 70 - 65, y + 62), str(i + 1).translate(AR), font=font(700, 52), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
        d.text((W - 70 - 140, y + 46), t, font=font(700, 44), fill=GREEN, anchor="rm", direction="rtl", language="ar"); d.text((W - 70 - 140, y + 92), s, font=font(500, 29), fill=(120, 90, 40), anchor="rm", direction="rtl", language="ar")
        if i == 1: pass
        y += 136
    q = qr(170, (4, 40, 24), (255, 255, 255)); d.rounded_rectangle((70, 1040, 70 + 210, 1040 + 210), 26, fill=WHITE, outline=GOLD, width=3); img.paste(q, (90, 1060))
    link_pill(img, 1180, dark=True, w=700) if False else None
    d.rounded_rectangle((310, 1060, W - 70, 1156), 48, fill=CREAM, outline=GOLD, width=3); d.text(((310 + W - 70) / 2, 1109), SHOW, font=ImageFont_latin(40), fill=GREEN, anchor="mm")
    d.text(((310 + W - 70) / 2, 1205), "اكتب رقم القرعة في الصفحة", font=font(600, 34), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    footer(img); return img

# ---- C: arch photo band + big link
def c():
    img = paper(W, H); img = add_lattice(img, (205, 183, 140), 36, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    band = gradient(W, 470, [(0, (0, 98, 84)), (1, (3, 60, 38))], 70); img.paste(band, (0, 0)); lp = star_field(W, 470, 200, GOLD_LT + (40,), 2); img.paste(lp, (0, 0), lp)
    d = ImageDraw.Draw(img); medallion(img, 150, 140, 72, back=(3, 56, 36), shadow=False); d = ImageDraw.Draw(img)
    d.text((W - 60, 100), "الهيئة العامة لشؤون الحج والعمرة", font=font(600, 28), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar"); d.text((W - 60, 150), NAME, font=font(700, 46), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    d.rectangle((0, 462, W, 470), fill=GOLD)
    med_cross(d, cx, 262, 64, GREEN, CREAM, GOLD); d.text((cx, 390), "الكشف الطبي", font=font(700, 84), fill=CREAM, anchor="mm", direction="rtl", language="ar")
    para(d, cx, 560, TXT, 38, (60, 50, 30), 600, 900)
    q = qr(300, (4, 40, 24), (255, 255, 255)); box = (cx - 180, 700, cx + 180, 1060); soft_shadow(img, box, 36, alpha=80, blur=16, off=8); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 36, fill=WHITE, outline=GOLD, width=5); img.paste(q, (cx - 150, 730))
    d.text((cx, 1085), "امسح الرمز أو افتح الرابط", font=font(700, 34), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    link_pill(img, 1170); footer(img); return img

if __name__ == "__main__":
    for n, fn in (("1-cream", a), ("2-steps", b), ("3-band", c)): fn().convert("RGB").save(f"Medical/Medical-{n}.png", optimize=True); print(n, flush=True)

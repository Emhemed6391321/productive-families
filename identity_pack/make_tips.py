#!/usr/bin/env python3
"""Pilgrim safety-tips poster (same guidance as the reference, Tripoli-B identity). 1080 x 1620, no third-party logos."""
import os, math
from PIL import Image, ImageDraw, ImageFilter
from pack_lib import *

W, H = 1080, 1620
TITLE1, TITLE2 = "تنبيهات مهمة", "للحجاج"
SUB = "ضيف الرحمن نظرًا لشدة حرارة الشمس"
MAIN = "التزم بالبقاء في المخيم يوم عرفة من 10 صباحًا حتى 4 عصرًا، وتجنب الخروج لمسجد نمرة أو جبل الرحمة"
ITEMS = [("اتبع جداول التفويج المعتمدة ولا تخالفها أثناء التنقل بين المشاعر", "1"),
         ("استخدم وسائل النقل الرسمية فقط، وتجنب المشي بين المشاعر", "2"),
         ("احمل بطاقة «نسك» دائمًا وأبرزها عند الطلب", "3")]
NAME, PHONE = "تنسيقية حجاج طرابلس ب", "0934455422"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

def wrap(f, text, maxw):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t, direction="rtl", language="ar") <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

def para(d, cx, y, text, size, fill, w=600, maxw=800, lh=1.55, anchor="mm"):
    f = font(w, size); ls = wrap(f, text, maxw)
    for i, l in enumerate(ls): d.text((cx, y + i * size * lh), l, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar")
    return y + len(ls) * size * lh

def sun(img, cx, cy, r):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(16):
        a = math.radians(k * 22.5); r0, r1 = r * 1.25, r * (1.75 if k % 2 == 0 else 1.5)
        d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=GOLD_LT + (255,), width=max(4, int(r * .12)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD + (255,)); d.ellipse((cx - r * .72, cy - r * .72, cx + r * .72, cy + r * .72), fill=GOLD_LT + (255,))
    img.paste(lay, (0, 0), lay)

def umbrella(img, cx, cy, s, tilt=0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # canopy: half-ellipse with scalloped edge, white with soft green ribs
    top, bot = cy - s * .55, cy
    d.pieslice((cx - s, top - s * .1, cx + s, bot + s * .55), 180, 360, fill=(255, 255, 255, 255), outline=GREEN + (255,), width=max(3, int(s * .03)))
    n = 4
    for k in range(1, n):
        x = cx - s + 2 * s * k / n; d.line((cx, top + s * .0, x, bot + s * .04), fill=(190, 205, 195, 255), width=max(2, int(s * .015)))
    for k in range(n):
        x0 = cx - s + 2 * s * k / n; x1 = cx - s + 2 * s * (k + 1) / n
        d.pieslice((x0, bot - s * .16, x1, bot + s * .16), 0, 180, fill=(255, 255, 255, 255), outline=GREEN + (255,), width=max(2, int(s * .02)))
    d.line((cx, bot, cx, bot + s * 1.0), fill=GREEN + (255,), width=max(4, int(s * .045)))
    d.arc((cx - s * .16, bot + s * .88, cx + s * .0, bot + s * 1.12), 0, 180, fill=GREEN + (255,), width=max(4, int(s * .045)))
    lay = lay.rotate(tilt, center=(cx, cy), resample=Image.BICUBIC)
    sh = lay.filter(ImageFilter.GaussianBlur(s * .05)); sh = Image.composite(Image.new("RGBA", img.size, (0, 40, 25, 60)), Image.new("RGBA", img.size, (0, 0, 0, 0)), sh.getchannel("A"))
    img.paste(sh, (int(s * .04), int(s * .06)), sh); img.paste(lay, (0, 0), lay)

def card(img, box, r=34, accent=True):
    soft_shadow(img, box, r, alpha=55, blur=14, off=7)
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, r, fill=CREAM, outline=(222, 204, 168), width=2)
    if accent: d.rounded_rectangle((box[2] - 14, box[1] + 26, box[2] - 6, box[3] - 26), 4, fill=GOLD)

def badge(d, cx, cy, n, r=36):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GREEN, outline=GOLD, width=4)
    d.text((cx, cy + 2), n.translate(AR), font=font(700, int(r * 1.05)), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")

def build():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); cx = W // 2
    paste(img, sky_layer(W, 0.7), 0, 1250)
    # sky-like soft glow at top (heat / sun)
    g, m = glow(W, H, W * .86, 120, 420, 320, (245, 220, 160), .55); img = over(img, (245, 220, 160), m)
    sun(img, 150, 150, 54)
    d = ImageDraw.Draw(img)
    # title block
    d.text((cx + 40, 195), TITLE1, font=font(700, 112), fill=TEAL, anchor="mm", direction="rtl", language="ar")
    d.text((cx + 40, 350), TITLE2, font=font(700, 150), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    f = font(700, 150); tl = f.getlength(TITLE2, direction="rtl", language="ar")
    diamond_divider(img, cx, 500, half=330, gap=34, col=GOLD, width=3, size=13)
    d = ImageDraw.Draw(img)
    d.text((cx, 565), SUB, font=font(700, 52), fill=GOLD, anchor="mm", direction="rtl", language="ar")
    # main instruction (wide emerald panel)
    box = (60, 625, W - 60, 830); soft_shadow(img, box, 36, alpha=90, blur=18, off=10, rgb=(0, 20, 12)); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 36, fill=GREEN, outline=GOLD, width=3); d.rounded_rectangle((box[0] + 12, box[1] + 12, box[2] - 12, box[3] - 12), 26, outline=GOLD_LT, width=1)
    para(d, cx, 688, MAIN, 42, CREAM, 700, 860, 1.55)
    # three tips
    cw, gap = 300, 30; x0 = (W - (3 * cw + 2 * gap)) // 2; y0, y1 = 880, 1150
    for i, (t, n) in enumerate(ITEMS):
        bx = x0 + (2 - i) * (cw + gap)                    # RTL: first tip on the right
        box = (bx, y0, bx + cw, y1); card(img, box, 32, accent=False); d = ImageDraw.Draw(img)
        badge(d, bx + cw // 2, y0, n)
        para(d, bx + cw // 2, y0 + 78, t, 32, GREEN, 700, cw - 44, 1.5)
    # umbrellas + pilgrims' shade motif over the skyline
    from make_welcome_set import medallion
    medallion(img, cx, 1330, 118, back=(3, 56, 36))
    d = ImageDraw.Draw(img)
    # footer
    d.rectangle((0, 1500, W, H), fill=GREEN_DK); d.rectangle((0, 1500, W, 1506), fill=GOLD)
    d.text((W - 60, 1560), NAME, font=font(700, 38), fill=CREAM, anchor="rm", direction="rtl", language="ar")
    d.text((W - 60, 1604), "بالتوفيق والسلامة إن شاء الله", font=font(500, 24), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar") if False else None
    d.text((60, 1556), PHONE, font=font(700, 44), fill=GOLD_LT, anchor="lm")
    from make_rollup import smooth
    return img

if __name__ == "__main__":
    im = build().convert("RGB"); im.save("Tips/Tips-heat-warning.png", optimize=True); print(im.size)

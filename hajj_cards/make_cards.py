#!/usr/bin/env python3
"""Generate Arabic Hajj cards (PNG). Usage: python3 make_cards.py [--page "اسم الصفحة"] [--size 1080x1080]"""
import argparse, glob, math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GOLD = (222, 184, 98)
CARDS = [  # (palette, title, body, small line)
    ("green", "حجًّا مبرورًا", "وسعيًا مشكورًا\nوذنبًا مغفورًا", "تقبّل الله منكم"),
    ("night", "لبّيك اللهم لبّيك", "لبّيك لا شريك لك لبّيك\nإنّ الحمد والنعمة لك والملك\nلا شريك لك", "تلبية الحجيج"),
    ("green", "الحج المبرور", "ليس له جزاء\nإلا الجنة", "متفق عليه"),
    ("teal", "ضيوف الرحمن", "أهلًا بكم\nفي أطهر البقاع", "حجًّا ميسّرًا وقلوبًا مطمئنة"),
    ("night", "عيد مبارك", "تقبّل الله طاعاتكم\nوكل عام وأنتم بخير", "عيد الأضحى المبارك"),
    ("green", "الحج القادم", "هل أنت مستعد؟", "{page}"),
]
PALETTES = {"green": ((6, 78, 59), (2, 32, 24)), "night": ((16, 32, 64), (4, 10, 28)),
            "teal": ((8, 92, 98), (3, 36, 46))}

def font(sz, bold=True):
    for pat in ("/usr/share/fonts/**/*Amiri*.ttf", "/usr/share/fonts/**/*Cairo*.ttf",
                "/usr/share/fonts/**/DejaVuSans-Bold.ttf", "/usr/share/fonts/**/FreeSerifBold.ttf"):
        h = glob.glob(pat, recursive=True)
        if h:
            return ImageFont.truetype(h[0], sz)
    raise SystemExit("no Arabic font")

def star(d, cx, cy, r, fill=None, outline=None, width=2):
    pts = []
    for i in range(16):
        a = math.pi * i / 8 - math.pi / 2
        rr = r if i % 2 == 0 else r * 0.62
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)

def background(w, h, pal):
    top, bot = PALETTES[pal]
    img = Image.new("RGB", (w, h))
    px = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        px.line((0, y, w, y), fill=tuple(int(top[i] * (1 - t) + bot[i] * t) for i in range(3)))
    pat = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(pat)
    step = w // 6
    for gy in range(-1, h // step + 2):
        for gx in range(-1, w // step + 2):
            star(d, gx * step, gy * step, step * .42, outline=GOLD + (38,), width=2)
            star(d, gx * step + step // 2, gy * step + step // 2, step * .2, outline=GOLD + (28,), width=1)
    img.paste(pat, (0, 0), pat)
    # soft centre glow
    glow = Image.new("L", (w, h), 0)
    ImageDraw.Draw(glow).ellipse((w * .15, h * .2, w * .85, h * .8), fill=90)
    glow = glow.filter(ImageFilter.GaussianBlur(w // 5))
    img = Image.composite(Image.new("RGB", (w, h), (20, 110, 80)), img, glow.point(lambda v: v // 3))
    return img

def text_w(d, t, f):
    b = d.textbbox((0, 0), t, font=f, direction="rtl", language="ar")
    return b[2] - b[0], b[3] - b[1], b

def center(d, t, f, y, w, fill, stroke=0):
    tw, th, b = text_w(d, t, f)
    d.text(((w - tw) // 2 - b[0], y), t, font=f, fill=fill, direction="rtl", language="ar",
           stroke_width=stroke, stroke_fill=(0, 0, 0))
    return th

def fit(d, t, size, maxw):
    while size > 24:
        f = font(size)
        if max(text_w(d, ln, f)[0] for ln in t.split("\n")) <= maxw:
            return f
        size -= 4
    return font(24)

def card(idx, spec, w, h, page):
    pal, title, body, small = spec
    img = background(w, h, pal)
    d = ImageDraw.Draw(img)
    m = int(w * .045)
    d.rectangle((m, m, w - m, h - m), outline=GOLD, width=4)
    d.rectangle((m * 1.6, m * 1.6, w - m * 1.6, h - m * 1.6), outline=GOLD + (), width=1)
    for cx, cy in ((m, m), (w - m, m), (m, h - m), (w - m, h - m)):
        star(d, cx, cy, m * .9, fill=GOLD)
    star(d, w // 2, int(h * .17), w * .07, fill=GOLD)
    star(d, w // 2, int(h * .17), w * .045, fill=PALETTES[pal][1])
    maxw = w * .78
    ft = fit(d, title, int(w * .115), maxw)
    y = int(h * .27)
    y += center(d, title, ft, y, w, GOLD, 1) + int(h * .05)
    d.line((w * .3, y, w * .7, y), fill=GOLD, width=3)
    y += int(h * .05)
    fb = fit(d, body, int(w * .075), maxw)
    for ln in body.split("\n"):
        y += center(d, ln, fb, y, w, (255, 255, 255), 1) + int(h * .025)
    small = small.format(page=page)
    if small.strip():
        fs = fit(d, small, int(w * .05), maxw)
        center(d, small, fs, int(h * .86), w, GOLD)
    return img

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="")
    ap.add_argument("--size", default="1080x1080")
    ap.add_argument("--out", default="out")
    a = ap.parse_args()
    w, h = map(int, a.size.split("x"))
    os.makedirs(a.out, exist_ok=True)
    for i, spec in enumerate(CARDS, 1):
        p = f"{a.out}/card{i}.png"
        card(i, spec, w, h, a.page).save(p)
        print(p)

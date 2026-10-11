#!/usr/bin/env python3
"""Announcement card: the required documents (final text, condensed).  Theme A light / B dark."""
from PIL import Image, ImageDraw
from pack_lib import *
from make_requirements import icon

W, M, GAP = 1080, 60, 16
NAME = "تنسيقية حجاج طرابلس ب"
TITLE = "إعلان بشأن المستندات المطلوبة"
INTRO = "على الحجاج المعنيين تجهيز المستندات التالية، مع الالتزام بالشروط لاستيفاء متطلبات التسجيل:"
ITEMS = [
    ("document", "عدد *(2)* إفادة وضع عائلي حديثة."),
    ("certificate", "عدد *(2)* شهادة ميلاد مفصّلة حديثة من السجل المدني."),
    ("passport", "عدد *(2)* صورة ملونة من جواز السفر، ساري المفعول لمدة لا تقل عن سنة كاملة اعتباراً من *01/10/2027*."),
    ("photos", "عدد *(4)* صور شخصية حديثة بخلفية بيضاء، والوجه واضح."),
]
NOTICE = "*تنبيه مهم:* أحضر جواز السفر الأصلي مع جميع المستندات المطلوبة، وتأكد من اكتمالها وحداثتها قبل الحضور."
DUA = "نسأل الله أن ييسّر أموركم، ويكتب لكم\n*حجًّا مبرورًا وسعيًا مشكورًا وذنبًا مغفورًا*"

def th(t, size, wd, lh=1.45, w=600):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    return bc.draw_text(d, wd, 0, 0, t, size, w, GREEN, "right", lh, measure=True)

def megaphone(size, col):
    k = 4; s = size * k; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda x, y: (x * s / 100, y * s / 100); c = col + (255,); w = 5 * k
    d.polygon([P(14, 40), P(40, 40), P(80, 16), P(80, 84), P(40, 60), P(14, 60)], outline=c, width=w)
    d.line((*P(30, 62), *P(36, 86)), fill=c, width=w); d.line((*P(88, 38), *P(88, 62)), fill=c, width=w)
    return im.resize((size, size), Image.LANCZOS)

def build(theme, H, s):
    dark = theme == "B"
    if dark:
        img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
        g, m = glow(W, H, W / 2, 230, 720, 360, (12, 120, 100), .5); img = over(img, (12, 120, 100), m)
        img = add_lattice(img, GOLD_LT, 34)
        paste(img, sky_layer(W, 0.45, tint=GOLD_LT, blur=1.1), 0, H - 300)
        frame(img, 30, GOLD, 3, 11, corner=0.9)
    else:
        img = paper(W, H)
        img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, H * .3, H, .1, 1))
        paste(img, sky_layer(W, 0.5), 0, H - 300)
    d = ImageDraw.Draw(img)
    ink = CREAM if dark else GREEN
    # ---- hero
    lw = 98
    logo(img, "hajj_logo_white", (W - lw) // 2, 34, w=lw, rgb=None if dark else GREEN)
    plate = (M + 20, 148, W - M - 20, 234)
    if dark:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(plate, 47, fill=(2, 34, 22, 235)); img.paste(lay, (0, 0), lay)
        d = ImageDraw.Draw(img); d.rounded_rectangle(plate, 47, outline=GOLD, width=3)
    else:
        bc.shadowed_round(img, plate, 47, CREAM, GOLD, 3, blur=14, off=7, alpha=60); d = ImageDraw.Draw(img)
    d.rounded_rectangle((plate[0] + 8, plate[1] + 8, plate[2] - 8, plate[3] - 8), 40, outline=GOLD, width=1)
    f = font(700, 62); tw_ = f.getlength(NAME, direction="rtl", language="ar"); cy = (plate[1] + plate[3]) / 2 + 2
    d.text((W / 2, cy), NAME, font=f, fill=GOLD_LT if dark else GREEN, anchor="mm", direction="rtl", language="ar")
    for sx in (-1, 1):
        cx = W / 2 + sx * (tw_ / 2 + 40)
        d.polygon([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)], fill=GOLD)
    # ---- title bar
    bar = (M, 254, W - M, 324)
    if dark:
        d.rounded_rectangle(bar, 38, fill=(3, 60, 44), outline=GOLD, width=2); tcol = GOLD_LT
    else:
        soft_shadow(img, bar, 38, alpha=55, blur=12, off=6)
        gg = gradient(W, H, [(0, (3, 78, 56)), (1, GREEN)], 0)
        mm = Image.new("L", (W, H), 0); ImageDraw.Draw(mm).rounded_rectangle(bar, 38, fill=255); img.paste(gg, (0, 0), mm)
        d = ImageDraw.Draw(img); d.rounded_rectangle(bar, 38, outline=GOLD, width=2); tcol = CREAM
    d = ImageDraw.Draw(img)
    d.text((W / 2 + 24, 289), TITLE, font=font(700, 46), fill=tcol, anchor="mm", direction="rtl", language="ar")
    d.ellipse((W - M - 68, 289 - 26, W - M - 16, 289 + 26), outline=tcol, width=3)
    paste(img, megaphone(34, tcol), W - M - 42 - 17, 289 - 17)
    # ---- intro
    y = 340
    ih = bc.draw_text(d, W - M - 10, M + 10, y, INTRO, s - 2, 600, ink, "center", 1.45)
    y += ih + 14
    # ---- items
    tw = (W - 2 * M) - 130 - 122 - 16
    hs = [max(96, th(t, s, tw) + 2 * 20) for _, t in ITEMS]
    x0, x1 = M, W - M
    for n, ((kind, t), h) in enumerate(zip(ITEMS, hs), 1):
        box = (x0, y, x1, y + h); cy = y + h / 2
        if dark:
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(box, 34, fill=(2, 40, 28, 210), outline=GOLD + (235,), width=2); img.paste(lay, (0, 0), lay)
            d = ImageDraw.Draw(img)
            star8(d, x1 - 56, cy, 42, fill=GOLD); d.text((x1 - 56, cy), str(n), font=font(700, 40), fill=GREEN_DK, anchor="mm")
            ix = x0 + 14 + 55
            d.ellipse((ix - 48, cy - 48, ix + 48, cy + 48), outline=GOLD, width=3)
            paste(img, icon(kind, 66, GOLD_LT, 5), ix - 33, cy - 33); col, hcol = CREAM, GOLD_LT
        else:
            bc.shadowed_round(img, box, 34, CREAM, (222, 204, 168), 2, blur=10, off=5, alpha=48); d = ImageDraw.Draw(img)
            tile = (x0 + 10, y + 10, x0 + 10 + 110, y + h - 10)
            d.rounded_rectangle(tile, 24, fill=(4, 70, 44)); paste(img, icon(kind, 76, WHITE, 5), (tile[0] + tile[2]) / 2 - 38, cy - 38)
            d.ellipse((x1 - 56 - 32, cy - 32, x1 - 56 + 32, cy + 32), fill=GREEN)
            d.text((x1 - 56, cy), str(n), font=font(700, 38), fill=WHITE, anchor="mm")
            d.line((x1 - 102, y + 24, x1 - 102, y + h - 24), fill=(214, 196, 160), width=3); col, hcol = GREEN, GOLD
        bc.draw_text(d, x1 - 122, x1 - 122 - tw, y + (h - th(t, s, tw)) / 2, t, s, 600, col, "right", 1.45, hl=hcol)
        y += h + GAP
    # ---- notice (bronze panel)
    ntw = (W - 2 * M) - 120 - 50
    nh = th(NOTICE, s - 2, ntw) + 2 * 22
    nb = (M, y, W - M, y + nh)
    if dark:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(nb, 34, fill=GOLD + (60,), outline=GOLD + (255,), width=2); img.paste(lay, (0, 0), lay)
    else:
        soft_shadow(img, nb, 34, alpha=60, blur=10, off=5); d = ImageDraw.Draw(img); d.rounded_rectangle(nb, 34, fill=BRONZE)
    d = ImageDraw.Draw(img)
    cx, cy = W - M - 60, y + nh / 2
    d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=GOLD_LT if not dark else GOLD)
    d.text((cx, cy + 1), "!", font=font(700, 44), fill=BRONZE if not dark else GREEN_DK, anchor="mm")
    bc.draw_text(d, W - M - 110, W - M - 110 - ntw, y + 22, NOTICE, s - 2, 600, WHITE if not dark else CREAM, "right", 1.45, hl=HL if (HL := (255, 232, 176)) else GOLD)
    y += nh + 18
    # ---- dua (on a soft plate so it stays readable over the skyline)
    dh = th(DUA, s - 2, W - 2 * M - 80, 1.5, 700) + 2 * 14
    db = (M + 30, y, W - M - 30, y + dh)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(db, 30, fill=(2, 34, 22, 200) if dark else (255, 252, 244, 215))
    img.paste(lay, (0, 0), lay); d = ImageDraw.Draw(img)
    bc.draw_text(d, W - M - 50, M + 50, y + 14, DUA, s - 2, 700, GREEN if not dark else CREAM, "center", 1.5, hl=GOLD if not dark else GOLD_LT)
    y += dh
    return img, y

def fit(theme, H):
    for s in (40, 38, 36, 35, 34, 33, 32, 30):
        img, y = build(theme, H, s)
        if y <= H - 112:
            return img, s, y
    return img, s, y

if __name__ == "__main__":
    import os; os.makedirs("Requirements", exist_ok=True)
    H = int(os.environ.get("CARD_H", "1350"))
    for th_, name in (("A", "Announcement-A-light"), ("B", "Announcement-B-dark")):
        img, s, y = fit(th_, H)
        # footer: Rakb al-Abrar logo centred
        d = ImageDraw.Draw(img); fy = H - 58
        rk = fit_w(asset("rakb_green"), 100) if th_ == "A" else fit_w(tinted("rakb_gold", GOLD_LT), 100)
        paste(img, rk, (W - rk.size[0]) // 2, fy - rk.size[1] // 2)
        for sx in (-1, 1):
            d.line((W / 2 + sx * 100, fy, W / 2 + sx * 300, fy), fill=GOLD, width=2)
            cx = W / 2 + sx * 314; d.polygon([(cx, fy - 8), (cx + 8, fy), (cx, fy + 8), (cx - 8, fy)], fill=GOLD)
        img.convert("RGB").save(f"Requirements/{name}-{W}x{H}.png"); print(th_, "font", s, "content ends", round(y), "of", H)

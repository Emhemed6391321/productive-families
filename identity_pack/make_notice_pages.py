#!/usr/bin/env python3
"""Notice text at roughly double size: the text is split over two pages on the same template.
Page 1 = notice + passport condition + intro; page 2 = the list of papers.  Three styles -> Notice/Big-<style>-page<1|2>.png"""
import os
from PIL import Image, ImageDraw
from pack_lib import *
import make_notice as N
from make_notice import GREEN_T, BRONZE_T, PASS, INTRO, LEAD, ITEMS, th, txt, bullet, heading

W = 1500
X0, X1 = 70, W - 70
TOP, BOT = 645, 1486
CREAM_C, LINE_C = (255, 252, 244), (222, 204, 168)

def card(img, box, r, fill=CREAM_C, outline=LINE_C, width=2, shadow=True):
    if shadow: bc.shadowed_round(img, box, r, fill, outline, width, blur=12, off=6, alpha=45)
    else: ImageDraw.Draw(img).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def page1(img, y, s, style):
    d = ImageDraw.Draw(img)
    hs = int(min(120, 70 * s))
    heading(img, y + hs // 2 + 6, hs); y += hs + 34
    pf = int(36 * s)
    if style == "B":
        ph = th(d, PASS, pf, X1 - X0 - 230, 700, 1.36) + 60
        box = (X0, y, X1, y + ph)
        soft_shadow(img, box, 40, alpha=70, blur=14, off=7); d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, 40, fill=GREEN_T, outline=BRONZE_T, width=3)
        cx, cy = X1 - 70, y + ph / 2
        d.ellipse((cx - 42, cy - 42, cx + 42, cy + 42), outline=(226, 196, 132), width=5)
        d.text((cx, cy + 3), "!", font=font(700, 54), fill=(226, 196, 132), anchor="mm")
        txt(d, X0 + 40, X1 - 140, y + 30, PASS, pf, 700, (255, 252, 244), "right", 1.36, hl=(236, 208, 148)); y += ph + 28
    elif style == "C":
        ph = th(d, PASS, pf, X1 - X0 - 330, 700, 1.36) + 60
        box = (X0, y, X1, y + ph)
        card(img, box, 70, CREAM_C, BRONZE_T, 4); d = ImageDraw.Draw(img)
        d.rounded_rectangle((box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10), 60, outline=LINE_C, width=2)
        cx, cy = X1 - 105, y + ph / 2
        d.ellipse((cx - 56, cy - 56, cx + 56, cy + 56), fill=GREEN_T, outline=BRONZE_T, width=3)
        star8(d, cx, cy, 34, fill=(226, 196, 132)); star8(d, cx, cy, 15, fill=GREEN_T, rot=-math.pi / 2 + math.pi / 8)
        txt(d, X0 + 50, X1 - 200, y + 30, PASS, pf, 700, GREEN_T, "right", 1.36); y += ph + 28
    else:
        ph = th(d, PASS, pf, X1 - X0 - 90, 700, 1.36) + 54
        box = (X0, y, X1, y + ph)
        card(img, box, 44, CREAM_C, BRONZE_T, 3); d = ImageDraw.Draw(img)
        d.rounded_rectangle((box[0] + 9, box[1] + 9, box[2] - 9, box[3] - 9), 36, outline=LINE_C, width=2)
        txt(d, X0 + 45, X1 - 45, y + 27, PASS, pf, 700, GREEN_T, "center", 1.36); y += ph + 28
    bf = int(32 * s)
    if style == "B":
        ih = th(d, INTRO, bf, X1 - X0 - 90, 600, 1.4) + 50
        box = (X0, y, X1, y + ih); card(img, box, 40); d = ImageDraw.Draw(img)
        txt(d, X0 + 45, X1 - 45, y + 25, INTRO, bf, 600, GREEN_T, "right", 1.4); y += ih
    else:
        y += txt(d, X0 + 10, X1 - 10, y, INTRO, bf, 600, GREEN_T, "center", 1.4)
    return y

def page2(img, y, s, style):
    d = ImageDraw.Draw(img)
    lf = int(40 * s)
    d.text((X1 - 20, y + lf * 0.7), LEAD, font=font(700, lf), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar"); y += int(lf * 1.6)
    bf = int(34 * s)
    for n, t in enumerate(ITEMS, 1):
        if style == "A":
            h = th(d, t, bf, X1 - X0 - 130, 600, 1.34)
            bullet(d, X1 - 28, y + bf * 0.75, "dia", n)
            txt(d, X0, X1 - 70, y, t, bf, 600, GREEN_T, "right", 1.34); y += h + int(bf * 0.35)
        else:
            tw = X1 - X0 - 120
            h = th(d, t, bf, tw, 600, 1.34)
            ch = h + 34
            box = (X0, y, X1, y + ch)
            card(img, box, 30); d = ImageDraw.Draw(img)
            if style == "B":
                bullet(d, X1 - 48, y + ch / 2, "num", n, 26)
            else:
                cx, cy = X1 - 48, y + ch / 2
                d.polygon([(cx, cy - 22), (cx + 22, cy), (cx, cy + 22), (cx - 22, cy)], fill=GREEN_T)
                d.text((cx, cy + 1), str(n), font=font(700, 24), fill=(255, 255, 255), anchor="mm")
            txt(d, X0 + 20, X1 - 100, y + 17, t, bf, 600, GREEN_T, "right", 1.34); y += ch + 12
    return y

def render(style, page, s, y0=None):
    im = Image.open(N.TPL).convert("RGB")
    fn = page1 if page == 1 else page2
    start = TOP + 8 if y0 is None else y0
    end = fn(im, start, s, style)
    return im, end

def best(style, page):
    s = 2.6
    while s > 0.8:
        im, end = render(style, page, s)
        if end <= BOT: break
        s -= 0.02
    # vertically centre the block inside the free band
    free = BOT - end
    y0 = TOP + 8 + max(0, free // 2 - 10)
    im, end = render(style, page, s, y0)
    return im, s, end

if __name__ == "__main__":
    os.makedirs("Notice", exist_ok=True)
    for st in "ABC":
        for pg in (1, 2):
            im, s, end = best(st, pg)
            im.save(f"Notice/Big-{st}-page{pg}.png", optimize=True)
            print(st, pg, "scale", round(s, 2), "body px", round(32 * s), "ends", round(end))

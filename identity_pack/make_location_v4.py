#!/usr/bin/env python3
"""Location cards v4 = v3 (route panel) with a 3-D isometric map in ALL four layouts + the enhanced new building photo."""
import os
from PIL import Image, ImageDraw
from pack_lib import *
import make_location_v2 as V
import make_location as L1
import real_map as rm
import map_lib as ml

L1.PHOTO = "mapdata/shop_photo3.jpg"
_photo = L1.photo
def photo(w, h, focus=None):
    if w <= 300:   focus = (0, .40, 1, .80)       # small round / square crops -> the shop front
    elif w / h > 1.1: focus = (0, .38, 1, .82)    # wide crops -> awning + door
    else:          focus = (0, .08, 1, .90)       # portrait crops -> whole facade
    return _photo(w, h, focus)
L1.photo = photo

def iso_map(img, box, pal=None, dark=False, labels=True, r=40):
    cw, ch = box[2] - box[0], box[3] - box[1]
    win = rm.window_for([l["pos"] for l in V.LM], pad=44)
    m3, proj = rm.iso(win, max(960, cw), L1.ISO_DARK if dark else L1.ISO_LIGHT, squash=.40, inset=.12)
    hx0, hy0 = proj(rm.PIN, 0)
    cx0 = int(min(max(hx0 - cw * .5, 0), max(0, m3.size[0] - cw))); cy0 = int(min(max(hy0 - ch * .6, 0), max(0, m3.size[1] - ch)))
    bgc = (2, 32, 24, 255) if dark else (236, 227, 208, 255)
    crop = Image.new("RGBA", (cw, ch), bgc); crop.alpha_composite(m3.crop((cx0, cy0, cx0 + cw, cy0 + ch)))
    soft_shadow(img, box, r, alpha=70, blur=16, off=9, rgb=(0, 20, 12) if dark else (90, 70, 30))
    mm = Image.new("L", img.size, 0); ImageDraw.Draw(mm).rounded_rectangle(box, r, fill=255)
    layer = Image.new("RGB", img.size); layer.paste(crop.convert("RGB"), (box[0], box[1])); img.paste(layer, (0, 0), mm)
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, r, outline=GOLD_LT if dark else GOLD, width=4)
    hx, hy = hx0 - cx0 + box[0], hy0 - cy0 + box[1]
    for n, l in enumerate(V.LM, 1):
        px, py = proj(l["pos"], 0); px = px - cx0 + box[0]; py = py - cy0 + box[1]
        py = min(max(py, box[1] + 40), box[3] - 40); px = min(max(px, box[0] + 40), box[2] - 40)
        if labels:
            side = "left" if px > (box[0] + box[2]) / 2 else "right"
            f = font(700, 23); w = f.getlength(l["name"], direction="rtl", language="ar") + 70
            x0 = px + 26 if side == "right" else px - 26 - w
            if x0 < hx + 60 and x0 + w > hx - 340 and abs(py - hy) < 130:
                py = hy + 120
            V.tag(img, px, py, n, l["name"], dark, side=side, size=23)
        else:
            ml.badge(ImageDraw.Draw(img), px, py, n, GOLD_LT if dark else GOLD, GREEN_DK if dark else WHITE, font(700, 24), r=22)
    return hx, hy - 24
V.flat_map = iso_map

import make_location_v3 as M3
M3.main("v4")

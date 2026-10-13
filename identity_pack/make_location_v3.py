#!/usr/bin/env python3
"""Location cards v3 = the four v2 layouts + a 'how to get there' route panel (Zenata traffic light -> 50 m -> office on the left, towards Al-Furnaj island).
Edit the strings below if a place name needs another spelling, then:  python3 make_location_v3.py"""
import os
from PIL import Image, ImageDraw
from pack_lib import *
import make_location_v2 as V
import map_lib as ml

STREET = os.environ.get("STREET", "شارع زناتة الجديدة")
NEXT_TO = os.environ.get("NEXT_TO", "مركز جوت الاطلاع")
LIGHT = os.environ.get("LIGHT", "إشارة زناتة الضوئية")
ISLAND = os.environ.get("ISLAND", "جزيرة الفرناج")
DIST = os.environ.get("DIST", "50 م")
W = V.W
V.H = 1800
HH = V.H
_orig_logo = V.logo
def _logo(img, name, x, y, **kw):
    if str(name).startswith("rakb") and y > 1200:      # footer logo is re-placed under the route panel
        return
    return _orig_logo(img, name, x, y, **kw)
V.logo = _logo

def traffic_light(d, cx, cy, h):
    w = h * .52
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(w * .3), fill=(30, 30, 30), outline=(235, 235, 235), width=2)
    r = h * .12
    for k, col in enumerate(((220, 50, 40), (245, 180, 30), (50, 190, 90))):
        d.ellipse((cx - r, cy - h * .32 + k * h * .32 - r, cx + r, cy - h * .32 + k * h * .32 + r), fill=col)

def island(d, cx, cy, r, col, ring):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=5)
    d.ellipse((cx - r * .45, cy - r * .45, cx + r * .45, cy + r * .45), fill=ring, outline=col, width=3)

def route_panel(img, top, dark):
    x0, x1, h = 60, W - 60, 316
    box = (x0, top, x1, top + h)
    if dark:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(box, 36, fill=(3, 52, 38), outline=GOLD, width=3)
        txt, acc, road, sub = CREAM, GOLD_LT, (200, 178, 120), (170, 205, 185)
    else:
        V.bc.shadowed_round(img, box, 36, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=55)
        txt, acc, road, sub = GREEN, GOLD, (150, 138, 110), (120, 108, 84)
    d = ImageDraw.Draw(img)
    # title chip
    cw = 250
    d.rounded_rectangle((x1 - 30 - cw, top + 16, x1 - 30, top + 62), 23, fill=GOLD if not dark else (GOLD))
    d.text((x1 - 30 - cw / 2, top + 39), "طريق الوصول", font=font(700, 28), fill=(2, 36, 22), anchor="mm", direction="rtl", language="ar")
    ry = top + 140
    xa, xb, xc = x1 - 120, (x0 + x1) // 2 + 20, x0 + 130          # light  ->  office  ->  island  (right to left = driving direction)
    d.line((xc, ry, xa, ry), fill=road, width=10)
    for xx in range(int(xc) + 40, int(xa) - 30, 46):                  # dashed centre line
        d.line((xx, ry, xx + 22, ry), fill=(250, 245, 230), width=3)
    # arrow head (driving towards the island = left)
    d.polygon([(xc - 26, ry), (xc + 4, ry - 16), (xc + 4, ry + 16)], fill=road)
    traffic_light(d, xa, ry, 64)
    island(d, xc - 6, ry, 28, acc, (4, 60, 44) if dark else (236, 227, 208))
    d.text((xa, top + 94), LIGHT, font=font(700, 24), fill=txt, anchor="mm", direction="rtl", language="ar")
    d.text((xc - 6, top + 94), ISLAND, font=font(700, 24), fill=txt, anchor="mm", direction="rtl", language="ar")
    # distance bubble
    mx = (xa + xb) / 2
    d.rounded_rectangle((mx - 52, ry - 44, mx + 52, ry - 6), 19, fill=acc)
    d.text((mx, ry - 25), DIST, font=font(700, 24), fill=(2, 36, 22), anchor="mm", direction="rtl", language="ar")
    # office pin on the LEFT-hand side of the driver (= below the road when travelling leftwards)
    d.line((xb, ry + 6, xb, ry + 30), fill=acc, width=5)
    ml.pin(img, xb, ry + 72, 32, TEAL if not dark else GOLD, ring=CREAM if not dark else (3, 52, 38), logo=asset("hajj_logo_white"))
    d = ImageDraw.Draw(img)
    d.text((xb - 44, ry + 46), "المقر — على يسارك", font=font(700, 24), fill=acc if dark else TEAL, anchor="rm", direction="rtl", language="ar")
    # sentence
    d.text(((x0 + x1) / 2, top + 252), f"يقع المقر على {STREET}، بجانب {NEXT_TO}،", font=font(600, 26), fill=txt, anchor="mm", direction="rtl", language="ar")
    d.text(((x0 + x1) / 2, top + 288), f"بعد {LIGHT} بنحو {DIST.replace('م', 'متر')} على اليسار باتجاه {ISLAND}", font=font(600, 26), fill=txt, anchor="mm", direction="rtl", language="ar")

TOPS = {1: 1310, 2: 1316, 3: 1356, 4: 1378}
def main(tag="v3"):
  for i, fn in enumerate(V.CARDS, 1):
      img = fn()
      dark = i == 2
      route_panel(img, TOPS[i], dark)
      if dark: logo(img, "rakb_gold", (W - 76) // 2, HH - 96, w=76, rgb=GOLD_LT)
      else: logo(img, "rakb_green", (W - 76) // 2, HH - 96, w=76)
      os.makedirs("Location", exist_ok=True)
      img.convert("RGB").save(f"Location/Location-{tag}-{i}.png", optimize=True); print(tag, i, flush=True)

if __name__ == "__main__":
    main()

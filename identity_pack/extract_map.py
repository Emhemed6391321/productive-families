#!/usr/bin/env python3
"""Turn the supplied Google-Maps screenshot into clean vector-like road masks (geometry only, no
labels / icons / traffic colours / Google UI) so the cards can show the real streets in our identity."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

im = Image.open("mapdata/zanatah_screenshot.jpg").convert("RGB")
im = im.resize((980, round(im.size[1] * 980 / im.size[0])), Image.LANCZOS)
a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
bgd = np.abs(a - np.array([246, 246, 248])).sum(2)
gray = (np.abs(r - g) < 26) & (b >= r - 6) & (bgd > 28) & (a.mean(2) < 236)
traffic = ((g > r + 35) & (g > b + 10)) | ((r > 215) & (g > 150) & (b < 130) & (r - b > 90)) | ((r > 130) & (g < 95) & (b < 95))

def clean(mask, ui):
    m = Image.fromarray((mask * 255).astype("uint8"))
    d = ImageDraw.Draw(m)
    for e in ui: d.rectangle(e, fill=0)
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))      # drop specks of anti-aliased text
    return m

UI = [(0, 0, 980, 165), (0, 1740, 980, 2000), (28, 180, 138, 300), (28, 318, 138, 430), (30, 1585, 162, 1710), (172, 1592, 390, 1698), (680, 1650, 950, 1730)]
ICONS = [(100, 318, 345, 362), (285, 300, 340, 362), (455, 1060, 530, 1130), (555, 1090, 640, 1200), (0, 1145, 90, 1225), (0, 395, 70, 470), (0, 500, 60, 575), (110, 575, 160, 640), (240, 850, 300, 905), (435, 925, 500, 985), (745, 545, 800, 600), (965, 1030, 980, 1100), (740, 1450, 800, 1510), (905, 125, 980, 190)]
minor = clean(gray | traffic, UI + ICONS)
major = clean(traffic, UI + ICONS).filter(ImageFilter.MaxFilter(9))
box = (0, 165, 980, 1740)
minor.crop(box).save("mapdata/roads_all.png"); major.crop(box).save("mapdata/roads_major.png")
print("saved", minor.crop(box).size)

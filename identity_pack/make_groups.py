#!/usr/bin/env python3
"""11 WhatsApp group pictures (1080x1080; WhatsApp shows them as a circle, so everything
sits inside the circle).  Each coordination gets its own colour from the identity family,
the Rakb al-Abrar logo and its number 1..11.   Output: Groups/Group-01.png ... Group-11.png"""
from PIL import Image, ImageDraw
from pack_lib import *

S = 1080
# 11 tones near the identity palette (greens/teal/gold/bronze + earthy neighbours), each with a lighter centre
COLORS = [
    ("teal",       (0, 80, 69)),
    ("green",      (4, 61, 31)),
    ("emerald",    (10, 110, 79)),
    ("olive",      (88, 98, 30)),
    ("bronze",     (128, 90, 44)),
    ("copper",     (128, 64, 36)),
    ("petrol",     (3, 84, 102)),
    ("deep blue",  (18, 56, 92)),
    ("burgundy",   (112, 42, 52)),
    ("aubergine",  (72, 44, 88)),
    ("slate",      (50, 64, 58)),
]

def group(n, base):
    light = tuple(min(255, int(c * 1.22 + 12)) for c in base)
    dark = tuple(int(c * 0.42) for c in base)
    img = gradient(S, S, [(0, light), (.55, base), (1, dark)], 45)
    g, m = glow(S, S, S / 2, S * .42, 520, 460, light, .55)
    img = over(img, light, m)
    img = add_lattice(img, GOLD_LT, 30, R=100)
    d = ImageDraw.Draw(img)
    d.ellipse((S / 2 - 486, S / 2 - 486, S / 2 + 486, S / 2 + 486), outline=GOLD_LT, width=7)
    d.ellipse((S / 2 - 466, S / 2 - 466, S / 2 + 466, S / 2 + 466), outline=GOLD_LT, width=2)
    logo(img, "rakb_gold", (S - 330) // 2, 135, w=330, rgb=GOLD_LT)
    diamond_divider(img, S / 2, 478, half=190, gap=30, col=GOLD_LT, width=3, size=12)
    size = 430 if n < 10 else 360
    d.text((S / 2, 700), str(n), font=font(700, size), fill=CREAM, anchor="mm")
    return img

def main():
    for i, (name, c) in enumerate(COLORS, 1):
        group(i, c).save(f"Groups/Group-{i:02d}.png", optimize=True)
        print(i, name, flush=True)
    # comparison sheet
    sh = Image.new("RGB", (4 * 360 + 5 * 24, 3 * 360 + 4 * 24), (236, 231, 222))
    for i in range(11):
        im = Image.open(f"Groups/Group-{i+1:02d}.png").resize((360, 360), Image.LANCZOS)
        m = Image.new("L", (360, 360), 0); ImageDraw.Draw(m).ellipse((0, 0, 359, 359), fill=255)
        sh.paste(im, (24 + (i % 4) * 384, 24 + (i // 4) * 384), m)
    sh.save("Previews/Groups-Preview-circle.png")

if __name__ == "__main__":
    main()

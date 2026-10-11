#!/usr/bin/env python3
"""Welcome card for pilgrims - Tripoli-B coordination (1080x1440).  Two colourways: A light, B dark."""
import os
from PIL import Image, ImageDraw
from pack_lib import *

W, H = 1080, 1440
NAME = "تنسيقية حجاج طرابلس ب"
PHONE, PLACE = "0934455422", "طرابلس - زناتة"

def centered(d, y, text, size, fill, maxw=900, weight=700):
    f = font(weight, size)
    while f.getlength(text, direction="rtl", language="ar") > maxw:
        f = font(weight, f.size - 4)
    d.text((W / 2, y), text, font=f, fill=fill, anchor="mm", direction="rtl", language="ar")

def build(dark):
    if dark:
        img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
        g, m = glow(W, H, W / 2, 520, 760, 520, (14, 128, 108), .5); img = over(img, (14, 128, 108), m)
        img = add_lattice(img, GOLD_LT, 32)
        paste(img, sky_layer(W, 0.4, tint=GOLD_LT, blur=1.1), 0, H - 330)
        frame(img, 34, GOLD, 3, 12, corner=0.9)
        ink, hero2, orn = CREAM, GOLD_LT, GOLD_LT
    else:
        img = paper(W, H)
        img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, H * .25, H, .12, 1))
        paste(img, sky_layer(W, 0.55), 0, H - 430)
        ink, hero2, orn = GREEN, GOLD, GOLD
    d = ImageDraw.Draw(img)
    # authority logo
    logo(img, "hajj_logo_white", (W - 130) // 2, 66, w=130, rgb=None if dark else GREEN)
    d = ImageDraw.Draw(img)
    # "حيّاكم الله" with the title ornaments
    centered(d, 262, "حيّاكم الله", 44, GOLD_LT if dark else BRONZE, 400, 600)
    for sx in (-1, 1):
        diamond_divider(img, W / 2 + sx * 0, 262, half=0, gap=0, col=orn, size=0) if False else None
    d = ImageDraw.Draw(img)
    for sx in (-1, 1):
        d.line((W / 2 + sx * 140, 262, W / 2 + sx * 300, 262), fill=orn, width=3)
        cx = W / 2 + sx * 318
        d.polygon([(cx, 250), (cx + 12, 262), (cx, 274), (cx - 12, 262)], fill=orn)
    # hero
    centered(d, 420, "أهلًا وسهلًا", 190, ink, 900)
    centered(d, 580, "بضيوف الرحمن", 128, hero2, 900)
    diamond_divider(img, W / 2, 676, half=270, gap=38, col=GOLD, width=3, size=14)
    d = ImageDraw.Draw(img)
    # plaque with the coordination name
    box = (70, 724, W - 70, 954)
    if dark:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(box, 70, fill=(2, 34, 22, 225)); img.paste(lay, (0, 0), lay)
    else:
        soft_shadow(img, box, 70, alpha=90, blur=22, off=12)
        d = ImageDraw.Draw(img); d.rounded_rectangle(box, 70, fill=GREEN)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 70, outline=GOLD, width=5)
    d.rounded_rectangle((box[0] + 14, box[1] + 14, box[2] - 14, box[3] - 14), 58, outline=GOLD_LT, width=2)
    for sx in (-1, 1):
        cx, cy = (box[0] if sx < 0 else box[2]), (box[1] + box[3]) // 2
        d.polygon([(cx, cy - 26), (cx + 26, cy), (cx, cy + 26), (cx - 26, cy)], fill=GOLD)
    centered(d, 810, NAME, 76, CREAM, 820)
    centered(d, 898, "ترحّب بكم أجمل ترحيب", 50, GOLD_LT, 800, 600)
    # dua card
    cb = (100, 1000, W - 100, 1196)
    if dark:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle(cb, 44, fill=(2, 36, 24, 215), outline=GOLD_LT + (255,), width=2); img.paste(lay, (0, 0), lay)
    else:
        bc.shadowed_round(img, cb, 44, CREAM, (222, 204, 168), 2, blur=14, off=7, alpha=55)
    d = ImageDraw.Draw(img)
    bc.draw_text(d, W - 130, 130, 1022, "نسأل الله أن يتقبّل منكم\n*حجًّا مبرورًا وسعيًا مشكورًا وذنبًا مغفورًا*", 42, 700,
                 CREAM if dark else GREEN, "center", 1.6, hl=GOLD_LT if dark else GOLD)
    # footer
    rk = fit_w(asset("rakb_gold") if dark else asset("rakb_green"), 120)
    if dark:
        rk = fit_w(tinted("rakb_gold", GOLD_LT), 120)
    paste(img, rk, (W - rk.size[0]) // 2, 1226)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1370), f"{PLACE}   |   {PHONE}", font=font(600, 30), fill=GOLD_LT if dark else GREEN, anchor="mm", direction="rtl", language="ar")
    return img

if __name__ == "__main__":
    os.makedirs("Welcome", exist_ok=True)
    for dark, n in ((False, "A-light"), (True, "B-dark")):
        build(dark).convert("RGB").save(f"Welcome/Welcome-{n}.png", optimize=True); print(n)

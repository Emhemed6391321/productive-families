#!/usr/bin/env python3
"""Welcome card C (1080 x 1440): duotone Mecca arch window + coordination-logo medallion + big green greeting. No Rakb logo."""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pack_lib import *

W, H = 1080, 1440
NAME, PHONE, PLACE = "تنسيقية حجاج طرابلس ب", "0934455422", "طرابلس - زناتة"

def T(d, y, text, size, fill, w=700, x=W // 2, maxw=960):
    f = font(w, size)
    while f.getlength(text, direction="rtl", language="ar") > maxw: f = font(w, f.size - 2)
    d.text((x, y), text, font=f, fill=fill, anchor="mm", direction="rtl", language="ar")

def build():
    img = paper(W, H, warm=True)
    img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1))
    cx = W // 2
    # arch window with duotone Mecca
    box = (80, 70, W - 80, 800); rad = (box[2] - box[0]) // 2
    soft_shadow(img, box, rad, alpha=100, blur=24, off=14, rgb=(0, 20, 12))
    ph_h = box[3] - box[1]
    plate = sky_photo(ph_h, box[2] - box[0]).filter(ImageFilter.GaussianBlur(2.0))
    duo = ImageOps.colorize(ImageOps.autocontrast(plate.convert("L"), cutoff=1), black=(1, 30, 20), mid=(34, 92, 68), white=(226, 205, 150))
    scrim = gradient(box[2] - box[0], ph_h, [(0, (1, 44, 32)), (.5, (2, 56, 38)), (1, (3, 60, 36))], 90)
    sa = Image.fromarray((vramp(ph_h, 0, ph_h, .62, .15)[:, None].repeat(box[2] - box[0], 1) * 255).astype("uint8"))
    duo = Image.composite(scrim, duo, sa)
    mk = Image.new("L", img.size, 0); md = ImageDraw.Draw(mk)
    md.ellipse((box[0], box[1], box[2], box[1] + 2 * rad), fill=255); md.rectangle((box[0], box[1] + rad, box[2], box[3]), fill=255); md.rectangle((0, box[3] + 1, W, H), fill=0)
    layer = Image.new("RGB", img.size); layer.paste(duo, (box[0], box[1])); img.paste(layer, (0, 0), mk)
    d = ImageDraw.Draw(img)
    # arch outlines (follow the shape): outer gold, inner light
    for off, col, wd in ((0, GOLD, 6), (16, GOLD_LT, 2)):
        b = (box[0] + off, box[1] + off, box[2] - off, box[3])
        d.arc((b[0], b[1], b[2], b[1] + (b[2] - b[0])), 180, 360, fill=col, width=wd)
        d.line((b[0], b[1] + (b[2] - b[0]) // 2, b[0], b[3]), fill=col, width=wd); d.line((b[2], b[1] + (b[2] - b[0]) // 2, b[2], b[3]), fill=col, width=wd)
    d.line((box[0], box[3], box[2], box[3]), fill=GOLD, width=6)
    star8(d, cx, 238, 62, fill=GOLD_LT); star8(d, cx, 238, 40, fill=(3, 56, 36), rot=-math.pi / 2 + math.pi / 8); star8(d, cx, 238, 19, fill=GOLD_LT)
    # medallion with the coordination logo straddling the arch base
    lg = Image.open("assets/coordination_logo.jpg").convert("RGB"); c = min(lg.size) / 2
    lg = lg.crop((int(lg.size[0] / 2 - c * .985), int(lg.size[1] / 2 - c * .985), int(lg.size[0] / 2 + c * .985), int(lg.size[1] / 2 + c * .985)))
    R = 150; my = 800
    ring = Image.new("RGBA", img.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(ring)
    rd.ellipse((cx - R - 20, my - R - 20 + 10, cx + R + 20, my + R + 20 + 10), fill=(0, 0, 0, 90)); img.paste(ring.filter(ImageFilter.GaussianBlur(14)), (0, 0), ring.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - R - 14, my - R - 14, cx + R + 14, my + R + 14), fill=CREAM, outline=GOLD, width=5)
    lg = lg.resize((2 * R, 2 * R), Image.LANCZOS); m2 = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(m2).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
    img.paste(lg, (cx - R, my - R), m2)
    d = ImageDraw.Draw(img)
    # greeting
    T(d, 1010, "أهلًا وسهلًا", 56, GOLD, 700, maxw=500)
    diamond_divider(img, cx, 1058, half=250, gap=30, col=GOLD, width=3, size=11)
    T(d, 1146, "بحجاج بيت الله الحرام", 112, GREEN, 700, maxw=960)
    T(d, 1244, f"{NAME} ترحّب بكم", 46, BRONZE, 600, maxw=900)
    # contact bar
    bar = (110, 1308, W - 110, 1388)
    soft_shadow(img, bar, 40, alpha=60, blur=10, off=5)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(bar, 40, fill=GREEN, outline=GOLD, width=3)
    d.text((bar[2] - 40, 1348), "للتواصل", font=font(600, 26), fill=GOLD_LT, anchor="rm", direction="rtl", language="ar")
    d.text((W // 2 - 10, 1349), PHONE, font=font(700, 46), fill=CREAM, anchor="mm")
    d.text((bar[0] + 36, 1348), PLACE, font=font(600, 26), fill=GOLD_LT, anchor="lm", direction="rtl", language="ar")
    logo(img, "hajj_green", W // 2 - 36, 1396, w=72) if False else None
    return img

if __name__ == "__main__":
    os.makedirs("Welcome", exist_ok=True)
    build().convert("RGB").save("Welcome/Welcome-C-arch-photo.png", optimize=True); print("ok")

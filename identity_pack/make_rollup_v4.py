#!/usr/bin/env python3
"""Roll-up 80 x 180 cm, 'D': coordination logo (medallion) -> authority plaque -> coordination name -> municipalities (smaller) -> Rakb al-Abrar -> phone / place.
    python3 make_rollup_v4.py preview    |    python3 make_rollup_v4.py print   (-> RollUp/RollUp-D-*.pdf/png at 100 dpi, 3150 x 7088 px)"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
from pack_lib import *
from make_rollup import smooth, PHONE, DW, DH
from make_rollup_v2 import fit_text, contact, BRONZE_TXT, AUTH1, AUTH2, COORD

MUNI = "بلدية سوق الجمعة   •   طرابلس الهضبة المركز   •   بلدية عين زارة"

def build_d(S):
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, P(300), P(2300), .25, 1), R=P(120))
    paste(img, sky_layer(W, 0.6), 0, P(1780))
    # ---- medallion carrying the supplied coordination logo
    cx, cy, r = W // 2, P(425), P(370)
    for rr, col, wd in ((r + P(44), GOLD, 3), (r + P(21), GOLD_LT, 2)):
        ImageDraw.Draw(img).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=max(2, P(wd)))
    lg = Image.open("assets/coordination_logo.jpg").convert("RGB")
    c = min(lg.size) / 2
    lg = lg.crop((int(lg.size[0] / 2 - c * .985), int(lg.size[1] / 2 - c * .985), int(lg.size[0] / 2 + c * .985), int(lg.size[1] / 2 + c * .985)))
    lg = lg.resize((2 * r, 2 * r), Image.LANCZOS)
    md = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(md).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255)
    img.paste(lg, (cx - r, cy - r), md.filter(ImageFilter.GaussianBlur(0.5 * S)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=max(4, P(7)))
    for k_ in range(8):
        a = math.radians(-90 + k_ * 45 + 22.5)
        star8(d, cx + int((r + P(44)) * math.cos(a)), cy + int((r + P(44)) * math.sin(a)), P(15), fill=GOLD)
    # ---- authority plaque (deep green, gold type)
    box = (P(150), P(895), P(DW - 150), P(1105))
    soft_shadow(img, box, P(60), alpha=110, blur=P(26), off=P(14), rgb=(0, 20, 12))
    pg = gradient(W, H, [(0, (3, 70, 44)), (1, (2, 36, 22))], 90)
    pm = Image.new("L", img.size, 0); ImageDraw.Draw(pm).rounded_rectangle(box, P(50), fill=255)
    img.paste(pg, (0, 0), pm)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, P(50), outline=GOLD, width=max(4, P(5)))
    d.rounded_rectangle((box[0] + P(12), box[1] + P(12), box[2] - P(12), box[3] - P(12)), P(38), outline=GOLD_LT, width=max(2, P(2)))
    lead_y, key_y = 950, 1042
    lf = font(600, P(52)); lt = lf.getlength(AUTH1, direction="rtl", language="ar")
    d.text((W // 2, P(lead_y)), AUTH1, font=lf, fill=CREAM, anchor="mm", direction="rtl", language="ar")
    for sx in (-1, 1):
        x0 = W // 2 + sx * (lt / 2 + P(28)); x1 = W // 2 + sx * P(DW / 2 - 205)
        d.line((x0, P(lead_y), x1, P(lead_y)), fill=GOLD, width=max(2, P(3)))
        d.polygon([(x1, P(lead_y) - P(10)), (x1 + P(10), P(lead_y)), (x1, P(lead_y) + P(10)), (x1 - P(10), P(lead_y))], fill=GOLD)
    kf = font(700, P(100))
    while kf.getlength(AUTH2, direction="rtl", language="ar") > P(DW - 420): kf = font(700, kf.size - 4)
    d.text((W // 2, P(key_y)), AUTH2, font=kf, fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    sx_, sy_ = W // 2, box[1]
    d.ellipse((sx_ - P(40), sy_ - P(40), sx_ + P(40), sy_ + P(40)), fill=PAPER_A, outline=GOLD, width=max(3, P(5)))
    star8(d, sx_, sy_, P(28), fill=GOLD); star8(d, sx_, sy_, P(13), fill=PAPER_A, rot=-math.pi / 2 + math.pi / 8)
    # ---- coordination name = hero (two lines) + municipalities (smaller)
    fit_text(d, (W / S / 2, 1245), "تنسيقية", 120, S, BRONZE_TXT, 700, weight=600)
    fit_text(d, (W / S / 2, 1445), "حجاج طرابلس ب", 220, S, GREEN, 980)
    diamond_divider(img, W // 2, P(1572), half=P(260), gap=P(32), col=GOLD, width=max(2, P(3)), size=P(12))
    fit_text(d, (W / S / 2, 1665), MUNI, 50, S, BRONZE_TXT, 990, weight=600)
    # ---- phone + place
    contact(img, S, 1870, dict(pfill=GREEN, pline=GOLD, icon=GOLD, icon_fg=GREEN, label=GOLD_LT, digits=CREAM,
                               lfill=CREAM, lline=GOLD, ltext=GREEN, pin=BRONZE_TXT, shadow=70),
            mx=170, ph_h=190, lab=40, dig=100, gap=22, pill_h=80, pill_font=46, pill_mx=300)
    return img

if __name__ == "__main__":
    os.makedirs("RollUp", exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        build_d(1.0).save("RollUp/v4-preview-D.png"); print("preview ok")
    else:
        S = 3150 / DW
        im = build_d(S).convert("RGB")
        im.save("RollUp/RollUp-D-coordination-logo-80x180cm.pdf", resolution=100.0)
        im.save("RollUp/RollUp-D-coordination-logo-80x180cm-100dpi.png", dpi=(100, 100)); print(im.size)

#!/usr/bin/env python3
"""Roll-up banner 80 x 180 cm, Tripoli-B coordination.  Design space = 1080 x 2430 (ratio 80:180);
all measures below are in that space and multiplied by S.   S=1 -> preview, S=2.9167 -> 100 dpi print (3150 x 7087 px).
Safe zones (roll-up): bottom 15 cm sits inside the cassette, top 5 cm is the hanging bar -> nothing important there."""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
from pack_lib import *

PHONE = "0934455422"
NAME1, NAME2 = "تنسيقية", "طرابلس ب"
PLACE = "طرابلس - زناتة"
DW, DH = 1080, 2430

def smooth(im, w, S):
    """Upscale a small raster logo to print size with smooth (de-stair-stepped) edges."""
    h = round(im.size[1] * w / im.size[0])
    big = im.resize((w, h), Image.BICUBIC)
    a = big.getchannel("A").filter(ImageFilter.GaussianBlur(1.3 * S))
    a = a.point(lambda v: max(0, min(255, int((v - 128) * 2.4 + 128))))
    big.putalpha(a)
    return big

def build(S):
    P = lambda v: int(round(v * S))
    W, H = P(DW), P(DH)
    # ---------------------------------------------------------------- background: green is the main colour
    img = gradient(W, H, [(0, (0, 96, 82)), (.38, (2, 70, 50)), (.75, (3, 52, 34)), (1, GREEN_DK)], 90)
    for cx, cy, rx, ry, col, a in ((DW / 2, 560, 760, 520, (14, 130, 110), .55), (DW / 2, 1500, 700, 560, (8, 100, 76), .35)):
        g, m = glow(W, H, P(cx), P(cy), P(rx), P(ry), col, a); img = over(img, col, m)
    ramp = None
    img = add_lattice(img, GOLD_LT, 34, R=P(120))
    d = ImageDraw.Draw(img)
    # skyline (Mecca) rising from the lower third, tinted gold; fades out before the cassette zone
    sk = sky_layer(W, 0.6, tint=GOLD_LT, blur=1.2 * S)
    paste(img, sk, 0, P(1790))
    # ---------------------------------------------------------------- frame (kept clear of the 5 cm / 15 cm zones)
    frame(img, P(40), GOLD, max(3, P(4)), P(14), corner=0.9)
    d = ImageDraw.Draw(img)
    # ---------------------------------------------------------------- 1) authority logo (top)
    lw = P(300)
    paste(img, smooth(asset("hajj_logo_white"), lw, S), (W - lw) // 2, P(150))
    # ---------------------------------------------------------------- 2) name cartouche
    box = (P(70), P(560), P(DW - 70), P(1180))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle(box, P(90), fill=(2, 34, 22, 214), outline=GOLD + (255,), width=max(3, P(5)))
    ld.rounded_rectangle((box[0] + P(16), box[1] + P(16), box[2] - P(16), box[3] - P(16)), P(76), outline=GOLD + (190,), width=max(2, P(2)))
    img.paste(lay, (0, 0), lay); d = ImageDraw.Draw(img)
    for sx in (-1, 1):                                          # diamond tips on the cartouche sides
        cx, cy = (box[0] if sx < 0 else box[2]), (box[1] + box[3]) // 2
        d.polygon([(cx, cy - P(30)), (cx + P(30), cy), (cx, cy + P(30)), (cx - P(30), cy)], fill=GOLD)
    # small 8-point star crown
    star8(d, W // 2, P(640), P(46), outline=GOLD_LT, width=max(2, P(3)))
    star8(d, W // 2, P(640), P(26), fill=GOLD, rot=-math.pi / 2 + math.pi / 8)
    d.text((W // 2, P(790)), NAME1, font=font(700, P(150)), fill=CREAM, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W // 2, P(884), half=P(250), gap=P(34), col=GOLD, width=max(2, P(4)), size=P(13))
    f = font(700, P(250))
    while f.getlength(NAME2, direction="rtl", language="ar") > P(DW - 260):
        f = font(700, f.size - 6)
    d = ImageDraw.Draw(img)
    d.text((W // 2, P(1040)), NAME2, font=f, fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    # ---------------------------------------------------------------- 3) Rakb al-Abrar
    rw = P(560)
    rk = smooth(tinted("rakb_gold", GOLD_LT), rw, S)
    paste(img, rk, (W - rw) // 2, P(1270))
    # ---------------------------------------------------------------- 4) phone + place
    ph = (P(100), P(1840), P(DW - 100), P(2080))
    soft_shadow(img, ph, P(100), alpha=130, blur=P(24), off=P(12), rgb=(0, 16, 10))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(ph, P(100), fill=CREAM, outline=GOLD, width=max(3, P(5)))
    d.rounded_rectangle((ph[0] + P(12), ph[1] + P(12), ph[2] - P(12), ph[3] - P(12)), P(88), outline=GOLD, width=max(1, P(2)))
    # label row: phone icon + text, centred
    lab = "للتواصل والاستفسار"
    lf = font(700, P(44))
    lw_ = lf.getlength(lab, direction="rtl", language="ar")
    ry = ph[1] + P(66)
    icx = W // 2 + int(lw_ / 2) + P(52)
    d.ellipse((icx - P(34), ry - P(34), icx + P(34), ry + P(34)), fill=GREEN)
    iw, ih = P(20), P(36)
    d.rounded_rectangle((icx - iw // 2, ry - ih // 2, icx + iw // 2, ry + ih // 2), P(5), outline=CREAM, width=max(2, P(4)))
    d.line((icx - P(5), ry + P(12), icx + P(5), ry + P(12)), fill=CREAM, width=max(2, P(3)))
    d.text((W // 2 + int(lw_ / 2), ry), lab, font=lf, fill=GOLD, anchor="rm", direction="rtl", language="ar")
    d.line((ph[0] + P(120), ph[1] + P(112), ph[2] - P(120), ph[1] + P(112)), fill=GOLD, width=max(2, P(2)))
    f = font(700, P(124))
    while f.getlength(PHONE) > P(DW - 300):
        f = font(700, f.size - 4)
    d.text((W // 2, ph[1] + P(176)), PHONE, font=f, fill=GREEN, anchor="mm")
    # place pill
    pl = (P(260), P(2106), P(DW - 260), P(2198))
    d.rounded_rectangle(pl, P(46), fill=(2, 34, 22), outline=GOLD_LT, width=max(2, P(3)))
    pf = font(700, P(50))
    tw = pf.getlength(PLACE, direction="rtl", language="ar")
    cx0 = W // 2
    px, py = cx0 + int(tw / 2) + P(40), (pl[1] + pl[3]) // 2
    d.ellipse((px - P(17), py - P(27), px + P(17), py + P(7)), fill=GOLD_LT)
    d.polygon([(px - P(15), py - P(5)), (px + P(15), py - P(5)), (px, py + P(27))], fill=GOLD_LT)
    d.ellipse((px - P(6), py - P(16), px + P(6), py - P(4)), fill=(2, 34, 22))
    d.text((cx0 + int(tw / 2), py + P(2)), PLACE, font=pf, fill=CREAM, anchor="rm", direction="rtl", language="ar")
    return img

if __name__ == "__main__":
    os.makedirs("RollUp", exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        build(1.0).save("RollUp/RollUp-preview.png"); print("preview ok")
    else:
        S = 3150 / DW
        im = build(S)
        print(im.size)
        im.save("RollUp/RollUp-80x180cm-100dpi.png", dpi=(100, 100), optimize=False)
        im.convert("RGB").save("RollUp/RollUp-80x180cm.pdf", resolution=100.0)
        print("print files ok")

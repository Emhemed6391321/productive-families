#!/usr/bin/env python3
"""Roll-up 80 x 180 cm - three redesigned layouts / colourways (A teal arch, B green+cream dome, C light + green medallion).
Design space 1080 x 2430; S scales to print (S = 3150/1080 -> 100 dpi).  Safe zones: top 5 cm, bottom 15 cm kept free of key content.
    python3 make_rollup_v2.py preview     -> RollUp/v2-preview-*.png (1x)
    python3 make_rollup_v2.py print       -> RollUp/RollUp-A-teal.pdf, -B-..., -C-...   (+ PNG)"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter
from pack_lib import *
from make_rollup import smooth, PHONE, NAME1, NAME2, PLACE, DW, DH

BRONZE_TXT = (150, 108, 48)

def fit_text(d, xy, text, size, S, fill, maxw, weight=700, anchor="mm", rtl=True):
    f = font(weight, int(size * S))
    while f.getlength(text, direction="rtl", language="ar") > maxw * S:
        f = font(weight, f.size - 4)
    d.text((xy[0] * S, xy[1] * S), text, font=f, fill=fill, anchor=anchor, direction="rtl", language="ar")

def contact(img, S, y_phone, th, mx=100, ph_h=240, lab=44, dig=124, gap=26, pill_h=92, pill_font=50, pill_mx=260):
    """phone panel (label + number) and place pill. th = colour dict. sizes are in design units."""
    P = lambda v: int(round(v * S)); W = img.size[0]
    ph = (P(mx), P(y_phone), P(DW - mx), P(y_phone + ph_h))
    soft_shadow(img, ph, P(ph_h // 2), alpha=th.get("shadow", 120), blur=P(24), off=P(12), rgb=(0, 16, 10))
    d = ImageDraw.Draw(img)
    r_ = P(ph_h // 2)
    d.rounded_rectangle(ph, r_, fill=th["pfill"], outline=th["pline"], width=max(3, P(5)))
    d.rounded_rectangle((ph[0] + P(12), ph[1] + P(12), ph[2] - P(12), ph[3] - P(12)), r_ - P(12), outline=th["pline"], width=max(1, P(2)))
    label = "للتواصل والاستفسار"; lf = font(700, P(lab)); lw = lf.getlength(label, direction="rtl", language="ar")
    ry = ph[1] + P(ph_h * 0.275); icx = W // 2 + int(lw / 2) + P(lab * 1.2)
    ir = P(lab * 0.77)
    d.ellipse((icx - ir, ry - ir, icx + ir, ry + ir), fill=th["icon"])
    iw, ih = P(lab * .45), P(lab * .82)
    d.rounded_rectangle((icx - iw // 2, ry - ih // 2, icx + iw // 2, ry + ih // 2), P(5), outline=th["icon_fg"], width=max(2, P(4)))
    d.line((icx - P(5), ry + P(lab * .27), icx + P(5), ry + P(lab * .27)), fill=th["icon_fg"], width=max(2, P(3)))
    d.text((W // 2 + int(lw / 2), ry), label, font=lf, fill=th["label"], anchor="rm", direction="rtl", language="ar")
    d.line((ph[0] + P(110), ph[1] + P(ph_h * 0.467), ph[2] - P(110), ph[1] + P(ph_h * 0.467)), fill=th["pline"], width=max(2, P(2)))
    f = font(700, P(dig))
    while f.getlength(PHONE) > P(DW - 2 * mx - 140): f = font(700, f.size - 4)
    d.text((W // 2, ph[1] + P(ph_h * 0.733)), PHONE, font=f, fill=th["digits"], anchor="mm")
    pl = (P(pill_mx), P(y_phone + ph_h + gap), P(DW - pill_mx), P(y_phone + ph_h + gap + pill_h))
    d.rounded_rectangle(pl, P(pill_h // 2), fill=th["lfill"], outline=th["lline"], width=max(2, P(3)))
    pf = font(700, P(pill_font)); tw = pf.getlength(PLACE, direction="rtl", language="ar")
    px, py = W // 2 + int(tw / 2) + P(40), (pl[1] + pl[3]) // 2
    d.ellipse((px - P(17), py - P(27), px + P(17), py + P(7)), fill=th["pin"])
    d.polygon([(px - P(15), py - P(5)), (px + P(15), py - P(5)), (px, py + P(27))], fill=th["pin"])
    d.ellipse((px - P(6), py - P(16), px + P(6), py - P(4)), fill=th["lfill"])
    d.text((W // 2 + int(tw / 2), py + P(2)), PLACE, font=pf, fill=th["ltext"], anchor="rm", direction="rtl", language="ar")

def arch_mask(S, box, size):
    P = lambda v: int(round(v * S))
    x0, y0, x1, y1 = [P(v) for v in box]
    r = (x1 - x0) // 2
    m = Image.new("L", size, 0); md = ImageDraw.Draw(m)
    md.ellipse((x0, y0, x1, y0 + 2 * r), fill=255)
    md.rectangle((x0, y0 + r, x1, y1), fill=255)
    md.rectangle((0, y1 + 1, size[0], size[1]), fill=0)      # nothing below the arch base
    return m

# ================================================================== A : teal, arch (mihrab) frame
def build_a(S):
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    img = gradient(W, H, [(0, (0, 104, 90)), (.45, (0, 78, 66)), (1, (2, 44, 36))], 90)
    g, m = glow(W, H, W // 2, P(700), P(780), P(600), (20, 150, 128), .5); img = over(img, (20, 150, 128), m)
    img = add_lattice(img, GOLD_LT, 30, R=P(120))
    paste(img, sky_layer(W, 0.7, tint=GOLD_LT, blur=1.2 * S), 0, P(1740))
    frame(img, P(40), GOLD, max(3, P(4)), P(14), corner=0.9)
    d = ImageDraw.Draw(img)
    # authority logo in a gold-ringed disc
    cx, cy, r = W // 2, P(290), P(185)
    d.ellipse((cx - r - P(16), cy - r - P(16), cx + r + P(16), cy + r + P(16)), outline=GOLD, width=max(2, P(3)))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(2, 40, 32), outline=GOLD, width=max(3, P(6)))
    lw = P(250); paste(img, smooth(asset("hajj_logo_white"), lw, S), cx - lw // 2, cy - int(lw * 0.5))
    # arch with the name
    box = (90, 560, 990, 1280)
    am = arch_mask(S, box, img.size)
    lay = Image.new("RGBA", img.size, (2, 34, 26, 0)); lay.putalpha(am.point(lambda v: 226 if v else 0)); img.paste(lay, (0, 0), lay)
    for inset, wd, col in ((0, 6, GOLD), (22, 2, GOLD_LT)):
        bb = (box[0] + inset, box[1] + inset, box[2] - inset, box[3] - inset)
        ox0, oy0, ox1, oy1 = [P(v) for v in bb]; rr = (ox1 - ox0) // 2
        d = ImageDraw.Draw(img)
        d.arc((ox0, oy0, ox1, oy0 + 2 * rr), 180, 360, fill=col, width=max(2, P(wd)))
        d.line((ox0, oy0 + rr, ox0, oy1), fill=col, width=max(2, P(wd))); d.line((ox1, oy0 + rr, ox1, oy1), fill=col, width=max(2, P(wd)))
        d.line((ox0, oy1, ox1, oy1), fill=col, width=max(2, P(wd)))
    d = ImageDraw.Draw(img)
    star8(d, W // 2, P(700), P(52), outline=GOLD_LT, width=max(2, P(3)))
    star8(d, W // 2, P(700), P(30), fill=GOLD, rot=-math.pi / 2 + math.pi / 8)
    fit_text(d, (W / S / 2, 880), NAME1, 150, S, CREAM, 560)
    diamond_divider(img, W // 2, P(980), half=P(260), gap=P(36), col=GOLD, width=max(2, P(4)), size=P(14))
    d = ImageDraw.Draw(img)
    fit_text(d, (W / S / 2, 1130), NAME2, 250, S, GOLD_LT, 720)
    # Rakb al-Abrar
    rw = P(500); paste(img, smooth(tinted("rakb_gold", GOLD_LT), rw, S), (W - rw) // 2, P(1330))
    contact(img, S, 1820, dict(pfill=CREAM, pline=GOLD, icon=GREEN, icon_fg=CREAM, label=BRONZE_TXT, digits=GREEN,
                               lfill=(2, 34, 26), lline=GOLD_LT, ltext=CREAM, pin=GOLD_LT))
    return img

# ================================================================== B : deep green top + cream dome bottom
def build_b(S):
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    top = gradient(W, H, [(0, (3, 66, 40)), (.5, (2, 52, 32)), (1, (2, 36, 22))], 90)
    g, m = glow(W, H, W // 2, P(520), P(760), P(520), (14, 110, 70), .5); top = over(top, (14, 110, 70), m)
    top = add_lattice(top, GOLD_LT, 30, R=P(120))
    bot = paper(W, H)
    bot = add_lattice(bot, (205, 183, 140), 38, ramp=vramp(H, P(1300), P(2300), .1, 1), R=P(120))
    paste(bot, sky_layer(W, 0.55), 0, P(1690))
    # cream "dome" rising into the green
    dome = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(dome)
    dd.rectangle((0, P(1340), W, H), fill=255)
    dd.ellipse((-P(420), P(1010), W + P(420), P(1670)), fill=255)
    img = top.copy(); img.paste(bot, (0, 0), dome.filter(ImageFilter.GaussianBlur(0.6 * S)))
    d = ImageDraw.Draw(img)
    d.arc((-P(420), P(1010), W + P(420), P(1670)), 192, 348, fill=GOLD, width=max(4, P(7)))
    d.arc((-P(420), P(1030), W + P(420), P(1690)), 192, 348, fill=GOLD, width=max(1, P(2)))
    frame(img, P(40), GOLD, max(3, P(4)), P(14), corner=0.9)
    d = ImageDraw.Draw(img)
    # top: authority logo + name
    lw = P(270); paste(img, smooth(asset("hajj_logo_white"), lw, S), (W - lw) // 2, P(120))
    ornament_pair(img, W // 2, P(470), P(DW - 330), col=GOLD_LT, h=P(96))
    star8(d, W // 2, P(470), P(40), outline=GOLD, width=max(2, P(3)))
    d.ellipse((W // 2 - P(8), P(462), W // 2 + P(8), P(478)), fill=GOLD)
    fit_text(d, (W / S / 2, 620), NAME1, 150, S, CREAM, 640)
    diamond_divider(img, W // 2, P(716), half=P(250), gap=P(36), col=GOLD, width=max(2, P(4)), size=P(14))
    d = ImageDraw.Draw(img)
    fit_text(d, (W / S / 2, 850), NAME2, 250, S, GOLD_LT, 880)
    # cream part: Rakb (green) + contact
    rw = P(540); paste(img, smooth(asset("rakb_green"), rw, S), (W - rw) // 2, P(1230))
    contact(img, S, 1830, dict(pfill=GREEN, pline=GOLD, icon=GOLD, icon_fg=GREEN, label=GOLD_LT, digits=CREAM,
                               lfill=CREAM, lline=GOLD, ltext=GREEN, pin=BRONZE_TXT, shadow=70))
    return img

# ================================================================== C : light paper + big green medallion
def build_c(S):
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, P(300), P(2300), .25, 1), R=P(120))
    paste(img, sky_layer(W, 0.6), 0, P(1700))
    # medallion
    cx, cy, r = W // 2, P(330), P(500)
    for rr, col, wd in ((r + P(46), GOLD, 3), (r + P(22), GOLD_LT, 2)):
        ImageDraw.Draw(img).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=max(2, P(wd)))
    md = Image.new("L", img.size, 0); ImageDraw.Draw(md).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    gg = gradient(W, H, [(0, (0, 98, 84)), (1, (3, 58, 36))], 60)
    gg = add_lattice(gg, GOLD_LT, 30, R=P(100))
    img.paste(gg, (0, 0), md.filter(ImageFilter.GaussianBlur(0.6 * S)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=max(4, P(7)))
    for k in range(8):                                        # ring of small stars around the medallion
        a = math.radians(-90 + k * 45 + 22.5)
        star8(d, cx + int((r + P(46)) * math.cos(a)), cy + int((r + P(46)) * math.sin(a)), P(16), fill=GOLD)
    lw = P(400); paste(img, smooth(asset("hajj_logo_white"), lw, S), cx - lw // 2, cy - int(lw * 0.5))
    # name on paper
    fit_text(d, (W / S / 2, 1000), NAME1, 150, S, BRONZE_TXT, 640)
    diamond_divider(img, W // 2, P(1100), half=P(250), gap=P(36), col=GOLD, width=max(2, P(4)), size=P(14))
    d = ImageDraw.Draw(img)
    fit_text(d, (W / S / 2, 1250), NAME2, 250, S, GREEN, 880)
    rw = P(440); paste(img, smooth(asset("rakb_gold"), rw, S), (W - rw) // 2, P(1400))
    contact(img, S, 1840, dict(pfill=GREEN, pline=GOLD, icon=GOLD, icon_fg=GREEN, label=GOLD_LT, digits=CREAM,
                               lfill=CREAM, lline=GOLD, ltext=GREEN, pin=BRONZE_TXT, shadow=70))
    return img

# ================================================================== C2 : layout C + authority name (Hajj & Umrah Authority) as hero
AUTH1, AUTH2 = "الهيئة العامة", "للحج والعمرة"
COORD = "تنسيقية حجاج طرابلس ب"

def build_c2(S):
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, P(300), P(2300), .25, 1), R=P(120))
    paste(img, sky_layer(W, 0.6), 0, P(1780))
    # medallion with the authority logo
    cx, cy, r = W // 2, P(290), P(410)
    for rr, col, wd in ((r + P(44), GOLD, 3), (r + P(21), GOLD_LT, 2)):
        ImageDraw.Draw(img).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=max(2, P(wd)))
    md = Image.new("L", img.size, 0); ImageDraw.Draw(md).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    gg = gradient(W, H, [(0, (0, 98, 84)), (1, (3, 58, 36))], 60)
    gg = add_lattice(gg, GOLD_LT, 30, R=P(100))
    img.paste(gg, (0, 0), md.filter(ImageFilter.GaussianBlur(0.6 * S)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=max(4, P(7)))
    for k_ in range(8):
        a = math.radians(-90 + k_ * 45 + 22.5)
        star8(d, cx + int((r + P(44)) * math.cos(a)), cy + int((r + P(44)) * math.sin(a)), P(15), fill=GOLD)
    lw = P(350); paste(img, smooth(asset("hajj_logo_white"), lw, S), cx - lw // 2, cy - int(lw * 0.5) + P(20))
    # ---- hero plaque: the Authority name
    box = (P(70), P(790), P(DW - 70), P(1215))
    soft_shadow(img, box, P(80), alpha=110, blur=P(26), off=P(14), rgb=(0, 20, 12))
    d = ImageDraw.Draw(img)
    pg = gradient(W, H, [(0, (3, 66, 42)), (1, (2, 38, 24))], 90)
    pm = Image.new("L", img.size, 0); ImageDraw.Draw(pm).rounded_rectangle(box, P(80), fill=255)
    img.paste(pg, (0, 0), pm)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, P(80), outline=GOLD, width=max(4, P(6)))
    d.rounded_rectangle((box[0] + P(16), box[1] + P(16), box[2] - P(16), box[3] - P(16)), P(66), outline=GOLD_LT, width=max(2, P(2)))
    for sx in (-1, 1):
        px_, py_ = (box[0] if sx < 0 else box[2]), (box[1] + box[3]) // 2
        d.polygon([(px_, py_ - P(34)), (px_ + P(34), py_), (px_, py_ + P(34)), (px_ - P(34), py_)], fill=GOLD)
    # star crown sitting on the top border
    sx_, sy_ = W // 2, box[1]
    d.ellipse((sx_ - P(52), sy_ - P(52), sx_ + P(52), sy_ + P(52)), fill=PAPER_A, outline=GOLD, width=max(3, P(5)))
    star8(d, sx_, sy_, P(34), fill=GOLD); star8(d, sx_, sy_, P(17), fill=PAPER_A, rot=-math.pi / 2 + math.pi / 8)
    fit_text(d, (W / S / 2, 920), AUTH1, 150, S, CREAM, 780)
    diamond_divider(img, W // 2, P(1020), half=P(250), gap=P(34), col=GOLD, width=max(2, P(4)), size=P(13))
    d = ImageDraw.Draw(img)
    fit_text(d, (W / S / 2, 1122), AUTH2, 150, S, GOLD_LT, 780)
    # ---- coordination name (smaller than the authority name)
    fit_text(d, (W / S / 2, 1350), COORD, 88, S, GREEN, 800)
    ornament_pair(img, W // 2, P(1350), P(DW - 170), col=GOLD, h=P(70))
    d = ImageDraw.Draw(img)
    diamond_divider(img, W // 2, P(1428), half=P(200), gap=P(30), col=GOLD, width=max(2, P(3)), size=P(11))
    # ---- Rakb al-Abrar
    rw = P(420); paste(img, smooth(asset("rakb_gold"), rw, S), (W - rw) // 2, P(1465))
    # ---- phone (a bit smaller) + place
    contact(img, S, 1870, dict(pfill=GREEN, pline=GOLD, icon=GOLD, icon_fg=GREEN, label=GOLD_LT, digits=CREAM,
                               lfill=CREAM, lline=GOLD, ltext=GREEN, pin=BRONZE_TXT, shadow=70),
            mx=170, ph_h=190, lab=36, dig=98, gap=22, pill_h=80, pill_font=44, pill_mx=300)
    return img

# ================================================================== C3 : refined typography system (authority name redesigned)
def build_c3(S):
    """One type system: Plex Arabic only. Scale (design units): authority key 190/700, authority lead 92/600,
    coordination 84/700, phone label 40/600, digits 100/700, place 46/600."""
    P = lambda v: int(round(v * S)); W, H = P(DW), P(DH)
    img = paper(W, H)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, P(300), P(2300), .25, 1), R=P(120))
    paste(img, sky_layer(W, 0.6), 0, P(1780))
    cx, cy, r = W // 2, P(290), P(400)
    for rr, col, wd in ((r + P(44), GOLD, 3), (r + P(21), GOLD_LT, 2)):
        ImageDraw.Draw(img).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=max(2, P(wd)))
    md = Image.new("L", img.size, 0); ImageDraw.Draw(md).ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    gg = add_lattice(gradient(W, H, [(0, (0, 98, 84)), (1, (3, 58, 36))], 60), GOLD_LT, 30, R=P(100))
    img.paste(gg, (0, 0), md.filter(ImageFilter.GaussianBlur(0.6 * S)))
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=GOLD, width=max(4, P(7)))
    for k_ in range(8):
        a = math.radians(-90 + k_ * 45 + 22.5)
        star8(d, cx + int((r + P(44)) * math.cos(a)), cy + int((r + P(44)) * math.sin(a)), P(15), fill=GOLD)
    lw = P(340); paste(img, smooth(asset("hajj_logo_white"), lw, S), cx - lw // 2, cy - int(lw * 0.5) + P(18))

    # ---- authority name: lead line (small, flanked by ornaments) + key line (large, gold) on a deep-green banner
    box = (P(60), P(770), P(DW - 60), P(1170))
    soft_shadow(img, box, P(70), alpha=110, blur=P(26), off=P(14), rgb=(0, 20, 12))
    pg = gradient(W, H, [(0, (3, 70, 44)), (1, (2, 36, 22))], 90)
    pm = Image.new("L", img.size, 0); ImageDraw.Draw(pm).rounded_rectangle(box, P(70), fill=255)
    img.paste(pg, (0, 0), pm)
    img.paste(add_lattice(Image.new("RGB", img.size, (0, 0, 0)), GOLD_LT, 18, R=P(90)), (0, 0), pm.point(lambda v: int(v * 0.0)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, P(70), outline=GOLD, width=max(4, P(6)))
    d.rounded_rectangle((box[0] + P(16), box[1] + P(16), box[2] - P(16), box[3] - P(16)), P(56), outline=GOLD_LT, width=max(2, P(2)))
    lead_y, key_y = 880, 1030
    lf = font(600, P(92)); lt = lf.getlength(AUTH1, direction="rtl", language="ar")
    d.text((W // 2, P(lead_y)), AUTH1, font=lf, fill=CREAM, anchor="mm", direction="rtl", language="ar")
    for sx in (-1, 1):                                          # ornament lines beside the lead
        x0 = W // 2 + sx * (lt / 2 + P(36)); x1 = W // 2 + sx * (P(DW / 2 - 130))
        d.line((x0, P(lead_y), x1, P(lead_y)), fill=GOLD, width=max(2, P(3)))
        dx = x1; d.polygon([(dx, P(lead_y) - P(11)), (dx + P(11) * sx * -1 * -1, P(lead_y)), (dx, P(lead_y) + P(11)), (dx - P(11) * sx * -1 * -1, P(lead_y))], fill=GOLD)
    kf = font(700, P(190))
    while kf.getlength(AUTH2, direction="rtl", language="ar") > P(DW - 260): kf = font(700, kf.size - 4)
    d.text((W // 2, P(key_y)), AUTH2, font=kf, fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    # star crown on the top border
    sx_, sy_ = W // 2, box[1]
    d.ellipse((sx_ - P(48), sy_ - P(48), sx_ + P(48), sy_ + P(48)), fill=PAPER_A, outline=GOLD, width=max(3, P(5)))
    star8(d, sx_, sy_, P(31), fill=GOLD); star8(d, sx_, sy_, P(15), fill=PAPER_A, rot=-math.pi / 2 + math.pi / 8)

    # ---- coordination name (smaller, same family/weight, green) with a thin gold underline
    fit_text(d, (W / S / 2, 1292), COORD, 84, S, GREEN, 860)
    diamond_divider(img, W // 2, P(1370), half=P(230), gap=P(30), col=GOLD, width=max(2, P(3)), size=P(11))
    # ---- Rakb al-Abrar
    rw = P(400); paste(img, smooth(asset("rakb_gold"), rw, S), (W - rw) // 2, P(1425))
    # ---- phone + place (same scale in both)
    contact(img, S, 1870, dict(pfill=GREEN, pline=GOLD, icon=GOLD, icon_fg=GREEN, label=GOLD_LT, digits=CREAM,
                               lfill=CREAM, lline=GOLD, ltext=GREEN, pin=BRONZE_TXT, shadow=70),
            mx=170, ph_h=190, lab=40, dig=100, gap=22, pill_h=80, pill_font=46, pill_mx=300)
    return img

BUILDS = [("A-teal", build_a), ("B-green-cream", build_b), ("C-light-medallion", build_c), ("C2-authority-name", build_c2), ("C3-refined-type", build_c3)]

if __name__ == "__main__":
    os.makedirs("RollUp", exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    if mode == "preview":
        for n, fn in BUILDS: fn(1.0).save(f"RollUp/v2-preview-{n}.png")
        print("preview ok")
    else:
        S = 3150 / DW
        for n, fn in BUILDS:
            im = fn(S).convert("RGB")
            im.save(f"RollUp/RollUp-{n}-80x180cm.pdf", resolution=100.0)
            im.save(f"RollUp/RollUp-{n}-80x180cm-100dpi.png", dpi=(100, 100))
            print(n, im.size, flush=True)

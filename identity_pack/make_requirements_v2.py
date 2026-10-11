#!/usr/bin/env python3
"""'المستندات المطلوبة' card - v2: the coordination name is the hero, centred; clean grid.
Theme A = light (refined first design), theme B = dark (same layout).  1080x1350."""
from PIL import Image, ImageDraw
from pack_lib import *
from make_requirements import icon, ITEMS, TITLE, NAME

W, H, M = 1080, 1350, 60            # canvas and side margin
GAP = 18

def text_h(t, size, wd, lh=1.46):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    return bc.draw_text(d, wd, 0, 0, t, size, 600, GREEN, "right", lh, measure=True)

def layout(size):
    """card heights for a text size; text column = card - tile - number zone"""
    tw = (W - 2 * M) - 130 - 122 - 16
    hs = [max(112, text_h(t, size, tw) + 2 * 26) for _, t in ITEMS]
    return tw, hs

def build(theme):
    dark = theme == "B"
    # ------------------------------------------------------------- background
    if dark:
        img = gradient(W, H, [(0, TEAL), (.5, (2, 54, 42)), (1, GREEN_DK)], 90)
        g, m = glow(W, H, W / 2, 250, 720, 380, (12, 120, 100), .5); img = over(img, (12, 120, 100), m)
        img = add_lattice(img, GOLD_LT, 34)
        paste(img, sky_layer(W, 0.5, tint=GOLD_LT, blur=1.1), 0, H - 340)
        frame(img, 34, GOLD, 3, 12, corner=0.9)
        ink, hl, sub = CREAM, GOLD_LT, GOLD_LT
    else:
        img = paper(W, H)
        img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, H * .3, H, .1, 1))
        paste(img, sky_layer(W, 0.55), 0, H - 340)
        ink, hl, sub = GREEN, GOLD, GREEN
    d = ImageDraw.Draw(img)

    # ------------------------------------------------------------- hero: logo + name (centred)
    lw = 128
    logo(img, "hajj_logo_white", (W - lw) // 2, 44, w=lw, rgb=None if dark else GREEN)
    plate = (M + 20, 196, W - M - 20, 304)
    if dark:
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle(plate, 54, fill=(2, 34, 22, 235)); img.paste(lay, (0, 0), lay)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle(plate, 54, outline=GOLD, width=3)
        d.rounded_rectangle((plate[0] + 9, plate[1] + 9, plate[2] - 9, plate[3] - 9), 46, outline=GOLD, width=1)
        ncol = GOLD_LT
    else:
        bc.shadowed_round(img, plate, 54, CREAM, GOLD, 3, blur=16, off=8, alpha=65)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((plate[0] + 9, plate[1] + 9, plate[2] - 9, plate[3] - 9), 46, outline=GOLD, width=1)
        ncol = GREEN
    f = font(700, 72)
    tw_name = f.getlength(NAME, direction="rtl", language="ar")
    cy = (plate[1] + plate[3]) / 2 + 2
    d.text((W / 2, cy), NAME, font=f, fill=ncol, anchor="mm", direction="rtl", language="ar")
    for sx in (-1, 1):                                   # diamonds flanking the name, inside the plate
        cx = W / 2 + sx * (tw_name / 2 + 44)
        d.polygon([(cx, cy - 14), (cx + 14, cy), (cx, cy + 14), (cx - 14, cy)], fill=GOLD)

    # ------------------------------------------------------------- title bar
    bar = (M, 330, W - M, 410)
    if dark:
        d.rounded_rectangle(bar, 40, fill=(3, 60, 44), outline=GOLD, width=2)
        tcol = GOLD_LT
    else:
        soft_shadow(img, bar, 40, alpha=60, blur=14, off=7)
        gg = gradient(W, H, [(0, (3, 78, 56)), (1, GREEN)], 0)
        mm = Image.new("L", (W, H), 0); ImageDraw.Draw(mm).rounded_rectangle(bar, 40, fill=255); img.paste(gg, (0, 0), mm)
        d = ImageDraw.Draw(img); d.rounded_rectangle(bar, 40, outline=GOLD, width=2)
        tcol = CREAM
    d = ImageDraw.Draw(img)
    d.text((W / 2 + 26, 370), TITLE, font=font(700, 54), fill=tcol, anchor="mm", direction="rtl", language="ar")
    ic = icon("clip", 46, tcol, 5)
    d.ellipse((W - M - 78, 370 - 31, W - M - 16, 370 + 31), outline=tcol, width=3)
    paste(img, ic, W - M - 47 - 23, 370 - 23)

    # ------------------------------------------------------------- cards
    for size in (40, 38, 36, 34):
        tw, hs = layout(size)
        y_end = 436 + sum(hs) + GAP * (len(hs) - 1)
        if y_end <= 1150:
            break
    y = 436 + (1150 - y_end) / 2 * 0.35                      # slight vertical centring in the free band
    x0, x1 = M, W - M
    for n, ((kind, t), h) in enumerate(zip(ITEMS, hs), 1):
        box = (x0, y, x1, y + h)
        cy = y + h / 2
        if dark:
            lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            ld.rounded_rectangle(box, 36, fill=(2, 40, 28, 210), outline=GOLD + (235,), width=2); img.paste(lay, (0, 0), lay)
            d = ImageDraw.Draw(img)
            star8(d, x1 - 58, cy, 44, fill=GOLD)
            d.text((x1 - 58, cy), str(n), font=font(700, 42), fill=GREEN_DK, anchor="mm")
            ix = x0 + 14 + 59
            d.ellipse((ix - 52, cy - 52, ix + 52, cy + 52), outline=GOLD, width=3)
            paste(img, icon(kind, 72, GOLD_LT, 5), ix - 36, cy - 36)
            col, hcol = CREAM, GOLD_LT
        else:
            bc.shadowed_round(img, box, 36, CREAM, (222, 204, 168), 2, blur=12, off=6, alpha=50)
            d = ImageDraw.Draw(img)
            tile = (x0 + 12, y + 12, x0 + 12 + 118, y + h - 12)
            d.rounded_rectangle(tile, 26, fill=(4, 70, 44))
            paste(img, icon(kind, 84, WHITE, 5), (tile[0] + tile[2]) / 2 - 42, cy - 42)
            d.ellipse((x1 - 58 - 34, cy - 34, x1 - 58 + 34, cy + 34), fill=GREEN)
            d.text((x1 - 58, cy), str(n), font=font(700, 40), fill=WHITE, anchor="mm")
            d.line((x1 - 106, y + 26, x1 - 106, y + h - 26), fill=(214, 196, 160), width=3)
            col, hcol = GREEN, GOLD
        th = text_h(t, size, tw)
        bc.draw_text(d, x1 - 122, x1 - 122 - tw, y + (h - th) / 2, t, size, 600, col, "right", 1.46, hl=hcol)
        y += h + GAP

    # ------------------------------------------------------------- footer: Rakb al-Abrar centred
    d = ImageDraw.Draw(img)
    fy = H - 100
    rk = fit_w(asset("rakb_green"), 150) if not dark else fit_w(tinted("rakb_gold", GOLD_LT), 150)
    paste(img, rk, (W - rk.size[0]) // 2, fy - rk.size[1] // 2)
    for sx in (-1, 1):
        d.line((W / 2 + sx * 120, fy, W / 2 + sx * 330, fy), fill=GOLD, width=2)
        cx = W / 2 + sx * 345
        d.polygon([(cx, fy - 9), (cx + 9, fy), (cx, fy + 9), (cx - 9, fy)], fill=GOLD)
    return img, y

if __name__ == "__main__":
    import os; os.makedirs("Requirements", exist_ok=True)
    for th, name in (("A", "Requirements/Requirements-v2-A-light.png"), ("B", "Requirements/Requirements-v2-B-dark.png")):
        im, y = build(th); im.convert("RGB").save(name); print(th, "cards end", round(y))

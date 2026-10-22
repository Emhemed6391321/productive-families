#!/usr/bin/env python3
"""Medical-exam place card, template 1 redesigned (no cross; one type scale; steps + QR row)."""
from make_medical import *

BRONZE_T = (120, 90, 40)
def build():
    img = paper(W, H, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(H, 0, H, .6, 1)); frame(img, 26, GOLD, 3, 12); cx = W // 2
    paste(img, sky_layer(W, .4), 0, 1085)
    # header
    medallion(img, 140, 140, 64, shadow=False); d = ImageDraw.Draw(img)
    d.text((W - 70, 112), "الهيئة العامة لشؤون الحج والعمرة", font=font(600, 28), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar")
    d.text((W - 70, 160), NAME, font=font(700, 46), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.line((220, 215, W - 70, 215), fill=GOLD, width=2)
    # title block
    ornament_pair(img, cx, 290, 760, col=GOLD, h=60); d = ImageDraw.Draw(img); crown(d, cx, 290, 30, GOLD, PAPER_A)
    d.text((cx, 380), "الكشف الطبي", font=font(700, 108), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((cx, 490), "اعرف مكان عيادتك ومكان مرافقك", font=font(700, 40), fill=GOLD, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, cx, 528, half=300, gap=30, col=GOLD, width=3, size=11)
    # instruction card
    box = (60, 562, W - 60, 712); soft_shadow(img, box, 34, alpha=55, blur=14, off=7); d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, 34, fill=CREAM, outline=(222, 204, 168), width=2); d.rounded_rectangle((box[2] - 14, box[1] + 26, box[2] - 6, box[3] - 26), 4, fill=GOLD)
    f = font(600, 38); ls = wrap(f, TXT, 860); y = (box[1] + box[3]) / 2 - (len(ls) - 1) * 30
    for i, l in enumerate(ls): d.text((cx - 6, y + i * 62), l, font=f, fill=GREEN, anchor="mm", direction="rtl", language="ar")
    # row: steps (right) + QR (left)
    y0 = 750; sx0, sx1 = 400, W - 60
    for i, (t, s) in enumerate(STEPS):
        yy = y0 + i * 112; d.ellipse((sx1 - 84, yy + 6, sx1, yy + 90), fill=GREEN, outline=GOLD, width=3)
        d.text((sx1 - 42, yy + 49), str(i + 1).translate(AR), font=font(700, 46), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
        d.text((sx1 - 104, yy + 32), t, font=font(700, 38), fill=GREEN, anchor="rm", direction="rtl", language="ar"); d.text((sx1 - 104, yy + 72), s, font=font(500, 28), fill=BRONZE_T, anchor="rm", direction="rtl", language="ar")
        if i < 2: d.line((sx1 - 42, yy + 92, sx1 - 42, yy + 120), fill=GOLD, width=3)
    qb = (60, y0 - 4, 60 + 290, y0 - 4 + 290 + 44); soft_shadow(img, qb, 30, alpha=80, blur=14, off=7); d = ImageDraw.Draw(img)
    d.rounded_rectangle(qb, 30, fill=WHITE, outline=GOLD, width=4); img.paste(qr(250, (4, 40, 24), (255, 255, 255)), (qb[0] + 20, qb[1] + 18))
    d.text(((qb[0] + qb[2]) / 2, qb[3] - 30), "امسح الرمز", font=font(700, 30), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    # link pill
    link_pill(img, 1176, w=900)
    footer(img); return img
if __name__ == "__main__":
    build().convert("RGB").save("Medical/Medical-1-cream-v2.png", optimize=True); print("ok")

#!/usr/bin/env python3
"""Edits the user's own notice design (Notice2/user_edit.jpg, 1200x1600):
 1) removes the Rakb al-Abrar logo (bottom-left), 2) writes the three districts under the title pill,
 3) adds "العدد (2)" to the national-number, passport-photo and family-status cards.
Everything else stays pixel-identical except the strip that is moved down to make room for the districts line."""
import numpy as np, cv2
from PIL import Image, ImageDraw
from pack_lib import *

SRC = "Notice2/user_edit.jpg"
DY = 56                                   # room for the districts line
CUT = 506                                 # first row moved down (just below the pill)
END = 1500                                # rows CUT..END move down

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).copy()
H, W = a.shape[:2]

# ---- 1) remove the Rakb al-Abrar logo (gold on skyline) before moving anything
x0, y0, x1, y1 = 110, 1360, 275, 1520
reg = a[y0:y1, x0:x1].astype(int)
mask = ((reg[..., 0] - reg[..., 2] > 38) & (reg[..., 0] > 110) & (reg.sum(2) < 520)).astype(np.uint8) * 255
mask = cv2.dilate(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
patch = cv2.inpaint(np.ascontiguousarray(a[y0:y1, x0:x1, ::-1]), mask, 7, cv2.INPAINT_TELEA)[..., ::-1]
# restore skyline grain in the repaired area from a nearby clean patch of the same band
src_p = a[y0:y1, 950:950 + (x1 - x0)].copy()               # clean skyline grain from the far right (no text there)
soft = cv2.GaussianBlur(mask.astype(np.float32) / 255, (0, 0), 3)[..., None]
grain = src_p.astype(np.float32) - cv2.GaussianBlur(src_p.astype(np.float32), (0, 0), 3)
patch = np.clip(patch.astype(np.float32) + grain * 0.7 * soft, 0, 255)
a[y0:y1, x0:x1] = (a[y0:y1, x0:x1] * (1 - soft) + patch * soft).astype(np.uint8)

# ---- 2) make room: move rows CUT..END down by DY
out = a.copy()
block = a[CUT:END].copy()
out[CUT + DY:END + DY] = block
# fill the opened strip with paper (stretch of the free rows just under the pill so the faint watermark continues)
free = a[CUT + 2:CUT + 26]
strip = cv2.resize(free, (W, DY + 2), interpolation=cv2.INTER_LINEAR)
out[CUT:CUT + DY] = strip[:DY]
# blend the seam at the top of the moved block and at the bottom (skyline fades)
def blend_rows(dst, y_start, y_end, top_img, bot_img):
    n = y_end - y_start
    for i in range(n):
        t = (i + 1) / (n + 1)
        dst[y_start + i] = (top_img[y_start + i] * (1 - t) + bot_img[y_start + i] * t).astype(np.uint8)
orig_shift = a.copy()
bot_seam = END + DY
for i in range(30):
    t = (i + 1) / 31
    y = bot_seam - 30 + i
    out[y] = (out[y] * (1 - t) + a[y] * t).astype(np.uint8)
img = Image.fromarray(out)

# ---- 3) districts under the title pill
d = ImageDraw.Draw(img)
GREEN_T, BRONZE_T = (5, 64, 32), (147, 106, 52)
places = ["طرابلس الهضبة المركز", "سوق الجمعة", "عين زارة"]
f = font(700, 31)
sp = 46
widths = [f.getlength(p, direction="rtl", language="ar") for p in places]
total = sum(widths) + sp * (len(places) - 1) + 2 * 34
cy = CUT + 26 + 6
x = W / 2 + total / 2
for p, w in zip(places, widths):
    d.text((x - 34, cy), p, font=f, fill=GREEN_T, anchor="rm", direction="rtl", language="ar")
    x -= w + sp
    if p is not places[-1]:
        mx = x + sp / 2 - 34 + 0
        d.polygon([(mx, cy - 8), (mx + 8, cy), (mx, cy + 8), (mx - 8, cy)], fill=BRONZE_T)
# little brackets (pin icon) before the whole line
# ---- 4) add "العدد (2)" to three cards (cards are now moved by DY)
def card_text(box, lines):
    bx0, by0, bx1, by1 = box
    d.rounded_rectangle((bx0 + 5, by0 + 5, bx1 - 5, by1 - 5), 18, fill=(238, 229, 212))
    ys = [by0 + (by1 - by0) * 0.34, by0 + (by1 - by0) * 0.72]
    for (t, size, col), yy in zip(lines, ys):
        ff = font(700, size)
        d.text(((bx0 + bx1) / 2, yy), t, font=ff, fill=col, anchor="mm", direction="rtl", language="ar")
BLACK = (14, 12, 8)
card_text((608, 1097 + DY, 1075, 1202 + DY), [("الرقم الوطني (أصلي) 2026م", 36, BLACK), ("العدد (2)", 32, BRONZE_T)])
card_text((125, 1097 + DY, 591, 1202 + DY), [("صورة ملونة لجواز السفر", 36, BLACK), ("العدد (2)", 32, BRONZE_T)])
card_text((608, 1226 + DY, 1075, 1331 + DY), [("الوضع العائلي (أصلي) 2026م", 36, BLACK), ("العدد (2)", 32, BRONZE_T)])
img.save("Notice2/Notice-edited.png", optimize=True)
print("ok", img.size)

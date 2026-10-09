#!/usr/bin/env python3
"""Cut brand assets (logos, ornament, skyline) out of the reference images in refs/.
Run once; results are written to assets/."""
import numpy as np
from PIL import Image, ImageFilter

def load(n): return Image.open(f"refs/{n}").convert("RGB")
def tint(alpha, rgb):
    a = (np.clip(alpha, 0, 1) * 255).astype("uint8")
    im = Image.new("RGBA", alpha.shape[::-1], rgb + (0,))
    im.putalpha(Image.fromarray(a))
    return im
def bbox_crop(im, pad=4):
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    x0, y0, x1, y1 = bb
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad))

r1, r2, r4, r5 = load("ref1_cover.jpg"), load("ref2_media.jpg"), load("ref4_tomorrow.jpg"), load("ref5_logo.jpg")

# ---- palette sampled from the references
a1 = np.asarray(r1).astype(float)
title = a1[150:340, 190:900]
dark = title[title.sum(2) < 220]
GREEN = tuple(int(v) for v in np.median(dark, 0))
logo_zone = a1[505:990, 250:790]
gold_px = logo_zone[(logo_zone[..., 2] < 90) & (logo_zone[..., 0] > 140)]
GOLD = tuple(int(v) for v in np.median(gold_px, 0))
print("GREEN", GREEN, "GOLD", GOLD)

# ---- Rakb al-Abrar calligraphy (gold on beige in ref1) -> alpha mask
z = a1[500:992, 240:800].copy()
# gold is far more saturated (R-B ~ 115) than beige sky (~25) or the grey minarets (~50)
rb = z[..., 0] - z[..., 2]
alpha = np.clip((rb - 48) / (108 - 48), 0, 1)
ys, xs = np.mgrid[500:992, 240:800]
alpha[ys > 990] = 0
alpha[(ys > 972) & (xs > 465) & (xs < 545)] = 0   # specks under the logo
alpha[(ys > 935) & (xs > 765)] = 0
alpha[alpha < 0.06] = 0
try:                                  # drop stray specks (skyline bits, JPEG noise)
    from scipy import ndimage as ndi
    lab, n = ndi.label(alpha > 0)
    sizes = ndi.sum(alpha > 0, lab, range(1, n + 1))
    for i, s_ in enumerate(sizes, 1):
        if s_ < 160:
            alpha[lab == i] = 0
except ImportError:
    pass
m = bbox_crop(tint(alpha, GOLD))
m.save("assets/rakb_gold.png")
tint(np.asarray(m.getchannel("A")) / 255.0, GREEN).save("assets/rakb_green.png")

# ---- Hajj authority logo (white on green, ref5) -> alpha mask
a5 = np.asarray(r5).astype(float)[150:920, 150:930]
lum = a5.mean(2)
alpha = np.clip((lum - 120) / (235 - 120), 0, 1)
h = bbox_crop(tint(alpha, GREEN))
h.save("assets/hajj_green.png")
tint(np.asarray(h.getchannel("A")) / 255.0, (255, 255, 255)).save("assets/hajj_white.png")

# ---- gold diamond ornament beside the titles (ref2)
a2 = np.asarray(r2).astype(float)
box = a2[160:262, 92:148]
al = np.clip((215 - box[..., 2]) / (215 - 80), 0, 1)
bbox_crop(tint(al, GOLD)).save("assets/ornament.png")

# ---- Mecca skyline band (ref1 = full-strength skyline).  The gold logo overlaps its top:
# gold is far more saturated than anything in the photo, so those pixels become plain sky.
sk = np.asarray(r1.crop((0, 930, 1080, 1290))).astype(float)
rb = sk[..., 0] - sk[..., 2]
gold = (rb > 92) | ((rb > 62) & (np.arange(sk.shape[0])[:, None] < 40))
gold[:, :245] = False
gold[:, 800:] = False
gold[70:] = False                        # only the strip of sky under the logo (abs y < 1000)
try:
    from PIL import ImageFilter as _F
    gold = np.asarray(Image.fromarray((gold * 255).astype("uint8")).filter(_F.MaxFilter(11))) > 0
except Exception:
    pass
sky_col = np.median(sk[6:40, 0:160].reshape(-1, 3), 0)
sk[gold] = sky_col
sk[:22, 532:562] = sky_col               # leftover curl of the logo above the middle minaret
Image.fromarray(sk.astype("uint8")).save("assets/skyline_raw.png")

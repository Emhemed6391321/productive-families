"""Shared building blocks for the Tripoli-B identity pack (templates + page covers).

Everything is derived from the reference designs (see ../dawah_cards/refs):
paper beige, deep green, authority teal, bronze/gold, Mecca skyline, girih lattice,
gold diamond ornament, the two logos.  Font: IBM Plex Sans Arabic.
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dawah_cards"))
import build_cards as bc            # fonts, asset loader, shadowed_round, text helpers

# ----------------------------------------------------------------- palette (sampled)
TEAL = (0, 80, 69)                  # authority-logo background (ref 5)
GREEN = (4, 61, 31)                 # title green (ref 1/2/4)
GREEN_DK = (2, 36, 22)
BRONZE = (148, 105, 52)             # gold panels (ref 3)
GOLD = (175, 137, 59)               # gold titles / ornaments (ref 1/2/4)
GOLD_LT = (226, 196, 132)           # highlight used on dark grounds
PAPER_A = (250, 241, 228)           # light centre of the paper
PAPER_B = (240, 230, 214)           # darker paper (ref 3)
PAPER_EDGE = (229, 220, 206)        # vignette corner (ref 1 top-right)
CREAM = (255, 252, 244)
WHITE = (255, 255, 255)

asset, fit_w, paste, font = bc.asset, bc.fit_w, bc.paste, bc.font

# ----------------------------------------------------------------- colour helpers
def lerp(c0, c1, t):
    return tuple(c0[i] * (1 - t) + c1[i] * t for i in range(3))

def gradient(W, H, stops, angle=90):
    """Multi-stop gradient. stops=[(pos, rgb)...]; angle 90 = top->bottom, 0 = left->right."""
    a = math.radians(angle)
    dx, dy = math.cos(a), math.sin(a)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    proj = (xs - W / 2) * dx + (ys - H / 2) * dy
    half = abs(W / 2 * dx) + abs(H / 2 * dy)
    t = np.clip(proj / (2 * half) + 0.5, 0, 1)
    pos = [s[0] for s in stops]
    out = np.zeros((H, W, 3), np.float32)
    for ch in range(3):
        out[..., ch] = np.interp(t, pos, [s[1][ch] for s in stops])
    return Image.fromarray(out.astype("uint8"))

def glow(W, H, cx, cy, rx, ry, rgb, alpha, blur=None):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=int(255 * alpha))
    m = m.filter(ImageFilter.GaussianBlur(blur or min(rx, ry) * 0.6))
    return Image.composite(Image.new("RGB", (W, H), rgb), Image.new("RGB", (W, H)), m), m

def over(img, rgb, mask):
    return Image.composite(Image.new("RGB", img.size, rgb), img, mask)

def tinted(name, rgb):
    im = asset(name)
    out = Image.new("RGBA", im.size, rgb + (0,))
    out.putalpha(im.getchannel("A"))
    return out

# ----------------------------------------------------------------- patterns
_lat = {}
def lattice_mask(W, H, R=110, width=3):
    """Girih-like lattice of overlapping circles (the faint pattern of the references)."""
    k = (W, H, R, width)
    if k not in _lat:
        pat = Image.new("L", (W * 2, H * 2), 0)
        pd = ImageDraw.Draw(pat)
        for j in range(-1, int(H / (R * 0.87)) + 3):
            for i in range(-1, W // R + 3):
                cx = i * R * 2 + (R if j % 2 else 0)
                cy = j * R * 0.87
                pd.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=width)
        _lat[k] = pat.resize((W, H), Image.LANCZOS).crop((0, 0, W, H))
    return _lat[k]

def star8(d, cx, cy, r, inner=0.62, fill=None, outline=None, width=2, rot=-math.pi / 2):
    pts = []
    for i in range(16):
        a = rot + math.pi * i / 8
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill, outline=outline, width=width)

def star_field(W, H, step, rgba_outline, width=2, sub=True):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for gy in range(-1, H // step + 2):
        for gx in range(-1, W // step + 2):
            star8(d, gx * step, gy * step, step * .42, outline=rgba_outline, width=width)
            if sub:
                star8(d, gx * step + step // 2, gy * step + step // 2, step * .2, outline=rgba_outline, width=max(1, width - 1))
    return layer

def apply_alpha(img, layer, a=1.0):
    if a != 1.0:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    img.paste(layer, (0, 0), layer)

# ----------------------------------------------------------------- backgrounds
def paper(W, H, warm=False):
    img = gradient(W, H, [(0, PAPER_A), (1, (243, 234, 219) if not warm else PAPER_B)], 90)
    light = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(light)
    ld.polygon([(W * .52, 0), (W * .84, 0), (W * .46, H * .5), (W * .18, H * .5)], fill=70)
    ld.polygon([(0, H * .1), (W * .24, 0), (W * .3, 0), (0, H * .3)], fill=55)
    light = light.filter(ImageFilter.GaussianBlur(W // 15))
    img = over(img, (255, 252, 244), light)
    # soft vignette in the corners, as in the references
    vg = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vg)
    vd.rectangle((0, 0, W, H), fill=70)
    vd.ellipse((-W * .25, -H * .2, W * 1.25, H * 1.2), fill=0)
    vg = vg.filter(ImageFilter.GaussianBlur(W // 5))
    return over(img, PAPER_EDGE, vg)

def add_lattice(img, rgb, strength, ramp=None, R=110):
    W, H = img.size
    m = np.asarray(lattice_mask(W, H, R, max(2, W // 360)), np.float32) / 255
    if ramp is not None:
        m = m * ramp[:, None]
    return over(img, rgb, Image.fromarray((m * strength).astype("uint8")))

def vramp(H, y0, y1, lo=0.0, hi=1.0):
    return np.clip((np.arange(H) - y0) / max(1, (y1 - y0)), 0, 1) * (hi - lo) + lo

# ----------------------------------------------------------------- skyline
def _raw():
    return np.asarray(asset("skyline_raw").convert("RGB")).astype(np.float32)

def sky_layer(W, strength=1.0, tint=None, blur=0.8):
    """Mecca skyline as an RGBA layer: everything that is not sky is kept (alpha = density).
    tint=None keeps the photo's sepia; tint=(r,g,b) paints it in one colour (for dark grounds)."""
    raw = _raw()
    sky = np.median(raw[6:40, 0:160].reshape(-1, 3), 0)
    dist = np.sqrt(((raw - sky) ** 2).sum(2))
    lo, span = (10, 70) if tint is None else (22, 60)
    alpha = np.clip((dist - lo) / span, 0, 1) ** 0.85 * strength
    rows = np.ones(raw.shape[0]); rows[:12] = np.linspace(0, 1, 12)
    if tint is not None:                       # tinted (dark grounds): fade the lattice-only bottom away
        rows[-100:] *= np.linspace(1, 0, 100)
    alpha *= rows[:, None]
    if tint is None:
        rgb = raw
    else:
        lum = raw.mean(2, keepdims=True) / 255
        rgb = np.array(tint, np.float32)[None, None] * (0.75 + 0.35 * (1 - lum))
    lay = Image.fromarray(np.clip(rgb, 0, 255).astype("uint8")).convert("RGBA")
    lay.putalpha(Image.fromarray((alpha * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(blur)))
    s = W / lay.size[0]
    return lay.resize((W, round(lay.size[1] * s)), Image.LANCZOS)

def sky_photo(height, width):
    """Opaque photographic crop of the skyline, scaled to cover width x height."""
    im = Image.open("assets/skyline_raw.png").convert("RGB")
    s = max(width / im.size[0], height / im.size[1])
    im = im.resize((round(im.size[0] * s), round(im.size[1] * s)), Image.LANCZOS)
    x0 = (im.size[0] - width) // 2
    return im.crop((x0, 0, x0 + width, height))

# ----------------------------------------------------------------- ornaments
def diamond_divider(img, cx, cy, half=230, gap=34, col=GOLD, width=3, size=14):
    d = ImageDraw.Draw(img)
    d.line((cx - half, cy, cx - gap, cy), fill=col, width=width)
    d.line((cx + gap, cy, cx + half, cy), fill=col, width=width)
    d.polygon([(cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)], fill=col)

def ornament_pair(img, cx, cy, span, col=None, h=100):
    o = asset("ornament")
    if col:
        o = tinted("ornament", col)
    s = h / o.size[1]
    o = o.resize((round(o.size[0] * s), h), Image.LANCZOS)
    paste(img, o, cx - span / 2 - o.size[0] / 2, cy - h / 2)
    paste(img, o, cx + span / 2 - o.size[0] / 2, cy - h / 2)

def frame(img, inset, col=GOLD, w=4, inner=14, corner=0.9, stars=True, mids=True):
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle((inset, inset, W - inset, H - inset), outline=col, width=w)
    d.rectangle((inset + inner, inset + inner, W - inset - inner, H - inset - inner), outline=col, width=1)
    if stars:
        for cx, cy in ((inset, inset), (W - inset, inset), (inset, H - inset), (W - inset, H - inset)):
            star8(d, cx, cy, inset * corner, fill=col)
            star8(d, cx, cy, inset * corner * .45, fill=PAPER_A if col == GOLD else GREEN_DK)
    if mids:
        for cx, cy in ((W / 2, inset), (W / 2, H - inset), (inset, H / 2), (W - inset, H / 2)):
            d.polygon([(cx, cy - 12), (cx + 12, cy), (cx, cy + 12), (cx - 12, cy)], fill=col)

def arch(draw_or_mask, box, r_top=None, **kw):
    x0, y0, x1, y1 = box
    r = (x1 - x0) / 2 if r_top is None else r_top
    draw_or_mask.rounded_rectangle(box, r, **kw)

def soft_shadow(img, box, r, alpha=60, blur=22, off=10, rgb=(90, 70, 30)):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + off, box[2], box[3] + off), r, fill=rgb + (alpha,))
    img.paste(sh.filter(ImageFilter.GaussianBlur(blur)), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))

def name_text(img, cx, cy, size, col, weight=700, anchor="mm"):
    from PIL import ImageDraw as ID
    ID.Draw(img).text((cx, cy), "تنسيقية طرابلس ب", font=font(weight, size), fill=col, anchor=anchor,
                      direction="rtl", language="ar")

def logo(img, name, x, y, w=None, h=None, rgb=None):
    im = tinted(name, rgb) if rgb else asset(name)
    if w:
        im = fit_w(im, w)
    else:
        s = h / im.size[1]
        im = im.resize((round(im.size[0] * s), h), Image.LANCZOS)
    paste(img, im, x, y)
    return im.size

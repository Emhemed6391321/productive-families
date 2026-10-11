"""Illustrative city-map renderers (flat + isometric 3D) for the location cards.
The street layout is ONLY a stylised sample - real roads / landmarks must come from the real location."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

N = 7
HQ = (3, 3)                                   # block that holds the headquarters
PARKS = {(1, 5), (5, 1)}
MAIN = {2: 0.78, 4: 0.78}                     # wider avenues after block index i (both directions)

def _axes():
    """block origins along one axis + gap widths"""
    xs, x = [], 0.0
    gaps = []
    for i in range(N):
        xs.append(x)
        g = MAIN.get(i, 0.42)
        gaps.append(g)
        x += 1.0 + g
    total = x - gaps[-1]
    return xs, gaps, total

def layout(seed=11):
    rnd = random.Random(seed)
    blocks = {}
    for i in range(N):
        for j in range(N):
            lots = []
            if (i, j) in PARKS:
                blocks[(i, j)] = dict(kind="park", lots=[]); continue
            if (i, j) == HQ:
                blocks[(i, j)] = dict(kind="hq", lots=[dict(u=.3, v=.3, w=.4, d=.4, h=.34, hq=True),
                                                      dict(u=.05, v=.05, w=.2, d=.2, h=.2),
                                                      dict(u=.75, v=.7, w=.2, d=.25, h=.28)]); continue
            mode = rnd.random()
            if mode < .25:
                lots = [dict(u=.08, v=.08, w=.84, d=.84, h=rnd.choice([.3, .45, .6, .8]))]
            elif mode < .6:
                lots = [dict(u=.06, v=.06, w=.42, d=.88, h=rnd.choice([.2, .3, .5])),
                        dict(u=.52, v=.06, w=.42, d=.88, h=rnd.choice([.25, .4, .65]))]
            else:
                for a in range(2):
                    for b in range(2):
                        if rnd.random() < .1:
                            continue
                        lots.append(dict(u=a * .5 + .06, v=b * .5 + .06, w=.38, d=.38, h=rnd.choice([.16, .22, .3, .42, .56])))
            blocks[(i, j)] = dict(kind="blk", lots=lots)
    return blocks

# ----------------------------------------------------------------------------- isometric
def iso(palette, width=1040, seed=11, pin_h=.0):
    """Returns (RGBA image, info) - info['hq'] = screen position of the HQ roof centre."""
    xs, gaps, total = _axes()
    blocks = layout(seed)
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    S = width / ((total + .4) * 2 * c30)
    ox = width / 2
    oy = 90 + 1.15 * S
    P = lambda x, y, z=0: (ox + (x - y) * c30 * S, oy + (x + y) * s30 * S - z * S)
    W = width
    H = int((total + .4) * 2 * s30 * S + 1.15 * S + 220)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = .22
    d.polygon([P(-pad, -pad), P(total + pad, -pad), P(total + pad, total + pad), P(-pad, total + pad)], fill=palette["road"])
    # slab thickness
    d.polygon([P(-pad, total + pad), P(total + pad, total + pad), P(total + pad, total + pad, -.12), P(-pad, total + pad, -.12)], fill=palette["slab_r"])
    d.polygon([P(total + pad, -pad), P(total + pad, total + pad), P(total + pad, total + pad, -.12), P(total + pad, -pad, -.12)], fill=palette["slab_l"])
    # road centre lines on the main avenues
    for k, g in MAIN.items():
        c = xs[k] + 1.0 + g / 2
        for t in range(0, 36):
            a, b = t * total / 36, (t + .55) * total / 36
            d.line([P(c, a), P(c, b)], fill=palette["marking"], width=max(2, int(S * .018)))
            d.line([P(a, c), P(b, c)], fill=palette["marking"], width=max(2, int(S * .018)))
    # ground of blocks
    order = sorted(blocks, key=lambda k: k[0] + k[1])
    for (i, j) in order:
        b = blocks[(i, j)]
        x0, y0 = xs[i], xs[j]
        col = palette["park"] if b["kind"] == "park" else palette["block"]
        d.polygon([P(x0, y0), P(x0 + 1, y0), P(x0 + 1, y0 + 1), P(x0, y0 + 1)], fill=col)
    hq_pos = None
    items = []
    for (i, j), b in blocks.items():
        x0, y0 = xs[i], xs[j]
        if b["kind"] == "park":
            for t in range(7):
                items.append(("tree", x0 + .15 + (t % 3) * .33, y0 + .2 + (t // 3) * .3, 0))
        for lot in b["lots"]:
            items.append(("box", x0 + lot["u"], y0 + lot["v"], lot))
    items.sort(key=lambda it: (it[1] + (it[3]["w"] if it[0] == "box" else 0)) + (it[2] + (it[3]["d"] if it[0] == "box" else 0)))
    for kind, x, y, lot in items:
        if kind == "tree":
            cx, cy = P(x, y, .12)
            r = S * .12
            d.ellipse((cx - r, cy - r * .8, cx + r, cy + r * .8), fill=palette["tree"])
            continue
        w, dd, h = lot["w"], lot["d"], lot["h"]
        x1, y1 = x + w, y + dd
        hq = lot.get("hq", False)
        roof = palette["hq_roof"] if hq else palette["roof"]
        fr, fl = (palette["hq_r"], palette["hq_l"]) if hq else (palette["face_r"], palette["face_l"])
        # soft shadow on the ground
        d.polygon([P(x1, y), P(x1 + h * .35, y + h * .15), P(x1 + h * .35, y1 + h * .15), P(x1, y1)], fill=palette["shadow"])
        d.polygon([P(x, y1), P(x1, y1), P(x1 + h * .35, y1 + h * .15), P(x + h * .35, y1 + h * .15)], fill=palette["shadow"])
        d.polygon([P(x1, y, 0), P(x1, y1, 0), P(x1, y1, h), P(x1, y, h)], fill=fl)
        d.polygon([P(x, y1, 0), P(x1, y1, 0), P(x1, y1, h), P(x, y1, h)], fill=fr)
        d.polygon([P(x, y, h), P(x1, y, h), P(x1, y1, h), P(x, y1, h)], fill=roof)
        if hq:
            hq_pos = P((x + x1) / 2, (y + y1) / 2, h)
            d.line([P(x, y, h), P(x1, y, h), P(x1, y1, h), P(x, y1, h), P(x, y, h)], fill=palette["hq_edge"], width=3)
    return img, dict(hq=hq_pos, S=S, P=P)

# ----------------------------------------------------------------------------- flat
def flat(palette, w, h, seed=11, rounded=0):
    """Top-down map.  Returns (RGB image, info) - info['pos'](bi,bj,u,v) -> pixel."""
    xs, gaps, total = _axes()
    blocks = layout(seed)
    pad = .3
    S = min(w / (total + 2 * pad), h / (total + 2 * pad))
    ox = (w - total * S) / 2
    oy = (h - total * S) / 2
    X = lambda x: ox + x * S
    Y = lambda y: oy + y * S
    img = Image.new("RGB", (w, h), palette["bg"])
    d = ImageDraw.Draw(img)
    d.rectangle((X(-pad), Y(-pad), X(total + pad), Y(total + pad)), fill=palette["road"])
    for (i, j), b in blocks.items():
        x0, y0 = xs[i], xs[j]
        col = palette["park"] if b["kind"] == "park" else palette["block"]
        d.rounded_rectangle((X(x0), Y(y0), X(x0 + 1), Y(y0 + 1)), int(S * .05), fill=col)
        for lot in b["lots"]:
            c = palette["hq_lot"] if lot.get("hq") else palette["lot"]
            d.rectangle((X(x0 + lot["u"]), Y(y0 + lot["v"]), X(x0 + lot["u"] + lot["w"]), Y(y0 + lot["v"] + lot["d"])), fill=c)
        if b["kind"] == "park":
            for t in range(6):
                cx, cy = X(x0 + .2 + (t % 3) * .3), Y(y0 + .25 + (t // 3) * .45)
                d.ellipse((cx - S * .09, cy - S * .09, cx + S * .09, cy + S * .09), fill=palette["tree"])
    for k, g in MAIN.items():
        c = xs[k] + 1.0 + g / 2
        for t in range(40):
            a, b = t * total / 40, (t + .5) * total / 40
            d.line((X(c), Y(a), X(c), Y(b)), fill=palette["marking"], width=max(2, int(S * .014)))
            d.line((X(a), Y(c), X(b), Y(c)), fill=palette["marking"], width=max(2, int(S * .014)))
    pos = lambda bi, bj, u=.5, v=.5: (X(xs[bi] + u), Y(xs[bj] + v))
    if rounded:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), rounded, fill=255)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(img, (0, 0), m)
        return out, dict(pos=pos, S=S, xs=xs, X=X, Y=Y)
    return img, dict(pos=pos, S=S, xs=xs, X=X, Y=Y)

# ----------------------------------------------------------------------------- pins
def pin(img, x, y, size, color, ring=(255, 255, 255), logo=None, glow_rgb=None):
    """Teardrop map pin whose tip is at (x, y)."""
    k = 3
    s = int(size * 2.2 * k)
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, r = s / 2, size * k * .5
    cy = s - size * k * 1.55 - 4
    d.polygon([(cx - r * .82, cy + r * .55), (cx + r * .82, cy + r * .55), (cx, s - 6)], fill=color)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
    d.ellipse((cx - r * .72, cy - r * .72, cx + r * .72, cy + r * .72), fill=ring)
    d.ellipse((cx - r * .6, cy - r * .6, cx + r * .6, cy + r * .6), fill=color)
    layer = layer.resize((s // k, s // k), Image.LANCZOS)
    if glow_rgb:
        gl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((layer.size[0] * .1, layer.size[1] * .78, layer.size[0] * .9, layer.size[1] * 1.05), fill=glow_rgb + (70,))
        img.paste(gl.filter(ImageFilter.GaussianBlur(10)), (int(x - layer.size[0] / 2), int(y - layer.size[1] + 6)), gl.filter(ImageFilter.GaussianBlur(10)))
    img.paste(layer, (int(x - layer.size[0] / 2), int(y - layer.size[1] + 6)), layer)
    if logo is not None:
        lw = int(size * .78)
        lg = logo.resize((lw, round(logo.size[1] * lw / logo.size[0])), Image.LANCZOS)
        ccx = x
        ccy = y - layer.size[1] + 6 + (layer.size[1] - (size * 1.55 + 4 / k)) * 1.0
        img.paste(lg, (int(ccx - lg.size[0] / 2), int(y - size * 1.55 - lg.size[1] / 2 + 2)), lg)
    return img

def badge(d, x, y, n, fill, text_fill, font, r=26):
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=(255, 255, 255), width=3)
    d.text((x, y + 1), str(n), font=font, fill=text_fill, anchor="mm")

"""Animated-map engine (PIL): worlds, camera, icons, text panel, header.  1080 x 1920 @ 30 fps."""
import sys, os, math, random, json
HS = os.path.dirname(os.path.abspath(__file__)) + '/'
IDP = os.path.abspath(HS + '../identity_pack') + '/'
sys.path.insert(0, IDP); sys.path.insert(0, HS)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
os.chdir(IDP)                      # pack_lib loads fonts/assets relative to identity_pack
from pack_lib import *
W, H, FPS = 1080, 1920, 30
SCX, SCY = 540, 1190              # screen position of the camera centre
INK = (4, 61, 31); EMER = (0, 98, 84); GOLDC = (175, 137, 59); CREAMC = (255, 252, 244)
PAPER_MAP = (241, 233, 217)
def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
def seg(t, a, b): return ease((t - a) / max(1e-6, b - a))
def lerp(a, b, k): return a + (b - a) * k
def F(w, s): return font(w, int(s))

# ------------------------------------------------------------------ world bitmaps
def _roads(img, seed, n=70, area=None, major=6):
    rnd = random.Random(seed); d = ImageDraw.Draw(img); w, h = img.size
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h); a = rnd.uniform(0, 6.28); pts = [(x, y)]
        for k in range(rnd.randint(14, 34)):
            a += rnd.uniform(-.35, .35); L = rnd.uniform(40, 90); x += L * math.cos(a); y += L * math.sin(a); pts.append((x, y))
        big = i < major
        d.line(pts, fill=(236, 214, 160) if big else (225, 211, 184), width=9 if big else rnd.choice([3, 4, 5]), joint="curve")
    return img

def _hills(img, seed, n=34):
    rnd = random.Random(seed); lay = Image.new("L", img.size, 0); d = ImageDraw.Draw(lay); w, h = img.size
    for i in range(n):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h); rx, ry = rnd.uniform(80, 260), rnd.uniform(60, 200); d.ellipse((x - rx, y - ry, x + rx, y + ry), fill=rnd.randint(40, 90))
    lay = lay.filter(ImageFilter.GaussianBlur(60)); img.paste(Image.new("RGB", img.size, (222, 207, 178)), (0, 0), lay)

def make_world(name):
    path = HS + f"work/world_{name}.png"
    if os.path.exists(path): return Image.open(path).convert("RGB")
    if name == "local": w, h = 1900, 2700
    else: w, h = 1500, 2700
    img = Image.new("RGB", (w, h), PAPER_MAP); _hills(img, 3 if name == "local" else 8); _roads(img, 11 if name == "local" else 5, 90 if name == "local" else 40)
    if name == "region":
        sea = Image.new("L", (w, h), 0); coast = [(0, 0), (330, 0), (350, 450), (310, 900), (370, 1350), (520, 1800), (540, 2100), (430, 2450), (380, 2700), (0, 2700)]
        ImageDraw.Draw(sea).polygon(coast, fill=255); sea = sea.filter(ImageFilter.GaussianBlur(2)); img.paste(Image.new("RGB", (w, h), (196, 222, 214)), (0, 0), sea)
        d = ImageDraw.Draw(img); d.line(coast[1:-1], fill=(150, 190, 180), width=6)
        for t, xy, s in (("البحر الأحمر", (150, 1500), 46), ("السعودية", (900, 2350), 54)): d.text(xy, t, font=F(600, s), fill=(190, 178, 150), anchor="mm", direction="rtl", language="ar")
    img = add_lattice(img, (205, 183, 140), 14, R=120)
    img.save(path); return img

_WORLDS = {}
def world(name):
    if name not in _WORLDS: _WORLDS[name] = make_world(name)
    return _WORLDS[name]

# ------------------------------------------------------------------ geometry helpers
def catmull(pts, n=18):
    p = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(p) - 2):
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p[i][j]) + (-p[i - 1][j] + p[i + 1][j]) * t + (2 * p[i - 1][j] - 5 * p[i][j] + 4 * p[i + 1][j] - p[i + 2][j]) * t2 + (-p[i - 1][j] + 3 * p[i][j] - 3 * p[i + 1][j] + p[i + 2][j]) * t3) for j in (0, 1)))
    out.append(pts[-1]); return out

def blob(c, rx, ry, seed, n=22, rough=.16, rot=0.):
    rnd = random.Random(seed); ph = [rnd.uniform(0, 6.28) for _ in range(3)]; out = []
    for i in range(n):
        a = i / n * 6.2832; r = 1 + rough * (math.sin(2 * a + ph[0]) * .6 + math.sin(3 * a + ph[1]) * .3 + math.sin(5 * a + ph[2]) * .2)
        x, y = rx * r * math.cos(a), ry * r * math.sin(a); out.append((c[0] + x * math.cos(rot) - y * math.sin(rot), c[1] + x * math.sin(rot) + y * math.cos(rot)))
    return out

def polylen(pts): return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
def polycut(pts, f):
    tot = polylen(pts) * max(0., min(1., f)); out = [pts[0]]; acc = 0
    for i in range(len(pts) - 1):
        L = math.dist(pts[i], pts[i + 1])
        if acc + L >= tot:
            k = (tot - acc) / L if L else 0; out.append((lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k))); return out
        acc += L; out.append(pts[i + 1])
    return out

# ------------------------------------------------------------------ the frame context
class Ctx:
    def __init__(self, wname, cam, t, T):
        self.t, self.T = t, T; self.cx, self.cy, self.z = cam; self.wname = wname
        self.S = 2                                                   # geometry supersampling
        self.geo = Image.new("RGBA", (W * self.S, H * self.S), (0, 0, 0, 0)); self.g = ImageDraw.Draw(self.geo)
        self.txt = []                                                # deferred 1x text draws (screen coords)
    def w2s(self, p): return ((p[0] - self.cx) * self.z + SCX, (p[1] - self.cy) * self.z + SCY)
    def sz(self, s): return s * min(max(self.z, .55), 2.4) ** .75
    # -- primitives (world coords in, drawn on the 2x layer)
    def poly(self, pts, fill=None, outline=None, width=4, dash=None, alpha=255):
        sp = [(x * self.S, y * self.S) for x, y in map(self.w2s, pts)]
        if fill: self.g.polygon(sp, fill=tuple(fill[:3]) + (int(fill[3] if len(fill) > 3 else 255) * alpha // 255,))
        if outline:
            if not dash: self.g.line(sp + [sp[0]], fill=tuple(outline) + (alpha,), width=int(width * self.S), joint="curve")
            else: self.dashed(sp + [sp[0]], outline, width * self.S, dash * self.S, alpha)
    def dashed(self, sp, col, width, dash, alpha=255):
        on = True; acc = 0
        for i in range(len(sp) - 1):
            a, b = sp[i], sp[i + 1]; L = math.dist(a, b); pos = 0
            while pos < L:
                step = min(dash if on else dash * .8, L - pos) if True else 0
                if on: self.g.line((lerp(a[0], b[0], pos / L), lerp(a[1], b[1], pos / L), lerp(a[0], b[0], (pos + step) / L), lerp(a[1], b[1], (pos + step) / L)), fill=tuple(col) + (alpha,), width=int(width))
                pos += step; on = not on
    def line(self, pts, col, width=8, alpha=255, dash=None, f=1.0, arrow=False):
        pp = polycut(pts, f); sp = [(x * self.S, y * self.S) for x, y in map(self.w2s, pp)]
        if len(sp) < 2: return
        if dash: self.dashed(sp, col, width * self.S, dash * self.S, alpha)
        else: self.g.line(sp, fill=tuple(col) + (alpha,), width=int(width * self.S), joint="curve")
        if arrow and f > .02:
            (x0, y0), (x1, y1) = sp[-2], sp[-1]; a = math.atan2(y1 - y0, x1 - x0); r = width * self.S * 2.2
            self.g.polygon([(x1 + r * math.cos(a), y1 + r * math.sin(a)), (x1 + r * math.cos(a + 2.5), y1 + r * math.sin(a + 2.5)), (x1 + r * math.cos(a - 2.5), y1 + r * math.sin(a - 2.5))], fill=tuple(col) + (alpha,))
    def circle(self, p, r, fill=None, outline=None, width=3, alpha=255):
        x, y = self.w2s(p); x, y, r = x * self.S, y * self.S, r * self.S
        self.g.ellipse((x - r, y - r, x + r, y + r), fill=tuple(fill) + (alpha,) if fill else None, outline=tuple(outline) + (alpha,) if outline else None, width=int(width * self.S))
    def spoly(self, pts, fill, alpha=255, outline=None, width=2):                  # polygon given in SCREEN px
        sp = [(x * self.S, y * self.S) for x, y in pts]; self.g.polygon(sp, fill=tuple(fill) + (alpha,))
        if outline: self.g.line(sp + [sp[0]], fill=tuple(outline) + (alpha,), width=int(width * self.S))
    # -- text (screen coords; drawn at 1x after geometry)
    def tag(self, p, text, size=30, side="left", alpha=1.0, dy=0, fill=INK, ink=CREAMC, leader=True, dist=70):
        x, y = self.w2s(p); f = F(700, size); w = f.getlength(text, direction="rtl", language="ar") + 36; h = size * 1.5
        tx = x - dist - w / 2 if side == "left" else x + dist + w / 2; ty = y + dy
        if leader: self.line_screen((x, y), (tx + (w / 2 if side == "left" else -w / 2), ty), (255, 255, 255), 4, alpha)
        self.txt.append(("tag", (tx, ty, w, h), text, size, fill, ink, alpha))
    def line_screen(self, a, b, col, width, alpha=1.0):
        self.g.line((a[0] * self.S, a[1] * self.S, b[0] * self.S, b[1] * self.S), fill=tuple(col) + (int(255 * alpha),), width=int(width * self.S))
    def label(self, p, text, size=34, alpha=1.0, col=INK, halo=True):
        x, y = self.w2s(p); self.txt.append(("label", (x, y), text, size, col, alpha, halo))

def draw_texts(img, ctx):
    d = ImageDraw.Draw(img, "RGBA")
    for it in ctx.txt:
        if it[0] == "tag":
            _, (cx, cy, w, h), text, size, fill, ink, alpha = it
            d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 9, fill=tuple(fill) + (int(235 * alpha),))
            d.text((cx, cy + 1), text, font=F(700, size), fill=tuple(ink) + (int(255 * alpha),), anchor="mm", direction="rtl", language="ar")
        else:
            _, (x, y), text, size, col, alpha, halo = it; f = F(700, size)
            if halo:
                for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, -2), (2, -2), (-2, 2)): d.text((x + dx, y + dy), text, font=f, fill=(255, 252, 244, int(230 * alpha)), anchor="mm", direction="rtl", language="ar")
            d.text((x, y), text, font=f, fill=tuple(col) + (int(255 * alpha),), anchor="mm", direction="rtl", language="ar")

# ------------------------------------------------------------------ icons (drawn on ctx 2x layer, world coords)
def kaaba(ctx, p, s=1.0, alpha=255):
    s = ctx.sz(46) * s; x, y = ctx.w2s(p); S = ctx.S; g = ctx.g
    top = [(x, y - s * .55), (x + s * .62, y - s * .25), (x, y + s * .05), (x - s * .62, y - s * .25)]
    left = [(x - s * .62, y - s * .25), (x, y + s * .05), (x, y + s * .75), (x - s * .62, y + s * .45)]
    right = [(x, y + s * .05), (x + s * .62, y - s * .25), (x + s * .62, y + s * .45), (x, y + s * .75)]
    ctx.spoly(top, (60, 60, 64), alpha); ctx.spoly(left, (18, 18, 20), alpha); ctx.spoly(right, (34, 34, 38), alpha)
    band = lambda f0, f1, A, B, col: ctx.spoly([(A[0][0], lerp(A[0][1], A[1][1], f0)), (A[1][0], lerp(A[0][1], A[1][1], f0) + (A[1][1] - A[0][1]) * 0), (B[1][0], lerp(B[0][1], B[1][1], f0)), (B[0][0], lerp(B[0][1], B[1][1], f0))], col, alpha)
    for pts in (left, right):                                    # gold band (upper third)
        a, b, c_, d_ = pts; k0, k1 = .12, .26
        P = lambda u, k: (lerp(a[0], d_[0], k) if u == 0 else lerp(b[0], c_[0], k), lerp(a[1], d_[1], k) if u == 0 else lerp(b[1], c_[1], k))
        ctx.spoly([P(0, k0), P(1, k0), P(1, k1), P(0, k1)], (226, 196, 132), alpha)
    ctx.spoly(top, (60, 60, 64), alpha, outline=(120, 120, 124), width=1)

def haram_rings(ctx, p, r=120, alpha=255, rot=0.0):
    for k, (rr, col) in enumerate(((r, (30, 30, 30)), (r * .78, (150, 140, 120)))):
        x, y = ctx.w2s(p); n = 56
        for i in range(n):
            a0 = i / n * 6.2832 + rot * (1 if k == 0 else -1); a1 = a0 + 6.2832 / n * .55; rs = ctx.sz(rr)
            ctx.g.line((x * ctx.S + rs * ctx.S * math.cos(a0), y * ctx.S + rs * .62 * ctx.S * math.sin(a0), x * ctx.S + rs * ctx.S * math.cos(a1), y * ctx.S + rs * .62 * ctx.S * math.sin(a1)), fill=col + (alpha,), width=int(5 * ctx.S))

def tents(ctx, poly_pts, n=60, seed=1, alpha=255, upto=1.0):
    rnd = random.Random(seed); xs = [p[0] for p in poly_pts]; ys = [p[1] for p in poly_pts]; got = 0; tries = 0; pts = []
    from shapely.geometry import Polygon, Point
    pg = Polygon(poly_pts)
    while got < n and tries < n * 30:
        tries += 1; q = (rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys)))
        if pg.contains(Point(q)): pts.append(q); got += 1
    for q in pts[:int(len(pts) * upto)]:
        x, y = ctx.w2s(q); s = ctx.sz(11)
        ctx.spoly([(x, y - s), (x + s * .9, y + s * .6), (x - s * .9, y + s * .6)], (255, 255, 255), alpha, outline=(120, 120, 110), width=1)

def jamarat(ctx, p, alpha=255, s=1.0):
    x, y = ctx.w2s(p); k = ctx.sz(16) * s
    ctx.spoly([(x - k * 3, y + k * .5), (x + k * 3, y + k * .5), (x + k * 3.4, y + k * 1.4), (x - k * 3.4, y + k * 1.4)], (150, 150, 150), alpha)
    for dx in (-2, 0, 2): ctx.spoly([(x + k * dx - k * .35, y - k * 1.8 + k * .5), (x + k * dx + k * .35, y - k * 1.8 + k * .5), (x + k * dx + k * .45, y + k * .6), (x + k * dx - k * .45, y + k * .6)], (110, 110, 112), alpha)

def jabal(ctx, p, alpha=255):
    x, y = ctx.w2s(p); r = ctx.sz(30); ctx.g.ellipse(((x - r) * ctx.S, (y - r) * ctx.S, (x + r) * ctx.S, (y + r) * ctx.S), fill=(255, 252, 244, alpha), outline=(175, 137, 59, alpha), width=int(3 * ctx.S))
    ctx.spoly([(x - r * .7, y + r * .45), (x - r * .1, y - r * .5), (x + r * .25, y - r * .1), (x + r * .45, y - r * .3), (x + r * .75, y + r * .45)], (150, 108, 62), alpha)

def sheep(ctx, p, alpha=255):
    x, y = ctx.w2s(p); k = ctx.sz(14); g = ctx.g; S = ctx.S
    g.ellipse(((x - k) * S, (y - k * .6) * S, (x + k * .9) * S, (y + k * .7) * S), fill=(255, 255, 255, alpha), outline=(90, 90, 90, alpha), width=2 * S)
    g.ellipse(((x + k * .7) * S, (y - k * .5) * S, (x + k * 1.5) * S, (y + k * .2) * S), fill=(60, 60, 60, alpha))
    for dx in (-.6, .5): g.line((((x + k * dx) * S), (y + k * .6) * S, (x + k * dx) * S, (y + k * 1.3) * S), fill=(60, 60, 60, alpha), width=3 * S)

def pin(ctx, p, col=GOLDC, r=15, alpha=255, ring=CREAMC):
    x, y = ctx.w2s(p); r = r * min(max(ctx.z, .7), 1.6) ** .5; S = ctx.S
    ctx.g.ellipse(((x - r - 4) * S, (y - r - 4) * S, (x + r + 4) * S, (y + r + 4) * S), fill=ring + (alpha,)); ctx.g.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=col + (alpha,))
    ctx.g.ellipse(((x - r * .4) * S, (y - r * .4) * S, (x + r * .4) * S, (y + r * .4) * S), fill=ring + (alpha,))

def moon(ctx, x, y, r, alpha=255):
    S = ctx.S; ctx.g.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(255, 241, 200, alpha)); ctx.g.ellipse(((x - r * .55) * S, (y - r * 1.1) * S, (x + r * 1.2) * S, (y + r * .7) * S), fill=(40, 50, 60, 0))
def sun_icon(ctx, x, y, r, alpha=255):
    S = ctx.S
    for k in range(12):
        a = k * .5236; ctx.g.line(((x + r * 1.3 * math.cos(a)) * S, (y + r * 1.3 * math.sin(a)) * S, (x + r * 1.8 * math.cos(a)) * S, (y + r * 1.8 * math.sin(a)) * S), fill=(226, 196, 132, alpha), width=int(5 * S))
    ctx.g.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(175, 137, 59, alpha)); ctx.g.ellipse(((x - r * .7) * S, (y - r * .7) * S, (x + r * .7) * S, (y + r * .7) * S), fill=(226, 196, 132, alpha))

# ------------------------------------------------------------------ chrome: header / panel / footer
_LOGO = None
def _logos():
    global _LOGO
    if _LOGO is None:
        lg = Image.open(IDP + "assets/coordination_logo.jpg").convert("RGB"); c = min(lg.size) / 2
        lg = lg.crop((int(lg.size[0] / 2 - c * .985), int(lg.size[1] / 2 - c * .985), int(lg.size[0] / 2 + c * .985), int(lg.size[1] / 2 + c * .985))).resize((150, 150), Image.LANCZOS)
        m = Image.new("L", (150, 150), 0); ImageDraw.Draw(m).ellipse((0, 0, 149, 149), fill=255); lg.putalpha(m)
        au = Image.open(IDP + "assets/hajj_green.png").convert("RGBA"); au = au.resize((96, int(au.size[1] * 96 / au.size[0])), Image.LANCZOS)
        _LOGO = (lg, au)
    return _LOGO

def header(img):
    lay = Image.new("RGBA", (W, 250), (0, 0, 0, 0)); gd = ImageDraw.Draw(lay)
    for y in range(250): gd.line((0, y, W, y), fill=(250, 241, 228, int(235 * (1 - y / 250) ** 1.3)))
    img.alpha_composite(lay, (0, 0)); lg, au = _logos(); d = ImageDraw.Draw(img, "RGBA")
    img.alpha_composite(lg, (46, 40)); d.ellipse((42, 36, 200, 194), outline=GOLD + (255,), width=3)
    d.text((W - 214, 74), "الهيئة العامة لشؤون الحج والعمرة", font=F(600, 33), fill=INK + (255,), anchor="rm", direction="rtl", language="ar")
    d.text((W - 214, 124), "تنسيقية حجاج طرابلس ب", font=F(700, 50), fill=INK + (255,), anchor="rm", direction="rtl", language="ar")
    d.line((W - 214 - 380, 160, W - 214, 160), fill=GOLD + (255,), width=3)
    img.alpha_composite(au, (W - 196 + 18, 52))

def wrap_ar(f, text, maxw):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t, direction="rtl", language="ar") <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]

def panel(img, t, T, tag, title, bullets, fs=37, top=250):
    """tag pill + title + bullet card.  bullets = [(text, t_start_frac)]"""
    d = ImageDraw.Draw(img, "RGBA"); a_in = seg(t, 0.15, 0.7); x1 = W - 56
    if tag:
        f = F(700, 38); w = f.getlength(tag, direction="rtl", language="ar") + 44; ox = (1 - a_in) * 40
        d.rounded_rectangle((x1 - w + ox, top, x1 + ox, top + 62), 12, fill=EMER + (int(255 * a_in),)); d.text((x1 - w / 2 + ox, top + 32), tag, font=f, fill=GOLD_LT + (int(255 * a_in),), anchor="mm", direction="rtl", language="ar")
    if title: d.text((x1 + (1 - a_in) * 40, top + 118), title, font=F(700, 64), fill=INK + (int(255 * a_in),), anchor="rm", direction="rtl", language="ar")
    if not bullets: return
    fb = F(600, fs); lh = int(fs * 1.5); lines = []
    for txt, tf in bullets: lines.append((wrap_ar(fb, txt, 840), tf * T))
    hh = sum(len(l) for l, _ in lines) * lh + len(lines) * 20 + 34; y0 = top + 160
    d.rounded_rectangle((44, y0, W - 44, y0 + hh), 30, fill=(255, 252, 244, int(226 * a_in)), outline=(222, 204, 168, int(255 * a_in)), width=2)
    y = y0 + 28
    for ls, ts in lines:
        n_tot = sum(len(x) for x in ls); done = 0; k = seg(t, ts, ts + max(1.2, n_tot / 24)) ; shown = int(n_tot * k)
        if k > 0: d.rectangle((W - 44 - 36, y + lh // 2 - 7, W - 44 - 22, y + lh // 2 + 7), fill=GOLD + (255,))
        for ln in ls:
            take = max(0, min(len(ln), shown - done)); done += len(ln)
            if take > 0:
                part = ln[:take] if take < len(ln) else ln
                d.text((W - 44 - 60, y + lh // 2), part, font=fb, fill=INK + (255,), anchor="rm", direction="rtl", language="ar")
            y += lh
        y += 20

def footer(img):
    d = ImageDraw.Draw(img, "RGBA"); f = F(600, 26)
    d.text((W // 2, H - 30), "الرسم توضيحي وغير مقيّد بمقياس رسم  •  تنسيقية حجاج طرابلس ب  •  0934455422", font=f, fill=(90, 80, 60, 230), anchor="mm", direction="rtl", language="ar")

# ------------------------------------------------------------------ frame renderer
def render(scene, t, T):
    cam = scene["cam"](t, T); wname = scene["world"]
    wim = world(wname); z = cam[2]
    base = wim.transform((W, H), Image.AFFINE, (1 / z, 0, cam[0] - SCX / z, 0, 1 / z, cam[1] - SCY / z), resample=Image.BICUBIC, fillcolor=PAPER_MAP)
    ctx = Ctx(wname, cam, t, T)
    scene["draw"](ctx, t, T)
    geo = ctx.geo.resize((W, H), Image.LANCZOS); img = base.convert("RGBA"); img.alpha_composite(geo)
    if scene.get("dusk"):
        k = scene["dusk"](t, T)
        if k > 0: img.alpha_composite(Image.new("RGBA", (W, H), (20, 38, 60, int(150 * k))))
    draw_texts(img, ctx)
    if scene.get("extra"): scene["extra"](img, ctx, t, T)
    header(img); p = scene.get("panel")
    if p: panel(img, t, T, *p)
    footer(img)
    fl = scene.get("flash_in", 0)
    if fl and t < fl: img.alpha_composite(Image.new("RGBA", (W, H), (250, 241, 228, int(255 * (1 - t / fl)))))
    fo = scene.get("flash_out", 0)
    if fo and t > T - fo: img.alpha_composite(Image.new("RGBA", (W, H), (250, 241, 228, int(255 * (t - (T - fo)) / fo))))
    return img.convert("RGB")

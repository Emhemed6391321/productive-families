"""3-D animated-map engine: pitched/rotating perspective camera, extruded areas, 3-D icons, moving pilgrims."""
from engine import *
from engine import _logos
import cv2

FOC = 2300.0
class Cam:
    def __init__(self, cx, cy, zoom, pitch, yaw):
        self.cx, self.cy, self.zoom, self.pitch, self.yaw = cx, cy, zoom, pitch, yaw
        self.th = math.radians(pitch); self.ya = math.radians(yaw); self.ct, self.st = math.cos(self.th), math.sin(self.th); self.cy_, self.sy_ = math.cos(self.ya), math.sin(self.ya)
    def project(self, wx, wy, h=0.0):
        dx, dy = wx - self.cx, wy - self.cy
        X = (dx * self.cy_ - dy * self.sy_) * self.zoom; Y = (dx * self.sy_ + dy * self.cy_) * self.zoom; Zh = h * self.zoom
        Yp = Y * self.ct - Zh * self.st; Dz = Y * self.st + Zh * self.ct; d = max(.35, 1 - Dz / FOC)
        return SCX + X / d, SCY + Yp / d, self.zoom / d, Dz

def warp_base(wim_np, cam, fill):
    R = 1700; src = np.float32([[cam.cx - R, cam.cy - R], [cam.cx + R, cam.cy - R], [cam.cx + R, cam.cy + R], [cam.cx - R, cam.cy + R]])
    dst = np.float32([cam.project(x, y)[:2] for x, y in src]); Hm = cv2.getPerspectiveTransform(src, dst)
    out = cv2.warpPerspective(wim_np, Hm, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=fill)
    return Image.fromarray(out)

def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c[:3])

class Ctx3:
    def __init__(self, wname, camp, t, T):
        self.t, self.T, self.wname = t, T, wname; self.cam = Cam(*camp); self.z = self.cam.zoom; self.cx, self.cy = camp[0], camp[1]
        self.S = 2; self.geo = Image.new("RGBA", (W * self.S, H * self.S), (0, 0, 0, 0)); self.g = ImageDraw.Draw(self.geo); self.txt = []
        self.queue = []                                            # depth-sorted 3-D draw calls
    # ---- projection helpers
    def P(self, p, h=0.0): return self.cam.project(p[0], p[1], h)
    def w2s(self, p, h=0.0): x, y, s, d = self.P(p, h); return (x, y)
    def ks(self): return self.cam.zoom
    def sk(self, p=None, h=0.0):
        pp = p or (self.cx, self.cy); return self.P(pp, h)[2] / self.cam.zoom
    def sz(self, s): return s
    def S2(self, pts): return [(x * self.S, y * self.S) for x, y in pts]
    # ---- ground / raised polygons
    def poly(self, pts, fill=None, outline=None, width=4, dash=None, alpha=255, h=0.0):
        sp = self.S2([self.P(p, h)[:2] for p in pts])
        if fill: self.g.polygon(sp, fill=tuple(fill[:3]) + (int(fill[3] if len(fill) > 3 else 255) * alpha // 255,))
        if outline:
            if dash: self.dashed(sp + [sp[0]], outline, width * self.S, dash * self.S, alpha)
            else: self.g.line(sp + [sp[0]], fill=tuple(outline) + (alpha,), width=int(width * self.S), joint="curve")
    def dashed(self, sp, col, width, dash, alpha=255):
        on = True
        for i in range(len(sp) - 1):
            a, b = sp[i], sp[i + 1]; L = math.dist(a, b); pos = 0
            while pos < L:
                step = min(dash if on else dash * .8, L - pos)
                if on: self.g.line((lerp(a[0], b[0], pos / L), lerp(a[1], b[1], pos / L), lerp(a[0], b[0], (pos + step) / L), lerp(a[1], b[1], (pos + step) / L)), fill=tuple(col) + (alpha,), width=int(width))
                pos += step; on = not on
    def extrude(self, pts, height, top, side, outline=None, alpha=255, shadow=True, edge=None):
        """3-D prism from a ground polygon. Sides painted far->near, then the top."""
        if shadow:
            sh = [(p[0] + height * .55, p[1] + height * .75) for p in pts]; self.poly(sh, fill=(40, 30, 10, 45), alpha=alpha)
        n = len(pts); faces = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]; q = [self.P(a, 0), self.P(b, 0), self.P(b, height), self.P(a, height)]
            nx, ny = b[1] - a[1], -(b[0] - a[0])                        # outward normal (polygon orientation agnostic below)
            faces.append((sum(v[3] for v in q) / 4, [v[:2] for v in q], a, b))
        cxm = sum(p[0] for p in pts) / n; cym = sum(p[1] for p in pts) / n
        for dz, q, a, b in sorted(faces, key=lambda f: f[0]):
            mx, my = (a[0] + b[0]) / 2 - cxm, (a[1] + b[1]) / 2 - cym; ang = math.atan2(my, mx)
            k = .72 + .22 * math.cos(ang - 2.2); self.g.polygon(self.S2(q), fill=shade(side, k) + (alpha,))
        self.poly(pts, fill=top, outline=outline, width=2, alpha=alpha, h=height)
    def box(self, c, w, d, h, top, side, alpha=255, shadow=True, rot=0.0):
        pts = [(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)]; cr, sr = math.cos(rot), math.sin(rot)
        self.extrude([(c[0] + x * cr - y * sr, c[1] + x * sr + y * cr) for x, y in pts], h, top, side, alpha=alpha, shadow=shadow)
    def line(self, pts, col, width=8, alpha=255, dash=None, f=1.0, arrow=False, h=2.0):
        pp = polycut(pts, f); sp = self.S2([self.P(p, h)[:2] for p in pp])
        if len(sp) < 2: return
        wpx = width * min(1.5, max(.6, self.sk(pts[len(pts) // 2])))
        if dash: self.dashed(sp, col, wpx * self.S, dash * self.S, alpha)
        else:
            self.g.line(sp, fill=tuple(shade(col, .6)) + (alpha // 2,), width=int(wpx * self.S * 1.5), joint="curve") if False else None
            self.g.line(sp, fill=tuple(col) + (alpha,), width=int(wpx * self.S), joint="curve")
        if arrow and f > .02:
            (x0, y0), (x1, y1) = sp[-2], sp[-1]; a = math.atan2(y1 - y0, x1 - x0); r = wpx * self.S * 2.4
            self.g.polygon([(x1 + r * math.cos(a), y1 + r * math.sin(a)), (x1 + r * math.cos(a + 2.5), y1 + r * math.sin(a + 2.5)), (x1 + r * math.cos(a - 2.5), y1 + r * math.sin(a - 2.5))], fill=tuple(col) + (alpha,))
    def circle(self, p, r, fill=None, outline=None, width=3, alpha=255, h=0.0):
        x, y, s, d = self.P(p, h); r = r * s / self.cam.zoom * 1.0; x, y, r = x * self.S, y * self.S, r * self.S
        self.g.ellipse((x - r, y - r, x + r, y + r), fill=tuple(fill) + (alpha,) if fill else None, outline=tuple(outline) + (alpha,) if outline else None, width=int(width * self.S))
    def disc(self, c, r, fill, outline=None, width=3, alpha=255, h=0.0, n=48):
        self.poly([(c[0] + r * math.cos(i / n * 6.2832), c[1] + r * math.sin(i / n * 6.2832)) for i in range(n)], fill=fill, outline=outline, width=width, alpha=alpha, h=h)
    def spoly(self, pts, fill, alpha=255, outline=None, width=2):
        sp = self.S2(pts); self.g.polygon(sp, fill=tuple(fill) + (alpha,))
        if outline: self.g.line(sp + [sp[0]], fill=tuple(outline) + (alpha,), width=int(width * self.S))
    def tag(self, p, text, size=30, side="left", alpha=1.0, dy=0, fill=INK, ink=CREAMC, leader=True, dist=70, h=0.0):
        x, y, s, d = self.P(p, h); f = F(700, size); w = f.getlength(text, direction="rtl", language="ar") + 36; hh = size * 1.5
        tx = x - dist - w / 2 if side == "left" else x + dist + w / 2; ty = y + dy
        if leader: self.g.line((x * self.S, y * self.S, (tx + (w / 2 if side == "left" else -w / 2)) * self.S, ty * self.S), fill=(255, 255, 255, int(255 * alpha)), width=4 * self.S)
        self.txt.append(("tag", (tx, ty, w, hh), text, size, fill, ink, alpha))
    def label(self, p, text, size=34, alpha=1.0, col=INK, halo=True, h=0.0):
        x, y, s, d = self.P(p, h); k = min(1.25, max(.8, s / self.cam.zoom)); self.txt.append(("label", (x, y), text, int(size * k), col, alpha, halo))

# ------------------------------------------------------------------ 3-D icons
def kaaba(ctx, p, s=1.0, alpha=255):
    a = 34 * s; h = 82 * s
    ctx.disc(p, a * 3.0, (255, 252, 244), outline=(222, 204, 168), width=3, alpha=alpha // 2)
    pts = [(p[0] - a, p[1] - a), (p[0] + a, p[1] - a), (p[0] + a, p[1] + a), (p[0] - a, p[1] + a)]
    ctx.extrude(pts, h, (48, 48, 52), (20, 20, 22), alpha=alpha)
    # gold band (thin ring just outside the walls)
    b = a * 1.02; ring = [(p[0] - b, p[1] - b), (p[0] + b, p[1] - b), (p[0] + b, p[1] + b), (p[0] - b, p[1] + b)]
    faces = []
    for i in range(4):
        u, v = ring[i], ring[(i + 1) % 4]; q = [ctx.P(u, h * .62), ctx.P(v, h * .62), ctx.P(v, h * .80), ctx.P(u, h * .80)]; faces.append((sum(z[3] for z in q) / 4, [z[:2] for z in q], i))
    cxm, cym = p
    for dz, q, i in sorted(faces):
        u, v = ring[i], ring[(i + 1) % 4]; ang = math.atan2((u[1] + v[1]) / 2 - cym, (u[0] + v[0]) / 2 - cxm); ctx.g.polygon(ctx.S2(q), fill=shade((226, 196, 132), .7 + .3 * math.cos(ang - 2.2)) + (alpha,))
def haram_rings(ctx, p, r=120, alpha=255, rot=0.0):
    rr = r * 1.55
    ctx.disc(p, rr * 1.15, (250, 244, 232), outline=(200, 186, 150), width=2, alpha=min(alpha, 235))
    for k, (R, col) in enumerate(((rr, (30, 30, 30)), (rr * .78, (150, 140, 120)))):
        n = 56
        for i in range(n):
            a0 = i / n * 6.2832 + rot * (1 if k == 0 else -1); a1 = a0 + 6.2832 / n * .55
            q0 = ctx.P((p[0] + R * math.cos(a0), p[1] + R * math.sin(a0)))[:2]; q1 = ctx.P((p[0] + R * math.cos(a1), p[1] + R * math.sin(a1)))[:2]
            ctx.g.line((q0[0] * ctx.S, q0[1] * ctx.S, q1[0] * ctx.S, q1[1] * ctx.S), fill=col + (alpha,), width=int(5 * ctx.S))
    for i in range(4):                                                  # minarets
        a = i * 1.5708 + .785; c = (p[0] + rr * 1.12 * math.cos(a), p[1] + rr * 1.12 * math.sin(a)); ctx.box(c, 13, 13, 85, (236, 228, 210), (200, 190, 168), alpha, shadow=False); ctx.box(c, 9, 9, 100, (226, 196, 132), (175, 137, 59), alpha, shadow=False)

def tents(ctx, poly_pts, n=60, seed=1, alpha=255, upto=1.0):
    from shapely.geometry import Polygon, Point
    rnd = random.Random(seed); xs = [p[0] for p in poly_pts]; ys = [p[1] for p in poly_pts]; pg = Polygon(poly_pts).buffer(-18); pts = []; tries = 0
    while len(pts) < n and tries < n * 40:
        tries += 1; q = (rnd.uniform(min(xs), max(xs)), rnd.uniform(min(ys), max(ys)))
        if pg.contains(Point(q)): pts.append(q)
    items = sorted(pts[:int(len(pts) * upto)], key=lambda q: ctx.P(q)[3])
    for q in items:
        s = 15; base = [(q[0] - s, q[1] - s), (q[0] + s, q[1] - s), (q[0] + s, q[1] + s), (q[0] - s, q[1] + s)]; apex = ctx.P(q, 24)[:2]
        ps = [ctx.P(b)[:2] for b in base]
        for i in sorted(range(4), key=lambda i: -(ctx.P(base[i])[3] + ctx.P(base[(i + 1) % 4])[3])):
            a, b = ps[i], ps[(i + 1) % 4]; mx = (base[i][0] + base[(i + 1) % 4][0]) / 2 - q[0]; my = (base[i][1] + base[(i + 1) % 4][1]) / 2 - q[1]
            k = .8 + .2 * math.cos(math.atan2(my, mx) - 2.2); ctx.g.polygon(ctx.S2([a, b, apex]), fill=shade((255, 255, 255), k) + (alpha,), outline=(150, 145, 130, alpha))

def jamarat(ctx, p, alpha=255, s=1.0):
    ctx.box(p, 150 * s, 62 * s, 7, (200, 196, 186), (150, 146, 138), alpha)
    for dx in (-52, 0, 52): ctx.box((p[0] + dx * s, p[1]), 15 * s, 40 * s, 52 * s, (170, 170, 172), (110, 110, 114), alpha, shadow=False)

def jabal(ctx, p, alpha=255):
    n = 14; r = 52; apex = ctx.P(p, 78)[:2]
    ring = [(p[0] + r * math.cos(i / n * 6.2832), p[1] + r * .8 * math.sin(i / n * 6.2832)) for i in range(n)]
    tri = []
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]; ang = i / n * 6.2832; tri.append((ctx.P(a)[3] + ctx.P(b)[3], [ctx.P(a)[:2], ctx.P(b)[:2], apex], ang))
    for _, q, ang in sorted(tri): ctx.g.polygon(ctx.S2(q), fill=shade((160, 118, 70), .7 + .3 * math.cos(ang - 2.2)) + (alpha,))

def sheep(ctx, p, alpha=255):
    x, y, s, d = ctx.P(p, 8); k = 14 * s / ctx.cam.zoom * .9; g = ctx.g; S = ctx.S
    g.ellipse(((x - k) * S, (y - k * .6) * S, (x + k * .9) * S, (y + k * .7) * S), fill=(255, 255, 255, alpha), outline=(90, 90, 90, alpha), width=2 * S)
    g.ellipse(((x + k * .7) * S, (y - k * .5) * S, (x + k * 1.5) * S, (y + k * .2) * S), fill=(60, 60, 60, alpha))
    for dx in (-.6, .5): g.line(((x + k * dx) * S, (y + k * .6) * S, (x + k * dx) * S, (y + k * 1.3) * S), fill=(60, 60, 60, alpha), width=3 * S)

def pin(ctx, p, col=GOLDC, r=15, alpha=255, ring=CREAMC):
    x0, y0, s, d = ctx.P(p, 0); x1, y1, _, _ = ctx.P(p, 48); S = ctx.S; rr = r * min(1.4, max(.8, s / ctx.cam.zoom))
    ctx.g.line((x0 * S, y0 * S, x1 * S, y1 * S), fill=(60, 60, 60, alpha), width=int(4 * S))
    ctx.g.ellipse(((x0 - 9) * S, (y0 - 4) * S, (x0 + 9) * S, (y0 + 4) * S), fill=(40, 30, 10, 90))
    ctx.g.ellipse(((x1 - rr - 4) * S, (y1 - rr - 4) * S, (x1 + rr + 4) * S, (y1 + rr + 4) * S), fill=ring + (alpha,)); ctx.g.ellipse(((x1 - rr) * S, (y1 - rr) * S, (x1 + rr) * S, (y1 + rr) * S), fill=col + (alpha,))
    ctx.g.ellipse(((x1 - rr * .4) * S, (y1 - rr * .4) * S, (x1 + rr * .4) * S, (y1 + rr * .4) * S), fill=ring + (alpha,))

def pilgrims(ctx, route, n=16, t=0.0, speed=.05, f=1.0, alpha=255, seed=1, spread=26):
    """white-clad pilgrims walking along a route (billboards, depth-sorted)."""
    rnd = random.Random(seed); items = []
    for i in range(n):
        off = rnd.random(); lat = rnd.uniform(-spread, spread); fr = (off + t * speed) % 1.0
        if fr > f: continue
        pp = polycut(route, fr); q = pp[-1]
        if len(pp) >= 2:
            dx, dy = pp[-1][0] - pp[-2][0], pp[-1][1] - pp[-2][1]; L = math.hypot(dx, dy) or 1; q = (q[0] - dy / L * lat, q[1] + dx / L * lat)
        items.append(q)
    for q in sorted(items, key=lambda q: ctx.P(q)[3]):
        x, y, s, d = ctx.P(q, 0); k = 1.0 * s / ctx.cam.zoom * ctx.cam.zoom ** .35 * 1.0; S = ctx.S; w = 7 * k * 1.1; h = 20 * k
        ctx.g.ellipse(((x - w * 1.2) * S, (y - w * .45) * S, (x + w * 1.2) * S, (y + w * .45) * S), fill=(40, 30, 10, 70))
        ctx.g.rounded_rectangle(((x - w) * S, (y - h) * S, (x + w) * S, y * S), radius=int(w * S), fill=(255, 255, 255, alpha), outline=(150, 145, 130, alpha), width=S) if hasattr(ctx.g, "rounded_rectangle") else None
        ctx.g.ellipse(((x - w * .7) * S, (y - h - w * 1.2) * S, (x + w * .7) * S, (y - h + w * .2) * S), fill=(176, 130, 96, alpha))

def sun_icon(ctx, x, y, r, alpha=255):
    S = ctx.S
    for k in range(12):
        a = k * .5236; ctx.g.line(((x + r * 1.3 * math.cos(a)) * S, (y + r * 1.3 * math.sin(a)) * S, (x + r * 1.8 * math.cos(a)) * S, (y + r * 1.8 * math.sin(a)) * S), fill=(226, 196, 132, alpha), width=int(5 * S))
    ctx.g.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=(175, 137, 59, alpha)); ctx.g.ellipse(((x - r * .7) * S, (y - r * .7) * S, (x + r * .7) * S, (y + r * .7) * S), fill=(226, 196, 132, alpha))

# ------------------------------------------------------------------ frame renderer
def render3d(scene, t, T):
    camp = scene["cam"](t, T); wname = scene["world"]; cam = Cam(*camp)
    base = warp_base(np.asarray(world(wname)), cam, PAPER_MAP)
    ctx = Ctx3(wname, camp, t, T); scene["draw"](ctx, t, T)
    img = base.convert("RGBA"); img.alpha_composite(ctx.geo.resize((W, H), Image.LANCZOS))
    if scene.get("dusk"):
        k = scene["dusk"](t, T)
        if k > 0: img.alpha_composite(Image.new("RGBA", (W, H), (20, 38, 60, int(150 * k))))
    # atmospheric haze toward the far (top) edge
    haze = Image.new("RGBA", (W, 560), (0, 0, 0, 0)); hd = ImageDraw.Draw(haze)
    for y in range(560): hd.line((0, y, W, y), fill=(250, 241, 228, int(255 * max(0, 1 - y / 560) ** 1.6 * .85)))
    img.alpha_composite(haze, (0, 230))
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

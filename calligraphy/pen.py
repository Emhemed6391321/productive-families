"""Broad-nib calligraphy engine: centre-line strokes -> variable-width filled outlines (SVG paths)."""
import math

def catmull(pts, step=3.0):
    """Centripetal-ish Catmull-Rom through pts, resampled ~step units apart."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        n = max(4, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out

def smooth_path(pts, passes=2):
    for _ in range(passes):
        pts = [pts[0]] + [((pts[i - 1][0] + 2 * pts[i][0] + pts[i + 1][0]) / 4, (pts[i - 1][1] + 2 * pts[i][1] + pts[i + 1][1]) / 4) for i in range(1, len(pts) - 1)] + [pts[-1]]
    return pts

def stroke(ctrl, L=22.0, phi=-52.0, taper=(0.35, 0.35), minw=3.2, step=2.5, press=None):
    """True broad-nib sweep: union of the quads swept by the nib segment between consecutive samples (shapely).
    Returns a list of polygons (exterior rings)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    c = smooth_path(catmull(ctrl, step), 1)
    n = len(c)
    ph = math.radians(phi); hx, hy = math.cos(ph), math.sin(ph)
    segs = []
    for i, (x, y) in enumerate(c):
        t = i / max(1, n - 1)
        s = 1.0
        if taper[0] > 0 and t < taper[0]: s = 0.18 + 0.82 * math.sin(t / taper[0] * math.pi / 2)
        if taper[1] > 0 and t > 1 - taper[1]: s = min(s, 0.18 + 0.82 * math.sin((1 - t) / taper[1] * math.pi / 2))
        if press: s *= press(t)
        h = max(minw / 2, L / 2 * s)
        segs.append(((x - h * hx, y - h * hy), (x + h * hx, y + h * hy)))
    quads = []
    for (a0, b0), (a1, b1) in zip(segs, segs[1:]):
        q = Polygon([a0, b0, b1, a1])
        if not q.is_valid: q = q.buffer(0)
        if q.area > 1e-6: quads.append(q)
    u = unary_union(quads).buffer(0.6).buffer(-0.6).simplify(0.12)
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    return geoms

def dot(cx, cy, size=15.0, phi=-52.0, angle=-35.0):
    """a nib-made dot: a short slanted stroke swept by the nib"""
    a = math.radians(angle); d = size * 0.34
    return stroke([(cx - d * math.cos(a), cy - d * math.sin(a)), (cx, cy), (cx + d * math.cos(a), cy + d * math.sin(a))],
                  L=size, phi=phi, taper=(0.25, 0.25), minw=size * 0.35, step=1.2)

def to_d(g, nd=1):
    """shapely polygon (with holes) -> SVG path (evenodd-safe)"""
    d = []
    for ring in [g.exterior] + list(g.interiors):
        pts = list(ring.coords)
        d.append("M" + "L".join(f"{x:.{nd}f},{y:.{nd}f}" for x, y in pts[:-1]) + "Z")
    return "".join(d)

def bbox(geoms):
    xs0, ys0, xs1, ys1 = zip(*[g.bounds for g in geoms]); return min(xs0), min(ys0), max(xs1), max(ys1)

"""Crescent calligraphy panel: shaped Amiri Bold outlines warped along an arc, plus nib-drawn filler marks."""
import math, random, sys
from shapely import affinity, segmentize
from shapely.geometry import Point
from shapely.ops import unary_union
import shapely
from fontline import text_geom, pieces
import pen
from pen import stroke, to_d, bbox

TEXT = "تنسيقية حجاج طرابلس ب"

def warp(geoms, total, R):
    mid = total / 2
    def f(arr):
        import numpy as np
        x, y = arr[:, 0], arr[:, 1]
        a = (x - mid) / R
        bx, by = R * np.sin(a), R * np.cos(a)
        nx, ny = -np.sin(a), -np.cos(a)
        up = -y
        return np.stack([bx + up * nx, by + up * ny], axis=1)
    return [shapely.transform(segmentize(g, 6.0), f) for g in geoms]

def fillers(solid, x0, x1, n=40, seed=5, band=(-900, -170), clear=90, spacing=200):
    rnd = random.Random(seed)
    shapes = [[(0, 0), (-5, -9), (-14, -12)], [(0, 0), (-4, -5), (-11, -6), (-14, -1)], [(0, 0), (-9, -3)], [(0, 0), (-3, -8), (-10, -9), (-13, -4)]]
    out, placed, tries = [], [], 0
    while len(out) < n and tries < 9000:
        tries += 1
        x = rnd.uniform(x0 + 40, x1 - 40); y = rnd.uniform(*band)
        sh = rnd.choice(shapes); k = rnd.uniform(6.0, 7.4)
        pts = [(x + px * k, y + py * k) for px, py in sh]
        if solid.distance(Point(x - 30, y - 24)) < clear: continue
        if any(math.hypot(x - px, y - py) < spacing for px, py in placed): continue
        placed.append((x, y))
        out += stroke(pts, L=58, phi=-52, taper=(.0, .5), minw=9, step=3)
    return out

def make(font="fonts/Amiri-Bold.ttf", R=None, with_fillers=True):
    u, adv = text_geom(font, TEXT)
    glyphs = pieces(u)
    x0, y0, x1, y1 = u.bounds
    total = x1 - x0
    shift = -x0
    glyphs = [affinity.translate(g, shift, 0) for g in glyphs]
    solid = unary_union(glyphs)
    fl = fillers(solid, 0, total) if with_fillers else []
    R = R or total / 2 / 0.82
    return warp(glyphs, total, R), warp(fl, total, R)

def svg_of(letters, marks, fill="#000000", pad=60, svg_id="art2"):
    allg = letters + marks
    x0, y0, x1, y1 = bbox(allg)
    vx, vy, vw, vh = x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    d = "".join(to_d(g, 0) for g in allg)
    return (f'<svg id="{svg_id}" xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" role="img" aria-label="تنسيقية حجاج طرابلس ب">'
            f'<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>')

if __name__ == "__main__":
    sys.path.insert(0, "/home/user/productive-families/brand_kit")
    import render
    L, M = make()
    s = svg_of(L, M)
    open("tansiqiya-thuluth.svg", "w", encoding="utf-8").write(s.replace(' id="art2"', ""))
    SC = "/tmp/claude-0/-home-user-productive-families/279b9344-f325-5676-997e-4eb1bcac3822/scratchpad/"
    open(SC + "pn.html", "w").write('<body style="margin:0;background:#fff">' + s.replace("<svg ", '<svg style="width:2000px;display:block" ') + "</body>")
    render.to_png(SC + "pn.html", SC + "pn.png", 2000, 1000)
    print(len(s) // 1024, "KB", [round(v) for v in bbox(L + M)])

"""Thuluth-style crescent composition built from the same broad-nib engine (words.py), warped onto an arc,
with stem flags and filler marks (mushakkal) like classical thuluth panels."""
import math, random
from shapely import affinity, segmentize
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union, transform
from pen import *
import words as W
from words import S, dot

def tall(g, k):  # taller stems: scale y of the glyph about the baseline (used only for alif / lam strokes)
    return affinity.scale(g, 1, k, origin=(0, 0))

def build_line(sc=1.0):
    """one baseline, right to left. returns list of (geom, kind) in local coordinates (origin = right end, baseline y=0)."""
    w1, w2, w3, w4 = W.word1(), W.word2(), W.word3(), W.word4()
    gap = 46
    out = []
    x = 0.0
    for wd, width in ((w1, 452), (w2, 447), (w3, 478), (w4, 142)):
        out += [affinity.translate(g, x, 0) for g in wd]
        x -= width + gap
    return out, abs(x) - gap

def flags(line):
    """thuluth stems carry a small leftward flag at the head: add one to every tall stroke (height > 100)."""
    extra = []
    for g in line:
        minx, miny, maxx, maxy = g.bounds
        if (maxy - miny) > 190 and (maxx - minx) < 60:      # alif / lam / ta stems
            cx = (minx + maxx) / 2
            extra += S([(cx + 14, miny + 22), (cx - 6, miny + 9), (cx - 30, miny + 6), (cx - 48, miny + 18)], L=24, taper=(.0, .5), step=1.5)
    return extra

def fillers(line, n=46, seed=7, band=(-170, 70)):
    rnd = random.Random(seed)
    solid = unary_union(line)
    x0, y0, x1, y1 = solid.bounds
    out, placed = [], []
    tries = 0
    shapes = [
        [(0, 0), (-5, -9), (-14, -12)],            # small comma / hook
        [(0, 0), (-4, -5), (-11, -6), (-14, -1)],  # little cup
        [(0, 0), (-9, -3)],                        # short dash
    ]
    while len(out) < n and tries < 4000:
        tries += 1
        x = rnd.uniform(x0 + 20, x1 - 20); y = rnd.uniform(*band)
        sh = rnd.choice(shapes)
        pts = [(x + px * 2.0, y + py * 2.0) for px, py in sh]
        probe = Point(x - 10, y - 8)
        if solid.distance(probe) < 26: continue
        if any(math.hypot(x - px, y - py) < 64 for px, py in placed): continue
        placed.append((x, y))
        out += S(pts, L=18, taper=(.0, .45), minw=3.0, step=1.5)
    return out

def warp(geoms, total, R=880, span_pad=0.0):
    a_half = (total / 2) / R
    mid = total / 2
    def f(x, y, z=None):
        s = -x                                        # distance from the right end
        a = (mid - s) / R
        bx, by = R * math.sin(a), R * math.cos(a)
        nx, ny = -math.sin(a), -math.cos(a)           # toward the circle centre (up for the letters)
        up = -y
        return (bx + up * nx, by + up * ny)
    out = []
    for g in geoms:
        g = segmentize(g, 3.0)
        out.append(transform(f, g))
    return out

K = 1.55
def make(R=1320):
    line, total = build_line()
    line = [affinity.scale(g, K, K, origin=(0, 0)) for g in line]
    total *= K
    line = line + flags(line)
    fill = fillers(line, n=70, band=(-250, 110))
    allg = line + fill
    return warp(allg, total, R)

def svg_of(geoms, fill="#000000", pad=40):
    x0, y0, x1, y1 = bbox(geoms)
    vx, vy, vw, vh = x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    d = "".join(to_d(g, 1) for g in geoms)
    return (f'<svg id="art" xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" role="img" aria-label="تنسيقية حجاج طرابلس ب">'
            f'<path fill="{fill}" fill-rule="nonzero" d="{d}"/></svg>')

if __name__ == "__main__":
    import sys; sys.path.insert(0, "/home/user/productive-families/brand_kit")
    import render
    G = make()
    s = svg_of(G)
    open("tansiqiya-thuluth.svg", "w", encoding="utf-8").write(s.replace(' id="art"', ""))
    SC = "/tmp/claude-0/-home-user-productive-families/279b9344-f325-5676-997e-4eb1bcac3822/scratchpad/"
    open(SC + "th.html", "w").write('<body style="margin:0;background:#fff">' + s.replace("<svg ", '<svg style="width:2000px;display:block" ') + "</body>")
    render.to_png(SC + "th.html", SC + "th.png", 2000, 1100)
    print(len(s) // 1024, "KB", [round(v) for v in bbox(G)])

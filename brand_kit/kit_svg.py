"""Vector building blocks of the Tripoli-B identity (SVG strings).
 - logos are TRACED from the supplied rasters (potrace) -> smooth bezier paths
 - ornaments / star / frame / patterns are drawn analytically."""
import math, functools
import numpy as np
from PIL import Image, ImageFilter
import potrace

PAL = dict(
    teal="#005045", green="#043D1F", deep="#022416", gold="#AF893B", bronze="#946934",
    gold_lt="#E2C484", paper="#FAF1E4", paper_dk="#F0E6D6", cream="#FFFCF4", white="#FFFFFF",
)

@functools.lru_cache(maxsize=None)
def trace(name, up=4, blur=1.4, size=None):
    """returns (path_d, w, h) in the traced coordinate system (source px * 1 after scale-back)."""
    im = Image.open(f"../dawah_cards/assets/{name}.png").convert("RGBA")
    a = im.getchannel("A")
    w, h = a.size
    a = a.resize((w * up, h * up), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur * up / 2))
    arr = np.asarray(a) > 128
    bm = potrace.Bitmap(~arr)
    plist = bm.trace(turdsize=int(8 * up), alphamax=1.15, opticurve=True, opttolerance=0.35)
    k = 1.0 / up
    f = lambda p: f"{p.x * k:.2f},{p.y * k:.2f}"
    d = []
    for c in plist:
        d.append(f"M{f(c.start_point)}")
        for s in c.segments:
            if s.is_corner:
                d.append(f"L{f(s.c)}L{f(s.end_point)}")
            else:
                d.append(f"C{f(s.c1)} {f(s.c2)} {f(s.end_point)}")
        d.append("Z")
    return "".join(d), w, h

def logo_group(name, fill, x=0, y=0, width=None):
    d, w, h = trace(name)
    s = (width / w) if width else 1
    return f'<g transform="translate({x},{y}) scale({s:.5f})"><path fill="{fill}" fill-rule="evenodd" d="{d}"/></g>', w * s, h * s

def logo_svg(name, fill, bg=None):
    d, w, h = trace(name)
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{rect}<path fill="{fill}" fill-rule="evenodd" d="{d}"/></svg>'

# ---------------------------------------------------------------- ornaments (analytic)
def star8_pts(cx, cy, r, inner=0.62, rot=-90):
    pts = []
    for i in range(16):
        a = math.radians(rot + 22.5 * i)
        rr = r if i % 2 == 0 else r * inner
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)

def star8(cx, cy, r, fill="none", stroke=None, sw=2, inner=0.62, rot=-90):
    st = f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter"' if stroke else ""
    return f'<polygon points="{star8_pts(cx, cy, r, inner, rot)}" fill="{fill}"{st}/>'

def diamond(cx, cy, r, fill):
    return f'<polygon points="{cx},{cy - r} {cx + r},{cy} {cx},{cy + r} {cx - r},{cy}" fill="{fill}"/>'

def divider(cx, cy, half, gap, col, sw=3, r=14):
    return (f'<g><line x1="{cx - half}" y1="{cy}" x2="{cx - gap}" y2="{cy}" stroke="{col}" stroke-width="{sw}"/>'
            f'<line x1="{cx + gap}" y1="{cy}" x2="{cx + half}" y2="{cy}" stroke="{col}" stroke-width="{sw}"/>{diamond(cx, cy, r, col)}</g>')

def ornament(cx, cy, h, col):
    """circle / diamond / circle stack (the reference title ornament)"""
    u = h / 100.0
    return (f'<g fill="{col}"><circle cx="{cx}" cy="{cy - 36 * u}" r="{12 * u}"/>'
            f'<polygon points="{cx},{cy - 17 * u} {cx + 17 * u},{cy} {cx},{cy + 17 * u} {cx - 17 * u},{cy}"/>'
            f'<circle cx="{cx}" cy="{cy + 36 * u}" r="{12 * u}"/></g>')

def frame(x, y, w, h, col, sw=4, inner=14, corner=36):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{col}" stroke-width="{sw}"/>',
           f'<rect x="{x + inner}" y="{y + inner}" width="{w - 2 * inner}" height="{h - 2 * inner}" fill="none" stroke="{col}" stroke-width="{max(1, sw / 3):.1f}"/>']
    for cx, cy in ((x, y), (x + w, y), (x, y + h), (x + w, y + h)):
        out.append(star8(cx, cy, corner, fill=col))
        out.append(star8(cx, cy, corner * .45, fill="#FFFFFF" if col == PAL["gold"] else PAL["deep"], rot=-90 + 22.5))
    for cx, cy in ((x + w / 2, y), (x + w / 2, y + h), (x, y + h / 2), (x + w, y + h / 2)):
        out.append(diamond(cx, cy, 11, col))
    return "<g>" + "".join(out) + "</g>"

def lattice_pattern(pid, col, opacity=.35, R=60, sw=1.6):
    """girih-like overlapping-circle lattice as an SVG <pattern> (tile = 2R x 1.7321R)"""
    tw, th = 2 * R, 2 * R * 0.866 * 2
    circles = []
    for (cx, cy) in ((0, 0), (2 * R, 0), (R, R * 0.866), (3 * R, R * 0.866), (0, 2 * R * 0.866), (2 * R, 2 * R * 0.866)):
        circles.append(f'<circle cx="{cx}" cy="{cy:.2f}" r="{R}"/>')
    return (f'<pattern id="{pid}" width="{2 * R}" height="{th:.2f}" patternUnits="userSpaceOnUse">'
            f'<g fill="none" stroke="{col}" stroke-width="{sw}" opacity="{opacity}">{"".join(circles)}</g></pattern>')

def starfield_pattern(pid, col, opacity=.4, step=120, sw=1.6):
    s = step
    return (f'<pattern id="{pid}" width="{s}" height="{s}" patternUnits="userSpaceOnUse"><g opacity="{opacity}">'
            f'{star8(0, 0, s * .42, stroke=col, sw=sw)}{star8(s, 0, s * .42, stroke=col, sw=sw)}{star8(0, s, s * .42, stroke=col, sw=sw)}{star8(s, s, s * .42, stroke=col, sw=sw)}'
            f'{star8(s / 2, s / 2, s * .2, stroke=col, sw=max(1, sw - .5))}</g></pattern>')

def standalone(inner, w, h, defs="", bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><defs>{defs}</defs>{rect}{inner}</svg>'

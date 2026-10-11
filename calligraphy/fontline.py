"""Shaped Arabic text -> shapely geometry (via HarfBuzz + fontTools outlines), then arc-warped like a thuluth panel."""
import math, random
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity, segmentize
import shapely

def _flatten(contour_ops, steps=10):
    pts = []; cur = None
    for op, args in contour_ops:
        if op == "moveTo": cur = args[0]; pts = [cur]
        elif op == "lineTo": cur = args[0]; pts.append(cur)
        elif op == "qCurveTo":
            # TrueType quadratic spline with implied on-curve points
            offs = list(args[:-1]); end = args[-1]
            if end is None: continue
            segs = []
            p0 = cur
            for i, c in enumerate(offs):
                nxt = offs[i + 1] if i + 1 < len(offs) else end
                on = ((c[0] + nxt[0]) / 2, (c[1] + nxt[1]) / 2) if i + 1 < len(offs) else end
                segs.append((p0, c, on)); p0 = on
            for a, c, b in segs:
                for k in range(1, steps + 1):
                    t = k / steps
                    pts.append(((1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t * t * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t * t * b[1]))
            cur = end
        elif op == "curveTo":
            c1, c2, e = args
            for k in range(1, steps + 1):
                t = k / steps
                pts.append(tuple((1 - t) ** 3 * cur[j] + 3 * (1 - t) ** 2 * t * c1[j] + 3 * (1 - t) * t * t * c2[j] + t ** 3 * e[j] for j in (0, 1)))
            cur = e
        elif op in ("closePath", "endPath"):
            yield pts; pts = []
    if pts: yield pts

def text_geom(fontfile, text, size=1.0, features=None):
    blob = hb.Blob.from_file_path(fontfile); face = hb.Face(blob); font = hb.Font(face)
    buf = hb.Buffer(); buf.add_str(text); buf.direction = "rtl"; buf.script = "Arab"; buf.language = "ar"
    hb.shape(font, buf, features or {"kern": True, "liga": True, "calt": True, "mark": True, "mkmk": True})
    tt = TTFont(fontfile); gs = tt.getGlyphSet(); order = tt.getGlyphOrder()
    x = 0.0; geoms = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        pen = DecomposingRecordingPen(gs); gs[name].draw(pen)
        polys = []
        for ring in _flatten(pen.value):
            if len(ring) >= 3:
                p = Polygon([(px + x + pos.x_offset, -(py + pos.y_offset)) for px, py in ring])
                if not p.is_valid: p = p.buffer(0)
                polys.append(p)
        g = Polygon()
        for p in polys: g = g.symmetric_difference(p)
        if not g.is_empty: geoms.append(g)
        x += pos.x_advance
    u = unary_union(geoms)
    return u, x

def pieces(u):
    return list(u.geoms) if hasattr(u, "geoms") else [u]

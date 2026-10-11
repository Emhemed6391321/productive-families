import math
from pen import *

def arc(cx, cy, r, a0, a1, n=14):
    """points on a circle; angles in degrees, y up like maths (screen y flipped)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy - r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

NIB = dict(L=22.0, phi=-52.0)

def S(ctrl, **kw):
    a = dict(NIB); a.update(kw); return stroke(ctrl, **a)

def tooth(x, h=44, w=9):
    return [(x + w, 1), (x + w * .35, -h * .55), (x - 1, -h), (x - w * .8, -h * .5), (x - w * 1.6, 2)]

# ---------------------------------------------------------------- word 1  تنسيقية
def word1():
    P = []
    P += [(-2, -40), (-6, -20), (-16, -3), (-36, 4), (-66, 2)]                       # ت
    P += tooth(-96, 40, 10)                                                          # ن
    P += [(-124, 3)]
    for x in (-146, -174, -202):                                                     # س (three teeth)
        P += [(x + 8, 2), (x - 1, -24), (x - 11, 2)]
    P += [(-222, 3)]
    P += tooth(-248, 40, 10)                                                         # ي
    P += [(-274, 3)]
    P += arc(-300, -17, 17, -55, 235, 16) + [(-326, 5), (-346, 2)]                  # ق (eye)
    P += tooth(-372, 40, 10)                                                         # ي
    P += [(-398, 3)]
    P += arc(-428, -19, 18, -40, 275, 18) + [(-450, 8)]                              # ة
    polys = S(P, taper=(.08, .12))
    dots = [dot(-8, -66), dot(-27, -66), dot(-97, -68), dot(-307, -56), dot(-290, -56),
            dot(-250, 28), dot(-267, 28), dot(-374, 28), dot(-391, 28), dot(-435, -58), dot(-418, -58)]
    return polys + [g for d_ in dots for g in d_]

# ---------------------------------------------------------------- word 2  حجاج
def word2():
    polys = []
    # ح initial: top arm + belly hook
    polys += (S([(0, -8), (-30, -26), (-72, -30), (-112, -14)], taper=(.12, .0)))
    polys += (S([(-100, -22), (-124, -2), (-120, 26), (-92, 38), (-56, 38), (-34, 28)], taper=(.0, .35)))
    # ج medial: top arm from the connection, belly, exit link
    polys += (S([(-112, -14), (-142, -26), (-184, -26), (-222, -10)], taper=(.0, .0)))
    polys += (S([(-210, -18), (-236, 2), (-232, 28), (-204, 38), (-170, 38), (-150, 28)], taper=(.0, .35)))
    polys += (S([(-222, 38), (-246, 44), (-274, 40), (-296, 30)], taper=(.1, .0)))
    # ا alif (stands on the link)
    polys += (S([(-292, -124), (-294, -80), (-296, -26), (-298, 34)], taper=(.0, .0), L=26))
    # ج final (isolated-type), left of the alif
    polys += (S([(-318, -26), (-352, -38), (-396, -34), (-428, -12), (-438, 14), (-420, 34), (-388, 42), (-352, 38), (-336, 26)], taper=(.06, .3)))
    polys += dot(-186, 20) + dot(-390, 22)
    return polys

# ---------------------------------------------------------------- word 3  طرابلس
def word3():
    polys = []
    # ط : stem + bowl
    polys += (S([(0, -124), (-1, -80), (-2, -26), (-4, 6)], taper=(.0, .0), L=26))
    bowl = [(-8 + (x + 8) * 1.45, -14 + (y + 14) * 0.62) for x, y in arc(-8, -14, 22, 0, -340, 20)]
    polys += S(bowl, taper=(.06, .06))
    # link + ر (final)
    polys += (S([(-58, 8), (-86, 8), (-104, 10), (-112, 30), (-108, 56), (-94, 80)], taper=(.05, .4), L=20))
    # ا alif
    polys += (S([(-168, -124), (-169, -80), (-171, -26), (-172, 6)], taper=(.0, .0), L=26))
    # ب initial (tooth) -> ل (stem) -> س (teeth + bowl)
    P = [(-190, 3)] + tooth(-212, 44) + [(-236, 5), (-262, 4)]
    for x in (-284, -306, -328):
        P += [(x + 6, 3), (x - 1, -26), (x - 9, 3)]
    P += [(-344, 8), (-358, 28), (-390, 44), (-430, 38), (-462, 14), (-474, -12)]
    polys += (S(P, taper=(.04, .22)))
    polys += (S([(-258, -134), (-259, -86), (-262, -26), (-262, 6)], taper=(.0, .0), L=26))      # ل stem
    polys += (dot(-214, 30))                                                                         # ب dot
    return polys

# ---------------------------------------------------------------- word 4  ب
def word4():
    polys = S([(0, -22), (-14, 8), (-46, 26), (-90, 24), (-124, 4), (-138, -22)], taper=(.1, .3))
    polys += dot(-72, 54)
    return polys

def place(polys, ox, oy, sc, rot=0.0):
    from shapely import affinity
    return [affinity.translate(affinity.rotate(affinity.scale(g, sc, sc, origin=(0, 0)), rot, origin=(0, 0)), ox, oy) for g in polys]

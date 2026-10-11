from words import *
import sys, os
W1, W2, W3, W4 = word1(), word2(), word3(), word4()
VB = (1240, 800)

def compose(fill="#000000", bg=None):
    s1, s2, s3, s4 = 1.18, 1.22, 1.14, 1.2
    rot = 4.0                                                  # Diwani rises toward the left
    o1x, o1y = 1160, 330
    P = place(W1, o1x, o1y, s1, rot)
    o2x = o1x - 452 * s1 - 40
    P += place(W2, o2x, o1y - 40, s2, rot)
    o3x, o3y = 1090, 650
    P += place(W3, o3x, o3y, s3, rot)
    o4x = o3x - 478 * s3 - 46
    P += place(W4, o4x, o3y - 40, s4, rot)
    return P

def svg(polys, fill="#000000", bg=None, vb=VB, pad=40):
    x0, y0, x1, y1 = bbox(polys)
    vx, vy, vw, vh = x0 - pad, y0 - pad, (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad
    d = "".join(to_d(p) for p in polys)
    rect = f'<rect x="{vx:.0f}" y="{vy:.0f}" width="{vw:.0f}" height="{vh:.0f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}" role="img" aria-label="تنسيقية حجاج طرابلس ب">'
            f'{rect}<path fill="{fill}" fill-rule="nonzero" d="{d}"/></svg>')

if __name__ == "__main__":
    P = compose()
    s = svg(P)
    open("tansiqiya-calligraphy.svg", "w", encoding="utf-8").write(s)
    print(len(s), "bytes")

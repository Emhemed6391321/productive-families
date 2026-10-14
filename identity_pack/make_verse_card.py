#!/usr/bin/env python3
"""Printable 1 x 1 m card with Quran 2:197 (text used verbatim, Amiri Quran). Design space 1080 x 1080, S = 3937/1080 -> 100 dpi at 100 x 100 cm.
    python3 make_verse_card.py preview | print"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from pack_lib import *
from make_rollup import smooth

DW = 1080
AYAH = "﴿ ٱلۡحَجُّ أَشۡهُرࣱ مَّعۡلُومَـٰتࣱۚ فَمَن فَرَضَ فِیهِنَّ ٱلۡحَجَّ فَلَا رَفَثَ وَلَا فُسُوقَ وَلَا جِدَالَ فِی ٱلۡحَجِّۗ وَمَا تَفۡعَلُوا۟ مِنۡ خَیۡرࣲ یَعۡلَمۡهُ ٱللَّهُۗ وَتَزَوَّدُوا۟ فَإِنَّ خَیۡرَ ٱلزَّادِ ٱلتَّقۡوَىٰۖ وَٱتَّقُونِ یَـٰۤأُو۟لِی ٱلۡأَلۡبَـٰبِ ۝١٩٧﴾"
REF = "[البقرة ١٩٧]"
# line breaks only at spaces (the text itself is untouched); (words, colour)
LINES = [("﴿ ٱلۡحَجُّ أَشۡهُرࣱ مَّعۡلُومَـٰتࣱۚ", "g"), ("فَمَن فَرَضَ فِیهِنَّ ٱلۡحَجَّ", "g"),
         ("فَلَا رَفَثَ وَلَا فُسُوقَ وَلَا جِدَالَ فِی ٱلۡحَجِّۗ", "o"),
         ("وَمَا تَفۡعَلُوا۟ مِنۡ خَیۡرࣲ یَعۡلَمۡهُ ٱللَّهُۗ", "g"),
         ("وَتَزَوَّدُوا۟ فَإِنَّ خَیۡرَ ٱلزَّادِ ٱلتَّقۡوَىٰۖ", "o"), ("وَٱتَّقُونِ یَـٰۤأُو۟لِی ٱلۡأَلۡبَـٰبِ ۝١٩٧﴾", "g")]
assert " ".join(t for t, _ in LINES) == AYAH, "verse text was altered!"
QF = "fonts/AmiriQuran.ttf"

def qfont(sz): return ImageFont.truetype(QF, int(sz), layout_engine=ImageFont.Layout.RAQM)
def qlen(f, t): return f.getlength(t, direction="rtl", language="ar", features=["-liga"] if False else None)

def build(S):
    P = lambda v: int(round(v * S)); W = H = P(DW)
    img = paper(W, H, warm=True)
    img = add_lattice(img, (205, 183, 140), 40, ramp=vramp(H, 0, H, .55, 1), R=P(110))
    paste(img, sky_layer(W, 0.55), 0, P(872))
    frame(img, P(34), GOLD, max(3, P(4)), P(14), corner=0.9)
    d = ImageDraw.Draw(img)
    # crown medallion + ornament
    cx = W // 2
    ornament_pair(img, cx, P(112), P(820), col=GOLD, h=P(84))
    star8(d, cx, P(112), P(44), fill=GOLD); star8(d, cx, P(112), P(28), fill=PAPER_A, rot=-math.pi / 2 + math.pi / 8); star8(d, cx, P(112), P(13), fill=GOLD)
    # verse: one font size for all lines, as large as the widest line allows
    sz = 80
    while True:
        f = qfont(P(sz))
        if max(f.getlength(t, direction="rtl", language="ar") for t, _ in LINES) <= P(930): break
        sz -= 2
    sz = min(sz, 66); f = qfont(P(sz)); lh = P(110); y = P(212) + lh // 2
    col = {"g": GREEN, "o": (160, 118, 40)}
    for t, c in LINES:
        d.text((cx, y), t, font=f, fill=col[c], anchor="mm", direction="rtl", language="ar"); y += lh
    # reference pill
    rf = font(700, P(42)); rw = rf.getlength(REF, direction="rtl", language="ar") + P(84)
    py = y + P(2)
    d.rounded_rectangle((cx - rw / 2, py, cx + rw / 2, py + P(70)), P(35), fill=GREEN, outline=GOLD, width=max(2, P(3)))
    d.text((cx, py + P(35)), REF, font=rf, fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    # footer: logos + name
    fy = P(1012)
    nf = font(700, P(32)); d.text((cx, fy), "تنسيقية حجاج طرابلس ب", font=nf, fill=GREEN, anchor="mm", direction="rtl", language="ar")
    rw_ = P(120); paste(img, smooth(asset("rakb_green"), rw_, S), P(100), fy - P(40))
    hw = P(78); paste(img, smooth(asset("hajj_green"), hw, S), W - P(100) - hw, fy - P(40))
    return img, sz

if __name__ == "__main__":
    os.makedirs("VerseCard", exist_ok=True)
    if (sys.argv[1] if len(sys.argv) > 1 else "preview") == "preview":
        im, sz = build(1.0); im.save("VerseCard/preview.png"); print("font units", sz)
    else:
        S = 3937 / DW; im, sz = build(S); im = im.convert("RGB")
        im.save("VerseCard/VerseCard-100x100cm.pdf", resolution=100.0); im.save("VerseCard/VerseCard-100x100cm-100dpi.png", dpi=(100, 100)); print(im.size)

#!/usr/bin/env python3
"""Series of dawah cards for pilgrims - Tripoli B coordination.

Visual identity is taken from the reference cards in refs/ (beige paper, deep green
titles, gold highlights, Mecca skyline, footer logos).  Logos / ornament / skyline are
cut from those references by extract_assets.py.  Font: IBM Plex Sans Arabic.

    python3 extract_assets.py      # once
    python3 build_cards.py         # -> out/card_01.png ... + out/dawah_cards.pdf
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1440                     # same size as the reference cards
GREEN = (4, 61, 31)
GOLD = (175, 137, 59)
BRONZE = (150, 108, 48)               # gold panels (as in the statistics reference)
PAPER_TOP, PAPER_BOT = (249, 242, 229), (243, 234, 219)
WHITE = (255, 255, 255)
ORG = "تنسيقية طرابلس ب"
DATE_LINE = "2027 ميلادي - 1448 هجري"
MARGIN = 90
SKY_Y = 930                            # top of the skyline band

_fonts = {}
def font(weight, size):
    k = (weight, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(f"fonts/IBMPlexSansArabic-{weight}.ttf", size)
    return _fonts[k]

def tlen(f, t):
    return f.getlength(t, direction="rtl", language="ar")

# --------------------------------------------------------------------------- text
HL_ON_DARK = (255, 232, 176)          # highlight colour inside the bronze panels

def parse(text, base, hl):
    """'*gold*' marks highlights.  -> lines of words; a word is a list of (segment, colour)
    so punctuation glued to a highlighted word keeps its place."""
    lines = []
    for raw in text.split("\n"):
        words, word, seg, on = [], [], "", False
        def close_seg():
            nonlocal seg
            if seg:
                word.append((seg, hl if on else base)); seg = ""
        def close_word():
            nonlocal word
            close_seg()
            if word:
                words.append(word); word = []
        for ch in raw:
            if ch == "*":
                close_seg(); on = not on
            elif ch == " ":
                close_word()
            else:
                seg += ch
        close_word()
        lines.append(words)
    return lines

def wlen(f, word):
    return sum(tlen(f, t) for t, _ in word)

def _greedy(words, f, sp, maxw):
    out, cur, w = [], [], 0
    for word in words:
        ww = wlen(f, word)
        add = ww + (sp if cur else 0)
        if cur and w + add > maxw:
            out.append((cur, w)); cur, w = [], 0; add = ww
        cur.append((word, ww)); w += add
    out.append((cur, w))
    return out

def wrap(lines, f, maxw):
    sp = f.size * 0.26
    out = []
    for words in lines:
        g = _greedy(words, f, sp, maxw)
        n = len(g)
        if n > 1:                          # balance: narrowest width that keeps the same line count
            lo, hi = max(w for _, w in g) * 0.55, maxw
            for _ in range(14):
                mid = (lo + hi) / 2
                if len(_greedy(words, f, sp, mid)) <= n:
                    hi = mid
                else:
                    lo = mid
            g = _greedy(words, f, sp, hi)
        out.extend(g)
    return out, sp

def draw_text(d, x_right, x_left, y, text, size, weight, color, align="center", lh=1.38,
              measure=False, hl=GOLD):
    """Draw (or measure) a wrapped RTL block between x_left..x_right. Returns height."""
    f = font(weight, size)
    lines, sp = wrap(parse(text, color, hl), f, x_right - x_left)
    asc, desc = f.getmetrics()
    lineh = size * lh
    if not measure:
        for i, (ws, w) in enumerate(lines):
            base = y + i * lineh + (lineh - asc - desc) / 2 + asc
            x = (x_left + x_right) / 2 + w / 2 if align == "center" else x_right
            for word, ww in ws:
                for seg, col in word:
                    d.text((x, base), seg, font=f, fill=col, anchor="rs", direction="rtl", language="ar")
                    x -= tlen(f, seg)
                x -= sp
    return len(lines) * lineh

# ------------------------------------------------------------------------ assets
A = {}
def asset(name):
    if name not in A:
        A[name] = Image.open(f"assets/{name}.png").convert("RGBA")
    return A[name]

def fit_w(im, w):
    return im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)

_bg = {}
def background(strength):
    """Paper + soft light + faint geometric lattice + Mecca skyline (cached per strength)."""
    if strength in _bg:
        return _bg[strength].copy()
    top, bot = np.array(PAPER_TOP, float), np.array(PAPER_BOT, float)
    t = np.linspace(0, 1, H)[:, None, None]
    img = Image.fromarray((top * (1 - t) + bot * t).repeat(W, 1).astype("uint8"))
    # soft diagonal light, like the reference
    light = Image.new("L", (W, H), 0)
    ld = ImageDraw.Draw(light)
    ld.polygon([(560, 0), (900, 0), (500, 700), (200, 700)], fill=70)
    ld.polygon([(0, 150), (260, 0), (330, 0), (0, 420)], fill=55)
    light = light.filter(ImageFilter.GaussianBlur(70))
    img = Image.composite(Image.new("RGB", (W, H), (255, 252, 244)), img, light)
    # lattice of overlapping circles (very faint at top, clearer at the bottom)
    pat = Image.new("L", (W * 2, H * 2), 0)
    pd = ImageDraw.Draw(pat)
    R = 110
    for j in range(-1, H // 95 + 3):
        for i in range(-1, W // R + 3):
            cx = i * R * 2 + (R if j % 2 else 0)
            cy = j * R * 0.87
            pd.ellipse((cx - R, cy - R, cx + R, cy + R), outline=255, width=3)
    pat = pat.resize((W, H), Image.LANCZOS).crop((0, 0, W, H))
    ramp = Image.fromarray((np.clip((np.arange(H) - 450) / 900, 0.12, 1) * 46).astype("uint8")[:, None]
                           .repeat(W, 1))
    mask = Image.fromarray((np.asarray(pat, float) * np.asarray(ramp, float) / 255).astype("uint8"))
    img = Image.composite(Image.new("RGB", (W, H), (205, 183, 140)), img, mask)
    # skyline: keep what is not sky
    raw = np.asarray(asset("skyline_raw").convert("RGB")).astype(float)
    sky = np.median(raw[6:40, 0:160].reshape(-1, 3), 0)
    dist = np.sqrt(((raw - sky) ** 2).sum(2))
    alpha = np.clip((dist - 10) / 70, 0, 1) ** 0.85 * strength
    rows = np.ones(raw.shape[0])
    rows[:12] = np.linspace(0, 1, 12)
    alpha *= rows[:, None]
    sk = Image.fromarray(raw.astype("uint8")).convert("RGBA")
    sk.putalpha(Image.fromarray((alpha * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8)))
    img.paste(sk, (0, SKY_Y), sk)
    _bg[strength] = img
    return img.copy()

def paste(img, im, x, y):
    img.paste(im, (int(x), int(y)), im)

def shadowed_round(img, box, r, fill, outline=None, width=0, blur=18, off=8, alpha=60):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + off, box[2], box[3] + off), r, fill=(90, 70, 30, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.paste(sh, (0, 0), sh)
    ImageDraw.Draw(img).rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def check_badge(d, cx, cy, r=34):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD)
    d.line([(cx - r * .42, cy + r * .02), (cx - r * .1, cy + r * .34), (cx + r * .46, cy - r * .32)],
           fill=WHITE, width=9, joint="curve")

def ornate_bracket(d, cx, cy, h, side, col=GOLD):
    """Quranic-style ornamental bracket; side=+1 bulges right (opening, RTL), -1 bulges left."""
    rx, ry = h * 0.30, h / 2
    ox = cx - side * rx * 0.55
    for k, (sh, wd) in enumerate(((0, 8), (rx * 0.34, 3))):
        r_x, r_y = rx - sh * 0.4, ry - sh
        c_x = ox - side * sh * 0.0
        a0, a1 = (-56, 56) if side > 0 else (124, 236)
        d.arc((c_x - r_x, cy - r_y, c_x + r_x, cy + r_y), a0, a1, fill=col, width=wd)
    for sgn in (-1, 1):                     # little rosettes at both ends
        ang = math.radians(56 if side > 0 else 124)
        ex = ox + rx * math.cos(ang)
        ey = cy + sgn * ry * math.sin(ang)
        d.ellipse((ex - 9, ey - 9, ex + 9, ey + 9), fill=col)

# ------------------------------------------------------------- card element kinds
BODY_L, BODY_R = MARGIN, W - MARGIN
def el_measure(e):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    k = e["k"]
    if k == "text":
        h = draw_text(d, BODY_R, BODY_L, 0, e["t"], e["size"], e.get("w", 700), e.get("c", GREEN),
                      e.get("align", "center"), e.get("lh", 1.38), measure=True)
        return h + e.get("gap", 30)
    if k == "head":
        return e["size"] * 1.4 + e.get("gap", 40)
    if k == "sep":
        return 44 + e.get("gap", 20)
    if k == "gap":
        return e["n"]
    if k in ("panel", "verse"):
        pad = e.get("pad", 34)
        h = _measure_panel(d, e, _inner(e, pad))
        return h + 2 * pad + e.get("gap", 28)

def _inner(e, pad):
    return (BODY_R - BODY_L) - 2 * pad - (100 if e.get("icon") else 0) - (170 if e["k"] == "verse" else 0)

def _measure_panel(d, e, inner):
    return draw_text(d, inner, 0, 0, e["t"], e["size"], e.get("w", 600), e.get("c", GREEN),
                     "center" if e["k"] == "verse" else "right", e.get("lh", 1.4), measure=True)

def el_draw(img, e, y):
    d = ImageDraw.Draw(img)
    k = e["k"]
    if k == "text":
        h = draw_text(d, BODY_R, BODY_L, y, e["t"], e["size"], e.get("w", 700), e.get("c", GREEN),
                      e.get("align", "center"), e.get("lh", 1.38))
        return y + h + e.get("gap", 30)
    if k == "head":                       # gold heading flanked by the diamond ornaments
        f = font(700, e["size"])
        tw = tlen(f, e["t"].replace("*", ""))
        orn = fit_w(asset("ornament"), 34)
        cy = y + e["size"] * 0.7
        d.text((W / 2 + tw / 2, cy), e["t"].replace("*", ""), font=f, fill=e.get("c", GOLD), anchor="rm",
               direction="rtl", language="ar")
        paste(img, orn, W / 2 + tw / 2 + 36, cy - orn.size[1] / 2)
        paste(img, orn, W / 2 - tw / 2 - 36 - orn.size[0], cy - orn.size[1] / 2)
        return y + e["size"] * 1.4 + e.get("gap", 40)
    if k == "sep":
        cy = y + 22
        d.line((W / 2 - 230, cy, W / 2 - 34, cy), fill=GOLD, width=3)
        d.line((W / 2 + 34, cy, W / 2 + 230, cy), fill=GOLD, width=3)
        d.polygon([(W / 2, cy - 14), (W / 2 + 14, cy), (W / 2, cy + 14), (W / 2 - 14, cy)], fill=GOLD)
        return y + 44 + e.get("gap", 20)
    if k == "gap":
        return y + e["n"]
    if k in ("panel", "verse"):
        pad = e.get("pad", 34)
        icon = e.get("icon")
        th = _measure_panel(d, e, _inner(e, pad))
        ph = th + 2 * pad
        box = (BODY_L, y, BODY_R, y + ph)
        gold_panel = e.get("style") == "gold"
        if k == "verse":
            shadowed_round(img, box, 40, (255, 252, 244), GOLD, 4)
            d = ImageDraw.Draw(img)
            d.rounded_rectangle((box[0] + 14, box[1] + 14, box[2] - 14, box[3] - 14), 30, outline=GOLD, width=1)
        else:
            shadowed_round(img, box, 36, BRONZE if gold_panel else (255, 252, 244),
                           None if gold_panel else (214, 190, 140), 0 if gold_panel else 2)
            d = ImageDraw.Draw(img)
        col = WHITE if gold_panel else e.get("c", GREEN)
        if icon == "check":
            check_badge(d, BODY_R - pad - 38, y + ph / 2)
            tr = BODY_R - pad - 100
        else:
            tr = BODY_R - pad
        tl = BODY_L + pad
        if k == "verse":
            bh = min(ph * 0.82, 230)
            ornate_bracket(d, BODY_R - pad - 40, y + ph / 2, bh, +1)
            ornate_bracket(d, BODY_L + pad + 40, y + ph / 2, bh, -1)
            draw_text(d, BODY_R - pad - 85, BODY_L + pad + 85, y + pad, e["t"], e["size"], e.get("w", 700), col, "center",
                      e.get("lh", 1.5))
        else:
            draw_text(d, tr, tl, y + pad, e["t"], e["size"], e.get("w", 600), col, e.get("align", "right"), e.get("lh", 1.4),
                      hl=HL_ON_DARK if gold_panel else GOLD)
        return y + ph + e.get("gap", 28)

def layout(img, elements, top, bottom, valign="center"):
    total = sum(el_measure(e) for e in elements)
    y = top + max(0, (bottom - top - total) / 2) if valign == "center" else top
    if total > bottom - top + 1:
        print(f"   ! content {total:.0f}px taller than area {bottom - top}px", flush=True)
    for e in elements:
        y = el_draw(img, e, y)
    return y

# ------------------------------------------------------------------------ chrome
def chrome(img, idx, total):
    d = ImageDraw.Draw(img)
    # card number, top-left (gold plate, as the gold bars of the reference)
    box = (60, 58, 222, 118)
    shadowed_round(img, box, 30, BRONZE, blur=10, off=4, alpha=50)
    d = ImageDraw.Draw(img)
    num = f"{idx:02d}/{total:02d}"
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 + 1), num, font=font(700, 34), fill=WHITE, anchor="mm")
    # footer: Rakb al-Abrar (left), Hajj authority logo (right), name + date in the middle
    rk = fit_w(asset("rakb_green"), 96)
    paste(img, rk, 70, 1286)
    hj = fit_w(asset("hajj_green"), 82)
    paste(img, hj, W - 70 - hj.size[0], 1288)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 1318), ORG, font=font(700, 42), fill=GREEN, anchor="mm", direction="rtl", language="ar")
    d.text((W / 2, 1366), DATE_LINE, font=font(600, 25), fill=GREEN, anchor="mm", direction="rtl", language="ar")

def make(idx, total, elements, strength=0.6, top=150, bottom=950, cover_logo=None, valign="center"):
    img = background(strength)
    if cover_logo:
        lg = fit_w(asset("rakb_gold"), cover_logo[0])
        paste(img, lg, (W - lg.size[0]) / 2, cover_logo[1])
    layout(img, elements, top, bottom, valign)
    chrome(img, idx, total)
    return img.convert("RGB")

# ------------------------------------------------------------------------ content
G = GOLD
VERSE = "فَلَا رَفَثَ وَلَا فُسُوقَ\nوَلَا جِدَالَ فِي الْحَجِّ"   # shown between ornamental ﴿ ﴾
CARDS = [
    # 01 cover
    dict(strength=1.0, top=130, bottom=640, valign="top", cover_logo=(400, 622), els=[
        dict(k="text", t="الحج بداية جديدة", size=112, gap=4, lh=1.25),
        dict(k="text", t="واختبار *حقيقي*", size=112, gap=34, lh=1.25),
        dict(k="text", t="قبل ما تخرج للحج… لازم تعرف الحقيقة\nالتي لا يتكلم عنها كثيرون:", size=44, w=600, gap=0, lh=1.5),
    ]),
    # 02
    dict(els=[
        dict(k="head", t="المشقة والواقع الميداني", size=52),
        dict(k="text", t="الحج ليس\nرحلة *مريحة*…", size=112, gap=30, lh=1.3),
        dict(k="sep", gap=30),
        dict(k="text", t="الحج تعب وزحام وانتظار\nواختبار حقيقي *للأخلاق*\nقبل الأجساد", size=58, w=600, lh=1.5),
    ]),
    # 03
    dict(els=[
        dict(k="text", t="ستجد *أحيانًا:*", size=96, gap=44),
        dict(k="panel", t="مخيمات مزدحمة.", size=52, icon="check", pad=28, gap=24),
        dict(k="panel", t="تأخيرًا في التحرك أو التنظيم.", size=52, icon="check", pad=28, gap=24),
        dict(k="panel", t="حرارة شديدة وإرهاقًا.", size=52, icon="check", pad=28, gap=24),
        dict(k="panel", t="قلة إشراف في بعض اللحظات.", size=52, icon="check", pad=28, gap=24),
    ]),
    # 04
    dict(els=[
        dict(k="head", t="الامتحان الحقيقي", size=52),
        dict(k="text", t="وهنا يبدأ\n*الامتحان* الحقيقي…", size=92, gap=26, lh=1.3),
        dict(k="sep", gap=22),
        dict(k="text", t="للأسف، بعض الناس عندما تتعب أو تغضب، تخرج منها كلمات لا تليق بحاجٍ جاء يطلب المغفرة، بل أحيانًا *كلمات اعتراض وسخط* قد تفسد أجر الرحلة كلها.",
             size=50, w=600, lh=1.55),
    ]),
    # 05
    dict(els=[
        dict(k="head", t="تذكّر دائمًا", size=64),
        dict(k="text", t="أنت لم تأتِ للسياحة…", size=84, gap=34, lh=1.3),
        dict(k="text", t="أنت جئت\n*لتُختبر.*", size=128, lh=1.28),
    ]),
    # 06
    dict(els=[
        dict(k="head", t="قال الله تعالى:", size=56, gap=34),
        dict(k="verse", t=VERSE, size=74, w=700, pad=44, gap=30, lh=1.6),
        dict(k="text", t="سورة البقرة – الآية ١٩٧", size=34, w=600, c=G, gap=34),
        dict(k="text", t="يعني أن أعظم عبادة في حياتك مرتبطة *بضبط لسانك* قبل أي شيء.", size=52, w=600, lh=1.5),
    ]),
    # 07
    dict(els=[
        dict(k="head", t="مواضع الاختبار", size=52),
        dict(k="text", t="وفي *المخيمات*، وعلى صعيد *عرفة*،\nوفي ليلة *مزدلفة*…", size=68, gap=26, lh=1.4),
        dict(k="sep", gap=22),
        dict(k="text", t="الشيطان لا يريدك أن تكمل حجك بقلبٍ سليم، فيدفعك للغضب، والشكوى، والجدال، وللنظر إلى *الأخطاء* بدل النظر إلى *العبادة.*",
             size=50, w=600, lh=1.55),
    ]),
    # 08
    dict(els=[
        dict(k="text", t="كيف *تتجنب* ذلك؟", size=80, gap=28),
        dict(k="panel", t="توقّع *المشقة* قبل السفر حتى لا تصدمك.", size=50, icon="check", pad=26, gap=22),
        dict(k="panel", t="اجعل *الدعاء* أول رد فعل بدل الغضب.", size=50, icon="check", pad=26, gap=22),
        dict(k="panel", t="تذكّر أن ملايين البشر حولك لهم نفس التعب.", size=50, icon="check", pad=26, gap=22),
    ]),
    # 09
    dict(els=[
        dict(k="text", t="كيف *تتجنب* ذلك؟", size=80, gap=28),
        dict(k="panel", t="لا تبحث عن الراحة الكاملة… بل عن *القبول.*", size=50, icon="check", pad=26, gap=22),
        dict(k="panel", t="إذا ضاق صدرك، اسكت دقيقة وقل:", size=50, icon="check", pad=26, gap=22),
        dict(k="panel", t="«اللهم تقبّل مني\nولا تحرمني الأجر»", size=58, w=700, style="gold", align="center", pad=32),
    ]),
    # 10
    dict(els=[
        dict(k="head", t="الخاتمة", size=60, gap=30),
        dict(k="text", t="الحج ليس أن\nتصل *مرتاحًا…*", size=96, gap=24, lh=1.3),
        dict(k="sep", gap=24),
        dict(k="text", t="الحج أن تعود\nبقلبٍ *جديد.*", size=112, lh=1.3),
    ]),
    # 11
    dict(els=[
        dict(k="text", t="فاحذر…", size=170, gap=30, lh=1.2),
        dict(k="panel", t="أصعب ما قد تخسره هناك ليس الراحة، بل *الأجر* إن تركت *الغضب* يقودك.",
             size=64, w=700, style="gold", align="center", pad=52, lh=1.55),
    ]),
    # 12 closing
    dict(strength=1.0, els=[
        dict(k="head", t="الدعاء الختامي", size=58, gap=26),
        dict(k="text", t="اللهم ارزقنا", size=74, gap=20, lh=1.3),
        dict(k="text", t="*حجًا مبرورًا*", size=118, gap=6, lh=1.28),
        dict(k="text", t="*وسعيًا مشكورًا*", size=118, gap=6, lh=1.28),
        dict(k="text", t="*وذنبًا مغفورًا*", size=118, lh=1.28),
    ]),
]

def main():
    os.makedirs("out", exist_ok=True)
    total = len(CARDS)
    pages = []
    for i, c in enumerate(CARDS, 1):
        print(f"card {i:02d}")
        img = make(i, total, c["els"], c.get("strength", 0.6), c.get("top", 150), c.get("bottom", 950),
                   c.get("cover_logo"), c.get("valign", "center"))
        path = f"out/card_{i:02d}.png"
        img.save(path, optimize=True)
        pages.append(img)
    pages[0].save("out/dawah_cards.pdf", save_all=True, append_images=pages[1:], resolution=144)
    print("done:", total, "cards + out/dawah_cards.pdf")

if __name__ == "__main__":
    main()

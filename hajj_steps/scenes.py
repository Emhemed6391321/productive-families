from engine import *
from engine import _logos
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def kf(keys):
    def f(t, T):
        p = t / T
        for (a, ca), (b, cb) in zip(keys, keys[1:]):
            if p <= b:
                k = ease((p - a) / max(1e-6, b - a)); return tuple(lerp(x, y, k) for x, y in zip(ca, cb))
        return keys[-1][1]
    return f

# ---------------------------------------------------------------- world constants
HARAM = (300, 560); JAM = (520, 690)
MINA_C, MUZ_C, ARA_C = (740, 880), (1070, 1370), (1330, 2020)
MINA = blob(MINA_C, 250, 170, 1, rot=.5); MUZ = blob(MUZ_C, 240, 170, 2, rot=.7); ARA = blob(ARA_C, 270, 210, 3, rot=.6)
R_HM = catmull([(300, 560), (420, 640), (560, 730), (690, 840)])
R_MA = catmull([(760, 900), (900, 1130), (1010, 1420), (1160, 1720), (1310, 1980)])
R_AMZ = catmull([(1360, 1950), (1270, 1720), (1190, 1520), (1110, 1410)])
R_ZM = catmull([(1030, 1310), (930, 1130), (830, 970), (760, 890)])
R_BACK = catmull([(660, 800), (520, 700), (400, 620), (320, 575)])
MECCA = (760, 1700)
MIQ = {"ذو الحليفة": ((560, 1030), "٤٥٠ كم", "right", 60), "الجحفة": ((440, 1330), "١٨٧ كم", "right", 60),
       "ذات عرق": ((1080, 1560), "٩٤ كم", "right", 45), "قرن المنازل": ((1110, 1770), "٧٨ كم", "right", 45), "يلملم": ((860, 2050), "٩٢ كم", "right", 70)}
ORDER = ["ذو الحليفة", "الجحفة", "ذات عرق", "قرن المنازل", "يلملم"]

def area(ctx, pts, active, name, alpha=1.0, lab_off=(0, 0), size=40):
    if active: ctx.poly(pts, fill=(175, 137, 59, 150), outline=(4, 61, 31), width=4, dash=14, alpha=int(255 * alpha))
    else: ctx.poly(pts, fill=(196, 186, 166, 150), outline=(120, 110, 92), width=4, dash=14, alpha=int(255 * alpha))
    c = (sum(p[0] for p in pts) / len(pts) + lab_off[0], sum(p[1] for p in pts) / len(pts) + lab_off[1]); ctx.label(c, name, size, alpha, INK if active else (80, 72, 60))

def km_label(ctx, route, text, f=.5, alpha=1.0, size=34, off=(0, -34)):
    pp = polycut(route, f); p = pp[-1] if f < 1 else route[len(route) // 2]; mid = route[len(route) // 2]; ctx.label((mid[0] + off[0] / ctx.z, mid[1] + off[1] / ctx.z), text, size, alpha, EMER)

def tag_ar(n): return str(n).translate(AR)

# ---------------------------------------------------------------- scenes
SC = []
def scene(**kw): SC.append(kw); return kw

# s0 -- intro
def d0(ctx, t, T):
    p = lambda a, b: seg(t, a * T, b * T)
    haram_rings(ctx, HARAM, 120, int(255 * p(0, .08)), rot=t * .6); kaaba(ctx, (HARAM[0], HARAM[1] - 10), 1.0, int(255 * p(0, .08)))
    ctx.label((HARAM[0], HARAM[1] + 130), "الحرم المكي", 36, p(.04, .12)); jamarat(ctx, JAM, int(255 * p(.12, .2))); ctx.label((JAM[0] + 40, JAM[1] + 70), "الجمرات", 32, p(.12, .2))
    area(ctx, MINA, True, "منى", p(.28, .36)); area(ctx, MUZ, False, "مزدلفة", p(.44, .52)); area(ctx, ARA, True, "عرفات", p(.56, .64))
    ctx.line(R_MA, (255, 255, 255), 6, 200, dash=18, f=p(.66, .86))
def extra0(img, ctx, t, T):
    a = 1 - seg(t, .55 * T, .75 * T); 
    if a <= 0: return
    d = ImageDraw.Draw(img, "RGBA")
    for i, (txt, bg, fg, y) in enumerate((("مناسك الحج", INK, CREAMC, 360), ("خطوة بخطوة", CREAMC, INK, 470))):
        f = F(700, 84); w = f.getlength(txt, direction="rtl", language="ar") + 90; k = seg(t, .05 * T + i * .6, .05 * T + i * .6 + .5)
        cx = W // 2 + (1 - k) * 120; al = int(255 * min(a, k))
        d.rounded_rectangle((cx - w / 2, y - 62, cx + w / 2, y + 62), 14, fill=tuple(bg) + (al,), outline=GOLDC + (al,), width=4); d.text((cx, y + 2), txt, font=f, fill=tuple(fg) + (al,), anchor="mm", direction="rtl", language="ar")
scene(key="s0", world="local", cam=kf([(0, (300, 600, 1.7)), (.3, (300, 600, 1.7)), (.7, (820, 1290, .62)), (1, (820, 1290, .62))]), draw=d0, extra=extra0, flash_in=0.0, flash_out=.4)

# s1 -- ihram / miqats
def d1(ctx, t, T):
    kaaba(ctx, MECCA, 1.7); ctx.label((MECCA[0] - 20, MECCA[1] - 85), "مكة المكرمة", 36, 1)
    for i, name in enumerate(ORDER):
        P, km, side, dist = MIQ[name]; a = seg(t, (.14 + i * .15) * T, (.14 + i * .15) * T + .5)
        if a <= 0: continue
        route = catmull([P, ((P[0] + MECCA[0]) / 2 + (18 if i % 2 else -18), (P[1] + MECCA[1]) / 2), MECCA])
        ctx.line(route, (80, 80, 80), 5, int(220 * a), dash=14, f=a); pin(ctx, P, GOLDC, 15, int(255 * a)); ctx.tag(P, name, 31, side, a, dist=dist)
        if a > .9: ctx.label(route[len(route) // 2], km, 28, min(1, (a - .9) * 10), EMER)
scene(key="s1", world="region", cam=kf([(0, (760, 1480, .86)), (1, (760, 1490, .9))]), draw=d1, flash_in=.5, flash_out=.0,
      panel=("الإحرام", None, [("من أحد المواقيت الخمسة حسب البلد الذي قدم منه الحاج", .08), ("ذو الحليفة: أهل المدينة • الجحفة: أهل الشام ومصر والمغرب", .3), ("ذات عرق: أهل العراق • قرن المنازل: أهل نجد • يلملم: أهل اليمن", .6)], 34))

# s2 -- types
def d2(ctx, t, T):
    kaaba(ctx, MECCA, 1.7); ctx.label((MECCA[0] - 20, MECCA[1] - 85), "مكة المكرمة", 36, 1)
    for i, name in enumerate(ORDER):
        P, km, side, dist = MIQ[name]; route = catmull([P, ((P[0] + MECCA[0]) / 2 + (18 if i % 2 else -18), (P[1] + MECCA[1]) / 2), MECCA])
        ctx.line(route, (80, 80, 80), 5, 140, dash=14); pin(ctx, P, GOLDC, 15); ctx.tag(P, name, 31, side, .9, dist=dist)
scene(key="s2", world="region", cam=kf([(0, (760, 1490, .9)), (1, (760, 1490, .9))]), draw=d2,
      panel=("أنواع الحج", None, [("المفرد: حج فقط", .12), ("القارن: حج وعمرة معًا", .4), ("المتمتع: عمرة في أشهر الحج ثم حج", .65)], 40))

# s3 -- tawaf
def d3(ctx, t, T):
    haram_rings(ctx, HARAM, 150, 255, rot=t * .5); kaaba(ctx, (HARAM[0], HARAM[1] - 8), 1.35)
    ctx.label((HARAM[0], HARAM[1] + 170), "الكعبة المشرفة", 40, 1)
    laps = 7; prog = seg(t, .25 * T, .9 * T) * laps
    x, y = ctx.w2s(HARAM); rs = ctx.sz(150) * .92
    for k in range(9):
        ang = -prog * 6.2832 + k * .11; px, py = x + rs * math.cos(ang), y + rs * .62 * math.sin(ang); r_ = 9 * ctx.S
        ctx.g.ellipse(((px * ctx.S - r_), (py * ctx.S - r_), (px * ctx.S + r_), (py * ctx.S + r_)), fill=(4, 61, 31, 255), outline=(255, 255, 255, 255), width=3)
    n = min(7, int(prog) + 1) if prog > 0.02 else 0
    if n: ctx.label((HARAM[0], HARAM[1] - 130), "الشوط " + tag_ar(n), 44, 1, EMER)
scene(key="s3", world="local", cam=kf([(0, (300, 610, 1.5)), (1, (300, 610, 1.6))]), draw=d3, flash_in=.5,
      panel=("طواف القدوم", None, [("٧ أشواط حول الكعبة المشرفة", .1), ("يبقى الحاج المفرد والقارن على إحرامه حتى يوم التروية", .45)], 38))

# s4 -- tarwiyah (8)
def d4(ctx, t, T):
    haram_rings(ctx, HARAM, 90, 255, rot=0); kaaba(ctx, (HARAM[0], HARAM[1] - 6), .8); ctx.label((HARAM[0] - 20, HARAM[1] + 100), "الحرم المكي", 32, 1)
    jamarat(ctx, JAM, 255)
    area(ctx, MINA, True, "منى", 1.0)
    f = seg(t, .22 * T, .62 * T); ctx.line(R_HM, EMER, 12, 255, f=f, arrow=True)
    if f > .5: ctx.label((470, 735), "٦ كم", 44, seg(f, .5, .8), EMER)
    tents(ctx, MINA, 70, 4, 255, upto=seg(t, .55 * T, .95 * T))
scene(key="s4", world="local", cam=kf([(0, (520, 790, 1.05)), (1, (540, 800, 1.1))]), draw=d4, flash_in=.0,
      panel=("الـ ٨ من ذي الحجة", "يوم التروية", [("يغادر الحجاج إلى منى على بعد ٦ كيلومترات من الحرم المكي", .1), ("تُصلّى فيها الصلوات قصرًا دون جمع", .6)], 36))

# s5 -- arafah (9)
def d5(ctx, t, T):
    kaaba(ctx, (HARAM[0], HARAM[1]), .8); haram_rings(ctx, HARAM, 90, 255); jamarat(ctx, JAM, 255)
    area(ctx, MINA, False, "منى", 1.0, size=44); area(ctx, MUZ, False, "مزدلفة", 1.0, size=44); area(ctx, ARA, True, "عرفات", 1.0, size=48)
    f = seg(t, .08 * T, .5 * T); ctx.line(R_MA, EMER, 12, 255, f=f, arrow=True)
    if f > .5: ctx.label((1040, 1450), "١٠ كم", 50, seg(f, .5, .8), EMER)
    jabal(ctx, (ARA_C[0] + 60, ARA_C[1] - 60), int(255 * seg(t, .5 * T, .6 * T)))
    k = seg(t, .55 * T, .8 * T)
    if k > 0: sun_icon(ctx, *ctx.w2s((ARA_C[0] - 150, ARA_C[1] - 200)), 26, int(255 * k))
scene(key="s5", world="local", cam=kf([(0, (1045, 1093, .6)), (1, (1045, 1093, .6))]), draw=d5,
      panel=("الـ ٩ من ذي الحجة", "يوم عرفة", [("يتوجه الحجاج إلى عرفات على بعد ١٠ كيلومترات من منى", .05), ("يقيمون فيها إلى ما بعد غروب الشمس", .38), ("تُقصر فيها صلاتا الظهر والعصر وتُجمعان جمع تقديم", .62)], 35))

# s6 -- evening: arafat -> muzdalifah
def d6(ctx, t, T):
    area(ctx, MINA, False, "منى", 1.0, size=44); area(ctx, MUZ, True, "مزدلفة", 1.0, size=48); area(ctx, ARA, False, "عرفات", 1.0, size=44)
    jabal(ctx, (ARA_C[0] + 60, ARA_C[1] - 60), 255)
    f = seg(t, .06 * T, .4 * T); ctx.line(R_AMZ, GOLDC, 12, 255, f=f, arrow=True)
    if f > .5: ctx.label((1240, 1650), "٧ كم", 50, seg(f, .5, .8), (226, 196, 132), )
    tents(ctx, MUZ, 40, 6, 255, upto=seg(t, .45 * T, .75 * T))
    rnd = random.Random(2); k = seg(t, .8 * T, .98 * T)
    for i in range(int(26 * k)): ctx.circle((MUZ_C[0] + rnd.uniform(-170, 170), MUZ_C[1] + rnd.uniform(-90, 100)), 6, fill=(120, 110, 100), outline=(255, 255, 255), width=1)
    mx, my = 120, 1010
scene(key="s6", world="local", cam=kf([(0, (1190, 1494, .85)), (1, (1190, 1494, .85))]), draw=d6, dusk=lambda t, T: seg(t, .05 * T, .3 * T) * (1 - seg(t, .93 * T, 1 * T) * .3),
      extra=lambda img, ctx, t, T: moon_screen(img, t, T),
      panel=("الـ ٩ من ذي الحجة", "مساءً", [("ينفر الحجاج إلى مزدلفة على بعد ٧ كيلومترات من عرفات", .04), ("تُجمع صلاتا المغرب والعشاء جمع تأخير مع القصر", .26), ("يبيت الحجاج في مزدلفة ويصلّون الفجر", .5), ("تُجمع منها الحصى لرمي الجمرات", .74)], 33))
def moon_screen(img, t, T):
    k = seg(t, .1 * T, .3 * T)
    if k <= 0: return
    d = ImageDraw.Draw(img, "RGBA"); x, y, r = 130, 1030, 44
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 241, 200, int(255 * k))); d.ellipse((x - r * .45, y - r * 1.15, x + r * 1.25, y + r * .85), fill=(30, 46, 70, int(200 * k)))
    for sx, sy in ((200, 960), (250, 1040), (170, 1110), (300, 990)): d.text((sx, sy), "✦", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26), fill=(255, 241, 200, int(220 * k)), anchor="mm")

# s7 -- nahr (10)
def d7(ctx, t, T):
    kaaba(ctx, HARAM, .8); haram_rings(ctx, HARAM, 90, 255); ctx.label((HARAM[0], HARAM[1] + 100), "الحرم المكي", 30, 1)
    area(ctx, MINA, True, "منى", 1.0, size=44); area(ctx, MUZ, False, "مزدلفة", 1.0, size=40); jamarat(ctx, JAM, 255, 1.2); ctx.label((JAM[0] + 20, JAM[1] + 85), "جمرة العقبة", 30, 1, EMER)
    f = seg(t, .06 * T, .26 * T); ctx.line(R_ZM, EMER, 12, 255, f=f, arrow=True)
    if f > .5: ctx.label((930, 1180), "٥ كم", 46, seg(f, .5, .8), EMER)
    tents(ctx, MINA, 40, 4, 255)
    k = seg(t, .4 * T, .5 * T)
    for i, q in enumerate(((690, 800), (760, 790), (820, 850))): sheep(ctx, q, int(255 * seg(t, (.36 + i * .04) * T, (.44 + i * .04) * T)))
    f2 = seg(t, .62 * T, .85 * T)
    ctx.line(R_BACK, GOLDC, 12, 255, f=f2, arrow=True); 
    if f2 > .5: ctx.label((430, 775), "طواف الإفاضة والسعي", 30, seg(f2, .5, .9), GOLDC)
scene(key="s7", world="local", cam=kf([(0, (750, 772, .8)), (1, (750, 772, .8))]), draw=d7,
      panel=("الـ ١٠ من ذي الحجة", "يوم النحر", [("يتوجه الحجاج إلى منى على بعد ٥ كيلومترات ويرمون جمرة العقبة", .02), ("ذبح الهدي والحلق أو التقصير والتحلل من الإحرام", .32), ("طواف الإفاضة والسعي بين الصفا والمروة", .58), ("يعود الحاج إلى منى للمبيت بها", .82)], 33))

# s8 -- tashreeq
def d8(ctx, t, T):
    kaaba(ctx, HARAM, .9); haram_rings(ctx, HARAM, 100, 255); ctx.label((HARAM[0], HARAM[1] + 110), "الحرم المكي", 32, 1)
    area(ctx, MINA, True, "منى", 1.0, size=48); tents(ctx, MINA, 90, 4, 255)
    for i, dx in enumerate((-70, 0, 70)):                                            # three jamarat
        jamarat(ctx, (JAM[0] + dx * 0, JAM[1]), 255, 1.4) if i == 0 else None
    for i, (nm, off) in enumerate((("الصغرى", -150), ("الوسطى", 0), ("الكبرى", 150))):
        a = seg(t, (.1 + i * .12) * T, (.1 + i * .12) * T + .5)
        if a > 0: ctx.circle((JAM[0] + 20 + off * .55, JAM[1] + 110 + off * .1), 12, fill=(255, 252, 244), outline=INK, width=3, alpha=int(255 * a)); ctx.label((JAM[0] + 20 + off * .55, JAM[1] + 150 + off * .1), "الجمرة " + nm, 26, a, INK)
    f = seg(t, .72 * T, .94 * T); ctx.line(R_BACK, GOLDC, 12, 255, f=f, arrow=True)
    if f > .6: ctx.label((440, 770), "طواف الوداع ٧ أشواط", 30, seg(f, .6, .95), GOLDC)
scene(key="s8", world="local", cam=kf([(0, (640, 680, 1.05)), (1, (640, 690, 1.1))]), draw=d8,
      panel=("الـ ١١ و١٢ و١٣ من ذي الحجة", "أيام التشريق", [("يبيت الحجاج أيام التشريق في منى", .02), ("يرمون الجمرات الصغرى والوسطى والكبرى كل يوم", .22), ("يجوز للمتعجل المغادرة في اليوم ١٢ قبل الغروب", .5), ("يطوف الحجاج طواف الوداع ٧ أشواط", .78)], 33), flash_out=.5)

# s9 -- closing card
def extra9(img, ctx, t, T):
    k = seg(t, .0, .6); d = ImageDraw.Draw(img, "RGBA"); card = Image.new("RGBA", (W, H), (250, 241, 228, int(255 * k))); img.alpha_composite(card)
    lg, au = _logos(); big = lg.resize((420, 420), Image.LANCZOS); img.alpha_composite(big, ((W - 420) // 2, 330)); d.ellipse(((W - 420) // 2 - 6, 324, (W + 420) // 2 + 6, 756), outline=GOLD + (255,), width=6)
    for i, (txt, sz, col, y, w) in enumerate((("تقبّل الله حجكم", 92, INK, 900, 700), ("حجًّا مبرورًا وسعيًا مشكورًا وذنبًا مغفورًا", 46, GOLDC, 1010, 700), ("الهيئة العامة لشؤون الحج والعمرة", 44, INK, 1190, 600), ("تنسيقية حجاج طرابلس ب", 76, EMER, 1280, 700))):
        a = seg(t, .4 + i * .35, .9 + i * .35); d.text((W // 2, y), txt, font=F(w, sz), fill=tuple(col) + (int(255 * a),), anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W // 2, 1135, half=300, gap=34, col=GOLD, width=3, size=12)
    d.rounded_rectangle((250, 1420, W - 250, 1500), 40, fill=GREEN + (int(255 * seg(t, 1.8, 2.4)),), outline=GOLD + (int(255 * seg(t, 1.8, 2.4)),), width=3); d.text((W // 2, 1460), "0934455422", font=F(700, 52), fill=GOLD_LT + (int(255 * seg(t, 1.8, 2.4)),), anchor="mm")
def d9(ctx, t, T): pass
SC9 = scene(key="s9", world="local", cam=kf([(0, (640, 690, 1.1)), (1, (640, 690, 1.1))]), draw=d9, extra=extra9)
for s_ in SC:
    if s_["key"] == "s9": s_["panel"] = None

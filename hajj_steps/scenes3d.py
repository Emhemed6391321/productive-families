from engine3d import *
from scenes import (kf, HARAM, JAM, MINA_C, MUZ_C, ARA_C, MINA, MUZ, ARA, R_HM, R_MA, R_AMZ, R_ZM, R_BACK, MECCA, MIQ, ORDER, tag_ar, extra9, d9)
import scenes as S1
SC = []
def scene(**kw): SC.append(kw); return kw

def area(ctx, pts, active, name, alpha=1.0, size=42, lab_dy=0):
    top, side = ((205, 166, 82), (150, 112, 46)) if active else ((206, 197, 178), (150, 140, 120))
    a = int(255 * alpha); ctx.extrude(pts, 14, top, side, alpha=a)
    ctx.poly(pts, outline=(4, 61, 31) if active else (120, 110, 92), width=4, dash=14, alpha=a, h=14)
    c = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts) + lab_dy); ctx.label(c, name, size, alpha, INK if active else (80, 72, 60), h=60)

def kf5(keys):
    def f(t, T):
        p = t / T
        for (a, ca), (b, cb) in zip(keys, keys[1:]):
            if p <= b:
                k = ease((p - a) / max(1e-6, b - a)); return tuple(lerp(x, y, k) for x, y in zip(ca, cb))
        return keys[-1][1]
    return f

# ----------------------------------------------------------------- s0 : cinematic fly-in + title
def d0(ctx, t, T):
    p = lambda a, b: seg(t, a * T, b * T)
    haram_rings(ctx, HARAM, 90, 255, rot=t * .5); kaaba(ctx, HARAM, 1.0, 255); ctx.label(HARAM, "الحرم المكي", 40, p(.1, .2), h=190)
    jamarat(ctx, JAM, int(255 * p(.2, .3))); ctx.label(JAM, "الجمرات", 32, p(.25, .35), h=80)
    area(ctx, MINA, True, "منى", p(.3, .4)); area(ctx, MUZ, False, "مزدلفة", p(.45, .55)); area(ctx, ARA, True, "عرفات", p(.6, .7))
    ctx.line(R_MA, (255, 255, 255), 7, 220, dash=18, f=p(.68, .9))
def extra0(img, ctx, t, T):
    a = 1 - seg(t, .62 * T, .85 * T)
    d = ImageDraw.Draw(img, "RGBA")
    for i, (txt, bg, fg, y) in enumerate((("مناسك الحج", INK, CREAMC, 380), ("خطوة بخطوة", CREAMC, INK, 500))):
        f = F(700, 92); w = f.getlength(txt, direction="rtl", language="ar") + 100; k = seg(t, .08 * T + i * .5, .08 * T + i * .5 + .6)
        if a <= 0: break
        cx = W // 2 + (1 - k) * 160; al = int(255 * min(a, k))
        d.rounded_rectangle((cx - w / 2, y - 66, cx + w / 2, y + 66), 16, fill=tuple(bg) + (al,), outline=GOLDC + (al,), width=4); d.text((cx, y + 2), txt, font=f, fill=tuple(fg) + (al,), anchor="mm", direction="rtl", language="ar")
scene(key="s0", world="local", cam=kf5([(0, (300, 600, 2.4, 62, -35)), (.35, (330, 650, 1.7, 58, -12)), (.8, (860, 1340, .72, 52, 14)), (1, (860, 1340, .72, 52, 14))]), draw=d0, extra=extra0, flash_out=.4, pad=5.0)

# ----------------------------------------------------------------- s1 : ihram / miqats
def d1(ctx, t, T):
    kaaba(ctx, MECCA, 1.3); ctx.label(MECCA, "مكة المكرمة", 38, 1, h=150)
    for i, name in enumerate(ORDER):
        P, km, side, dist = MIQ[name]; a = seg(t, (.1 + i * .13) * T, (.1 + i * .13) * T + .5)
        if a <= 0: continue
        route = catmull([P, ((P[0] + MECCA[0]) / 2 + (18 if i % 2 else -18), (P[1] + MECCA[1]) / 2), MECCA])
        ctx.line(route, (70, 70, 70), 5, int(220 * a), dash=14, f=a); pin(ctx, P, GOLDC, 15, int(255 * a)); ctx.tag(P, name, 31, side, a, dist=dist, h=48)
        pilgrims(ctx, route, 6, t, .07, f=a, seed=i + 3, spread=10)
        if a > .9: ctx.label(route[len(route) // 2], km, 28, min(1, (a - .9) * 10), EMER)
scene(key="s1", world="region", cam=kf5([(0, (760, 1500, 1.1, 50, -14)), (1, (760, 1470, 1.2, 52, 10))]), draw=d1, flash_in=.5,
      panel=("الإحرام", None, [("من أحد المواقيت الخمسة حسب البلد الذي قدم منه الحاج", .06), ("ذو الحليفة: أهل المدينة • الجحفة: أهل الشام ومصر والمغرب", .3), ("ذات عرق: أهل العراق • قرن المنازل: أهل نجد • يلملم: أهل اليمن", .55), ("ومن تلك اللحظة تبدأ محظورات الإحرام", .8)], 33))

# ----------------------------------------------------------------- s2 : intentions
def d2(ctx, t, T):
    kaaba(ctx, MECCA, 1.3); ctx.label(MECCA, "مكة المكرمة", 38, 1, h=150)
    for i, name in enumerate(ORDER):
        P, km, side, dist = MIQ[name]; route = catmull([P, ((P[0] + MECCA[0]) / 2 + (18 if i % 2 else -18), (P[1] + MECCA[1]) / 2), MECCA])
        ctx.line(route, (70, 70, 70), 5, 140, dash=14); pin(ctx, P, GOLDC, 15); ctx.tag(P, name, 31, side, .9, dist=dist, h=48); pilgrims(ctx, route, 6, t, .07, seed=i + 3, spread=10)
scene(key="s2", world="region", cam=kf5([(0, (760, 1470, 1.2, 52, 10)), (1, (760, 1500, 1.1, 50, 24))]), draw=d2,
      panel=("النية عند الإحرام", None, [("الحج فقط: حج الإفراد", .1), ("الحج مع العمرة: حج القِران", .4), ("التمتع بالعمرة إلى الحج: حج التمتع", .65)], 38))

# ----------------------------------------------------------------- s3 : tawaf al-qudum
def d3(ctx, t, T):
    haram_rings(ctx, HARAM, 100, 255, rot=t * .4); kaaba(ctx, HARAM, 1.35); ctx.label(HARAM, "الكعبة المشرفة", 40, 1, h=300)
    prog = seg(t, .22 * T, .9 * T) * 7; rr = 100 * 1.55 * .9
    pil = []
    for k in range(14):
        ang = -prog * 6.2832 + k * .13; pil.append((HARAM[0] + rr * math.cos(ang), HARAM[1] + rr * math.sin(ang)))
    for q in sorted(pil, key=lambda q: ctx.P(q)[3]):
        x, y, s, d = ctx.P(q, 0); k = s / ctx.cam.zoom * ctx.cam.zoom ** .4; w = 6 * k; h = 18 * k; S2 = ctx.S
        ctx.g.rounded_rectangle(((x - w) * S2, (y - h) * S2, (x + w) * S2, y * S2), radius=int(w * S2), fill=(255, 255, 255, 255), outline=(150, 145, 130, 255), width=S2)
        ctx.g.ellipse(((x - w * .7) * S2, (y - h - w * 1.2) * S2, (x + w * .7) * S2, (y - h + w * .2) * S2), fill=(176, 130, 96, 255))
    n = min(7, int(prog) + 1) if prog > .02 else 0
    if n: ctx.label(HARAM, "الشوط " + tag_ar(n), 52, 1, EMER, h=200)
scene(key="s3", world="local", cam=kf5([(0, (300, 600, 1.7, 56, -30)), (1, (300, 590, 1.9, 54, 30))]), draw=d3, flash_in=.5,
      panel=("طواف القدوم", None, [("٧ أشواط حول الكعبة المشرفة", .08), ("المفرد والقارن يبقيان على إحرامهما", .35), ("المتمتع يتحلل ثم يُحرم مجددًا يوم التروية", .6)], 36))

# ----------------------------------------------------------------- s4 : tarwiyah
def d4(ctx, t, T):
    haram_rings(ctx, HARAM, 70, 255); kaaba(ctx, HARAM, .75); ctx.label(HARAM, "الحرم المكي", 32, 1, h=140); jamarat(ctx, JAM, 255)
    area(ctx, MINA, True, "منى", 1.0, lab_dy=90)
    f = seg(t, .18 * T, .66 * T); ctx.line(R_HM, EMER, 12, 255, f=f, arrow=True)
    pilgrims(ctx, R_HM, 22, t, .05, f=f, seed=2, spread=22)
    if f > .5: ctx.label((470, 760), "٦ كم", 46, seg(f, .5, .8), EMER, h=0)
    tents(ctx, MINA, 70, 4, 255, upto=seg(t, .55 * T, .95 * T))
scene(key="s4", world="local", cam=kf5([(0, (520, 800, 1.2, 54, -20)), (1, (560, 810, 1.25, 52, 14))]), draw=d4,
      panel=("الـ ٨ من ذي الحجة", "يوم التروية", [("يغادر الحجيج إلى منى قاطعين ٦ كيلومترات", .08), ("يصلون جميع الصلوات قصرًا في مواقيتها", .6)], 36))

# ----------------------------------------------------------------- s5 : arafah
def d5(ctx, t, T):
    haram_rings(ctx, HARAM, 70, 255); kaaba(ctx, HARAM, .75); jamarat(ctx, JAM, 255)
    area(ctx, MINA, False, "منى", 1.0, 46); area(ctx, MUZ, False, "مزدلفة", 1.0, 46); area(ctx, ARA, True, "عرفات", 1.0, 52)
    f = seg(t, .06 * T, .46 * T); ctx.line(R_MA, EMER, 12, 255, f=f, arrow=True); pilgrims(ctx, R_MA, 26, t, .045, f=f, seed=5, spread=30)
    if f > .5: ctx.label((1040, 1450), "١٠ كم", 52, seg(f, .5, .8), EMER, h=0)
    jabal(ctx, (ARA_C[0] + 70, ARA_C[1] - 70), int(255 * seg(t, .46 * T, .56 * T)))
    k = seg(t, .55 * T, .8 * T)
    if k > 0:
        pilgrims(ctx, catmull([(1250, 2000), (1320, 2030), (1400, 2000)]), 28, t * 0.0, 0, 1.0, int(255 * k), 9, 70)
        sun_icon(ctx, *ctx.w2s((ARA_C[0] - 150, ARA_C[1] - 200), 150), 26, int(255 * k))
scene(key="s5", world="local", cam=kf5([(0, (1000, 1100, .72, 50, -18)), (.5, (1100, 1500, .75, 52, 0)), (1, (1250, 1900, 1.0, 50, 16))]), draw=d5,
      panel=("الـ ٩ من ذي الحجة", "يوم عرفة", [("الوقوف بعرفات حتى غروب الشمس: الركن الأعظم", .04), ("تُقصر صلاتا الظهر والعصر وتُجمعان", .4), ("في أول وقت صلاة الظهر (جمع تقديم)", .62)], 35))

# ----------------------------------------------------------------- s6 : muzdalifah
def d6(ctx, t, T):
    area(ctx, MINA, False, "منى", 1.0, 44); area(ctx, MUZ, True, "مزدلفة", 1.0, 50); area(ctx, ARA, False, "عرفات", 1.0, 44)
    jabal(ctx, (ARA_C[0] + 70, ARA_C[1] - 70), 255)
    f = seg(t, .05 * T, .4 * T); ctx.line(R_AMZ, GOLDC, 12, 255, f=f, arrow=True); pilgrims(ctx, R_AMZ, 24, t, .05, f=f, seed=6, spread=26)
    if f > .5: ctx.label((1240, 1650), "٧ كم", 52, seg(f, .5, .8), (226, 196, 132), h=0)
    tents(ctx, MUZ, 45, 6, 255, upto=seg(t, .45 * T, .75 * T))
    rnd = random.Random(2); k = seg(t, .8 * T, .98 * T)
    for i in range(int(30 * k)): ctx.disc((MUZ_C[0] + rnd.uniform(-170, 170), MUZ_C[1] + rnd.uniform(-90, 100)), 6, (120, 110, 100), outline=(255, 255, 255), width=1, h=15)
scene(key="s6", world="local", cam=kf5([(0, (1300, 1850, 1.0, 50, 16)), (.5, (1190, 1550, .85, 52, 6)), (1, (1090, 1380, 1.0, 52, -14))]), draw=d6,
      dusk=lambda t, T: seg(t, .05 * T, .3 * T), extra=lambda img, ctx, t, T: S1.moon_screen(img, t, T),
      panel=("الـ ٩ من ذي الحجة", "مساءً", [("بغروب الشمس ينفر الحجاج إلى مزدلفة (٧ كم)", .04), ("يصلون المغرب والعشاء جمع تأخير وقصرًا", .3), ("يبيتون في مزدلفة", .55), ("ويجمعون الحصى لرمي الجمرات", .75)], 34))

# ----------------------------------------------------------------- s7 : nahr (jamarat, hady, halq)
def d7(ctx, t, T):
    haram_rings(ctx, HARAM, 70, 255); kaaba(ctx, HARAM, .75); ctx.label(HARAM, "الحرم المكي", 30, 1, h=140)
    area(ctx, MINA, True, "منى", 1.0, 44); area(ctx, MUZ, False, "مزدلفة", 1.0, 40); jamarat(ctx, JAM, 255, 1.3); ctx.label(JAM, "جمرة العقبة الكبرى", 28, 1, EMER, h=110)
    f = seg(t, .04 * T, .24 * T); ctx.line(R_ZM, EMER, 12, 255, f=f, arrow=True); pilgrims(ctx, R_ZM, 20, t, .06, f=f, seed=7, spread=20)
    if f > .5: ctx.label((930, 1180), "رمي الحصى", 40, seg(f, .5, .8), EMER, h=0)
    tents(ctx, MINA, 40, 4, 255)
    for i, q in enumerate(((690, 800), (760, 790), (820, 850), (880, 830))): sheep(ctx, q, int(255 * seg(t, (.34 + i * .04) * T, (.42 + i * .04) * T)))
    k = seg(t, .6 * T, .75 * T)
    if k > 0: ctx.label((780, 700), "الحلق أو التقصير", 36, k, EMER, h=60)
scene(key="s7", world="local", cam=kf5([(0, (1000, 1300, .9, 52, 14)), (.35, (800, 1000, 1.0, 52, 0)), (1, (640, 820, 1.25, 52, -16))]), draw=d7,
      panel=("الـ ١٠ من ذي الحجة", "يوم النحر", [("رمي جمرة العقبة الكبرى فقط", .04), ("ذبح الهدي", .3), ("الحلق أو التقصير: التحلل الأصغر", .5), ("يباح كل المحظورات عدا الجماع", .75)], 35))

# ----------------------------------------------------------------- s7b : ifadah + sa'i
def d7b(ctx, t, T):
    haram_rings(ctx, HARAM, 90, 255, rot=t * .4); kaaba(ctx, HARAM, 1.0); ctx.label(HARAM, "الكعبة المشرفة", 36, 1, h=220)
    area(ctx, MINA, True, "منى", 1.0, 44); tents(ctx, MINA, 60, 4, 255)
    safa = (HARAM[0] + 230, HARAM[1] + 40); marwa = (HARAM[0] + 230, HARAM[1] + 470)
    ctx.line([safa, marwa], (150, 110, 60), 14, 255, f=seg(t, .35 * T, .5 * T)); ctx.circle(safa, 18, fill=GOLDC, outline=(255, 255, 255), width=3); ctx.circle(marwa, 18, fill=GOLDC, outline=(255, 255, 255), width=3)
    ctx.label((safa[0] + 70, safa[1]), "الصفا", 34, seg(t, .35 * T, .45 * T), INK, h=0); ctx.label((marwa[0] + 70, marwa[1]), "المروة", 34, seg(t, .35 * T, .45 * T), INK, h=0)
    sa = seg(t, .45 * T, .8 * T); nlap = sa * 7; ph = (nlap % 2); pos = ph if ph <= 1 else 2 - ph; q = (lerp(safa[0], marwa[0], pos), lerp(safa[1], marwa[1], pos))
    if 0 < sa < 1: pilgrims(ctx, [q, (q[0], q[1] + .01)], 1, 0, 0, 1.0, 255, 3, 0)
    back = seg(t, .82 * T, .98 * T); ctx.line(R_BACK[::-1], GOLDC, 12, 255, f=back, arrow=True); pilgrims(ctx, R_BACK[::-1], 14, t, .06, f=back, seed=8, spread=16)
    pr = seg(t, .08 * T, .3 * T) * 7
    for k in range(10):
        a = -pr * 6.2832 + k * .13; qq = (HARAM[0] + 140 * math.cos(a), HARAM[1] + 140 * math.sin(a)); x, y, s, d = ctx.P(qq, 0); w = 5 * s / ctx.cam.zoom; hh = 15 * s / ctx.cam.zoom
        ctx.g.rounded_rectangle(((x - w) * 2, (y - hh) * 2, (x + w) * 2, y * 2), radius=int(w * 2), fill=(255, 255, 255, 255), outline=(150, 145, 130, 255), width=2)
scene(key="s7b", world="local", cam=kf5([(0, (330, 640, 1.5, 54, -24)), (.6, (480, 760, 1.2, 52, 4)), (1, (560, 800, 1.1, 50, 18))]), draw=d7b,
      panel=("الـ ١٠ من ذي الحجة", "طواف الإفاضة", [("طواف الإفاضة حول الكعبة", .04), ("السعي بين الصفا والمروة", .3), ("التحلل الأكبر ثم العودة إلى منى للمبيت", .62)], 36))

# ----------------------------------------------------------------- s8 : tashreeq + wada'
def d8(ctx, t, T):
    haram_rings(ctx, HARAM, 80, 255, rot=t * .3); kaaba(ctx, HARAM, .85); ctx.label(HARAM, "الحرم المكي", 32, 1, h=160)
    area(ctx, MINA, True, "منى", 1.0, 48, lab_dy=100); tents(ctx, MINA, 90, 4, 255)
    jamarat(ctx, JAM, 255, 1.5)
    for i, (nm, dx) in enumerate((("الصغرى", -140), ("الوسطى", 0), ("الكبرى", 140))):
        a = seg(t, (.08 + i * .1) * T, (.08 + i * .1) * T + .5)
        if a > 0: ctx.label((JAM[0] + dx * .9, JAM[1] + 85 + (i % 2) * 40), "الجمرة " + nm, 26, a, INK, h=0)
    f = seg(t, .72 * T, .95 * T); ctx.line(R_BACK, GOLDC, 12, 255, f=f, arrow=True); pilgrims(ctx, R_BACK, 16, t, .06, f=f, seed=9, spread=16)
    if f > .6: ctx.label((430, 790), "طواف الوداع ٧ أشواط", 32, seg(f, .6, .95), GOLDC, h=0)
scene(key="s8", world="local", cam=kf5([(0, (700, 760, 1.25, 52, 16)), (.6, (600, 740, 1.15, 52, -4)), (1, (440, 680, 1.35, 54, -22))]), draw=d8, flash_out=.5,
      panel=("الـ ١١ و١٢ و١٣ من ذي الحجة", "أيام التشريق", [("المبيت في منى ثلاث ليالٍ", .02), ("رمي الجمرات الثلاث كل يوم", .22), ("يجوز للمتعجل المغادرة في ١٢ قبل الغروب", .48), ("طواف الوداع ٧ أشواط وتنتهي المناسك", .76)], 34))

scene(key="s9", world="local", cam=kf5([(0, (640, 690, 1.1, 52, 0)), (1, (640, 690, 1.1, 52, 0))]), draw=d9, extra=extra9)
for s_ in SC:
    if s_["key"] == "s9": s_["panel"] = None

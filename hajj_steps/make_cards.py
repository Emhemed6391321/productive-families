import json, os
from scenes3d import *
from engine import _logos
os.makedirs(HS + "Cards", exist_ok=True)
dur = json.load(open(HS + 'work/durations3.json')); BY = {s["key"]: s for s in SC}
CARDS = [  # scene, t-fraction, tag, title, body
 ("s0", .95, None, "مناسك الحج", "رحلة الحاج بين مكة المكرمة ومنى وعرفات ومزدلفة، خطوة بخطوة"),
 ("s1", .95, "الإحرام", "المواقيت الخمسة", "يُحرم الحاج من أحد خمسة مواقيت قبل مكة المكرمة، بحسب البلد الذي قدم منه"),
 ("s1", .70, "الإحرام", "ذو الحليفة والجحفة", "ذو الحليفة: أهل المدينة المنورة • الجحفة: أهل الشام ومصر والمغرب"),
 ("s1", .99, "الإحرام", "ذات عرق وقرن المنازل ويلملم", "ذات عرق: أهل العراق • قرن المنازل: أهل نجد • يلملم: أهل اليمن"),
 ("s2", .30, "الإحرام", "محظورات الإحرام", "من لحظة الإحرام لا يجوز للحاج الإتيان بمحظورات الإحرام"),
 ("s2", .45, "النية", "حج الإفراد", "ينوي الحاج متلفظًا: الحج فقط"),
 ("s2", .65, "النية", "حج القِران", "ينوي الحاج الحج مع العمرة معًا"),
 ("s2", .90, "النية", "حج التمتع", "ينوي الحاج التمتع بالعمرة إلى الحج"),
 ("s3", .60, "طواف القدوم", "سبعة أشواط", "يطوف الحاج حول الكعبة المشرفة سبعة أشواط"),
 ("s3", .92, "طواف القدوم", "بعد الطواف", "المفرد والقارن يبقيان على إحرامهما، والمتمتع يتحلل ثم يُحرم مجددًا يوم التروية"),
 ("s4", .85, "الـ ٨ من ذي الحجة", "يوم التروية", "يغادر الحجيج إلى منى قاطعين ٦ كيلومترات"),
 ("s4", .99, "الـ ٨ من ذي الحجة", "المبيت في منى", "يصلون جميع الصلوات قصرًا في مواقيتها"),
 ("s5", .70, "الـ ٩ من ذي الحجة", "يوم عرفة", "الوقوف بعرفات حتى غروب الشمس: الركن الأعظم للحج"),
 ("s5", .99, "الـ ٩ من ذي الحجة", "الظهر والعصر", "تُقصر الصلاتان وتُجمعان جمع تقديم في أول وقت الظهر"),
 ("s6", .60, "مساء يوم عرفة", "النفرة إلى مزدلفة", "بغروب شمس عرفة ينفر الحجاج إلى مزدلفة (٧ كيلومترات)"),
 ("s6", .97, "مساء يوم عرفة", "المبيت وجمع الحصى", "يصلون المغرب والعشاء جمع تأخير وقصرًا، ويبيتون ويجمعون الحصى"),
 ("s7", .40, "الـ ١٠ من ذي الحجة", "جمرة العقبة والهدي", "بعد الفجر يرمي الحاج جمرة العقبة الكبرى فقط، ثم يذبح الهدي"),
 ("s7", .95, "الـ ١٠ من ذي الحجة", "الحلق والتحلل الأصغر", "يحلق أو يقصر، فيباح له كل المحظورات عدا الجماع"),
 ("s7b", .75, "الـ ١٠ من ذي الحجة", "طواف الإفاضة والسعي", "الطواف بالكعبة والسعي بين الصفا والمروة، ثم التحلل الأكبر والعودة إلى منى"),
 ("s8", .85, "الـ ١١ و١٢ و١٣ من ذي الحجة", "أيام التشريق والوداع", "المبيت في منى ورمي الجمرات الثلاث، ثم طواف الوداع سبعة أشواط وتنتهي المناسك"),
]
OFF = {"s1": 190, "s2": 190, "s3": 40}
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def wrap(f, text, maxw):
    out, cur = [], ""
    for w in text.split(" "):
        t = (cur + " " + w).strip()
        if f.getlength(t, direction="rtl", language="ar") <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
CW, CH = 1080, 1350
def card(i, sc, fr, tag, title, body):
    s = BY[sc]; T = dur[sc] + s.get("pad", .8)
    fr_img = render3d(s, T * fr, T, chrome=False).convert("RGB").crop((0, 560, 1080, 1700))
    img = paper(CW, CH, warm=True); img = add_lattice(img, (205, 183, 140), 38, ramp=vramp(CH, 0, CH, .6, 1)); d = ImageDraw.Draw(img)
    frame(img, 26, GOLD, 3, 12)
    lg, au = _logos(); img.paste(lg.resize((96, 96), Image.LANCZOS), (58, 52), lg.resize((96, 96), Image.LANCZOS).getchannel("A")); d = ImageDraw.Draw(img); d.ellipse((55, 49, 157, 151), outline=GOLD, width=3)
    d.text((CW - 70, 78), "الهيئة العامة لشؤون الحج والعمرة", font=font(600, 28), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    d.text((CW - 70, 120), "تنسيقية حجاج طرابلس ب", font=font(700, 42), fill=GREEN, anchor="rm", direction="rtl", language="ar")
    # number chip
    d.rounded_rectangle((180, 66, 330, 124), 29, fill=GREEN, outline=GOLD, width=3)
    d.text((255, 96), f"{i:02d}/20".translate(AR), font=font(700, 32), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    # map window
    box = (50, 190, CW - 50, 190 + 640); soft_shadow(img, box, 40, alpha=80, blur=16, off=9)
    mk = Image.new("L", img.size, 0); ImageDraw.Draw(mk).rounded_rectangle(box, 40, fill=255)
    lay = Image.new("RGB", img.size); lay.paste(fr_img.resize((box[2] - box[0], int((box[2] - box[0]) * fr_img.size[1] / fr_img.size[0]))).crop((0, OFF.get(sc, 70), box[2] - box[0], OFF.get(sc, 70) + box[3] - box[1])), (box[0], box[1])); img.paste(lay, (0, 0), mk)
    d = ImageDraw.Draw(img); d.rounded_rectangle(box, 40, outline=GOLD, width=5)
    if tag:
        f = font(700, 34); w = f.getlength(tag, direction="rtl", language="ar") + 50
        d.rounded_rectangle((CW - 70 - w, box[3] + 28, CW - 70, box[3] + 92), 32, fill=GREEN, outline=GOLD, width=2); d.text((CW - 70 - w / 2, box[3] + 61), tag, font=f, fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    ft = font(700, 78)
    while ft.getlength(title, direction="rtl", language="ar") > CW - 130: ft = font(700, ft.size - 3)
    d.text((CW - 70, box[3] + 160), title, font=ft, fill=GREEN, anchor="rm", direction="rtl", language="ar")
    diamond_divider(img, CW // 2 + 200, box[3] + 215, half=330, gap=30, col=GOLD, width=3, size=11); d = ImageDraw.Draw(img)
    fb = font(600, 38); ls = wrap(fb, body, CW - 150)
    for k, l in enumerate(ls[:3]): d.text((CW - 70, box[3] + 262 + k * 58), l, font=fb, fill=(120, 90, 40), anchor="rm", direction="rtl", language="ar")
    d.rectangle((0, CH - 78, CW, CH), fill=GREEN_DK); d.rectangle((0, CH - 78, CW, CH - 73), fill=GOLD)
    d.text((CW - 60, CH - 38), "تنسيقية حجاج طرابلس ب", font=font(700, 32), fill=CREAM, anchor="rm", direction="rtl", language="ar"); d.text((60, CH - 38), "0934455422", font=font(700, 36), fill=GOLD_LT, anchor="lm")
    img.convert("RGB").save(HS + f"Cards/Hajj-Card-{i:02d}.png", optimize=True)
if __name__ == "__main__":
    for i, c in enumerate(CARDS, 1): card(i, *c); print(i, flush=True)
    sh = Image.new("RGB", (5 * 330, 4 * 413), (50, 50, 50))
    for i in range(20): sh.paste(Image.open(HS + f"Cards/Hajj-Card-{i + 1:02d}.png").resize((324, 405)), ((i % 5) * 330, (i // 5) * 413))
    sh.save(HS + "work/cards_sheet.png")

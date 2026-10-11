#!/usr/bin/env python3
"""Builds the Tripoli-B brand kit:  svg/*.svg, png/*.png, Tripoli-B-Palette.ase,
Tripoli-B-Brand-Guide.pdf (A4 landscape, live text) and Tripoli-B-Brand-Elements.ai (one artboard, text outlined).
    python3 build_kit.py"""
import os, struct, subprocess, shutil, math
import kit_svg as k
import render

P = k.PAL
NAME = "تنسيقية حجاج طرابلس ب"
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

COLORS = [  # key, arabic name, hex, role
    ("teal", "أخضر الهيئة", P["teal"], "الخلفيات الداكنة، خلفية شعار الهيئة"),
    ("green", "أخضر العناوين", P["green"], "العناوين والنصوص الأساسية"),
    ("deep", "أخضر عميق", P["deep"], "نهايات التدرجات، اللوحات الداكنة"),
    ("gold", "ذهبي", P["gold"], "الكلمات المبرزة، الزخارف، الإطارات"),
    ("bronze", "برونزي", P["bronze"], "لوحات الإبراز، أزرار الأرقام"),
    ("gold_lt", "ذهبي فاتح", P["gold_lt"], "الذهبي فوق الخلفيات الداكنة"),
    ("paper", "ورق فاتح", P["paper"], "الخلفية الفاتحة الأساسية"),
    ("paper_dk", "ورق أغمق", P["paper_dk"], "أطراف الخلفية، الظلال الورقية"),
]

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def cmyk(h):
    r, g, b = [v / 255 for v in rgb(h)]; kk = 1 - max(r, g, b)
    if kk >= 1: return (0, 0, 0, 100)
    return tuple(round(v * 100) for v in ((1 - r - kk) / (1 - kk), (1 - g - kk) / (1 - kk), (1 - b - kk) / (1 - kk), kk))

# ============================================================== 1) SVG / PNG elements
def write(path, s): open(path, "w", encoding="utf-8").write(s)

def build_svgs():
    out = []
    variants = {
        "hajj_logo_white": [("white", P["white"], P["teal"]), ("green", P["green"], P["paper"]), ("teal", P["teal"], P["paper"]), ("gold", P["gold"], P["deep"]), ("gold-light", P["gold_lt"], P["deep"])],
        "rakb_gold": [("green", P["green"], P["paper"]), ("gold", P["gold"], P["deep"]), ("gold-light", P["gold_lt"], P["deep"]), ("white", P["white"], P["green"])],
    }
    names = {"hajj_logo_white": "Logo-Coordination", "rakb_gold": "Logo-RakbAlAbrar"}
    for src, vs in variants.items():
        for tag, fill, bg in vs:
            f = f"svg/{names[src]}-{tag}.svg"; write(f, k.logo_svg(src, fill)); out.append(f)
            f2 = f"svg/{names[src]}-{tag}-on-bg.svg"; write(f2, k.logo_svg(src, fill, bg=bg)); out.append(f2)
    # ornaments
    write("svg/Star8-gold.svg", k.standalone(k.star8(100, 100, 90, fill=P["gold"]), 200, 200)); out.append("svg/Star8-gold.svg")
    write("svg/Star8-outline.svg", k.standalone(k.star8(100, 100, 90, stroke=P["gold"], sw=4), 200, 200)); out.append("svg/Star8-outline.svg")
    write("svg/Divider-gold.svg", k.standalone(k.divider(250, 30, 230, 34, P["gold"], 3, 14), 500, 60)); out.append("svg/Divider-gold.svg")
    write("svg/Ornament-gold.svg", k.standalone(k.ornament(50, 100, 180, P["gold"]), 100, 200)); out.append("svg/Ornament-gold.svg")
    write("svg/Frame-gold.svg", k.standalone(k.frame(60, 60, 680, 960, P["gold"], 5, 16, 40), 800, 1080)); out.append("svg/Frame-gold.svg")
    write("svg/Pattern-lattice-tile.svg", k.standalone(f'<rect width="600" height="600" fill="url(#p)"/>', 600, 600, defs=k.lattice_pattern("p", P["gold"], .7, 60, 1.8), bg=P["paper"])); out.append("svg/Pattern-lattice-tile.svg")
    write("svg/Pattern-starfield-tile.svg", k.standalone(f'<rect width="600" height="600" fill="url(#p)"/>', 600, 600, defs=k.starfield_pattern("p", P["gold"], .8, 120, 2), bg=P["paper"])); out.append("svg/Pattern-starfield-tile.svg")
    return out

def build_pngs():
    os.makedirs("png", exist_ok=True)
    for f in sorted(os.listdir("svg")):
        if f.startswith(("Logo-")) and "-on-bg" not in f:
            from PIL import Image
            d, w, h = k.trace("hajj_logo_white" if "Coordination" in f else "rakb_gold")
            sc = 2000 / w
            render.to_png("svg/" + f, "png/" + f.replace(".svg", ".png"), w, h, scale=sc)

# ============================================================== 2) Adobe swatches (.ase)
def build_ase(path):
    blocks = []
    for key, name, hx, role in COLORS:
        r, g, b = [v / 255 for v in rgb(hx)]
        nm = (f"{name} {hx}" + "\0").encode("utf-16-be")
        body = struct.pack(">H", len(nm) // 2) + nm + b"RGB " + struct.pack(">fff", r, g, b) + struct.pack(">H", 2)
        blocks.append(struct.pack(">HI", 0x0001, len(body)) + body)
    gname = ("Tripoli-B" + "\0").encode("utf-16-be")
    start = struct.pack(">HI", 0xC001, 2 + len(gname)) + struct.pack(">H", len(gname) // 2) + gname
    end = struct.pack(">HI", 0xC002, 0)
    data = b"ASEF" + struct.pack(">HHI", 1, 0, len(blocks) + 2) + start + b"".join(blocks) + end
    open(path, "wb").write(data)

# ============================================================== 3) outlining helper (text -> paths)
def outline_svg_to_pdf(svg_inline, w, h, out_pdf, tmp="_tmp_outline"):
    """HTML (live Arabic text, shaped by Chromium) -> PDF -> pdftocairo -svg (glyphs become paths) -> PDF"""
    os.makedirs(tmp, exist_ok=True)
    html = f'<!doctype html><meta charset="utf-8"><style>{FONT_CSS} @page{{size:{w}px {h}px;margin:0}} html,body{{margin:0;padding:0}}</style><body>{svg_inline}</body>'
    write(f"{tmp}/a.html", html)
    render.to_pdf(f"{tmp}/a.html", f"{tmp}/a.pdf", w_px=w, h_px=h)
    subprocess.run(["pdftocairo", "-svg", f"{tmp}/a.pdf", f"{tmp}/a.svg"], check=True)
    write(f"{tmp}/b.html", f'<!doctype html><meta charset="utf-8"><style>@page{{size:{w}px {h}px;margin:0}} html,body{{margin:0}} img{{display:block;width:{w}px;height:{h}px}}</style><body><img src="a.svg"></body>')
    return f"{tmp}/a.svg", f"{tmp}/a.pdf"

FONT_CSS = "".join(
    f"@font-face{{font-family:'IBM Plex Sans Arabic';font-weight:{w};src:url('{HERE}/fonts/IBMPlexSansArabic-{w}.ttf')}}" for w in (400, 500, 600, 700)
) + "body{font-family:'IBM Plex Sans Arabic',sans-serif}"

# ============================================================== 4) shared SVG defs (symbols + patterns)
def symbols():
    dh, wh, hh = k.trace("hajj_logo_white"); dr, wr, hr = k.trace("rakb_gold")
    return (f'<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>'
            f'<symbol id="s-hajj" viewBox="0 0 {wh} {hh}"><path fill="currentColor" fill-rule="evenodd" d="{dh}"/></symbol>'
            f'<symbol id="s-rakb" viewBox="0 0 {wr} {hr}"><path fill="currentColor" fill-rule="evenodd" d="{dr}"/></symbol>'
            f'{k.lattice_pattern("lat-dark", P["gold_lt"], .30, 60, 1.6)}{k.lattice_pattern("lat-light", "#CDB78C", .55, 60, 1.6)}'
            f'{k.starfield_pattern("sf-light", P["gold"], .55, 120, 1.8)}{k.starfield_pattern("sf-dark", P["gold_lt"], .35, 120, 1.6)}'
            f'</defs></svg>'), (wh, hh), (wr, hr)

SYM, (HW, HH), (RW, RH) = symbols()

def lg(kind, color, width, extra=""):
    w, h = (HW, HH) if kind == "hajj" else (RW, RH)
    return f'<svg viewBox="0 0 {w} {h}" style="color:{color};width:{width};height:auto;display:block;{extra}"><use href="#s-{kind}"/></svg>'

def swatch_svg(inner, w, h, bg=None, style=""):
    r = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    st = style or "height:88%;width:auto"
    return f'<svg viewBox="0 0 {w} {h}" style="display:block;{st}">{r}{inner}</svg>'

# ============================================================== 5) Guide pages
CSS = FONT_CSS + """
@page{size:297mm 210mm;margin:0}
*{box-sizing:border-box}
html,body{margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.pg{width:297mm;height:210mm;position:relative;overflow:hidden;page-break-after:always;background:#FAF1E4;color:#043D1F;direction:rtl}
.pg:last-child{page-break-after:auto}
.bg{position:absolute;inset:0}
.hd{position:absolute;top:12mm;right:16mm;left:16mm;display:flex;justify-content:space-between;align-items:center}
.hd h2{margin:0;font-size:25pt;font-weight:700}
.hd .n{font-size:11pt;font-weight:600;color:#946934;letter-spacing:.5px}
.sub{position:absolute;top:27mm;right:16mm;left:16mm;font-size:11pt;font-weight:500;color:#5b4a2a;line-height:1.7}
.body{position:absolute;top:44mm;right:16mm;left:16mm;bottom:14mm}
.ft{position:absolute;bottom:6mm;right:16mm;left:16mm;display:flex;justify-content:space-between;font-size:8pt;color:#8a7a58;font-weight:500}
.card{background:#FFFCF4;border:1.2px solid #DECCA8;border-radius:5mm;padding:5mm}
.dark{background:#005045;color:#fff}
.tile{border-radius:4mm;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}
.lab{font-size:8.5pt;font-weight:600;margin-top:2mm;text-align:center}
.mono{font-family:'IBM Plex Sans Arabic';direction:ltr;unicode-bidi:isolate}
.gold{color:#AF893B}
.row{display:flex;gap:6mm}
.grid{display:grid;gap:6mm}
"""

def page_bg(kind):
    if kind == "dark":
        return (f'<div class="bg" style="background:linear-gradient(180deg,#005045,#033b2a 60%,#022416)"></div>'
                f'<svg class="bg" width="100%" height="100%"><rect width="100%" height="100%" fill="url(#lat-dark)"/></svg>')
    return (f'<div class="bg" style="background:linear-gradient(180deg,#FAF1E4,#F2E7D3)"></div>'
            f'<svg class="bg" width="100%" height="100%" style="opacity:.55"><rect width="100%" height="100%" fill="url(#lat-light)"/></svg>')

def header(n, title, sub=""):
    return (f'<div class="hd"><h2>{title}</h2><div class="n">{n:02d}</div></div>' + (f'<div class="sub">{sub}</div>' if sub else "") +
            f'<div class="ft"><span>الهوية البصرية - {NAME}</span><span>IBM Plex Sans Arabic</span></div>')

def divider_svg(col=P["gold"], w=120):
    return f'<svg viewBox="0 0 500 40" style="width:{w}mm;display:block;margin:0 auto">{k.divider(250, 20, 230, 34, col, 3, 12)}</svg>'

def page_cover():
    frame = k.frame(40, 40, 1043, 714, P["gold"], 3.5, 12, 30)
    return (f'<div class="pg">{page_bg("dark")}<svg class="bg" viewBox="0 0 1123 794" width="100%" height="100%">{frame}</svg>'
            f'<div style="position:absolute;top:0;bottom:0;right:0;left:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5mm;color:#fff">'
            f'{lg("hajj", "#fff", "62mm")}<div style="height:4mm"></div>'
            f'<div style="font-size:21pt;font-weight:600;color:#E2C484">دليل الهوية البصرية</div>{divider_svg(P["gold"], 90)}'
            f'<div style="font-size:50pt;font-weight:700;line-height:1.15;text-align:center">تنسيقية حجاج<br><span style="color:#E2C484">طرابلس ب</span></div>'
            f'<div style="font-size:11pt;font-weight:500;color:#cfe4da;margin-top:3mm">الشعارات - الألوان - الخطوط - الزخارف - الأنماط - قواعد الاستخدام</div>'
            f'</div></div>')

def page_contents():
    items = ["شعار التنسيقية (شعار الهيئة)", "شعار ركب الأبرار", "الاسم والتوليفات", "الألوان", "الخطوط", "الزخارف والإطارات", "الأنماط والخلفيات", "قواعد الاستخدام", "نماذج التطبيق", "ملفات الحزمة"]
    cells = "".join(f'<div class="card" style="display:flex;align-items:center;gap:5mm"><div style="width:11mm;height:11mm;border-radius:50%;background:#043D1F;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:13pt">{i + 3}</div><div style="font-size:13pt;font-weight:600">{t}</div></div>' for i, t in enumerate(items))
    return f'<div class="pg">{page_bg("light")}{header(2, "عناصر الهوية", "هذا الدليل يجمع كل عناصر الهوية البصرية المستخلصة من التصاميم المرجعية، وكل شعار وزخرفة فيه ملف متجه (SVG) مرفق في الحزمة.")}<div class="body"><div class="grid" style="grid-template-columns:1fr 1fr;gap:5mm">{cells}</div></div></div>'

def tile(inner, bg, h="48mm", extra=""):
    return f'<div class="tile" style="background:{bg};height:{h};{extra}">{inner}</div>'

def page_logo(n, kind, title, desc, variants):
    tiles = "".join(f'<div>{tile(lg(kind, c, w), bg, "46mm", border)}<div class="lab">{lab}</div></div>' for lab, c, bg, w, border in variants)
    wd = HW if kind == "hajj" else RW; ht = HH if kind == "hajj" else RH
    # clear-space diagram
    s = 52
    cs = (f'<div class="card" style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%"><div style="position:relative;padding:{s * .25}mm;border:1.2px dashed #AF893B;background:#fff">'
          f'<div style="width:{s}mm">{lg(kind, "#043D1F" if kind == "rakb" else "#005045", "100%")}</div>'
          f'<div style="position:absolute;top:0;right:0;width:{s * .25}mm;height:{s * .25}mm;background:#AF893B33;border:1px solid #AF893B;font-size:8pt;text-align:center;line-height:{s * .25}mm;font-weight:700">x</div></div>'
          f'<div style="font-size:9.5pt;font-weight:600;margin-top:3mm;text-align:center">المساحة الآمنة = ربع عرض الشعار (x) من كل جهة</div></div>')
    return (f'<div class="pg">{page_bg("light")}{header(n, title, desc)}<div class="body"><div class="row" style="height:100%">'
            f'<div style="flex:1.45"><div class="grid" style="grid-template-columns:1fr 1fr;gap:5mm">{tiles}</div></div><div style="flex:1">{cs}</div></div></div></div>')

def page_names():
    wm = f'<div style="font-size:34pt;font-weight:700;line-height:1.2;text-align:center">{NAME}</div>'
    lock_stack = (f'<div class="tile dark" style="height:78mm;flex-direction:column;gap:3mm;background:linear-gradient(180deg,#005045,#022416)">{lg("hajj", "#fff", "26mm")}'
                  f'<div style="font-size:19pt;font-weight:700;color:#fff;text-align:center;line-height:1.25">تنسيقية حجاج<br><span style="color:#E2C484">طرابلس ب</span></div>{divider_svg(P["gold_lt"], 40)}{lg("rakb", "#E2C484", "30mm")}</div>')
    lock_h = (f'<div class="tile" style="height:36mm;background:#FFFCF4;border:1.2px solid #DECCA8;gap:6mm">{lg("rakb", "#043D1F", "23mm")}'
              f'<div style="font-size:20pt;font-weight:700;color:#043D1F">{NAME}</div>{lg("hajj", "#005045", "17mm")}</div>')
    lock_mini = (f'<div class="tile" style="height:36mm;background:#043D1F;gap:5mm">{lg("hajj", "#fff", "17mm")}'
                 f'<div style="font-size:17pt;font-weight:700;color:#E2C484">{NAME}</div></div>')
    return (f'<div class="pg">{page_bg("light")}{header(5, "الاسم والتوليفات", "اسم التنسيقية يُكتب دائمًا بخط IBM Plex Sans Arabic وزن Bold. الكلمة الأخيرة (طرابلس ب) تُبرز بالذهبي على الخلفيات الداكنة وبالأخضر على الفاتحة.")}'
            f'<div class="body"><div class="row" style="height:100%"><div style="flex:1">{lock_stack}<div class="lab">التوليفة العمودية (الأساسية)</div></div>'
            f'<div style="flex:1.5;display:flex;flex-direction:column;gap:5mm"><div class="card" style="padding:7mm 4mm">{wm}</div>{lock_h}<div class="lab" style="margin-top:-3mm">التوليفة الأفقية</div>{lock_mini}<div class="lab" style="margin-top:-3mm">التوليفة المختصرة</div></div></div></div></div>')

def page_colors():
    sw = ""
    for key, name, hx, role in COLORS:
        r, g, b = rgb(hx); c, m, y, kk = cmyk(hx)
        light = key in ("paper", "paper_dk", "gold_lt")
        sw += (f'<div class="card" style="padding:0;overflow:hidden"><div style="height:30mm;background:{hx};{"border-bottom:1.2px solid #DECCA8" if light else ""}"></div>'
               f'<div style="padding:3.5mm 4mm"><div style="font-size:11pt;font-weight:700">{name}</div><div class="mono" style="font-size:10pt;font-weight:700;color:#946934">{hx}</div>'
               f'<div class="mono" style="font-size:8pt;color:#5b4a2a;margin-top:1mm">RGB {r} {g} {b}<br>CMYK {c} {m} {y} {kk}</div><div style="font-size:8pt;color:#5b4a2a;margin-top:1.5mm;line-height:1.5">{role}</div></div></div>')
    grads = [("تدرج أخضر داكن", "linear-gradient(90deg,#005045,#033b2a 55%,#022416)"), ("تدرج أخضر وبرونزي", "linear-gradient(90deg,#00624f,#033e26 55%,#604624)"), ("تدرج الورق", "linear-gradient(90deg,#FAF1E4,#F0E6D6)")]
    gr = "".join(f'<div style="flex:1"><div style="height:11mm;border-radius:3mm;background:{g};border:1.2px solid #DECCA8"></div><div class="lab" style="margin-top:1.5mm">{t}</div></div>' for t, g in grads)
    return (f'<div class="pg">{page_bg("light")}{header(6, "الألوان", "ألوان القياس الفعلي من التصاميم المرجعية. قيم CMYK تقريبية رياضيًا - اطلب من المطبعة مطابقة اللون على عينة قبل الطباعة الكبيرة.")}'
            f'<div class="body"><div class="grid" style="grid-template-columns:repeat(4,1fr);gap:4.5mm">{sw}</div><div class="row" style="margin-top:5mm">{gr}</div></div></div>')

def page_type():
    specs = "".join(f'<div style="display:flex;align-items:baseline;justify-content:space-between;border-bottom:1px solid #DECCA8;padding:2.2mm 0"><span style="font-size:{s}pt;font-weight:{w}">{t}</span><span class="mono" style="font-size:8.5pt;color:#946934;font-weight:600">{lab}</span></div>'
                    for t, s, w, lab in (("تنسيقية طرابلس ب", 30, 700, "Bold 700 - العناوين الرئيسية"), ("الحج بداية جديدة", 21, 700, "Bold 700 - عناوين فرعية"), ("نص تفصيلي مريح للقراءة", 15, 600, "SemiBold 600 - النص"), ("ملاحظة أو توضيح", 12, 500, "Medium 500 - ملاحظات"), ("نص خفيف للتفاصيل", 12, 400, "Regular 400 - تفاصيل")))
    dig = '<div class="mono" style="font-size:38pt;font-weight:700;letter-spacing:2px">0123456789</div>'
    return (f'<div class="pg">{page_bg("light")}{header(7, "الخطوط", "خط الهوية: IBM Plex Sans Arabic (ملفاته في مجلد fonts). الإبراز بتلوين الكلمة بالذهبي دون تغيير الوزن.")}'
            f'<div class="body"><div class="row" style="height:100%"><div class="card" style="flex:1.5">{specs}</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:5mm"><div class="tile dark" style="height:52mm;flex-direction:column;background:#005045"><div style="font-size:78pt;font-weight:700;line-height:1;color:#E2C484">أ ب</div><div class="mono" style="font-size:12pt;color:#fff;margin-top:2mm">IBM Plex Sans Arabic</div></div>'
            f'<div class="card" style="text-align:center">{dig}<div class="lab">الأرقام بالخط نفسه (لاتينية)</div></div>'
            f'<div class="card" style="font-size:13pt;font-weight:600;line-height:1.8">مثال على إبراز: الحج <span class="gold" style="font-weight:600">بداية جديدة</span> واختبار <span class="gold">حقيقي</span></div></div></div></div></div>')

def page_ornaments():
    t1 = tile(swatch_svg(k.star8(100, 100, 80, fill=P["gold"]) + k.star8(100, 100, 36, fill=P["paper"], rot=-67.5), 200, 200), "#FFFCF4", "42mm", "border:1.2px solid #DECCA8")
    t2 = tile(f'<div style="width:90%">{divider_svg(P["gold"], 70)}</div>', "#FFFCF4", "42mm", "border:1.2px solid #DECCA8")
    t3 = tile(swatch_svg(k.ornament(60, 100, 150, P["gold"]) + k.ornament(140, 100, 150, P["gold"]), 200, 200), "#FFFCF4", "42mm", "border:1.2px solid #DECCA8")
    t4 = tile(swatch_svg(k.frame(30, 30, 140, 140, P["gold"], 3, 8, 14), 200, 200), "#043D1F", "42mm")
    badge = (f'<div style="display:flex;gap:5mm;align-items:center;justify-content:center">'
             f'<div style="width:12mm;height:12mm;border-radius:50%;background:#043D1F;color:#fff;font-weight:700;font-size:15pt;display:flex;align-items:center;justify-content:center">1</div>'
             f'<div style="width:38mm;height:12mm;border-radius:6mm;background:#946934;color:#fff;font-weight:700;font-size:12pt;display:flex;align-items:center;justify-content:center">01/12</div>'
             f'<svg viewBox="0 0 60 60" style="width:12mm"><circle cx="30" cy="30" r="28" fill="{P["gold"]}"/><path d="M16 31 L26 41 L45 20" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg></div>')
    t5 = tile(badge, "#FFFCF4", "42mm", "border:1.2px solid #DECCA8")
    t6 = tile(f'<div style="display:flex;align-items:center;gap:3mm;background:#005045;border:1.6px solid #AF893B;border-radius:12mm;padding:3.5mm 9mm;color:#fff;font-weight:700;font-size:15pt">{k.diamond(0,0,0,"#000") if False else ""}تنسيقية <span style="color:#E2C484">طرابلس ب</span></div>', "#FAF1E4", "42mm", "border:1.2px solid #DECCA8")
    labs = ["نجمة ثمانية", "فاصل المعين", "زخرفة العنوان", "الإطار الذهبي", "رقم البطاقة والأيقونات", "كبسولة العنوان"]
    ts = "".join(f"<div>{t}<div class='lab'>{l}</div></div>" for t, l in zip((t1, t2, t3, t4, t5, t6), labs))
    return f'<div class="pg">{page_bg("light")}{header(8, "الزخارف والإطارات", "عناصر مرسومة بالخطوط المتجهة (SVG / AI) ويمكن تكبيرها دون فقدان الجودة.")}<div class="body"><div class="grid" style="grid-template-columns:repeat(3,1fr);gap:5mm">{ts}</div></div></div>'

def page_patterns():
    def pat(pid, bg, h="46mm"):
        return f'<div class="tile" style="height:{h};background:{bg};border:1.2px solid #DECCA8">{swatch_svg(f"<rect width=\"400\" height=\"300\" fill=\"url(#{pid})\"/>", 400, 300, style="position:absolute;inset:0;width:100%;height:100%")}</div>'
    sky = f'<div class="tile" style="height:46mm;background:#F6EEDD;border:1.2px solid #DECCA8"><img src="_thumbs/sky.jpg" style="width:100%;height:100%;object-fit:cover;opacity:.85"></div>'
    g1 = '<div class="tile" style="height:46mm;background:linear-gradient(180deg,#00604f,#022416)"></div>'
    items = [(pat("lat-light", "#FAF1E4"), "شبكة الدوائر (فاتح)"), (pat("lat-dark", "#043D1F"), "شبكة الدوائر (داكن)"), (pat("sf-light", "#FAF1E4"), "حقل النجوم (فاتح)"),
             (pat("sf-dark", "#005045"), "حقل النجوم (داكن)"), (sky, "أفق مكة (يتلاشى إلى لون الخلفية)"), (g1, "الخلفية الخضراء المتدرجة")]
    ts = "".join(f"<div>{t}<div class='lab'>{l}</div></div>" for t, l in items)
    return f'<div class="pg">{page_bg("light")}{header(9, "الأنماط والخلفيات", "الشبكة تكون خافتة جدًا (شفافية 30-45%) وتقوى قليلًا نحو أسفل التصميم. أفق مكة صورة فوتوغرافية بلون السيبيا، تتلاشى حوافها العلوية.")}<div class="body"><div class="grid" style="grid-template-columns:repeat(3,1fr);gap:5mm">{ts}</div></div></div>'

def page_rules():
    def ex(label, inner, ok=True, bg="#FFFCF4"):
        mark = f'<span style="position:absolute;top:2mm;left:2.5mm;font-weight:700;font-size:15pt;color:{"#1d7a3a" if ok else "#b3261e"}">{"✓" if ok else "✕"}</span>'
        return f'<div><div class="tile" style="height:36mm;background:{bg};border:1.2px solid #DECCA8">{mark}{inner}</div><div class="lab">{label}</div></div>'
    L = lambda c, w="26mm", ex_="": lg("hajj", c, w, ex_)
    cells = [
        ex("استخدام صحيح على الأخضر", L("#fff"), True, "#005045"),
        ex("استخدام صحيح على الورق", L("#005045"), True, "#FAF1E4"),
        ex("لا تمطّ الشعار", L("#005045", "22mm", "transform:scaleX(1.55)"), False),
        ex("لا تغيّر لونه", L("#d6336c"), False),
        ex("لا تضعه على خلفية مزدحمة", L("#fff"), False, "repeating-linear-gradient(45deg,#7a5a2e 0 6px,#d9b970 6px 12px,#2e6b4f 12px 18px)"),
        ex("لا تدوّره", L("#005045", "26mm", "transform:rotate(25deg)"), False),
    ]
    rules = ["الحد الأدنى لحجم شعار الهيئة: 20 مم عرضًا في الطباعة (80 بكسل على الشاشة).", "اترك مساحة آمنة حول الشعار بمقدار ربع عرضه من كل جهة.", "يُكتب الاسم بخط IBM Plex Sans Arabic Bold فقط، ولا يُستبدل بخط آخر.",
             "الأخضر هو اللون الأساسي، والذهبي للإبراز والزخارف، ولا يزيد الزخرف عن ثلث مساحة التصميم.", "على الخلفيات الداكنة: الذهبي الفاتح #E2C484 بدل الذهبي #AF893B.", "الأفضل أن يتصدّر الاسم أو شعار الهيئة التصميم، ولا يتنافسان على الانتباه."]
    rl = "".join(f'<li style="margin-bottom:2.2mm">{r}</li>' for r in rules)
    return (f'<div class="pg">{page_bg("light")}{header(10, "قواعد الاستخدام")}<div class="body"><div class="row" style="height:100%"><div class="grid" style="flex:1.7;grid-template-columns:repeat(3,1fr);gap:5mm;align-content:start">{"".join(cells)}</div>'
            f'<div class="card" style="flex:1;font-size:10.5pt;font-weight:500;line-height:1.7"><ul style="margin:0;padding-right:5mm">{rl}</ul></div></div></div></div>')

def page_apps():
    im = lambda f, w: f'<img src="_thumbs/{f}.jpg" style="width:{w};border-radius:3mm;box-shadow:0 1.5mm 4mm rgba(60,40,10,.3)">'
    return (f'<div class="pg">{page_bg("light")}{header(11, "نماذج التطبيق", "تصاميم أُنجزت بهذه الهوية: بطاقات دعوية، أغلفة، صور مجموعات، إعلانات، رول أب.")}'
            f'<div class="body"><div class="row" style="align-items:flex-start;gap:5mm;height:100%">'
            f'<div style="flex:1;display:flex;flex-direction:column;gap:4mm">{im("cover1", "100%")}{im("cover2", "100%")}<div class="row" style="gap:3mm">{im("group1", "33%")}{im("group2", "33%")}{im("group3", "33%")}</div></div>'
            f'<div style="flex:.75;display:flex;flex-direction:column;gap:4mm">{im("cards1", "100%")}{im("cards6", "100%")}</div>'
            f'<div style="flex:.75;display:flex;flex-direction:column;gap:4mm">{im("ann", "100%")}{im("loc", "100%")}</div>'
            f'<div style="flex:.9;display:flex;gap:3mm;align-items:flex-start">{im("ru", "33%")}{im("ru2", "33%")}{im("ru3", "33%")}</div></div></div></div>')

def page_files():
    rows = [("Tripoli-B-Brand-Guide.pdf", "هذا الدليل"), ("Tripoli-B-Brand-Elements.ai", "كل العناصر في لوحة واحدة (متجهة، النصوص محوّلة إلى منحنيات) - يُفتح في Illustrator"),
            ("svg/", "الشعارات بكل الألوان + النجمة والفاصل والزخرفة والإطار والأنماط (SVG)"), ("png/", "الشعارات بخلفية شفافة بعرض 2000 بكسل"), ("fonts/", "خط IBM Plex Sans Arabic بأربعة أوزان"), ("Tripoli-B-Palette.ase", "لوحة ألوان Adobe (Illustrator / Photoshop / InDesign)")]
    rw = "".join(f'<div class="card" style="display:flex;justify-content:space-between;align-items:center;gap:6mm"><span class="mono" style="font-weight:700;color:#043D1F;font-size:11pt">{a}</span><span style="font-size:10.5pt;font-weight:500">{b}</span></div>' for a, b in rows)
    note = ('<div class="card" style="margin-top:5mm;font-size:10pt;font-weight:500;line-height:1.8;background:#FFF7E3"><b>ملاحظة:</b> الشعاران متجهان بالتتبع الآلي من الصور المرجعية (حواف ناعمة وقابلة للتكبير)، '
            'لكنهما ليسا الملف الأصلي الذي رسمه المصمم. للمطبوعات الدقيقة يُفضّل استبدالهما بالملفات الأصلية إن توفرت. أفق مكة صورة نقطية.</div>')
    return f'<div class="pg">{page_bg("light")}{header(12, "ملفات الحزمة")}<div class="body"><div class="grid" style="gap:3.5mm">{rw}</div>{note}</div></div>'

def build_guide():
    pages = [page_cover(), page_contents(),
             page_logo(3, "hajj", "شعار التنسيقية (شعار الهيئة)", "الشعار الأساسي للتنسيقية. الأبيض على الأخضر هو الأصل، وتتوفر نسخ بالأخضر والذهبي للخلفيات الفاتحة والداكنة.",
                       [("أبيض على أخضر الهيئة", "#fff", "#005045", "30mm", ""), ("أخضر على الورق", "#005045", "#FAF1E4", "30mm", "border:1.2px solid #DECCA8"),
                        ("ذهبي على الأخضر العميق", "#AF893B", "#022416", "30mm", ""), ("ذهبي فاتح على الأخضر", "#E2C484", "#043D1F", "30mm", "")]),
             page_logo(4, "rakb", "شعار ركب الأبرار", "الخط الذهبي لركب الأبرار. يوضع في التذييل أو أسفل التصميم، ولا ينافس الاسم أو شعار الهيئة.",
                       [("أخضر على الورق", "#043D1F", "#FAF1E4", "46mm", "border:1.2px solid #DECCA8"), ("ذهبي على الورق", "#AF893B", "#FFFCF4", "46mm", "border:1.2px solid #DECCA8"),
                        ("ذهبي فاتح على الأخضر", "#E2C484", "#043D1F", "46mm", ""), ("أبيض على أخضر الهيئة", "#fff", "#005045", "46mm", "")]),
             page_names(), page_colors(), page_type(), page_ornaments(), page_patterns(), page_rules(), page_apps(), page_files()]
    html = f'<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>دليل الهوية البصرية - {NAME}</title><style>{CSS}</style><body>{SYM}{"".join(pages)}</body></html>'
    write("_guide.html", html)
    render.to_pdf("_guide.html", "Tripoli-B-Brand-Guide.pdf", w_mm=297, h_mm=210)

# ============================================================== 6) the .ai elements sheet (one artboard, outlined)
def build_ai():
    W, H = 2000, 1580
    parts = [f'<rect width="{W}" height="{H}" fill="{P["paper"]}"/>']
    defs = k.lattice_pattern("lat", P["gold"], .35, 60, 1.6)
    def txt(x, y, s, size=34, fill=P["green"], w=700, anchor="right"):
        a = {"right": "start", "left": "end", "middle": "middle", "end": "start"}[anchor]      # RTL: 'start' is the right edge
        return f'<text x="{x}" y="{y}" font-family="IBM Plex Sans Arabic" font-weight="{w}" font-size="{size}" fill="{fill}" text-anchor="{a}" direction="rtl">{s}</text>'
    def lgp(name, fill, x, y, width):
        g, w, h = k.logo_group(name, fill, x, y, width); return g
    parts.append(f'<rect width="{W}" height="150" fill="{P["green"]}"/>' + txt(W - 70, 100, f"عناصر الهوية البصرية - {NAME}", 54, P["gold_lt"], 700, "right") + lgp("hajj_logo_white", "#fff", 70, 25, 100))
    # logos row
    y0 = 200
    parts.append(txt(W - 70, y0, "الشعارات", 34, P["bronze"]))
    xs = 70
    boxes = [("hajj_logo_white", "#FFFFFF", P["teal"], 300), ("hajj_logo_white", P["teal"], P["paper_dk"], 300), ("hajj_logo_white", P["gold_lt"], P["deep"], 300), ("rakb_gold", P["gold"], P["cream"], 340), ("rakb_gold", P["green"], P["paper_dk"], 340), ("rakb_gold", P["gold_lt"], P["green"], 340)]
    x = 70
    for name, fill, bg, w in boxes:
        parts.append(f'<rect x="{x}" y="{y0 + 30}" width="{w + 40}" height="{w + 40}" rx="22" fill="{bg}"/>')
        g, ww, hh = k.logo_group(name, fill, x + 20, 0, w); parts.append(f'<g transform="translate(0,{y0 + 50 + (w - hh) / 2})">{g}</g>')
        x += w + 70
        if x > W - 340: break
    # wordmark + lockups
    y1 = 700
    parts.append(txt(W - 70, y1, "الاسم والتوليفات", 34, P["bronze"]))
    parts.append(f'<rect x="70" y="{y1 + 30}" width="900" height="300" rx="22" fill="{P["green"]}"/>' + txt(520, y1 + 140, "تنسيقية حجاج", 90, "#fff", 700, "middle") + txt(520, y1 + 270, "طرابلس ب", 120, P["gold_lt"], 700, "middle"))
    parts.append(f'<rect x="1000" y="{y1 + 30}" width="930" height="140" rx="22" fill="{P["cream"]}" stroke="#DECCA8" stroke-width="2"/>' + lgp("rakb_gold", P["green"], 1020, y1 + 45, 120) + txt(1480, y1 + 120, NAME, 62, P["green"], 700, "middle") + lgp("hajj_logo_white", P["teal"], 1800, y1 + 40, 100))
    parts.append(f'<rect x="1000" y="{y1 + 190}" width="930" height="140" rx="22" fill="{P["teal"]}"/>' + lgp("hajj_logo_white", "#fff", 1030, y1 + 205, 100) + txt(1900, y1 + 290, NAME, 62, P["gold_lt"], 700, "right"))
    # palette
    y2 = 1090
    parts.append(txt(W - 70, y2, "الألوان", 34, P["bronze"]))
    for i, (key, name, hx, role) in enumerate(COLORS):
        x = 70 + i * 238
        parts.append(f'<rect x="{x}" y="{y2 + 25}" width="215" height="130" rx="18" fill="{hx}" stroke="#DECCA8" stroke-width="2"/>' + txt(x + 215, y2 + 195, name, 24, P["green"], 700) + f'<text x="{x + 215}" y="{y2 + 228}" font-family="IBM Plex Sans Arabic" font-weight="600" font-size="22" fill="{P["bronze"]}" text-anchor="end">{hx}</text>')
    # ornaments
    y3 = 1410
    parts.append(txt(W - 70, y3, "الزخارف", 34, P["bronze"]) )
    parts.append(k.star8(1700, y3 + 60, 55, fill=P["gold"]) + k.star8(1700, y3 + 60, 25, fill=P["paper"], rot=-67.5))
    parts.append(k.star8(1560, y3 + 60, 55, stroke=P["gold"], sw=4))
    parts.append(k.divider(1280, y3 + 60, 150, 26, P["gold"], 3, 12))
    parts.append(k.ornament(1000, y3 + 60, 100, P["gold"]) + k.ornament(1060, y3 + 60, 100, P["gold"]))
    parts.append(f'<rect x="760" y="{y3 + 5}" width="150" height="120" fill="{P["green"]}" rx="10"/>' + k.frame(775, y3 + 20, 120, 90, P["gold"], 2.5, 6, 11))
    parts.append(f'<rect x="530" y="{y3 + 5}" width="180" height="120" fill="url(#lat)" stroke="#DECCA8" rx="10"/>')
    parts.append(f'<circle cx="440" cy="{y3 + 60}" r="30" fill="{P["green"]}"/>' + txt(440, y3 + 72, "1", 36, "#fff", 700, "middle"))
    parts.append(f'<rect x="330" y="{y3 + 40}" width="70" height="40" rx="20" fill="{P["bronze"]}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" style="display:block"><defs>{defs}</defs>{"".join(parts)}</svg>'
    a_svg, a_pdf = outline_svg_to_pdf(svg, W, H, "x")
    # rebuild a PDF from the outlined SVG (glyphs are now plain paths)
    render.to_pdf("_tmp_outline/b.html", "Tripoli-B-Brand-Elements.ai", w_px=W, h_px=H)
    write("svg/Brand-Elements-sheet-outlined.svg", open(a_svg, encoding="utf-8").read())

if __name__ == "__main__":
    os.makedirs("svg", exist_ok=True); os.makedirs("png", exist_ok=True)
    build_svgs(); print("svgs ok", flush=True)
    build_pngs(); print("pngs ok", flush=True)
    build_ase("Tripoli-B-Palette.ase"); print("ase ok", flush=True)
    build_guide(); print("guide ok", flush=True)
    build_ai(); print("ai ok", flush=True)
    shutil.rmtree("_tmp_outline", ignore_errors=True)
    for f in ("_guide.html",):
        pass

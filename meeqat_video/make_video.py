import os, sys, json, wave, subprocess, time, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright
from rec_core import *
from script import LINES

DRY = os.environ.get('DRY') == '1'
FROM = os.environ.get('FROM') or None          # render only from this beat key (earlier beats run dry)
UNTIL = os.environ.get('UNTIL') or None        # stop after this beat key
OUT = os.environ.get('OUT', 'work/video_silent.mp4')
DUR = json.load(open('tts/durations.json'))
PORT = int(os.environ.get('PORT', '8765'))
URL = f'http://127.0.0.1:{PORT}/index.html'
PASSPORT = os.path.abspath('assets/sample_passport.jpg')
SITE = 'https://tripoli-b.ly/?view=public-form'
ID_OK, ID_BAD, ID_COMP = '119900000001', '119900000999', '219900000002'
AR = str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')

# ------------------------------------------------------------------ cards (brand = the component's own palette)
def glow_bg(top=True):
    img = Image.new('RGB', (OW, OH), STONE900); a = np.zeros((OH, OW, 3), np.float32)
    yy = np.linspace(0, 1, OH)[:, None]; base = np.array(STONE900)[None, None, :] * (1 - yy[..., None]) + np.array((12, 10, 9))[None, None, :] * yy[..., None]
    a = np.broadcast_to(base, (OH, OW, 3)).copy()
    Y, X = np.mgrid[0:OH, 0:OW]
    for (cx, cy, r, col, k) in ((OW * .5, 260, 760, EMERALD, .26), (140, 1500, 600, TEAL, .16), (OW * .9, 980, 420, EMERALD_L, .07)):
        m = np.clip(1 - np.hypot(X - cx, Y - cy) / r, 0, 1) ** 2 * k
        a = a * (1 - m[..., None]) + np.array(col)[None, None, :] * m[..., None]
    return Image.fromarray(a.astype('uint8'))
BG = glow_bg()
def pill(d, cx, y, text, fill, fg, f, padx=44, h=84, outline=None):
    w = tw(f, text) + padx * 2; d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + h), h / 2, fill=fill, outline=outline, width=2)
    d.text((cx, y + h / 2), text, font=f, fill=fg, anchor='mm', direction='rtl', language='ar')
def centered(d, lines, cx, y, f, fill, lh):
    for ln in lines: d.text((cx, y), ln, font=f, fill=fill, anchor='mm', direction='rtl', language='ar'); y += lh
    return y

def logo_img(sz):
    im = Image.open('assets/coordination_logo.png').convert('RGB').resize((sz, sz), Image.LANCZOS)
    mk = Image.new('L', (sz, sz), 0); ImageDraw.Draw(mk).rounded_rectangle((0, 0, sz - 1, sz - 1), sz // 7, fill=255)
    o = Image.new('RGBA', (sz, sz)); o.paste(im, (0, 0)); o.putalpha(mk); return o
def intro_card():
    img = BG.copy().convert('RGBA'); d = ImageDraw.Draw(img, 'RGBA'); cx = OW / 2
    sh = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((cx - 280, 300, cx + 280, 860), 80, fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    img.alpha_composite(logo_img(560), (int(cx - 280), 260))
    d.text((cx, 960), 'منظومة ميقات الإلكترونية للحج', font=font(46, 600), fill=(168, 162, 158), anchor='mm', direction='rtl', language='ar')
    t = 'دليل الحاج والمرافق لتعبئة الاستبيان وتحديث البيانات'
    f = font(78, 700); centered(d, wrap(f, t, 900), cx, 1080, f, WHITE, 116)
    pill(d, cx, 1330, 'تنسيقية حجاج طرابلس (ب)', (16, 185, 129, 40), (110, 231, 183), font(42, 700), outline=(16, 185, 129, 110))
    return img.convert('RGB')
def light_card(url_text='', n=None, cursor_on=True):
    img = Image.new('RGB', (OW, OH), (245, 245, 244)); d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle((70, 520, OW - 70, 640), 60, fill=WHITE, outline=(214, 211, 209), width=3)
    d.ellipse((108, 556, 152, 600), fill=(5, 150, 105))        # lock-ish dot
    d.rounded_rectangle((120, 576, 140, 592), 3, fill=WHITE); d.arc((121, 561, 139, 579), 180, 360, fill=WHITE, width=3)
    f = ImageFont.truetype(FONT_DIR + 'Plex-latin-600.ttf', 42)
    txt = (url_text if n is None else url_text[:n]) + ('│' if cursor_on else '')
    d.text((180, 580), txt, font=f, fill=STONE900, anchor='lm')
    return img
def outro_card():
    img = BG.copy(); d = ImageDraw.Draw(img, 'RGBA'); cx = OW / 2
    img = img.convert('RGBA'); img.alpha_composite(logo_img(300), (int(cx - 150), 130)); d = ImageDraw.Draw(img, 'RGBA')
    f = font(62, 700); d.text((cx, 500), 'أنهيت تعبئة الاستبيان؟', font=f, fill=(110, 231, 183), anchor='mm', direction='rtl', language='ar')
    items = ['ادخل بالرقم الوطني', 'راجع البيانات الشخصية والتواصل', 'أجب عن الإفصاح الصحي بصدق', 'ارفع صورة الجواز الواضحة', 'تأكد من اكتمال البيانات 100%', 'احفظ وأرسل للاعتماد']
    y = 600; fi = font(46, 600)
    for i, t in enumerate(items):
        d.ellipse((OW - 190, y - 4, OW - 190 + 62, y + 58), fill=(16, 185, 129, 60), outline=(16, 185, 129, 200), width=3)
        d.text((OW - 159, y + 27), str(i + 1).translate(AR), font=font(34, 700), fill=(110, 231, 183), anchor='mm', direction='rtl', language='ar')
        d.text((OW - 215, y + 27), t, font=fi, fill=WHITE, anchor='rm', direction='rtl', language='ar'); y += 96
    pill(d, cx, 1190, 'تنسيقية حجاج طرابلس (ب)', (16, 185, 129, 40), (110, 231, 183), font(40, 700), h=78, outline=(16, 185, 129, 110))
    fu = ImageFont.truetype(FONT_DIR + 'Plex-latin-600.ttf', 40); d.text((cx, 1300), SITE, font=fu, fill=(214, 211, 209), anchor='mm')
    return img.convert('RGB')

# ------------------------------------------------------------------ helpers on the real DOM
def Q(pg, prefix):      # question block by its numbered title
    return pg.locator(f'xpath=//span[starts-with(normalize-space(),"{prefix}")]/ancestor::div[.//button[normalize-space()="نعم"]][1]').first
def block_of(pg, text):  return pg.get_by_text(text, exact=False).first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl") or contains(@class,"rounded-xl")][1]')
def section(pg, title):  return pg.get_by_text(title, exact=True).first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl") or contains(@class,"rounded-3xl")][1]')

def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT), '--directory', 'app'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    os.makedirs('work', exist_ok=True)
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args=['--no-sandbox'])
            ctx = b.new_context(viewport={'width': VW, 'height': VH}, device_scale_factor=DSF, locale='ar', has_touch=False)
            pg = ctx.new_page(); pg.goto(URL); pg.add_style_tag(content='#root > div{padding-bottom:640px !important}'); pg.evaluate('window.__netDelay=250; window.__ocrDelay=330'); pg.wait_for_timeout(900)
            R = Recorder(pg, OUT, dry=DRY, render_from=FROM, durations=DUR)
            if FROM is None and not DRY: R.started = True
            try: run(R, pg)
            except Exception:
                pg.screenshot(path='work/fail.png'); print('FAIL t=%.1f' % R.t); raise
            R.finish(); json.dump({'marks': R.beat_marks, 'frames': R.frame_no}, open(OUT + '.marks.json', 'w'))
            print('frames', R.frame_no, 'seconds', round(R.t, 1)); b.close()
    finally:
        srv.terminate()

class Stop(Exception): pass
def run(R, pg):
    def B(key, gap=0.35):
        return R.beat(key, gap)
    def end(key):
        if UNTIL == key: raise Stop()
    try:
        R.badge = False
        # ============================== 1 intro
        R.card = intro_card(); R.card_alpha = 1; R.cur = None
        with B('i1'): R.card_hold(DUR['i1'] - 0.1)
        with B('i2'): R.card_hold(DUR['i2'] - 0.1)
        end('i2')
        # ============================== 2 access
        R.step = (1, 11, 'الدخول إلى الاستبيان')
        st = {'n': 0}
        R.card = lambda: light_card(SITE, st['n'], int(R.t * 2) % 2 == 0)
        R.badge = True
        with B('a1') as bt:
            R.card_alpha = 0; R.card_in(R.card, 0.5)
            for i in range(1, len(SITE) + 1):
                st['n'] = i; R.card_hold(0.045)
            R.note('ثم اضغط Enter لفتح الرابط', 1.6, 1000); R.card_hold(0.9); R.card_out(0.7)
        with B('a2'):
            R.hold(0.4)
            R.focus('h1', 0.9, fy=0.34, maxz=1.25); R.frame_on('h1', 2.2, 'استكمال وتحديث بيانات الحاج'); R.hold(2.2)
            R.unfocus(0.7); R.clear_frames()
            R.hold(1.5)
        end('a2')
        # ============================== 3 search
        R.step = (2, 11, 'البحث عن سجل الحاج')
        inp = pg.locator('input[inputmode=numeric]').first
        with B('s1'):
            R.focus('input[inputmode=numeric]', 0.8, fy=0.42); R.frame_on('input[inputmode=numeric]', 3.0, 'الرقم الوطني (١٢ رقمًا)')
            R.typing(inp, ID_BAD, cps=9)
            R.clear_frames(); R.unfocus(0.5); R.click('button[type=submit]', 0.7, 0.2)
        with B('s2'):
            R.hold(0.9, live=True)
            R.focus(pg.locator('text=لم يتم العثور على حاج').locator('xpath=ancestor::div[contains(@class,"rounded-xl")][1]'), 0.8, fy=0.45)
            R.frame_on(pg.locator('text=لم يتم العثور على حاج').locator('xpath=ancestor::div[contains(@class,"rounded-xl")][1]'), 3.0, 'تحقق من الرقم')
            R.hold(3.0); R.clear_frames()
        with B('s3'):
            R.unfocus(0.4)
            R.click('button:has(svg.lucide-x)', 0.6, 0.15)               # the clear (X) button inside the input
            R.typing(inp, ID_OK, cps=11)
            R.click('button[type=submit]', 0.5, 0.1); pg.locator('h2').first.wait_for(timeout=15000); R.hold(0.8, live=True); R.scroll_to(0, 0.1)
            R.hold(0.3); ban = pg.locator('h2').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.focus(ban, 0.8, fy=0.30); R.frame_on(ban, 2.2, 'تأكد أن الاسم يخص الحاج')
            R.hold(0.5); R.cursor_to(pg.get_by_text('تغيير الحاج').first, 0.7); R.frame_on(pg.get_by_text('تغيير الحاج').first, 1.6, 'للبحث من جديد'); R.hold(1.6); R.clear_frames()
        end('s3')
        # ============================== 4 personal
        R.step = (3, 11, 'البيانات الشخصية')
        sec = pg.locator('#section-personal')
        with B('p1'):
            R.unfocus(0.4); R.cursor = None; R.scroll_el(sec, 0.9, at=0.22)
            R.focus(sec, 0.8, fy=0.45, maxz=1.35)
            for lab in ('الاسم الرباعي', 'الرقم الوطني', 'رقم القرعة', 'تاريخ الميلاد'):
                el = pg.locator('#section-personal').get_by_text(lab, exact=True).first.locator('xpath=..')
                R.frame_on(el, 1.65, lab); R.hold(1.7)
            R.clear_frames()
        with B('p2'):
            R.frame_on(sec, 3.6, 'للقراءة فقط — من منظومة القرعة'); R.unfocus(0.9); R.hold(2.6); R.clear_frames()
        end('p2')
        # ============================== 5 contact
        R.step = (4, 11, 'التواصل والطوارئ')
        con = pg.locator('#section-contact')
        phone = con.locator('input[type=tel]').nth(0); wa2 = con.locator('input[type=tel]').nth(1); emph = con.locator('input[type=tel]').nth(2)
        with B('c1'):
            R.scroll_el(con, 1.0, at=0.28)
            R.focus(phone, 0.8, fy=0.36, maxz=1.45); R.frame_on(phone, 3.0, 'رقم الهاتف الأساسي')
            R.typing(phone, '0912345678', cps=8); R.hold(1.0); R.clear_frames()
        with B('c2'):
            blk = pg.get_by_text('هل هذا الرقم الأساسي مرتبط بحساب واتساب؟').first.locator('xpath=ancestor::div[.//button][1]')
            R.focus(blk, 0.9, fy=0.40, maxz=1.35); R.frame_on(blk, 6.5, 'هل يستخدم واتساب؟'); R.hold(1.3)
            R.click(pg.get_by_role('button', name='نعم، الرقم يستخدم واتساب'), 0.8, 0.3); R.hold(1.5); R.clear_frames()
        with B('c3'):
            R.focus(wa2, 0.8, fy=0.38, maxz=1.45); R.frame_on(wa2, 4.5, 'رقم واتساب إضافي')
            R.typing(wa2, '0925550123', cps=8); R.hold(1.0); R.clear_frames()
        with B('c4'):
            off = con.locator('select').first
            R.unfocus(0.4); R.scroll_el(off, 0.7, at=0.30)
            R.cursor_to(off, 0.6); R.ripple = dict(t0=R.t, pt=R.cursor['pt']); R.emit(4)
            off.select_option(index=1); R.hold(0.4, live=True); R.frame_on(off, 1.4, 'المكتب')
            R.hold(1.0); R.clear_frames()
            R.typing(emph, '0945550188', cps=30)
            nm = pg.get_by_placeholder('مثال: محمد أحمد (الابن)'); R.typing(nm, 'محمد عبدالله (الابن)', cps=30)
            rl = pg.get_by_placeholder('مثال: ابن، زوج، أخ، أخت...'); R.typing(rl, 'ابن', cps=8)
        end('c4')
        # ============================== 6 companion
        R.step = (5, 11, 'ربط المرافق')
        comp = pg.get_by_text('ربط المرافق (المحرم / الزوجة)').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl") or contains(@class,"rounded-3xl")][1]')
        with B('m1'):
            R.cursor = None; R.scroll_el(comp, 1.1, at=0.18, extra=0)
            R.focus(comp, 0.9, fy=0.46, maxz=1.3); R.frame_on(comp, 3.6, 'ربط المرافق')
            ci = pg.get_by_placeholder('أدخل الرقم الوطني للمرافق...')
            R.typing(ci, ID_COMP, cps=9); R.click(pg.locator('button:has(span:text("بحث وربط"))').first, 0.6, 0.2); pg.get_by_text('تم ربط المرافق بنجاح').first.wait_for(timeout=15000)
        with B('m2'):
            R.hold(1.0, live=True); R.clear_frames()
            R.frame_on(comp, 4.2, 'سجل المرافق منفصل عن سجلك'); R.hold(4.2)
            R.clear_frames()
        end('m2')
        # ============================== 7 health
        R.step = (6, 11, 'الإفصاح الصحي')
        hs = pg.locator('#section-health')
        with B('h1'):
            R.unfocus(0.5); R.cursor = None; R.scroll_el(hs, 1.1, at=0.10)
            R.focus(pg.get_by_text('استمارة الإفصاح الصحي الإلكتروني').first, 0.8, fy=0.30, maxz=1.35)
            R.frame_on(pg.get_by_text('استمارة الإفصاح الصحي الإلكتروني').first, 3.0, 'الإفصاح الصحي'); R.hold(3.0); R.clear_frames()
        with B('h2'):
            q1 = Q(pg, '1.'); R.scroll_el(q1, 0.7, at=0.20); R.focus(q1, 0.6, fy=0.35, maxz=1.35)
            R.click(q1.get_by_role('button', name='نعم', exact=True), 0.6, 0.5)
            for dz in ('السكري', 'ارتفاع ضغط الدم'):
                R.click(pg.get_by_text(dz, exact=True).first, 0.55, 0.25)
            R.unfocus(0.3)
            custom = pg.get_by_placeholder('إضافة مرض مزمن آخر غير مدرج...'); R.scroll_el(custom, 0.6, at=0.5)
            R.typing(custom, 'ربو موسمي', cps=10); R.click(pg.get_by_role('button', name='إضافة'), 0.5, 0.4)
        with B('h3'):
            q2 = Q(pg, '2.') if False else pg.get_by_text('2. تقييم القدرة الحركية').first
            R.scroll_el(q2, 0.7, at=0.14); R.focus(pg.get_by_text('يمشي مسافات قصيرة فقط').first, 0.7, fy=0.40, maxz=1.15)
            R.frame_on(pg.get_by_text('2. تقييم القدرة الحركية').first, 3.0, 'القدرة الحركية')
            R.click(pg.get_by_text('يمشي مسافات قصيرة فقط').first, 0.7, 0.5); R.hold(1.5); R.clear_frames()
        with B('h4'):
            q3 = Q(pg, '3.'); R.scroll_el(q3, 0.8, at=0.20); R.focus(q3, 0.6, fy=0.35, maxz=1.3)
            R.click(q3.get_by_role('button', name='نعم', exact=True), 0.5, 0.4)
            R.typing(pg.get_by_placeholder('مثال: جراحة قسطرة قلبية في شهر يناير 2026، استئصال مرارة...'), 'جراحة مرارة قبل ثلاثة أشهر', cps=14)
            q4 = Q(pg, '4.'); R.scroll_el(q4, 0.7, at=0.20)
            R.click(q4.get_by_role('button', name='نعم', exact=True), 0.5, 0.3)
            R.typing(pg.get_by_placeholder('مثال: حساسية شديدة من البنسلين ومشتقاته...'), 'حساسية من البنسلين', cps=14)
            q5 = Q(pg, '5.'); R.scroll_el(q5, 0.7, at=0.25)
            R.click(q5.get_by_role('button', name='لا', exact=True), 0.5, 0.5); R.clear_frames()
        with B('h5'):
            med = pg.get_by_placeholder('أدخل أسماء الأدوية بوضوح (مثال: إنسولين لانتوس 20 وحدة، كونكور 5 ملغ، جلوكوفاج 500)...')
            R.scroll_el(med, 0.8, at=0.30); R.focus(med, 0.6, fy=0.40, maxz=1.3)
            R.typing(med, 'ميتفورمين 500 ملغ مرتين يوميًا', cps=14)
            bt_sel = pg.locator('select:has(option:text("غير محدد"))').first
            R.cursor_to(bt_sel, 0.6); R.ripple = dict(t0=R.t, pt=R.cursor['pt']); R.emit(4); bt_sel.select_option('O+'); R.hold(0.5, live=True)
            R.frame_on(bt_sel, 1.5, 'فصيلة الدم'); R.hold(1.5); R.clear_frames()
        with B('h6'):
            lg = pg.get_by_text('الصيغة القانونية المعتمدة للإقرار الصحي').first.locator('xpath=ancestor::div[contains(@class,"rounded-xl") or contains(@class,"rounded-2xl")][1]')
            R.unfocus(0.3); R.scroll_el(lg, 0.8, at=0.20); R.focus(lg, 0.7, fy=0.42, maxz=1.25)
            R.frame_on(lg, 8.0, 'الإقرار القانوني'); R.hold(9.0); R.clear_frames()
        end('h6')
        # ============================== 8 passport
        R.step = (7, 11, 'جواز السفر والمستندات')
        ps = pg.locator('#section-passport')
        with B('d1'):
            R.unfocus(0.4); R.scroll_el(ps, 1.0, at=0.18)
            up = pg.get_by_text('التقاط صورة بالجوال أو اختيار ملف').first.locator('xpath=ancestor::label[1]|ancestor::div[contains(@class,"border-dashed")][1]').first
            R.focus(up, 0.8, fy=0.40, maxz=1.3); R.frame_on(up, 3.0, 'رفع صورة الجواز')
            R.cursor_to(up, 0.7); R.ripple = dict(t0=R.t, pt=R.cursor['pt']); R.emit(5)
            R.note('اختيار الملف من الجهاز (صورة تجريبية)', 2.4, 1050)
            pg.locator('input[type=file]').first.set_input_files(PASSPORT); R.clear_frames(); R.hold(2.0, live=True)
        with B('d2'):
            R.hold(3.8, live=True)                                 # OCR progress runs live
            mod = pg.get_by_text('تمت قراءة بيانات الجواز والتحقق منها').first
            mod.wait_for(timeout=15000)
            mdl = mod.locator('xpath=ancestor::div[contains(@class,"rounded-2xl") or contains(@class,"rounded-3xl")][1]')
            R.unfocus(0.3); R.hold(1.2, live=True)
            okb = pg.get_by_role('button', name='تأكيد البيانات والمتابعة')
            R.frame_on(okb, 2.2, 'راجع ثم أكّد'); R.hold(1.6); R.click(okb, 0.7, 0.3); R.clear_frames()
        with B('d3'):
            R.scroll_el(pg.get_by_text('تم إرفاق صورة الجواز بنجاح').first, 0.8, at=0.30)
            okc = pg.get_by_text('تم إرفاق صورة الجواز بنجاح').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl") or contains(@class,"rounded-xl")][1]')
            R.focus(okc, 0.7, fy=0.40, maxz=1.3); R.frame_on(okc, 3.0, 'تم الإرفاق بنجاح'); R.hold(3.0); R.clear_frames()
            for nm_ in ('معاينة مكبرة', 'تغيير الصورة', 'حذف'):
                el = pg.get_by_text(nm_, exact=True).first; R.frame_on(el, 1.2, nm_); R.hold(1.3)
            R.clear_frames()
        with B('d4'):
            ex = ps.locator('input[type=date]').first
            R.scroll_el(ex, 0.6, at=0.35); R.focus(ex, 0.6, fy=0.38, maxz=1.4)
            R.note('مثال: تاريخ جواز قريب الانتهاء', 2.6, 1080)
            ex.fill('2026-05-01'); R.hold(0.5, live=True)
            warn = pg.get_by_text('جواز السفر غير مطابق لشروط القبول').first
            wb = warn.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.focus(wb, 0.7, fy=0.40, maxz=1.25); R.frame_on(wb, 3.5, 'تنبيه — لن يُقبل الإرسال'); R.hold(3.8)
            R.clear_frames(); ex.fill('2031-05-18'); R.hold(1.2, live=True)
        end('d4')
        # ============================== 9 review
        R.step = (8, 11, 'مؤشر اكتمال البيانات')
        with B('r1'):
            R.unfocus(0.4); R.scroll_to(0, 1.4)
            ind = pg.get_by_text('مؤشر اكتمال البيانات والمتطلبات').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.focus(ind, 0.8, fy=0.34, maxz=1.35); R.frame_on(ind, 3.2, 'مؤشر الاكتمال'); R.hold(3.0); R.clear_frames()
        with B('r2'):
            pill_ = pg.get_by_text('مؤشر اكتمال البيانات والمتطلبات').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.frame_on(pill_.locator('div.rounded-full').first, 2.2, 'النسبة'); R.hold(2.4); R.clear_frames()
            R.click(pg.get_by_text('عرض قائمة النواقص').first, 0.7, 0.3)
            R.focus(pill_, 0.7, fy=0.38, maxz=1.2); R.hold(3.5)
        with B('r3'):
            chip = pg.get_by_role('button', name='المدينة').first
            R.click(chip, 0.6, 0.2); R.hold(1.0, live=True)
            R.typing(pg.get_by_placeholder('مثال: طرابلس'), 'طرابلس', cps=8)
            R.typing(pg.get_by_placeholder('مثال: حي الأندلس / فشلوم / السراج'), 'الهضبة', cps=8)
            R.unfocus(0.3); R.cursor = None; R.scroll_to(0, 1.2)
            R.focus(ind, 0.8, fy=0.34, maxz=1.35); R.frame_on(ind, 2.6, 'اكتمال ١٠٠٪'); R.hold(2.6); R.clear_frames()
        end('r3')
        # ============================== 10 submit
        R.step = (9, 11, 'حفظ وإرسال البيانات')
        sub = pg.get_by_role('button', name='حفظ وإرسال البيانات للاعتماد')
        with B('x1'):
            R.unfocus(0.5); R.cursor = None
            R.frame_on(sub, 3.6, 'حفظ وإرسال البيانات للاعتماد'); R.focus(sub, 0.8, fy=0.60, maxz=1.35); R.hold(2.0)
            R.click(sub, 0.8, 0.3); R.clear_frames()
        with B('x2'):
            R.hold(0.6, live=True)
            R.unfocus(0.3); okx = pg.get_by_role('button', name='تأكيد الإرسال').first
            R.frame_on(pg.get_by_text('نسبة اكتمال النموذج:').first.locator('xpath=ancestor::div[1]'), 3.0, 'نسبة الاكتمال'); R.hold(3.2)
            R.clear_frames(); R.frame_on(okx, 3.2, 'تأكيد الإرسال'); R.hold(1.6); R.click(okx, 0.8, 0.3)
        pg.get_by_text('تم حفظ البيانات بنجاح!').first.wait_for(timeout=15000)
        with B('x3'):
            R.hold(1.3, live=True); R.clear_frames(); R.scroll_to(0, 0.8)
            sm = pg.get_by_text('تم حفظ البيانات بنجاح!').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.note('رسالة النظام بعد الإرسال (بيئة اختبار)', 2.4, 1080)
            R.focus(sm, 0.8, fy=0.36, maxz=1.3); R.frame_on(sm, 3.2, 'تم الحفظ والإرسال'); R.hold(3.0); R.clear_frames()
        end('x3')
        # ============================== 11 edit before verification
        R.step = (10, 11, 'التعديل قبل تأكيد المطابقة')
        with B('u1'):
            R.unfocus(0.4); R.click(pg.get_by_text('تغيير الحاج').first, 0.7, 0.5)
            R.focus('input[inputmode=numeric]', 0.6, fy=0.42); R.typing(inp, ID_OK, cps=14); R.unfocus(0.3)
            R.click('button[type=submit]', 0.5, 0.1); pg.locator('h2').first.wait_for(timeout=15000); R.hold(0.8, live=True)
        with B('u2'):
            bn = pg.get_by_text('بياناتك محفوظة ومُرسلة للاعتماد').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.scroll_el(bn, 0.7, at=0.25); R.focus(bn, 0.7, fy=0.38, maxz=1.35); R.frame_on(bn, 4.5, 'قابلة للتعديل حتى تأكيد المطابقة'); R.hold(4.8); R.clear_frames()
        with B('u3'):
            con = pg.locator('#section-contact'); phone = con.locator('input[type=tel]').nth(0)
            R.unfocus(0.3); R.scroll_el(con, 0.8, at=0.28); R.focus(phone, 0.6, fy=0.36, maxz=1.35)
            R.click(phone, 0.5, 0.1); phone.press('Control+a'); R.typing(phone, '0912345699', cps=10, click=False)
            wn = pg.get_by_text('قمت بتعديل رقم الهاتف الأساسي').first
            R.focus(wn, 0.7, fy=0.45, maxz=1.35); R.frame_on(wn, 3.0, 'أعد تأكيد واتساب'); R.hold(2.6); R.clear_frames()
            R.click(pg.get_by_role('button', name='نعم، الرقم يستخدم واتساب'), 0.6, 0.4)
        # silent: re-submit
        R.unfocus(0.4); R.note('إعادة الإرسال بعد التعديل', 2.0, 1080)
        R.click(sub, 0.8, 0.3); R.hold(0.6, live=True); R.click(pg.get_by_role('button', name='تأكيد الإرسال').first, 0.7, 0.3); pg.get_by_text('تم حفظ البيانات بنجاح!').first.wait_for(timeout=15000); R.hold(1.0, live=True)
        R.scroll_to(0, 0.8); R.hold(1.0)
        end('u3')
        # ============================== 12 locked
        R.step = (11, 11, 'بعد تأكيد المطابقة')
        with B('k1'):
            R.click(pg.get_by_text('تغيير الحاج').first, 0.7, 0.4)
            R.note('المنسق الإداري يؤكد المطابقة (محاكاة)', 2.6, 1080)
            pg.evaluate("window.__db['%s'].docStatus='VERIFIED'" % ID_OK); R.hold(1.8)
            R.typing(inp, ID_OK, cps=18); R.click('button[type=submit]', 0.5, 0.1); pg.locator('h2').first.wait_for(timeout=15000); R.hold(0.8, live=True)
            lk = pg.get_by_text('تم تأكيد المطابقة والاعتماد رسميًا').first.locator('xpath=ancestor::div[contains(@class,"rounded-2xl")][1]')
            R.scroll_el(lk, 0.7, at=0.25); R.focus(lk, 0.7, fy=0.38, maxz=1.3); R.frame_on(lk, 3.2, 'معتمد رسميًا — للقراءة فقط'); R.hold(3.0); R.clear_frames()
        with B('k2'):
            R.unfocus(0.4); R.scroll_el(pg.locator('#section-contact'), 1.1, at=0.28)
            R.frame_on(pg.locator('#section-contact').locator('input[type=tel]').first, 3.4, 'الحقول مقفلة'); R.hold(3.4); R.clear_frames()
            btn = pg.get_by_text('البحث عن حاج آخر').first; R.scroll_el(btn, 1.2, at=0.4)
            R.frame_on(btn, 3.0, 'البحث عن حاج آخر'); R.hold(3.0); R.clear_frames()
        end('k2')
        # ============================== 13 outro
        R.badge = False
        R.card = outro_card(); R.card_alpha = 0
        with B('z1'): R.card_in(R.card, 0.8); R.card_hold(DUR['z1'] - 0.9)
        with B('z2', gap=1.2): R.card_hold(DUR['z2'])
    except Stop:
        pass

if __name__ == '__main__': main()

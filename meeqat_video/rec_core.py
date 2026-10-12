"""Recorder core: drives the real (bundled) PublicPilgrimForm in Chromium, composes 1080x1920 frames
(camera zoom, cursor, highlight frames, captions, step chip) and pipes them to ffmpeg."""
import io, math, os, subprocess, time, json, re, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OW, OH, FPS = 1080, 1920, 30
TOP = 250; PH = OH - TOP
VW, VH, DSF = 432, 668, 3
FONT_DIR = '/home/user/productive-families/dawah_cards/fonts/'
def font(sz, w=700): return ImageFont.truetype(FONT_DIR + f'IBMPlexSansArabic-{w}.ttf', int(sz), layout_engine=ImageFont.Layout.RAQM)
def tw(f, t): return f.getlength(t, direction='rtl', language='ar')
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)

# palette = Tailwind colours used by the component itself
STONE900 = (28, 25, 23); STONE800 = (41, 37, 36); EMERALD = (5, 150, 105); EMERALD_L = (16, 185, 129); TEAL = (13, 148, 136)
AMBER = (251, 191, 36); ROSE = (225, 29, 72); WHITE = (255, 255, 255)

def cursor_sprite():
    S = 4; im = Image.new('RGBA', (40 * S, 52 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(6, 4), (6, 38), (14, 30), (20, 44), (26, 41), (20, 28), (31, 28)]
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x * S + 3 * S, y * S + 4 * S) for x, y in pts], fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3 * S)))
    d.polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=2 * S)
    return im.resize((40 * 2, 52 * 2), Image.LANCZOS)
CURSOR = cursor_sprite()

def wrap(f, text, maxw):
    words, lines, cur = text.split(' '), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if tw(f, t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def chunk_caption(text, maxchars=44):
    """split narration into caption chunks at punctuation / length"""
    parts = re.split(r'(?<=[،,.؟:!])\s+', text.strip()); out, cur = [], ''
    for p in parts:
        if cur and len(cur) + len(p) + 1 > maxchars: out.append(cur); cur = p
        else: cur = (cur + ' ' + p).strip()
    if cur: out.append(cur)
    m = []
    for c in out:
        if m and len(c) < 16: m[-1] = m[-1] + ' ' + c
        elif m and len(m[-1]) < 16: m[-1] = m[-1] + ' ' + c
        else: m.append(c)
    out = m; res = []
    for c in out:                      # hard split very long chunks
        while len(c) > maxchars * 1.45:
            k = c.rfind(' ', 0, maxchars + 6); res.append(c[:k]); c = c[k + 1:]
        res.append(c)
    return res

class Recorder:
    def __init__(self, page, out_path, dry=False, render_from=None, durations=None):
        self.page, self.dry, self.dur = page, dry, durations
        self.render_from = render_from; self.rendering = (render_from is None) and not dry
        self.frame_no = 0; self.cam = dict(z=1.0, cx=VW / 2, cy=VH / 2)
        self.cur = None; self.cursor = None; self.ripple = None; self.hl = []; self.cap = None; self.chip = None
        self.beat_marks = []; self.step = (1, 11, ''); self.badge = True
        self.card = None; self.card_alpha = 0.0; self.note_sched = []; self.started = (render_from is None); self.last = None
        self.proc = None; self.out_path = out_path
        if not dry and render_from is None: self._open()

    def _open(self):
        self.proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OW}x{OH}', '-r', str(FPS), '-i', '-',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', self.out_path], stdin=subprocess.PIPE)

    # ---------------------------------------------------------------- time
    @property
    def t(self): return self.frame_no / FPS
    def snap(self):
        if not self.rendering: return
        b = self.page.screenshot(type='jpeg', quality=93)
        self.cur = Image.open(io.BytesIO(b)).convert('RGB')

    def _compose(self):
        c = self.cam; z = c['z']; w, h = VW / z, VH / z
        x0 = min(max(c['cx'] - w / 2, 0), VW - w); y0 = min(max(c['cy'] - h / 2, 0), VH - h)
        crop = self.cur.crop((int(x0 * DSF), int(y0 * DSF), int((x0 + w) * DSF), int((y0 + h) * DSF))).resize((OW, PH), Image.BICUBIC)
        img = Image.new('RGBA', (OW, OH), STONE900 + (255,)); img.paste(crop.convert('RGBA'), (0, TOP)); k = z * OW / VW
        M = lambda x, y: ((x - x0) * k, (y - y0) * k + TOP)
        lay = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        tnow = self.t
        for hl in self.hl:                                   # annotation frames
            if not (hl['t0'] <= tnow <= hl['t1']): continue
            a = min(1, (tnow - hl['t0']) / .25, (hl['t1'] - tnow) / .25); pulse = .75 + .25 * math.sin(tnow * 6)
            bx = hl['box']; l, t = M(bx[0], bx[1]); r, b = M(bx[0] + bx[2], bx[1] + bx[3]); pad = 8
            for g, al in ((10, 40), (5, 80)):
                d.rounded_rectangle((l - pad - g, t - pad - g, r + pad + g, b + pad + g), 26 + g, outline=AMBER + (int(al * a * pulse),), width=4)
            d.rounded_rectangle((l - pad, t - pad, r + pad, b + pad), 26, outline=AMBER + (int(255 * a),), width=6)
            if hl.get('label'):
                f = font(34, 700); txt = hl['label']; wdt = tw(f, txt) + 44; ty = t - pad - 70
                if ty < TOP + 10: ty = b + pad + 16
                cx = min(max((l + r) / 2, wdt / 2 + 24), OW - wdt / 2 - 24)
                d.rounded_rectangle((cx - wdt / 2, ty, cx + wdt / 2, ty + 56), 28, fill=AMBER + (int(255 * a),))
                d.text((cx, ty + 28), txt, font=f, fill=STONE900 + (int(255 * a),), anchor='mm', direction='rtl', language='ar')
        if self.ripple and 0 <= tnow - self.ripple['t0'] <= .55:
            p = (tnow - self.ripple['t0']) / .55; rx, ry = M(*self.ripple['pt'])
            for i, (rad, al) in enumerate(((22 + 70 * p, 200 * (1 - p)), (10 + 40 * p, 255 * (1 - p)))):
                d.ellipse((rx - rad, ry - rad, rx + rad, ry + rad), outline=EMERALD_L + (int(al),), width=7 - 3 * i)
        img.alpha_composite(lay)
        if self.cursor is not None and self.cursor['vis']:
            cx_, cy_ = M(*self.cursor['pt']); img.alpha_composite(CURSOR, (int(cx_ - 8), int(cy_ - 6)))
        self._chrome(img)
        out = img.convert('RGB')
        if self.card is not None and self.card_alpha > 0:
            cimg = self.card() if callable(self.card) else self.card
            cimg = cimg.convert('RGBA'); self._chrome(cimg, card=True); cimg = cimg.convert('RGB')
            out = cimg if self.card_alpha >= 1 else Image.blend(out, cimg, self.card_alpha)
        self.last = out
        return out

    def _chrome(self, img, card=False):
        base = img; img = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        for (a, b, txt, y) in self.note_sched:
            if a <= self.t <= b and not card:
                al = int(255 * min(1, (self.t - a) / .3, (b - self.t) / .3)); f = font(36, 700); wdt = tw(f, txt) + 70
                d.rounded_rectangle((OW / 2 - wdt / 2, y, OW / 2 + wdt / 2, y + 74), 37, fill=(5, 150, 105, int(al * .95)), outline=(255, 255, 255, int(al * .6)), width=2)
                d.text((OW / 2, y + 37), txt, font=f, fill=(255, 255, 255, al), anchor='mm', direction='rtl', language='ar')
        if self.badge and not card:
            n, tot, title = self.step
            f = font(33, 700); txt = f'{title}'; ft = font(27, 600)
            wdt = max(tw(f, txt) + 150, 460); x0 = (OW - wdt) / 2; y0 = 112
            d.rounded_rectangle((x0, y0, x0 + wdt, y0 + 112), 56, fill=(41, 37, 36, 240), outline=EMERALD_L + (150,), width=2)
            d.text((OW / 2, y0 + 38), txt, font=f, fill=WHITE, anchor='mm', direction='rtl', language='ar')
            d.text((OW / 2, y0 + 78), f'الخطوة {n} من {tot}'.translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩')), font=ft, fill=EMERALD_L + (255,), anchor='mm', direction='rtl', language='ar')
            sx = x0 + 28; seg = (wdt - 56) / tot
            for i in range(tot): d.rounded_rectangle((sx + i * seg + 2, y0 + 100, sx + (i + 1) * seg - 2, y0 + 105), 2, fill=(EMERALD_L if i < n else (90, 90, 90)) + (255,))
            fb = font(23, 600); d.rounded_rectangle((OW - 262, 40, OW - 40, 86), 23, fill=(255, 255, 255, 26))
            d.text((OW - 151, 63), 'بيانات تجريبية وهمية', font=fb, fill=(255, 255, 255, 235), anchor='mm', direction='rtl', language='ar')
        if self.cap:
            txt = self.cap; f = font(54, 700); lines = wrap(f, txt, 900)[:3]; lh = 82; hgt = len(lines) * lh + 46
            y1 = 1560; y0 = y1 - hgt
            d.rounded_rectangle((60, y0, OW - 60, y1), 40, fill=(12, 10, 9, 222))
            d.rounded_rectangle((60, y0, 74, y1), 7, fill=EMERALD_L + (255,))
            for i, ln in enumerate(lines):
                d.text((OW / 2, y0 + 23 + lh * i + lh / 2), ln, font=f, fill=WHITE, anchor='mm', direction='rtl', language='ar')
        base.alpha_composite(img)

    # ---------------------------------------------------------------- frames
    def emit(self, n=1, live=False, every=2):
        """write n output frames; live => fresh screenshot each `every` frames."""
        for i in range(n):
            self._tick_state()
            if self.rendering:
                if live and (i % every == 0): self.snap()
                elif self.cur is None: self.snap()
                self.proc.stdin.write(self._compose().tobytes())
            self.frame_no += 1
            if (not self.rendering) and self.render_from is None and False: pass
    def _tick_state(self):
        if self.cap_sched:
            tt = self.t - self.cap_t0; self.cap = None
            for (a, b, txt) in self.cap_sched:
                if a <= tt < b: self.cap = txt; break
        else: self.cap = None
    cap_sched = None; cap_t0 = 0

    def hold(self, sec, live=False):
        n = max(1, round(sec * FPS))
        if live and self.rendering: self.emit(n, live=True)
        else:
            if self.rendering: self.snap()
            self.emit(n)
    def pace(self, sec):   # let the page settle in dry mode without wasting time
        self.page.wait_for_timeout(int(sec * 1000) if not self.dry else min(int(sec * 1000), 120))

    # ---------------------------------------------------------------- camera / overlays
    def bbox(self, sel):
        loc = sel if not isinstance(sel, str) else self.page.locator(sel).first
        b = loc.bounding_box(); return (b['x'], b['y'], b['width'], b['height'])
    def cam_to(self, z, cx, cy, sec=0.8):
        c0 = dict(self.cam); n = max(1, round(sec * FPS))
        for i in range(1, n + 1):
            e = ease(i / n); self.cam = dict(z=c0['z'] + (z - c0['z']) * e, cx=c0['cx'] + (cx - c0['cx']) * e, cy=c0['cy'] + (cy - c0['cy']) * e)
            self.emit(1)
    def focus(self, sel, sec=0.9, zoom=None, fy=0.40, maxz=1.7):
        x, y, w, h = self.bbox(sel) if not isinstance(sel, tuple) else sel
        z = zoom or max(1.0, min(maxz, 0.9 * VW / max(w, 1), 0.55 * VH / max(h, 1)))
        hh = VH / z; cy = (y + h / 2 - fy * hh) + hh / 2
        self.cam_to(z, x + w / 2, cy, sec)
    def unfocus(self, sec=0.8): self.cam_to(1.0, VW / 2, VH / 2, sec)
    def frame_on(self, sel, sec, label=None, pad=0):
        b = self.bbox(sel) if not isinstance(sel, tuple) else sel
        self.hl.append(dict(box=(b[0] - pad, b[1] - pad, b[2] + 2 * pad, b[3] + 2 * pad), t0=self.t, t1=self.t + sec, label=label))
    def clear_frames(self): self.hl = []

    # ---------------------------------------------------------------- cursor
    def cursor_to(self, sel, sec=0.7, dx=0, dy=0):
        x, y, w, h = self.bbox(sel) if not isinstance(sel, tuple) else sel
        tgt = (x + w / 2 + dx, y + h / 2 + dy)
        if self.cursor is None: self.cursor = dict(pt=(VW * .75, VH * .75), vis=True)
        p0 = self.cursor['pt']; n = max(1, round(sec * FPS))
        for i in range(1, n + 1):
            e = ease(i / n); arc = math.sin(e * math.pi) * 14
            self.cursor['pt'] = (p0[0] + (tgt[0] - p0[0]) * e + arc * .3, p0[1] + (tgt[1] - p0[1]) * e - arc)
            self.emit(1)
        self.cursor['pt'] = tgt
    def click(self, sel, sec=0.6, after=0.35, dx=0, dy=0, live_after=True):
        """move cursor, ripple, perform real click"""
        loc = self.page.locator(sel).first if isinstance(sel, str) else sel
        self.cursor_to(loc, sec, dx, dy)
        self.ripple = dict(t0=self.t, pt=self.cursor['pt']); self.emit(4)
        loc.click(); self.pace(0.05)
        self.hold(after, live=live_after)
    def typing(self, sel, text, cps=9, click=True):
        loc = self.page.locator(sel).first if isinstance(sel, str) else sel
        if click: self.click(loc, 0.55, 0.15)
        else: loc.focus()
        step = max(1, round(FPS / cps))
        for ch in text:
            self.page.keyboard.type(ch); self.emit(step, live=True, every=step)
    def scroll_to(self, y, sec=1.0):
        y0 = self.page.evaluate('window.scrollY'); n = max(1, round(sec * FPS)); cur = self.cursor
        for i in range(1, n + 1):
            e = ease(i / n); self.page.evaluate(f'window.scrollTo(0,{y0 + (y - y0) * e})')
            if self.rendering: self.snap()
            self.emit(1)
    def scroll_el(self, sel, sec=1.0, at=0.34, extra=0):
        """scroll so the element's top sits at fraction `at` of the viewport"""
        loc = self.page.locator(sel).first if isinstance(sel, str) else sel
        top = loc.evaluate('e => e.getBoundingClientRect().top + window.scrollY')
        mx = self.page.evaluate('document.documentElement.scrollHeight - window.innerHeight')
        self.scroll_to(max(0, min(mx, top - at * VH + extra)), sec)

    # ---------------------------------------------------------------- beats / captions
    def beat(self, key, gap=0.35):
        return Beat(self, key, gap)
    def card_in(self, card, sec=0.6):
        self.card = card; n = max(1, round(sec * FPS))
        for i in range(1, n + 1): self.card_alpha = ease(i / n); self.emit(1)
    def card_out(self, sec=0.6):
        n = max(1, round(sec * FPS))
        for i in range(1, n + 1): self.card_alpha = 1 - ease(i / n); self.emit(1)
        self.card = None
    def card_hold(self, sec):
        n = max(1, round(sec * FPS))
        for i in range(n): self.emit(1)
    def note(self, text, sec=2.4, y=1180): self.note_sched.append((self.t, self.t + sec, text, y))
    def finish(self):
        if self.proc: self.proc.stdin.close(); self.proc.wait()

class Beat:
    def __init__(self, rec, key, gap): self.rec, self.key, self.gap = rec, key, gap
    def __enter__(self):
        r = self.rec; D = r.dur[self.key]; self.D = D
        if (not r.started) and r.render_from == self.key:
            r.started = True; r.frame_no = 0; r._open()
        r.rendering = (not r.dry) and r.started
        self.t0 = r.t
        from script import LINES
        text = LINES[self.key]; chunks = chunk_caption(text); tot = sum(len(c) for c in chunks); a = 0.0; sched = []
        for c in chunks:
            b = a + D * len(c) / tot; sched.append((a, b, c)); a = b
        r.cap_sched, r.cap_t0 = sched, r.t
        if r.started: r.beat_marks.append((self.key, r.t))
        return self
    def __exit__(self, *e):
        r = self.rec; rest = self.t0 + self.D + self.gap - r.t
        self.over = -rest
        if rest > 0: r.hold(rest)
        else: print(f'  !! beat {self.key} overran by {-rest:.2f}s')
        r.cap_sched = None

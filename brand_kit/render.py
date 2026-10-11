import os, asyncio
from playwright.sync_api import sync_playwright
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

def _launch(p):
    return p.chromium.launch(executable_path=CHROME, args=["--no-sandbox", "--allow-file-access-from-files"])

def to_png(path, out, w, h, scale=1):
    with sync_playwright() as p:
        b = _launch(p); pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        pg.goto("file://" + os.path.abspath(path)); pg.wait_for_timeout(300)
        pg.screenshot(path=out, omit_background=True); b.close()

def to_pdf(path, out, w_mm=None, h_mm=None, w_px=None, h_px=None):
    with sync_playwright() as p:
        b = _launch(p); pg = b.new_page()
        pg.goto("file://" + os.path.abspath(path)); pg.wait_for_timeout(600)
        pg.evaluate("document.fonts.ready")
        kw = dict(print_background=True, margin=dict(top="0", right="0", bottom="0", left="0"), prefer_css_page_size=True)
        if w_px:
            kw.update(width=f"{w_px}px", height=f"{h_px}px", prefer_css_page_size=False)
        elif w_mm:
            kw.update(width=f"{w_mm}mm", height=f"{h_mm}mm", prefer_css_page_size=False)
        pg.pdf(path=out, **kw); b.close()

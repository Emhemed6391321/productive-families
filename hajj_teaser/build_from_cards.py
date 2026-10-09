#!/usr/bin/env python3
"""30 s silent vertical teaser (1080x1920) made from the identity-pack designs.
27 slides x 1.0 s (no slide longer than a second) + 3 s closing card.  No audio track.
    python3 build_from_cards.py [-o hajj_teaser_cards.mp4]
"""
import argparse, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "identity_pack"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_teaser as bt                     # photo_clip(): zoom/pan + flash + grade
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "identity_pack"))
from pack_lib import *                        # palette, logos, helpers

R = "../dawah_cards/out/card_%02d.png"
T = "Templates/Template-%02d.png"
C = "Covers/Cover-%02d.png"
SLIDES = ([T % i for i in (4, 2, 3, 1, 5, 6)] +                    # A: visual hook (captions)
          [R % i for i in range(1, 13)] +                          # B: the 12 dawah cards
          [C % 2, R % 5, C % 3, R % 6, C % 4, R % 10, C % 1, R % 11, C % 5])   # C: finale
CAPS = [(0, 3, "ملايين القلوب…"), (3, 6, "وجهة واحدة")]
W, H, FPS, DUR, END = 1080, 1920, 30, 1.0, 3.0

def canvas(path):
    im = Image.open(path).convert("RGB")
    bgp = im.resize((W, H), Image.LANCZOS) if im.size[1] > im.size[0] else im
    s = max(W / bgp.size[0], H / bgp.size[1])
    bg = bgp.resize((round(bgp.size[0] * s), round(bgp.size[1] * s)), Image.LANCZOS)
    x0, y0 = (bg.size[0] - W) // 2, (bg.size[1] - H) // 2
    bg = bg.crop((x0, y0, x0 + W, y0 + H)).filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.62)
    fg = im.resize((W, round(im.size[1] * W / im.size[0])), Image.LANCZOS)
    bg.paste(fg, (0, (H - fg.size[1]) // 2))
    return bg

def end_card(path):
    img = gradient(W, H, [(0, (0, 98, 84)), (.55, (3, 56, 36)), (1, GREEN_DK)], 90)
    g, m = glow(W, H, W / 2, H * .38, 700, 520, (14, 128, 108), .55)
    img = over(img, (14, 128, 108), m)
    img = add_lattice(img, GOLD_LT, 34)
    paste(img, sky_layer(W, 0.9, tint=GOLD_LT, blur=1.1), 0, H - 520)
    d = ImageDraw.Draw(img)
    star8(d, W / 2, 380, 64, outline=GOLD, width=3)
    star8(d, W / 2, 380, 36, outline=GOLD, width=2, rot=-math.pi / 2 + math.pi / 8)
    paste(img, fit_w(asset("rakb_gold"), 520), (W - 520) // 2, 520)
    d.text((W / 2, 1040), "الحج القادم… هل أنت مستعد؟", font=font(700, 70), fill=GOLD_LT, anchor="mm", direction="rtl", language="ar")
    diamond_divider(img, W / 2, 1120, half=240, col=GOLD)
    name_text(img, W / 2, 1210, 64, CREAM)
    paste(img, fit_w(asset("hajj_white"), 130), (W - 130) // 2, 1290)
    img.save(path)

def caption(text, path):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = font(700, 112)
    tw = f.getlength(text, direction="rtl", language="ar")
    x, y = W / 2, H / 2
    d.rounded_rectangle((x - tw / 2 - 50, y - 90, x + tw / 2 + 50, y + 90), 40, fill=(2, 36, 22, 170), outline=GOLD_LT + (255,), width=3)
    d.text((x, y), text, font=f, fill=WHITE, anchor="mm", direction="rtl", language="ar")
    img.save(path)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("-o", "--output", default="hajj_teaser_cards.mp4")
    a = ap.parse_args()
    out = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), a.output)) if not os.path.isabs(a.output) else a.output
    assert DUR <= 1.0 and len(SLIDES) * DUR + END == 30
    tmp = tempfile.mkdtemp()
    clips = []
    for i, p in enumerate(SLIDES):
        src = f"{tmp}/s{i:02d}.png"; canvas(p).save(src)
        c = f"{tmp}/c{i:02d}.mp4"
        bt.photo_clip(src, c, W, H, DUR, i)
        clips.append(c); print("slide", i + 1, flush=True)
    ec = f"{tmp}/end.png"; end_card(ec)
    end = f"{tmp}/end.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", str(END), "-i", ec, "-vf",
         f"fade=in:0:10,fade=out:st={END - 0.5}:d=0.5,format=yuv420p", "-r", str(FPS), "-an", "-c:v", "libx264", "-crf", "18", end])
    clips.append(end)
    lst = f"{tmp}/l.txt"; open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    base = f"{tmp}/base.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", base])
    ins, fc, last = ["-i", base], "", "0:v"
    for k, (s, e, t) in enumerate(CAPS):
        png = f"{tmp}/cap{k}.png"; caption(t, png)
        ins += ["-loop", "1", "-t", "30", "-i", png]
        fc += (f"[{k+1}:v]format=rgba,fade=in:st={s}:d=0.3:alpha=1,fade=out:st={e-0.3}:d=0.3:alpha=1[c{k}];"
               f"[{last}][c{k}]overlay=0:0:enable='between(t,{s},{e})'[v{k}];")
        last = f"v{k}"
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc.rstrip(";"), "-map", f"[{last}]", "-t", "30",
         "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-movflags", "+faststart", out])
    print("done:", out)

if __name__ == "__main__":
    main()

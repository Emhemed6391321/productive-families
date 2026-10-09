#!/usr/bin/env python3
"""Build a 30-second silent Hajj teaser video from a folder of photos.

Usage:
    python3 build_teaser.py PHOTOS_DIR [-o teaser.mp4] [--page "اسم الصفحة"]
                            [--font /path/to/arabic.ttf] [--size 1080x1920]

Rules: total length 30s, no photo shown longer than 1s, no audio track.
Effects: slow zoom / pan (Ken Burns), white flash cut, colour grade,
vignette, film grain, Arabic captions following the story below.
"""
import argparse, glob, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

TOTAL = 30.0
END_CARD = 3.0          # closing card (not a photo)
PHOTO_DUR = 0.75        # seconds per photo (must be <= 1)
FPS = 30

# Story: (start second, end second, caption)
SCRIPT = [
    (0.0, 3.0, "ملايين القلوب…"),
    (3.0, 6.0, "وجهة واحدة"),
    (6.0, 12.0, "لبّيك اللهم لبّيك"),
    (12.0, 18.0, "رحلة عمر… في أيام معدودات"),
    (18.0, 24.0, "دموع، دعاء، وسكينة لا توصف"),
    (24.0, 27.0, "هذا كان حج العام الماضي"),
]
CLOSING = ["الحج القادم… هل أنت مستعد؟", None]  # second line = page name


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def find_font(arg):
    if arg:
        return arg
    for pat in ("/usr/share/fonts/**/*Cairo*.ttf", "/usr/share/fonts/**/*Amiri*.ttf",
                "/usr/share/fonts/**/*Noto*Arabic*.ttf", "/usr/share/fonts/**/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/**/DejaVuSans.ttf"):
        hits = glob.glob(pat, recursive=True)
        if hits:
            return hits[0]
    sys.exit("No Arabic-capable font found; pass --font")


def caption_png(text, w, h, font_path, path, y_frac=0.78, size_frac=0.075):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = int(w * size_frac)
    while True:  # shrink until the caption fits inside 88% of the width
        f = ImageFont.truetype(font_path, size)
        box = d.textbbox((0, 0), text, font=f, direction="rtl", language="ar")
        if box[2] - box[0] <= w * 0.88 or size < 20:
            break
        size -= 4
    tw, th = box[2] - box[0], box[3] - box[1]
    x, y = (w - tw) // 2 - box[0], int(h * y_frac) - th // 2
    pad = 28
    d.rounded_rectangle((x - pad, y - pad, x + tw + pad, y + th + pad + 10), 24, fill=(0, 0, 0, 120))
    d.text((x, y), text, font=f, fill=(255, 255, 255, 255), direction="rtl", language="ar",
           stroke_width=2, stroke_fill=(0, 0, 0, 255))
    img.save(path)


def photo_clip(src, out, w, h, dur, idx):
    """One photo -> short clip with zoom/pan + flash-in, graded."""
    frames = int(round(dur * FPS))
    # alternate zoom in / zoom out / pan left / pan right
    mode = idx % 4
    z_expr = {0: "min(1.0+0.0012*on,1.12)", 1: "max(1.12-0.0012*on,1.0)",
              2: "1.10", 3: "1.10"}[mode]
    x_expr = {0: "iw/2-(iw/zoom/2)", 1: "iw/2-(iw/zoom/2)",
              2: f"(iw-iw/zoom)*on/{frames}", 3: f"(iw-iw/zoom)*(1-on/{frames})"}[mode]
    vf = (f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
          f"zoompan=z='{z_expr}':x='{x_expr}':y='ih/2-(ih/zoom/2)':d={frames}:s={w}x{h}:fps={FPS},"
          "eq=contrast=1.12:saturation=1.25:brightness=0.02,"
          "curves=preset=medium_contrast,"
          "vignette=PI/5,noise=alls=6:allf=t,"
          # white flash on the first 4 frames
          "eq=brightness='0.35*max(0,1-n/4)':eval=frame,"
          "format=yuv420p")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf, "-frames:v", str(frames),
         "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", out])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photos")
    ap.add_argument("-o", "--output", default="hajj_teaser.mp4")
    ap.add_argument("--page", default="", help="page name for the closing card")
    ap.add_argument("--font")
    ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    assert PHOTO_DUR <= 1.0

    photos = sorted(p for ext in ("jpg", "jpeg", "png", "webp")
                    for p in glob.glob(os.path.join(a.photos, f"*.{ext}")) +
                    glob.glob(os.path.join(a.photos, f"*.{ext.upper()}")))
    if not photos:
        sys.exit("no photos found")
    photo_time = TOTAL - END_CARD
    n = int(photo_time / PHOTO_DUR)          # 36 photo slots
    dur = photo_time / n                      # exact slot length (0.75s)
    font = find_font(a.font)
    tmp = tempfile.mkdtemp()
    print(f"{len(photos)} photos -> {n} slots of {dur:.3f}s (cycled if fewer)")

    clips = []
    for i in range(n):
        out = os.path.join(tmp, f"c{i:03d}.mp4")
        photo_clip(photos[i % len(photos)], out, w, h, dur, i)
        clips.append(out)

    # end card: darkened last photo + closing text
    end = os.path.join(tmp, "end.mp4")
    lines = [CLOSING[0]] + ([a.page] if a.page else [])
    for k, t in enumerate(lines):
        caption_png(t, w, h, font, os.path.join(tmp, f"end{k}.png"), 0.42 + 0.1 * k, 0.07 if k == 0 else 0.055)
    ins = ["-loop", "1", "-t", str(END_CARD), "-i", photos[-1]]
    fc = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"eq=brightness=-0.25,gblur=sigma=6,fade=in:0:10,fade=out:st={END_CARD-0.6}:d=0.6[bg]")
    last = "bg"
    for k in range(len(lines)):
        ins += ["-i", os.path.join(tmp, f"end{k}.png")]
        fc += f";[{last}][{k+1}:v]overlay=0:0:format=auto[o{k}]"
        last = f"o{k}"
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc, "-map", f"[{last}]",
         "-r", str(FPS), "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", end])
    clips.append(end)

    lst = os.path.join(tmp, "list.txt")
    open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    base = os.path.join(tmp, "base.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", base])

    # story captions (fade in/out) over the photo section
    ins, fc, last = ["-i", base], "", "0:v"
    for k, (s, e, text) in enumerate(SCRIPT):
        png = os.path.join(tmp, f"cap{k}.png")
        caption_png(text, w, h, font, png)
        ins += ["-loop", "1", "-t", str(TOTAL), "-i", png]
        fc += (f"[{k+1}:v]format=rgba,fade=in:st={s}:d=0.3:alpha=1,fade=out:st={e-0.3}:d=0.3:alpha=1[c{k}];"
               f"[{last}][c{k}]overlay=0:0:enable='between(t,{s},{e})'[v{k}];")
        last = f"v{k}"
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fc.rstrip(";"),
         "-map", f"[{last}]", "-t", str(TOTAL), "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-crf", "19", "-movflags", "+faststart", a.output])
    print("done:", a.output)


if __name__ == "__main__":
    main()

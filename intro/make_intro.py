#!/usr/bin/env python3
"""5-second animated intro from the supplied coordination logo (1080x1080, 30 fps, silent).
Layers are separated from the artwork itself: white lettering/ornament (alpha) vs the green patterned ground (inpainted).
Timeline: 0-0.4 fade-in | 0-3 ground settles + rotating light rays | 0.5-2.4 circular draw-on reveal with glowing edge |
2.6-3.7 diagonal shine | sparkles throughout | 3.7-5 breathing glow + slow push-in."""
import math, subprocess, sys
import numpy as np, cv2

S, FPS, DUR = 1080, 30, 5.0
N = int(FPS * DUR)
src = cv2.resize(cv2.imread("logo_source.jpg"), (S, S), interpolation=cv2.INTER_AREA)
b, g, r = [c.astype(int) for c in cv2.split(src)]
mx = np.maximum(np.maximum(r, g), b); mn = np.minimum(np.minimum(r, g), b)
hard = ((mn > 150) & (mx - mn < 70)).astype(np.uint8) * 255
hard = cv2.morphologyEx(hard, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
alpha = cv2.GaussianBlur(cv2.dilate(hard, np.ones((2, 2), np.uint8)), (0, 0), 0.9).astype(np.float32) / 255
# ground without the white artwork
wide = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (43, 43)))          # also covers the 3-D shadow around the letters
small = cv2.resize(src, (540, 540), interpolation=cv2.INTER_AREA)
bg_s = cv2.inpaint(small, cv2.resize(wide, (540, 540), interpolation=cv2.INTER_NEAREST), 9, cv2.INPAINT_TELEA)
bg_l = cv2.resize(bg_s, (S, S), interpolation=cv2.INTER_CUBIC).astype(np.float32)
bg_l = cv2.GaussianBlur(bg_l, (0, 0), 6)
wm = cv2.GaussianBlur(wide.astype(np.float32) / 255, (0, 0), 7)[..., None]
bg = src.astype(np.float32) * (1 - wm) + bg_l * wm                                         # keep the real pattern outside the logo
fg = src.astype(np.float32)

yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
cx = cy = S / 2
dx, dy = xx - cx, yy - cy
theta = (np.arctan2(dx, -dy) % (2 * np.pi)) / (2 * np.pi)          # 0 at top, clockwise
rad = np.sqrt(dx * dx + dy * dy) / (S / 2)
vig = np.clip(1.0 - 0.55 * np.clip(rad - 0.45, 0, 1) ** 1.6, 0, 1)[..., None]
glow_a = cv2.GaussianBlur(alpha, (0, 0), 22)
edge_a = cv2.GaussianBlur(alpha, (0, 0), 3)

def ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)
def ease_out(x): x = np.clip(x, 0, 1); return 1 - (1 - x) ** 3
def scale_about(img, s, center=(S / 2, S / 2)):
    M = np.array([[s, 0, center[0] * (1 - s)], [0, s, center[1] * (1 - s)]], np.float32)
    return cv2.warpAffine(img, M, (S, S), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

rng = np.random.default_rng(7)
P = dict(x=rng.uniform(0.08, 0.92, 70) * S, y=rng.uniform(0.1, 1.0, 70) * S, sp=rng.uniform(18, 60, 70),
         ph=rng.uniform(0, 6.28, 70), sz=rng.uniform(1.2, 3.4, 70), t0=rng.uniform(0.6, 3.6, 70))

def frame(t):
    # ---- ground
    gs = 1.10 - 0.10 * ease(t / 3.0) + 0.02 * ease((t - 3) / 2)
    base = scale_about(bg, gs)
    # rotating light rays behind the artwork
    ang = (theta * 2 * np.pi)
    rays = (0.5 + 0.5 * np.cos(14 * ang + t * 0.9)) ** 5 * np.clip(1.05 - rad, 0, 1)
    ray_int = 0.20 * ease((t - 0.2) / 1.0) * (1 - 0.65 * ease((t - 2.6) / 1.4))
    out = base + rays[..., None] * ray_int * np.array([150, 215, 255], np.float32)      # BGR warm gold
    # ---- artwork reveal (circular draw-on)
    p = ease((t - 0.5) / 1.9) * 1.06
    reveal = np.clip((p - theta) / 0.05, 0, 1)
    fs = 0.93 + 0.07 * ease_out((t - 0.5) / 1.7)
    a_fg = scale_about(alpha, fs) * scale_about(reveal, fs) * ease((t - 0.45) / 0.5)
    fg_s = scale_about(fg, fs)
    out = out * (1 - a_fg[..., None]) + fg_s * a_fg[..., None]
    # glow behind / around the artwork, breathing after the reveal
    breathe = 0.5 + 0.5 * math.sin(2 * math.pi * (t - 2.2) / 1.6)
    gi = (0.10 + 0.07 * breathe) * ease((t - 1.0) / 1.5)
    out += scale_about(glow_a, fs)[..., None] * gi * np.array([190, 235, 255], np.float32)
    # glowing leading edge while drawing on
    if 0.5 < t < 2.6:
        edge = np.exp(-((theta - p) / 0.014) ** 2) * scale_about(edge_a, fs)
        out += edge[..., None] * 230 * np.array([0.75, 0.93, 1.0], np.float32)
    # diagonal shine
    if 2.6 <= t <= 3.8:
        pos = (-0.4 + 1.8 * ease((t - 2.6) / 1.2)) * S
        band = np.exp(-(((xx + yy * 0.55) - pos) / 70) ** 2)
        out += (band * a_fg)[..., None] * 120 * np.array([0.9, 0.97, 1.0], np.float32)
    # sparkles
    sp = np.zeros((S, S), np.float32)
    for i in range(70):
        life = t - P["t0"][i]
        if life < 0: continue
        yv = (P["y"][i] - P["sp"][i] * life) % (S * 1.1)
        xv = P["x"][i] + 10 * math.sin(life * 1.3 + P["ph"][i])
        tw = 0.5 + 0.5 * math.sin(life * 3.2 + P["ph"][i])
        v = tw * ease(life / 0.6)
        cv2.circle(sp, (int(xv), int(yv)), max(1, int(P["sz"][i])), v, -1, cv2.LINE_AA)
        if P["sz"][i] > 2.4:
            cv2.line(sp, (int(xv) - 7, int(yv)), (int(xv) + 7, int(yv)), v * 0.6, 1, cv2.LINE_AA)
            cv2.line(sp, (int(xv), int(yv) - 7), (int(xv), int(yv) + 7), v * 0.6, 1, cv2.LINE_AA)
    sp = cv2.GaussianBlur(sp, (0, 0), 1.1)
    out += sp[..., None] * 200 * np.array([0.7, 0.9, 1.0], np.float32)
    # global push-in and vignette, fade from black
    out = scale_about(out, 1.0 + 0.035 * ease((t - 0.2) / 4.8))
    out = out * (0.55 + 0.45 * vig) * ease(t / 0.45)
    return np.clip(out, 0, 255).astype(np.uint8)

def main(path="Intro-Tripoli-B-5s.mp4"):
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{S}x{S}", "-r", str(FPS), "-i", "-",
                           "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "medium", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for i in range(N):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("done", path)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        for t in (0.3, 1.0, 1.7, 2.3, 3.1, 4.8):
            cv2.imwrite(f"/tmp/claude-0/-home-user-productive-families/279b9344-f325-5676-997e-4eb1bcac3822/scratchpad/in_{t}.png", cv2.resize(frame(t), (540, 540)))
    else:
        main()

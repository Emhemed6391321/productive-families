import sys, json, subprocess, math, time
from multiprocessing import Pool
from scenes3d import *
dur = json.load(open(HS + 'work/durations3.json'))
def T_of(s): return dur[s["key"]] + s.get("pad", .8) + (2.4 if s["key"] == "s9" else 0)
def run(i):
    s = SC[i]; T = T_of(s); n = int(math.ceil(T * FPS)); out = HS + f"work/seg3_{s['key']}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t0 = time.time()
    for k in range(n): p.stdin.write(render3d(s, k / FPS, T).tobytes())
    p.stdin.close(); p.wait(); return s["key"], n, round(time.time() - t0)
if __name__ == "__main__":
    order = sorted(range(len(SC)), key=lambda i: -T_of(SC[i]))
    with Pool(4) as pool:
        for r in pool.imap_unordered(run, order): print(r, flush=True)

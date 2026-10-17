import json, wave, subprocess, numpy as np
from scenes3d import SC, HS
dur = json.load(open(HS + 'work/durations3.json')); SR = 22050
def T_of(s): return dur[s["key"]] + s.get("pad", .8) + (2.4 if s["key"] == "s9" else 0)
order = [s["key"] for s in SC]; t0 = 0.0; starts = {}
for s in SC: starts[s["key"]] = t0; t0 += T_of(s)
buf = np.zeros(int((t0 + 1) * SR), np.float32)
for k in order:
    w = wave.open(HS + f'work/tts3/{k}.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    off = 1.6 if k == "s0" else .4
    i = int((starts[k] + off) * SR); buf[i:i + len(a)] += a[:len(buf) - i]
wv = wave.open(HS + 'work/narration3.wav', 'wb'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(buf, -1, 1) * 32767).astype('int16').tobytes()); wv.close()
open(HS + 'work/concat3.txt', 'w').write(''.join(f"file '{HS}work/seg3_{k}.mp4'\n" for k in order))
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', HS + 'work/concat3.txt', '-i', HS + 'work/narration3.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-shortest', '-movflags', '+faststart', HS + 'work/Hajj-Steps-3D-9x16.mp4'])
print('total', round(t0, 1))

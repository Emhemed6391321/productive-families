import json, wave, subprocess, numpy as np
from scenes import SC, HS
dur = json.load(open(HS + 'work/durations.json')); PAD = {"s9": 3.2}; SR = 22050
order = [s["key"] for s in SC]; t0 = 0.0; starts = {}
for k in order: starts[k] = t0; t0 += dur[k] + PAD.get(k, .8)
buf = np.zeros(int((t0 + 1) * SR), np.float32)
for k in order:
    w = wave.open(HS + f'work/tts/{k}.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    i = int((starts[k] + .4) * SR); buf[i:i + len(a)] += a[:len(buf) - i]
wv = wave.open(HS + 'work/narration.wav', 'wb'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes((np.clip(buf, -1, 1) * 32767).astype('int16').tobytes()); wv.close()
open(HS + 'work/concat.txt', 'w').write(''.join(f"file '/home/user/productive-families/hajj_steps/work/seg_{k}.mp4'\n" for k in order))
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', HS + 'work/concat.txt', '-i', HS + 'work/narration.wav', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-shortest', '-movflags', '+faststart', HS + 'work/Hajj-Steps-9x16.mp4'])
print('total', round(t0, 1))

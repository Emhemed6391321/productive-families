import json, wave, subprocess, numpy as np, os, sys
from script import LINES
from rec_core import chunk_caption, FPS
SEGS = ['work/seg1.mp4', 'work/seg2.mp4', 'work/seg3.mp4', 'work/seg4.mp4']
DUR = json.load(open('tts/durations.json'))
off, events = 0.0, []
for s in SEGS:
    m = json.load(open(s + '.marks.json'))
    for k, t in m['marks']: events.append((k, off + t))
    off += m['frames'] / FPS
total = off; SR = 22050
buf = np.zeros(int((total + 1) * SR), np.float32)
for k, t in events:
    w = wave.open(f'tts/out/{k}.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    i = int(t * SR); buf[i:i + len(a)] += a[:len(buf) - i]
buf = np.clip(buf, -1, 1)
wav = wave.open('work/narration.wav', 'wb'); wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(SR); wav.writeframes((buf * 32767).astype('int16').tobytes()); wav.close()
# SRT
def ts(x): h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.', ',')
srt, n = [], 1
for k, t in events:
    ch = chunk_caption(LINES[k]); tot = sum(len(c) for c in ch); a = t
    for c in ch:
        b = a + DUR[k] * len(c) / tot; srt.append(f'{n}\n{ts(a)} --> {ts(b)}\n{c}\n'); n += 1; a = b
open('work/subtitles.srt', 'w', encoding='utf8').write('\n'.join(srt))
open('work/concat.txt', 'w').write(''.join(f"file '{os.path.abspath(s)}'\n" for s in SEGS))
subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', 'work/concat.txt', '-i', 'work/narration.wav',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '44100', '-ac', '2', '-shortest', '-movflags', '+faststart', 'work/Meeqat-Guide-9x16.mp4'])
print('total', round(total, 1), 's')

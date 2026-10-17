import sys, json
from scenes3d import *
dur = json.load(open(HS + 'work/durations3.json'))
sel = sys.argv[1:] or [s["key"] for s in SC]; tiles = []
for s in SC:
    if s["key"] not in sel: continue
    T = dur[s["key"]] + s.get("pad", .8)
    for fr in (.2, .55, .9): tiles.append(render3d(s, T * fr, T).resize((360, 640)))
cols = 6; rows = (len(tiles) + cols - 1) // cols; sh = Image.new("RGB", (cols * 364, rows * 644), (50, 50, 50))
for i, t_ in enumerate(tiles): sh.paste(t_, ((i % cols) * 364, (i // cols) * 644))
sh.save(HS + "work/preview3d.png"); print(len(tiles))

import sys, json
from scenes import *
dur = json.load(open(HS+'work/durations.json'))
sel = sys.argv[1:] or [s["key"] for s in SC]
tiles = []
for s in SC:
    if s["key"] not in sel: continue
    T = dur[s["key"]] + .8
    for fr in (.25, .85):
        im = render(s, T * fr, T); tiles.append(im.resize((432, 768)))
cols = 6; rows = (len(tiles) + cols - 1) // cols
sh = Image.new("RGB", (cols * 436, rows * 772), (50, 50, 50))
for i, t_ in enumerate(tiles): sh.paste(t_, ((i % cols) * 436, (i // cols) * 772))
sh.save(HS+"work/preview.png"); print(len(tiles))

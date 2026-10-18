# Office walkthrough (3D model, stills and video)

A browser-rendered 3D model of the office design, built from the floor plan
(dimensions in metres as labelled on the plan) and the design renders. It produces
still images of each area and a walkthrough video that goes from the corridor,
through the open office and into the manager's office.

## Files

- `index.html`, `scene.js`: the scene (geometry, materials, lights, camera path).
- `render.mjs`: renders stills or video frames with headless Chromium (Playwright).
- `vendor/three.module.min.js`: three.js r160 (MIT), copied locally so no CDN is needed.

## Rebuild

```bash
cd office-walkthrough
python3 -m http.server 8765 --bind 127.0.0.1 &
node render.mjs stills  /path/to/stills
node render.mjs video   /path/to/frames 24 24
ffmpeg -framerate 24 -i /path/to/frames/frame_%04d.jpg -c:v libx264 -pix_fmt yuv420p -crf 20 -movflags +faststart walkthrough.mp4
```

## Assumptions to check

- Ceiling height is 3.2 m. It is not on the plan.
- Partition positions are read from the plan labels (20.35 m, 26.35 m, 6.20 m, 8.35 m, etc.)
  and the renders. Furniture is placed to match the renders and is approximate.
- The TV on the manager's wall shows a generic blue screen, not any brand artwork.
- Materials are procedural (plaster, tile, wood grain, fluted glass), not scanned.

## Changing the layout

Walls are declared in `scene.js` with `wallSeg` / `wallRange` (metres, plan axes).
Desks use `desk(x0, x1, z, side)`, shelves `shelf(...)`, and camera keyframes are in `KEYS`.
Adjust the numbers there and re-render.

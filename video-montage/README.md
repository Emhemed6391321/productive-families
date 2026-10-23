# Walking Montage (Remotion)

A 9:16 (1080x1920, 30fps, 12s) montage built with Remotion from a single walking photo.
It cuts between four camera framings (wide establishing, close-up, tracking side shot,
low-angle hero) with cross-fades, a gentle walking bob, and a progress bar.

## Usage

```bash
npm install
npm start      # open Remotion Studio to preview
npm run render # writes out/walking-montage.mp4
```

If Remotion tries to download Chrome in a locked-down environment, pass a local
browser: `npx remotion render WalkingMontage out/walking-montage.mp4 --browser-executable=/path/to/chromium`.

## Notes

- Source still: `public/walker.jpg`. Replace it to change the subject.
- The "angles" are simulated with crops, zooms, and moves on one still. Real multi-angle
  footage would need to be added as separate clips in `src/WalkingMontage.tsx`.

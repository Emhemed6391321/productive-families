// Renders still views and the walkthrough frames from scene.js using headless Chromium.
// Usage:
//   node render.mjs stills <outDir>
//   node render.mjs video  <framesDir> [fps] [seconds]
import { createRequire } from 'node:module';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');

const [, , mode, outDir, fpsArg = '24', secArg = '24'] = process.argv;
const BASE = process.env.BASE_URL || 'http://localhost:8765/index.html';
mkdirSync(outDir, { recursive: true });

const STILLS = [
  { name: '01_overview_cutaway', cut: true, p: [-5, 15, -5], l: [12, 0, 9] },
  { name: '02_corridor', p: [1.3, 1.6, 0.9], l: [1.3, 1.4, 12] },
  { name: '03_waiting_bench', p: [2.3, 1.6, 13.8], l: [0.0, 1.2, 9.5] },
  { name: '04_elevator', p: [2.3, 1.6, 2.8], l: [0.0, 1.5, 0.9] },
  { name: '05_open_office', p: [3.2, 1.6, 4.2], l: [13, 1.3, 8] },
  { name: '06_reception', p: [4.0, 1.6, 2.2], l: [11, 1.2, 1.2] },
  { name: '07_workstations', p: [7.0, 1.6, 8.5], l: [15, 1.1, 6.5] },
  { name: '08_manager_office', p: [21.6, 1.6, 17.0], l: [16.5, 1.2, 13.0] },
  { name: '09_lounge', p: [5.5, 1.6, 22.3], l: [1.5, 1.2, 18.5] },
];

const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });

async function openPage(w, h, cut) {
  const page = await browser.newPage({ viewport: { width: w, height: h } });
  page.on('pageerror', (e) => console.error('PAGE ERROR:', e.message));
  page.on('console', (m) => { if (m.type() === 'error') console.error('CONSOLE:', m.text()); });
  await page.goto(`${BASE}?w=${w}&h=${h}${cut ? '&cut=1' : ''}`);
  await page.waitForFunction(() => window.ready === true, null, { timeout: 120000 });
  return page;
}

const decode = (dataUrl) => Buffer.from(dataUrl.split(',')[1], 'base64');

if (mode === 'stills') {
  for (const s of STILLS) {
    const page = await openPage(1920, 1080, s.cut);
    const url = await page.evaluate(([p, l]) => window.view(p, l, 'png'), [s.p, s.l]);
    const file = join(outDir, `${s.name}.png`);
    writeFileSync(file, decode(url));
    console.log('wrote', file);
    await page.close();
  }
} else if (mode === 'video') {
  const fps = Number(fpsArg), seconds = Number(secArg);
  const n = Math.round(fps * seconds);
  const page = await openPage(1280, 720, false);
  const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const url = await page.evaluate((tt) => window.frame(tt), t);
    writeFileSync(join(outDir, `frame_${String(i).padStart(4, '0')}.jpg`), decode(url));
    if (i % 24 === 0) console.log(`frame ${i + 1}/${n} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  await page.close();
  console.log('done frames:', n);
} else {
  console.error('unknown mode');
  process.exitCode = 1;
}

await browser.close();

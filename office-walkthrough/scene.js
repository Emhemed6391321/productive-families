import * as THREE from './vendor/three.module.min.js';

// Layout is read from the floor plan (metres). Ceiling height is an assumption.
const CEIL = 3.2;
const T = 0.15; // wall thickness

const q = new URLSearchParams(location.search);
const W = Number(q.get('w') || 1280);
const H = Number(q.get('h') || 720);
const CUT = q.get('cut') === '1';

let seed = 11;
const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

// ---------- renderer ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
document.getElementById('stage').appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x5b6178);
const camera = new THREE.PerspectiveCamera(62, W / H, 0.05, 120);

// ---------- procedural textures ----------
function tex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  return t;
}
// Returns a copy of a texture repeated so one tile covers `per` metres.
function tiled(t, sx, sz, per) {
  const c = t.clone();
  c.repeat.set(sx / per, sz / per);
  c.needsUpdate = true;
  return c;
}

const texFloor = tex(512, 512, (g, w, h) => {
  g.fillStyle = '#ebe8e1'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 1800; i++) {
    const v = (225 + rnd() * 25) | 0;
    g.fillStyle = `rgba(${v},${v},${v - 4},0.18)`;
    g.fillRect(rnd() * w, rnd() * h, 3, 3);
  }
  g.strokeStyle = '#c9c3b8'; g.lineWidth = 2; g.strokeRect(0, 0, w, h);
});

const texWall = tex(512, 512, (g, w, h) => {
  g.fillStyle = '#d3cfc6'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 6000; i++) {
    const v = (200 + rnd() * 30) | 0;
    g.fillStyle = `rgba(${v},${v},${v},0.06)`;
    g.fillRect(rnd() * w, rnd() * h, 2, 2);
  }
});

const texWood = tex(512, 512, (g, w, h) => {
  g.fillStyle = '#7b5236'; g.fillRect(0, 0, w, h);
  for (let i = 0; i < 220; i++) {
    g.strokeStyle = `rgba(40,20,10,${rnd() * 0.25})`;
    g.lineWidth = 0.5 + rnd() * 1.5;
    const y = rnd() * h;
    g.beginPath();
    g.moveTo(0, y);
    g.bezierCurveTo(w * 0.3, y + rnd() * 10 - 5, w * 0.6, y + rnd() * 10 - 5, w, y + rnd() * 6 - 3);
    g.stroke();
  }
});

const texFluted = tex(256, 256, (g, w, h) => {
  for (let x = 0; x < w; x += 8) {
    const v = (170 + Math.sin(x / 8) * 30) | 0;
    g.fillStyle = `rgb(${v},${v + 4},${v + 8})`;
    g.fillRect(x, 0, 8, h);
  }
});

const texScreen = tex(256, 160, (g, w, h) => {
  const s = g.createLinearGradient(0, 0, 0, h);
  s.addColorStop(0, '#14306b'); s.addColorStop(1, '#2a6fb8');
  g.fillStyle = s; g.fillRect(0, 0, w, h);
  g.fillStyle = 'rgba(255,255,255,0.25)';
  g.fillRect(12, 14, 120, 8); g.fillRect(12, 30, 200, 4); g.fillRect(12, 40, 160, 4); g.fillRect(12, 50, 180, 4);
});

const texTV = tex(512, 288, (g, w, h) => {
  const s = g.createLinearGradient(0, 0, 0, h);
  s.addColorStop(0, '#05070f'); s.addColorStop(1, '#0c2a55');
  g.fillStyle = s; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(80,160,255,0.35)'; g.lineWidth = 1.5;
  for (let i = 0; i < 40; i++) {
    g.beginPath(); g.moveTo(w / 2, h * 0.9);
    g.lineTo(w / 2 + (i - 20) * 40, 0); g.stroke();
  }
  const glow = g.createRadialGradient(w / 2, h * 0.5, 4, w / 2, h * 0.5, 160);
  glow.addColorStop(0, 'rgba(120,190,255,0.7)'); glow.addColorStop(1, 'rgba(120,190,255,0)');
  g.fillStyle = glow; g.fillRect(0, 0, w, h);
});

// Dusk garden seen through the office window.
const texGarden = tex(1024, 512, (g, w, h) => {
  const s = g.createLinearGradient(0, 0, 0, h * 0.6);
  s.addColorStop(0, '#2c3352'); s.addColorStop(0.7, '#6d6a86'); s.addColorStop(1, '#c7a07a');
  g.fillStyle = s; g.fillRect(0, 0, w, h * 0.6);
  g.fillStyle = '#8a8f98'; g.fillRect(0, h * 0.36, w, h * 0.14);
  g.fillStyle = '#2b3a2a'; g.fillRect(0, h * 0.5, w, h * 0.5);
  g.fillStyle = '#1c2a1f';
  for (let x = 0; x < w; x += 60) { g.beginPath(); g.ellipse(x + 30, h * 0.52, 40, 28, 0, 0, Math.PI * 2); g.fill(); }
  for (let i = 0; i < 8; i++) {
    const x = 80 + i * 120 + rnd() * 30, y = h * 0.66;
    const gr = g.createRadialGradient(x, y, 2, x, y, 90);
    gr.addColorStop(0, 'rgba(255,220,150,0.9)'); gr.addColorStop(1, 'rgba(255,200,120,0)');
    g.fillStyle = gr; g.fillRect(x - 90, y - 90, 180, 180);
    g.fillStyle = '#fff3d0'; g.fillRect(x - 3, y - 3, 6, 6);
  }
});

const texPlaque = tex(256, 128, (g, w, h) => {
  g.fillStyle = '#e9e7e2'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#8a6a3a'; g.font = 'bold 72px sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText('▲ 3 ▼', w / 2, h / 2);
});

// ---------- materials ----------
const M = {
  wall: new THREE.MeshStandardMaterial({ map: tiled(texWall, 1, 1, 2), roughness: 0.95, side: THREE.DoubleSide }),
  ceil: new THREE.MeshStandardMaterial({ color: 0xf2f0eb, roughness: 1 }),
  wood: new THREE.MeshStandardMaterial({ map: texWood, roughness: 0.5 }),
  woodDark: new THREE.MeshStandardMaterial({ color: 0x3a261b, roughness: 0.55 }),
  frame: new THREE.MeshStandardMaterial({ color: 0x17181a, roughness: 0.35, metalness: 0.5 }),
  glass: new THREE.MeshPhysicalMaterial({ color: 0xdde9ee, transparent: true, opacity: 0.16, roughness: 0.05, depthWrite: false, side: THREE.DoubleSide }),
  fluted: new THREE.MeshStandardMaterial({ map: texFluted, roughness: 0.35, transparent: true, opacity: 0.8, side: THREE.DoubleSide }),
  white: new THREE.MeshStandardMaterial({ color: 0xf5f5f3, roughness: 0.45 }),
  deskTop: new THREE.MeshStandardMaterial({ color: 0xd9d4cb, roughness: 0.4 }),
  mesh: new THREE.MeshStandardMaterial({ color: 0x5f6468, roughness: 0.8 }),
  chrome: new THREE.MeshStandardMaterial({ color: 0xbfc4c8, roughness: 0.25, metalness: 0.9 }),
  leather: new THREE.MeshStandardMaterial({ color: 0x5a4632, roughness: 0.55 }),
  imac: new THREE.MeshStandardMaterial({ color: 0xe7e7ea, roughness: 0.3 }),
  screen: new THREE.MeshBasicMaterial({ map: texScreen }),
  tvScreen: new THREE.MeshBasicMaterial({ map: texTV }),
  blue: new THREE.MeshStandardMaterial({ color: 0x1f3d86, roughness: 0.85 }),
  binder: new THREE.MeshStandardMaterial({ color: 0x1f3a6e, roughness: 0.6 }),
  mug: new THREE.MeshStandardMaterial({ color: 0xc41e2a, roughness: 0.35 }),
  leaf: new THREE.MeshStandardMaterial({ color: 0x2e6a35, roughness: 0.6 }),
  pot: new THREE.MeshStandardMaterial({ color: 0xe9e6e0, roughness: 0.6 }),
  beige: new THREE.MeshStandardMaterial({ color: 0xd6bf9c, roughness: 0.9 }),
  brownDoor: new THREE.MeshStandardMaterial({ color: 0x4e2b1a, roughness: 0.5 }),
  gold: new THREE.MeshStandardMaterial({ color: 0xc8a050, metalness: 1, roughness: 0.3 }),
  brushed: new THREE.MeshStandardMaterial({ color: 0x9b9489, metalness: 0.7, roughness: 0.35 }),
  elevWood: new THREE.MeshStandardMaterial({ color: 0x5b5751, roughness: 0.6 }),
  lawn: new THREE.MeshStandardMaterial({ color: 0x3a4a34, roughness: 1 }),
  light: new THREE.MeshBasicMaterial({ color: 0xfff3e0 }),
};
const BINDER_COLORS = [0x1f3a6e, 0xa33b2f, 0xe6dccb, 0x2e5c45, 0xc9a14a, 0x3a3a3a, 0x7a2e6e];

// ---------- helpers ----------
const B = (w, h, d) => new THREE.BoxGeometry(w, h, d);
function mesh(geo, mat, x, y, z) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.castShadow = true;
  m.receiveShadow = true;
  return m;
}
const put = (m) => { scene.add(m); return m; };

// Full-height wall along an axis-aligned line.
function wallSeg(x0, z0, x1, z1) {
  return wallRange(x0, z0, x1, z1, 0, CEIL);
}
function wallRange(x0, z0, x1, z1, y0, y1) {
  const len = Math.hypot(x1 - x0, z1 - z0);
  const h = y1 - y0;
  const cx = (x0 + x1) / 2, cz = (z0 + z1) / 2;
  const alongX = Math.abs(x1 - x0) > Math.abs(z1 - z0);
  return put(alongX
    ? mesh(B(len, h, T), M.wall, cx, y0 + h / 2, cz)
    : mesh(B(T, h, len), M.wall, cx, y0 + h / 2, cz));
}
// Thin glass pane along an axis-aligned line.
function pane(x0, z0, x1, z1, y0, y1, mat = M.glass) {
  const len = Math.hypot(x1 - x0, z1 - z0);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(len, y1 - y0), mat);
  m.position.set((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  if (Math.abs(x1 - x0) < Math.abs(z1 - z0)) m.rotation.y = Math.PI / 2;
  return put(m);
}

function imac(x, y, z, rot) {
  const g = new THREE.Group();
  g.add(mesh(B(0.2, 0.012, 0.16), M.imac, 0, y + 0.006, 0));
  g.add(mesh(B(0.05, 0.22, 0.04), M.imac, 0, y + 0.12, -0.02));
  g.add(mesh(B(0.56, 0.36, 0.035), M.imac, 0, y + 0.37, -0.03));
  const scr = new THREE.Mesh(B(0.52, 0.31, 0.005), M.screen);
  scr.position.set(0, y + 0.37, 0.0);
  g.add(scr);
  g.position.set(x, 0, z);
  g.rotation.y = rot;
  return put(g);
}

function chair(x, z, rot, mat = M.mesh) {
  const g = new THREE.Group();
  g.add(mesh(B(0.5, 0.08, 0.5), mat, 0, 0.47, 0));
  g.add(mesh(B(0.48, 0.55, 0.06), mat, 0, 0.8, -0.24));
  g.add(mesh(new THREE.CylinderGeometry(0.025, 0.025, 0.42, 10), M.chrome, 0, 0.25, 0));
  g.add(mesh(new THREE.CylinderGeometry(0.28, 0.28, 0.03, 16), M.chrome, 0, 0.05, 0));
  g.position.set(x, 0, z);
  g.rotation.y = rot;
  return put(g);
}

// Two-sided workstation row. s = side the seats are on (+1 or -1).
function desk(x0, x1, z, s) {
  const len = x1 - x0;
  put(mesh(B(len, 0.035, 0.8), M.deskTop, (x0 + x1) / 2, 0.75, z));
  put(mesh(B(0.05, 0.72, 0.72), M.mesh, x0 + 0.1, 0.36, z));
  put(mesh(B(0.05, 0.72, 0.72), M.mesh, x1 - 0.1, 0.36, z));
  for (let i = 0; i < 4; i++) {
    const x = x0 + len * (i + 0.5) / 4;
    imac(x, 0.77, z, s > 0 ? 0 : Math.PI);
    chair(x, z + s * 0.9, s > 0 ? Math.PI : 0);
    put(mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.095, 16), M.mug, x + 0.3, 0.82, z + s * 0.1));
    put(mesh(B(0.07, 0.28, 0.24), M.binder, x - 0.3, 0.91, z - s * 0.05));
  }
}

function plant(x, z, s = 1) {
  const g = new THREE.Group();
  g.add(mesh(new THREE.CylinderGeometry(0.2 * s, 0.17 * s, 0.42 * s, 20), M.pot, 0, 0.21 * s, 0));
  for (let i = 0; i < 14; i++) {
    const a = rnd() * Math.PI * 2;
    const r = (0.08 + rnd() * 0.22) * s;
    const h = (0.55 + rnd() * 0.5) * s;
    const leaf = mesh(new THREE.SphereGeometry(1, 12, 8), M.leaf, Math.cos(a) * r, h, Math.sin(a) * r);
    leaf.scale.set(0.09 * s, 0.32 * s, 0.2 * s);
    leaf.rotation.set(rnd() * 0.8 - 0.4, a, rnd() * 0.8 - 0.4);
    g.add(leaf);
  }
  g.position.set(x, 0, z);
  return put(g);
}

// Tall storage with binders. w runs along local x; the front faces +z.
function shelf(x, z, w, h, rot, depth = 0.36) {
  const g = new THREE.Group();
  g.add(mesh(B(w, h, depth), M.woodDark, 0, h / 2, 0));
  const rows = Math.max(2, Math.round(h / 0.36));
  const rowH = h / rows;
  for (let r = 0; r < rows; r++) {
    const y = r * rowH + 0.02;
    for (let x0 = -w / 2 + 0.05; x0 < w / 2 - 0.05; x0 += 0.09) {
      if (rnd() < 0.15) continue;
      const c = BINDER_COLORS[(rnd() * BINDER_COLORS.length) | 0];
      const bm = new THREE.MeshStandardMaterial({ color: c, roughness: 0.6 });
      g.add(mesh(B(0.07, rowH * 0.8, 0.22), bm, x0, y + rowH * 0.4, depth / 2 + 0.01));
    }
  }
  g.position.set(x, 0, z);
  g.rotation.y = rot;
  return put(g);
}

function armchair(x, z, rot) {
  const g = new THREE.Group();
  g.add(mesh(B(0.8, 0.36, 0.8), M.blue, 0, 0.3, 0));
  g.add(mesh(B(0.8, 0.5, 0.16), M.blue, 0, 0.62, -0.32));
  g.add(mesh(B(0.14, 0.3, 0.8), M.blue, -0.4, 0.45, 0));
  g.add(mesh(B(0.14, 0.3, 0.8), M.blue, 0.4, 0.45, 0));
  for (const [lx, lz] of [[-0.3, -0.3], [0.3, -0.3], [-0.3, 0.3], [0.3, 0.3]]) {
    g.add(mesh(B(0.04, 0.12, 0.04), M.woodDark, lx, 0.06, lz));
  }
  g.position.set(x, 0, z);
  g.rotation.y = rot;
  return put(g);
}

// Three-seat waiting bench, backed against a wall at x = wallX, seats running along z.
function bench(wallX, z0, n = 3) {
  const g = new THREE.Group();
  const zc = z0 + (n - 1) * 0.85 / 2;
  for (let i = 0; i < n; i++) {
    const z = z0 + i * 0.85;
    g.add(mesh(B(0.55, 0.09, 0.8), M.beige, wallX + 0.4, 0.46, z));
    g.add(mesh(B(0.12, 0.5, 0.8), M.beige, wallX + 0.12, 0.74, z));
    g.add(mesh(B(0.5, 0.03, 0.05), M.chrome, wallX + 0.4, 0.66, z - 0.42));
    g.add(mesh(B(0.5, 0.03, 0.05), M.chrome, wallX + 0.4, 0.66, z + 0.42));
  }
  g.add(mesh(B(0.5, 0.03, n * 0.85), M.frame, wallX + 0.4, 0.2, zc));
  g.add(mesh(B(0.03, 0.4, n * 0.85), M.frame, wallX + 0.4, 0.3, zc));
  return put(g);
}

function column(x, z) {
  return put(mesh(B(0.4, CEIL, 0.4), M.white, x, CEIL / 2, z));
}

// ---------- shell: floors, ceilings, exterior ----------
const floorMat = tiled(texFloor, 22.6, 18, 1.2);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(22.6, 18), new THREE.MeshStandardMaterial({ map: floorMat, roughness: 0.55 }));
floor.rotation.x = -Math.PI / 2; floor.position.set(11.3, 0, 9); floor.receiveShadow = true; put(floor);

const floor2 = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), new THREE.MeshStandardMaterial({ map: tiled(texFloor, 6, 5, 1.2), roughness: 0.55 }));
floor2.rotation.x = -Math.PI / 2; floor2.position.set(3, 0, 20.5); floor2.receiveShadow = true; put(floor2);

const ceilGroup = new THREE.Group();
const ceil1 = new THREE.Mesh(new THREE.PlaneGeometry(22.6, 18), M.ceil);
ceil1.rotation.x = Math.PI / 2; ceil1.position.set(11.3, CEIL, 9);
const ceil2 = new THREE.Mesh(new THREE.PlaneGeometry(6, 5), M.ceil);
ceil2.rotation.x = Math.PI / 2; ceil2.position.set(3, CEIL, 20.5);
ceilGroup.add(ceil1, ceil2);
scene.add(ceilGroup);
if (CUT) ceilGroup.visible = false;

// Outside: lawn and garden backdrop seen through the window.
const ground = new THREE.Mesh(new THREE.PlaneGeometry(300, 300), M.lawn);
ground.rotation.x = -Math.PI / 2; ground.position.y = -0.05; put(ground);
const backdrop = new THREE.Mesh(new THREE.PlaneGeometry(60, 8), new THREE.MeshBasicMaterial({ map: texGarden }));
backdrop.rotation.y = -Math.PI / 2; backdrop.position.set(26, 2.6, 9);
scene.add(backdrop);
if (CUT) backdrop.visible = false;

// ---------- walls ----------
// Corridor (left wall x=0, right wall x=2.6)
wallSeg(0, 0, 0, 0.4);
wallRange(0, 0.4, 0, 1.8, 2.45, CEIL);                 // header over elevator opening
wallSeg(0, 1.8, 0, 7.0);
wallRange(0, 7.0, 0, 9.0, 2.15, CEIL);                 // header over brown double door
wallSeg(0, 9.0, 0, 18);
wallSeg(0, 18, 0, 23);                                  // lounge outer wall
wallSeg(2.6, 0, 2.6, 2.5);
wallRange(2.6, 2.5, 2.6, 5.5, 2.3, CEIL);              // header over office entry
wallSeg(2.6, 5.5, 2.6, 18);

// Back wall of corridor and office (exterior), long side of office
wallSeg(0, 0, 22.6, 0);
// Far wall (z=18) with frosted door to lounge
wallSeg(0, 18, 0.2, 18);
wallRange(0.2, 18, 2.4, 18, 2.3, CEIL);
wallSeg(2.4, 18, 22.6, 18);
// Lounge
wallSeg(6, 18, 6, 23);
wallSeg(0, 23, 6, 23);
// Exterior east wall with horizontal window
wallSeg(22.6, 0, 22.6, 9);
wallRange(22.6, 9, 22.6, 15, 0, 1.0);
wallRange(22.6, 9, 22.6, 15, 2.2, CEIL);
wallSeg(22.6, 15, 22.6, 18);
pane(22.6, 9, 22.6, 15, 1.0, 2.2).rotation.y = 0;
// Window frame
put(mesh(B(0.06, 0.06, 6), M.frame, 22.6, 2.2, 12));
put(mesh(B(0.06, 0.06, 6), M.frame, 22.6, 1.0, 12));

// Manager office (z 12-18, x 14.5-22.6) with glass front and glass door
wallSeg(14.5, 12, 14.5, 18);
pane(14.5, 12, 17.2, 12, 0.05, CEIL - 0.1);
pane(18.4, 12, 22.6, 12, 0.05, CEIL - 0.1);
put(mesh(B(0.06, CEIL, 0.06), M.frame, 14.5, CEIL / 2, 12));
put(mesh(B(0.06, CEIL, 0.06), M.frame, 17.2, CEIL / 2, 12));
put(mesh(B(0.06, CEIL, 0.06), M.frame, 18.4, CEIL / 2, 12));
put(mesh(B(0.06, CEIL, 0.06), M.frame, 22.6, CEIL / 2, 12));
put(mesh(B(8.1, 0.06, 0.06), M.frame, 18.55, CEIL - 0.03, 12));

// ---------- corridor details ----------
// Elevator (left wall, z 0.4-1.8) with dark grain surround and floor plaque "3"
put(mesh(B(0.04, 2.25, 1.4), M.brushed, 0.1, 1.125, 1.1));
put(mesh(B(0.2, 0.9, 2.0), M.elevWood, 0.1, 2.85, 1.1));
put(mesh(B(0.2, 2.45, 0.12), M.elevWood, 0.1, 1.225, 0.36));
put(mesh(B(0.2, 2.45, 0.12), M.elevWood, 0.1, 1.225, 1.84));
const plaque = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.2), new THREE.MeshStandardMaterial({ map: texPlaque, roughness: 0.4 }));
plaque.rotation.y = Math.PI / 2; plaque.position.set(0.21, 2.75, 1.1); scene.add(plaque);
// Call buttons
put(mesh(B(0.02, 0.2, 0.1), M.white, 0.14, 1.2, 2.0));

// Brown double door (left wall, z 7-9) with gold handles
put(mesh(B(0.06, 2.15, 0.98), M.brownDoor, 0.1, 1.075, 7.5));
put(mesh(B(0.06, 2.15, 0.98), M.brownDoor, 0.1, 1.075, 8.5));
put(mesh(B(0.04, 0.04, 0.22), M.gold, 0.16, 1.0, 7.9));
put(mesh(B(0.04, 0.04, 0.22), M.gold, 0.16, 1.0, 8.1));

// Waiting bench along left wall, z 10-12.5
bench(0, 10.3, 3);

// Wood cabinet on left wall
put(mesh(B(0.45, 2.0, 2.0), M.wood, 0.225, 1.0, 15.0));

// Frosted sliding panels, parked beside the office entry (x=2.6, z 1.2-2.5)
put(mesh(B(0.03, 2.2, 1.3), M.fluted, 2.45, 1.1, 1.85));
put(mesh(B(0.04, 0.05, 1.3), M.frame, 2.45, 2.2, 1.85));

// Frosted triple panel door at the corridor end (z=18)
const endDoor = mesh(B(2.2, 2.3, 0.03), M.fluted, 1.3, 1.15, 18.0);
put(endDoor);
put(mesh(B(2.2, 0.04, 0.05), M.frame, 1.3, 2.3, 18.0));

// ---------- lounge ----------
armchair(4.4, 20.4, -Math.PI / 2);
{
  const t = mesh(B(1.1, 0.04, 0.6), M.marble ?? M.white, 2.9, 0.42, 21.0);
  put(t);
  put(mesh(B(0.9, 0.38, 0.4), M.woodDark, 2.9, 0.19, 21.0));
}
put(mesh(B(0.5, 1.2, 1.8), M.wood, 0.25, 0.6, 21.5));
plant(5.4, 22.2, 1.2);

// ---------- open office ----------
// Reception counter facing the entry, staff on the back side
put(mesh(B(5, 1.05, 0.65), M.wood, 10, 0.525, 1.5));
put(mesh(B(5.1, 0.05, 0.75), M.deskTop, 10, 1.075, 1.5));
imac(9.0, 1.1, 1.5, Math.PI);
imac(11.0, 1.1, 1.5, Math.PI);
chair(9.0, 0.7, 0);
chair(11.0, 0.7, 0);

// Two workstation rows
desk(8, 17, 6.5, -1);
desk(8, 17, 10.5, 1);

// Columns
column(11.6, 4.0);
column(17.2, 4.0);
column(9.0, 13.0);

// Library against the corridor wall (office side)
shelf(2.7, 11.0, 2.4, 2.1, Math.PI / 2);
shelf(3.0, 15.0, 2.4, 0.9, Math.PI / 2);

// Plants
plant(3.6, 17.0, 1.0);
plant(22.0, 0.9, 1.0);

// ---------- manager office ----------
// Executive desk (back to the window side), visitor chairs, pedestal, whiteboard, cabinet, TV
put(mesh(B(2.4, 0.04, 0.9), M.wood, 19.6, 0.75, 15.8));
put(mesh(B(0.6, 0.72, 0.84), M.woodDark, 18.6, 0.36, 15.8));
imac(19.6, 0.77, 15.6, 0);
chair(18.8, 14.6, 0);
chair(20.4, 14.6, 0);
chair(19.6, 16.6, Math.PI, M.leather);
// Whiteboard on wheeled stand
put(mesh(B(0.04, 1.2, 1.6), M.white, 14.75, 1.5, 16.2));
put(mesh(B(0.02, 0.1, 1.5), M.chrome, 14.75, 0.9, 16.2));
// Cream storage cabinet
put(mesh(B(0.5, 2.2, 1.4), M.white, 22.3, 1.1, 16.6));
// TV on the back wall
put(mesh(B(1.6, 0.92, 0.05), M.frame, 18.5, 1.6, 17.85));
const tvFace = new THREE.Mesh(new THREE.PlaneGeometry(1.52, 0.84), M.tvScreen);
tvFace.position.set(18.5, 1.6, 17.81);
tvFace.rotation.y = Math.PI;
put(tvFace);
// Visitor-facing side: plant
plant(21.8, 13.0, 1.0);

// ---------- ceiling lights ----------
const LIGHTS = [
  [1.3, 3], [1.3, 9], [1.3, 15],
  [6, 4], [12, 4], [18, 4],
  [6, 9], [12, 9], [18, 9],
  [8, 15], [14, 15],
  [3, 20.5], [18.5, 15.5],
];
for (const [x, z] of LIGHTS) {
  const strip = new THREE.Mesh(B(0.6, 0.02, 1.2), M.light);
  strip.position.set(x, CEIL - 0.005, z);
  scene.add(strip);
  const pl = new THREE.PointLight(0xfff1dd, 9, 0, 2);
  pl.position.set(x, CEIL - 0.25, z);
  scene.add(pl);
}

// Hemisphere fill and dusk light coming in through the window
scene.add(new THREE.HemisphereLight(0xfff7ec, 0x8c8474, 0.7));
const sun = new THREE.DirectionalLight(0xcfd8ff, 1.0);
sun.position.set(34, 6, 9);
sun.target.position.set(12, 0, 9);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -16, right: 16, top: 16, bottom: -16, near: 1, far: 90 });
sun.shadow.camera.updateProjectionMatrix();
sun.shadow.bias = -0.0005;
sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);

// ---------- camera paths ----------
// Walkthrough keyframes: [position, look-at]
const KEYS = [
  [[1.3, 1.55, 0.7], [1.3, 1.4, 8]],          // enter corridor
  [[1.3, 1.55, 3.9], [6.0, 1.35, 4.2]],       // turn toward office door
  [[3.2, 1.6, 4.2], [12.0, 1.3, 5.2]],        // step into the office
  [[7.0, 1.6, 8.5], [18.0, 1.2, 8.5]],        // walk the aisle between workstations
  [[17.8, 1.6, 8.4], [17.8, 1.3, 14.5]],      // to the manager office door
  [[18.0, 1.6, 13.2], [21.5, 1.3, 15.0]],     // look around the manager office
  [[17.8, 1.6, 11.0], [12.0, 1.4, 2.5]],      // back out, look to reception
  [[10.6, 1.6, 4.6], [10.0, 1.1, 0.8]],       // end at reception
];
const posCurve = new THREE.CatmullRomCurve3(KEYS.map((k) => new THREE.Vector3(...k[0])), false, 'centripetal');
const lookCurve = new THREE.CatmullRomCurve3(KEYS.map((k) => new THREE.Vector3(...k[1])), false, 'centripetal');

window.frame = (t) => {
  camera.position.copy(posCurve.getPoint(t));
  camera.lookAt(lookCurve.getPoint(t));
  renderer.render(scene, camera);
  return renderer.domElement.toDataURL('image/jpeg', 0.92);
};
window.view = (p, l, format = 'png') => {
  camera.position.set(...p);
  camera.lookAt(...l);
  renderer.render(scene, camera);
  return renderer.domElement.toDataURL(format === 'jpg' ? 'image/jpeg' : 'image/png', 0.95);
};
window.ready = true;

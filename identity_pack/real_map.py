"""Real street geometry of the office area (extracted from the supplied map screenshot) rendered in the
Tripoli-B identity: flat, or 3-D (extruded city blocks + perspective tilt)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy import ndimage as ndi

PIN = (595, 965)                                   # office, in cropped-mask coordinates (980 x 1575)
SCALE_PX_PER_M = 1.2                               # from the screenshot's 100 m scale bar
LANDMARKS = [                                      # names read from the supplied screenshot
    dict(name="مستشفى الساقية التخصصي", pos=(770, 405)),
    dict(name="شنابو زناتة الجديدة", pos=(272, 713)),
    dict(name="ليبيا توزيع - فرع زناتة الجديدة", pos=(465, 785)),
    dict(name="درب السبيل لخدمات التوصيل", pos=(940, 905)),
    dict(name="مقهى الحاج فتحي", pos=(768, 1313)),
    dict(name="بيتزا السمعة", pos=(130, 440)),
]

def distance_m(pos):
    return math.hypot(pos[0] - PIN[0], pos[1] - PIN[1]) / SCALE_PX_PER_M

def _roads():
    m = Image.open("mapdata/roads_all.png").convert("L")
    d = ImageDraw.Draw(m)
    for e in [(700, 860, 975, 975)]:               # leftover grey label "درب السبيل ..." (cropped coords)
        d.rectangle(e, fill=0)
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))      # close tiny gaps
    return m

def _major(road, scale):
    m0 = road.filter(ImageFilter.MinFilter(13)).filter(ImageFilter.MaxFilter(17))
    arr = np.asarray(m0) > 0
    lab, n = ndi.label(arr)
    if n == 0:
        return m0
    sizes = ndi.sum(arr, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, a in enumerate(sizes) if a > 2600 * scale * scale])
    out = Image.fromarray((keep * 255).astype("uint8"))
    return out.filter(ImageFilter.MaxFilter(5))

def window_for(landmarks_pos, pad=70, aspect=None):
    xs = [p[0] for p in landmarks_pos] + [PIN[0]]; ys = [p[1] for p in landmarks_pos] + [PIN[1]]
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    if aspect:
        w, h = x1 - x0, y1 - y0
        if max(w, h * aspect) > 980:
            print('warning: landmarks do not fit the frame aspect', round(w), round(h))
        if w / h < aspect: x0 -= (h * aspect - w) / 2; x1 += (h * aspect - w) / 2
        else: y0 -= (w / aspect - h) / 2; y1 += (w / aspect - h) / 2
    # keep the window inside the extracted map (980 x 1575): shift, don't stretch
    if x1 > 980: x0 -= x1 - 980; x1 = 980
    if x0 < 0: x1 -= x0; x0 = 0
    if y1 > 1575: y0 -= y1 - 1575; y1 = 1575
    if y0 < 0: y1 -= y0; y0 = 0
    return [x0, y0, x1, y1]

def _crop(mask, win, scale):
    x0, y0, x1, y1 = win
    sw, sh = int((x1 - x0) * scale), int((y1 - y0) * scale)
    out = Image.new("L", (sw, sh), 0)
    src = mask.crop((int(max(0, x0)), int(max(0, y0)), int(min(980, x1)), int(min(1575, y1))))
    out.paste(src.resize((int((src.size[0]) * scale), int(src.size[1] * scale)), Image.LANCZOS),
              (int(max(0, -x0) * scale), int(max(0, -y0) * scale)))
    return out.point(lambda v: 255 if v > 110 else 0)

def to_out(win, scale):
    return lambda p: ((p[0] - win[0]) * scale, (p[1] - win[1]) * scale)

# ---------------------------------------------------------------------------------------- flat
def flat(win, width, pal):
    scale = width / (win[2] - win[0])
    road = _crop(_roads(), win, scale)
    major = _major(road, scale)
    sw, sh = road.size
    img = Image.new("RGB", (sw, sh), pal["block"])
    arr = np.asarray(img).copy()
    # block shading: every enclosed block gets a slightly different tint (keeps the map lively)
    lab, n = ndi.label(np.asarray(road) == 0)
    rnd = random.Random(3)
    tints = np.array([[rnd.uniform(-1, 1)] for _ in range(n + 1)])
    base = np.array(pal["block"], float)
    shade = (tints[lab][..., 0:1] * np.array(pal["tint"], float)[None, None])
    arr = np.clip(base[None, None] + shade, 0, 255).astype("uint8")
    img = Image.fromarray(arr)
    img.paste(Image.new("RGB", img.size, pal["edge"]), (0, 0), road.filter(ImageFilter.MaxFilter(5)))
    img.paste(Image.new("RGB", img.size, pal["road"]), (0, 0), road)
    img.paste(Image.new("RGB", img.size, pal["major"]), (0, 0), major)
    return img, to_out(win, scale)

# ---------------------------------------------------------------------------------------- 3-D
def _homography(src, dst):
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    h = np.linalg.solve(np.array(A, float), np.array([c for p in dst for c in p], float))
    return np.append(h, 1).reshape(3, 3)

def iso(win, width, pal, squash=.56, inset=.16, seed=5, hq_roof=None, neighbor=None, front_road=False):
    """neighbor=(wall, roof) highlights the lot touching the office lot (e.g. the Jotun paints shop); its projected roof centre is returned as project.neighbor."""
    scale = width / (win[2] - win[0])
    road = _crop(_roads(), win, scale)
    major = _major(road, scale)
    sw, sh = road.size
    free = np.asarray(road) == 0
    # split the blocks into building lots, aligned with the street direction (~54 deg)
    ys_, xs_ = np.mgrid[0:sh, 0:sw].astype(np.float32)
    th = math.radians(54)
    u = xs_ * math.cos(th) + ys_ * math.sin(th); v = -xs_ * math.sin(th) + ys_ * math.cos(th)
    cs = 88 * scale; gw = 5 * scale
    gap = ((u % cs) < gw) | ((v % (cs * .85)) < gw)
    lots = free & ~gap
    lab, n = ndi.label(lots)
    blab, bn = ndi.label(free)
    areas = ndi.sum(free, blab, range(1, bn + 1))
    ox, oy = to_out(win, scale)(PIN)
    ys, xs = np.nonzero(lots)
    k = int(np.argmin((xs - ox) ** 2 + (ys - oy) ** 2)); pin_lab = lab[ys[k], xs[k]]
    nb_lab = None; nb_xy_ok = False
    if neighbor:
        cents = ndi.center_of_mass(lots, lab, range(1, n + 1)); hq_c = cents[pin_lab - 1]
        objs0 = ndi.find_objects(lab); cand = []
        touch = set(np.unique(lab[ndi.binary_dilation(lab == pin_lab, iterations=max(2, int(7 * scale)))]).tolist()) - {0, pin_lab}
        for i in touch:
            sl0 = objs0[i - 1]; m0 = lab[sl0] == i; a0 = int(m0.sum())
            if a0 < 200 * scale * scale or areas[blab[sl0][m0][0] - 1] > .35 * sw * sh: continue
            cand.append((-a0, i))
        if not cand:
            cand = [(math.hypot(c[1] - hq_c[1], c[0] - hq_c[0]), i + 1) for i, c in enumerate(cents) if i + 1 != pin_lab]
        nb_lab = min(cand)[1]
    pad_top = int(150 * scale)
    img = Image.new("RGBA", (sw, sh + pad_top), (0, 0, 0, 0))
    ground = Image.new("RGBA", (sw, sh), pal["road"] + (255,))
    ground.paste(Image.new("RGBA", road.size, pal["edge"] + (255,)), (0, 0), road.filter(ImageFilter.MaxFilter(3)))
    ground.paste(Image.new("RGBA", road.size, pal["roadline"] + (255,)), (0, 0), road)
    ground.paste(Image.new("RGBA", road.size, pal["major"] + (255,)), (0, 0), major)
    gmask = Image.fromarray((free * 255).astype("uint8"))
    ground.paste(Image.new("RGBA", road.size, pal["block"] + (255,)), (0, 0), gmask)          # ground inside blocks
    if front_road and nb_lab:
        cents2 = ndi.center_of_mass(lots, lab, [pin_lab, nb_lab]); (hy_, hx_), (ny_, nx_) = cents2
        dx_, dy_ = nx_ - hx_, ny_ - hy_; L_ = math.hypot(dx_, dy_) or 1; dx_, dy_ = dx_ / L_, dy_ / L_
        nx2, ny2 = -dy_, dx_
        rd = np.asarray(road) > 0
        def score(sg):
            tot = 0
            for k in range(20, int(90 * scale), 4):
                for t in (-60, 0, 60):
                    px_ = int(hx_ + nx2 * sg * k + dx_ * t * scale); py_ = int(hy_ + ny2 * sg * k + dy_ * t * scale)
                    if 0 <= px_ < sw and 0 <= py_ < sh and rd[py_, px_]: tot += 1
            return tot
        sg = 1 if score(1) >= score(-1) else -1
        ys_l, xs_l = np.nonzero(lab == pin_lab); depth = float(((xs_l - hx_) * nx2 * sg + (ys_l - hy_) * ny2 * sg).max())
        rw = 40 * scale; off = depth + rw * .5 + 6 * scale
        mx_, my_ = (hx_ + nx_) / 2 + nx2 * sg * off, (hy_ + ny_) / 2 + ny2 * sg * off
        ext = 2400 * scale; a_ = (mx_ - dx_ * ext, my_ - dy_ * ext); b_ = (mx_ + dx_ * ext, my_ + dy_ * ext)
        rl = Image.new("L", ground.size, 0); rdr = ImageDraw.Draw(rl)
        rdr.line([a_, b_], fill=255, width=int(rw + 8 * scale)); edge_m = rl.copy()
        rl2 = Image.new("L", ground.size, 0); ImageDraw.Draw(rl2).line([a_, b_], fill=255, width=int(rw)); 
        ground.paste(Image.new("RGBA", ground.size, (214, 196, 150, 255)), (0, 0), edge_m)
        ground.paste(Image.new("RGBA", ground.size, (92, 88, 84, 255)), (0, 0), rl2)
        gd = ImageDraw.Draw(ground); seg = 26 * scale; n_ = int(2 * ext / (seg * 2))
        for q in range(n_):
            t0 = -ext + q * 2 * seg; t1 = t0 + seg
            gd.line([(mx_ + dx_ * t0, my_ + dy_ * t0), (mx_ + dx_ * t1, my_ + dy_ * t1)], fill=(250, 245, 230, 255), width=max(2, int(3 * scale)))
        band = np.asarray(ImageChops.add(rl, Image.new('L', rl.size, 0))) > 0
    img.paste(ground, (0, pad_top))
    band = band if (front_road and nb_lab) else None
    rnd = random.Random(seed)
    objs = ndi.find_objects(lab)
    order = sorted(range(1, n + 1), key=lambda i: (objs[i - 1][0].start + objs[i - 1][0].stop) / 2)
    for i in order:
        sl = objs[i - 1]
        m_ = lab[sl] == i
        if band is not None and i not in (pin_lab, nb_lab): m_ = m_ & ~band[sl]
        area = int(m_.sum())
        if area < 140 * scale * scale:
            continue
        y0, x0 = sl[0].start, sl[1].start
        # huge free areas (open ground) stay flat
        if areas[blab[sl][m_][0] - 1] > .35 * sw * sh:
            continue
        bm = Image.fromarray((m_ * 255).astype("uint8"))
        is_hq = i == pin_lab; is_nb = i == nb_lab
        h = int((rnd.choice([5, 8, 11, 15, 20, 27]) if not (is_hq or is_nb) else 36) * scale * 1.2)
        wall = pal["hq_wall"] if is_hq else (neighbor[0] if is_nb else pal["wall"])
        k_ = rnd.uniform(.93, 1.0)
        roof = (hq_roof or pal["hq_roof"]) if is_hq else (neighbor[1] if is_nb else tuple(int(c * k_) for c in pal["roof"]))
        if is_nb:
            cy_, cx_ = ndi.center_of_mass(m_); nb_xy = (x0 + cx_, y0 + cy_ + pad_top - h); nb_xy_ok = True
        img.paste(Image.new("RGBA", bm.size, pal["shadow"]), (x0 + int(h * .3), y0 + pad_top + int(h * .12)), bm)
        for t in range(0, h, 2):
            col = tuple(int(c * (0.74 + 0.26 * t / h)) for c in wall) + (255,)
            img.paste(Image.new("RGBA", bm.size, col), (x0, y0 + pad_top - t), bm)
        img.paste(Image.new("RGBA", bm.size, roof + (255,)), (x0, y0 + pad_top - h), bm)
        edge = bm.filter(ImageFilter.MaxFilter(3))
        img.paste(Image.new("RGBA", bm.size, pal["roof_edge"] + (255,)), (x0, y0 + pad_top - h), ImageChops_sub(edge, bm))
    # perspective tilt
    W, Hh = img.size
    dw = width; dh = int(Hh * squash)
    src = [(0, 0), (W, 0), (W, Hh), (0, Hh)]
    dst = [(dw * inset, 0), (dw * (1 - inset), 0), (dw, dh), (0, dh)]
    Hm = _homography(src, dst)
    coef = np.linalg.inv(Hm).flatten()[:8] / np.linalg.inv(Hm)[2, 2]
    out = img.transform((dw, dh), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC)
    def project(p, z=0):
        x, y = to_out(win, scale)(p); y += pad_top - z * scale
        v = Hm @ np.array([x, y, 1.0]); return v[0] / v[2], v[1] / v[2]
    if neighbor and nb_xy_ok:
        v_ = Hm @ np.array([nb_xy[0], nb_xy[1], 1.0]); project.neighbor = (v_[0] / v_[2], v_[1] / v_[2])
    return out, project

def ImageChops_sub(a, b):
    from PIL import ImageChops
    return ImageChops.subtract(a, b)

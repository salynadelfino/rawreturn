"""
Raw Return — placeholder photography renderer: core materials, light and grade.

Every placeholder image on the site is rendered by this package so that they
read as one shoot: the same denim, the same concrete, the same two lights
(available light at the bench, direct flash on the street) and the same film
grade. When the founder's photography arrives, it replaces these files 1:1.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = None  # set by render.py


# ───────────────────────────────────────────────────────────── utilities

def fbm(h, w, rng, scale=64.0, octaves=4, persistence=0.5, aniso=(1.0, 1.0)):
    """Fractal value noise in 0..1 built from upscaled random grids."""
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        sh = max(2, int(h / (scale * aniso[0]) * 2 ** o))
        sw = max(2, int(w / (scale * aniso[1]) * 2 ** o))
        n = rng.random((sh, sw)).astype(np.float32)
        out += amp * cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= persistence
    out /= tot
    lo, hi = np.percentile(out, 0.5), np.percentile(out, 99.5)
    return np.clip((out - lo) / (hi - lo + 1e-6), 0, 1)


def lerp(a, b, t):
    return a + (b - a) * t


def blur(a, sigma):
    if sigma <= 0:
        return a
    k = int(sigma * 3) * 2 + 1
    return cv2.GaussianBlur(a, (k, k), sigma)


def poly_mask(h, w, pts, ss=1):
    """Anti-aliased polygon mask (float 0..1)."""
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).polygon([(x * ss, y * ss) for x, y in pts], fill=255)
    if ss > 1:
        m = m.resize((w, h), Image.LANCZOS)
    return np.asarray(m, np.float32) / 255.0


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def font(name, size, axes=None):
    f = ImageFont.truetype(str(FONT_DIR / name), size)
    if axes:
        try:
            f.set_variation_by_axes(axes)
        except Exception:
            pass
    return f


def mono(size, medium=False):
    return font("IBMPlexMono-Medium.ttf" if medium else "IBMPlexMono-Regular.ttf", size)


def stamp(size, weight=800):
    # Archivo variable: axes are (wght, wdth). wdth 125 = Expanded.
    return font("Archivo[wdth,wght].ttf", size, axes=[weight, 125])


# ───────────────────────────────────────────────────────────── palette (brand)

INDIGO_RAW = hexrgb("#141B33")
INDIGO = hexrgb("#1F2A44")
WORN = hexrgb("#3D5A80")
FADED = hexrgb("#8FA6BF")
BLEACH = hexrgb("#C9D2DA")
ECRU = hexrgb("#EDE6D8")
STONE = hexrgb("#C8C1B3")
CONCRETE = hexrgb("#8A8781")
CHARCOAL = hexrgb("#2B2B2B")
TAN = hexrgb("#C9682F")
SADDLE = hexrgb("#8A4520")
STEEL = hexrgb("#9A9EA3")
BRASS = hexrgb("#8C7A5B")
THREAD_GOLD = hexrgb("#C98A3A")


def wash_color(w):
    """Map a wash level (0 raw → 1 bleached) to indigo yarn colour."""
    xs = np.array([0.0, 0.25, 0.5, 0.78, 1.0], np.float32)
    cs = np.stack([INDIGO_RAW, INDIGO, WORN, FADED, BLEACH])
    w = np.clip(w, 0, 1)
    return np.stack([np.interp(w, xs, cs[:, c]).astype(np.float32) for c in range(3)], -1)


# ───────────────────────────────────────────────────────────── denim

@dataclass
class Wash:
    base: float = 0.35          # overall wash level
    spread: float = 0.22        # mottling amount
    seed: int = 0
    knee: tuple | None = None   # (cx, cy, rx, ry) in local px — fade patch
    whiskers: int = 0
    ghost: tuple | None = None  # (x, y, w, h, angle) — unfaded pocket ghost
    phone: tuple | None = None  # (x, y, w, h) — worn phone outline
    streaks: float = 0.5        # vertical wash streaking
    extra: list = field(default_factory=list)


def denim(h, w, wash: Wash, thread=1.8, angle=0.0, ss=2):
    """Render a woven 3/1 twill denim patch (RGB 0..1) plus a height map.

    thread: warp yarn pitch in output pixels; angle: grain rotation (rad).
    """
    rng = np.random.default_rng(wash.seed)
    H, W = h * ss, w * ss
    t = thread * ss
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    ca, sa = math.cos(angle), math.sin(angle)
    u = (xx * ca + yy * sa) / t
    v = (-xx * sa + yy * ca) / (t * 0.92)
    # yarns are never perfectly straight: domain-warp the weave
    wu = cv2.resize(rng.normal(0, 1, (max(2, H // 40), max(2, W // 40))).astype(np.float32), (W, H),
                    interpolation=cv2.INTER_CUBIC)
    wv = cv2.resize(rng.normal(0, 1, (max(2, H // 40), max(2, W // 40))).astype(np.float32), (W, H),
                    interpolation=cv2.INTER_CUBIC)
    u = u + wu * 0.22
    v = v + wv * 0.22
    j = np.floor(u).astype(np.int64)
    i = np.floor(v).astype(np.int64)
    fu, fv = u - j, v - i
    warp_top = ((j - i) % 4) != 3

    # wash map at output resolution, then upscaled
    wm = wash.base + (fbm(h, w, rng, scale=max(h, w) / 3.5, octaves=5) - 0.5) * 2 * wash.spread
    if wash.streaks:
        st = fbm(h, w, rng, scale=18, octaves=3, aniso=(6.0, 0.4))
        wm += (st - 0.5) * 0.16 * wash.streaks
    yy0, xx0 = np.mgrid[0:h, 0:w].astype(np.float32)
    if wash.knee:
        cx, cy, rx, ry = wash.knee
        d = ((xx0 - cx) / rx) ** 2 + ((yy0 - cy) / ry) ** 2
        wm += np.exp(-d * 1.6) * 0.38 * (0.7 + 0.6 * fbm(h, w, rng, scale=20, octaves=3))
    for _ in range(wash.whiskers):
        m = np.zeros((h, w), np.float32)
        x0 = rng.uniform(0.15, 0.85) * w
        y0 = rng.uniform(0.2, 0.8) * h
        L = rng.uniform(0.15, 0.32) * w
        a = rng.uniform(-0.35, 0.35)
        pts = []
        for k in range(12):
            s = k / 11
            pts.append((x0 + math.cos(a) * L * (s - 0.5),
                        y0 + math.sin(a) * L * (s - 0.5) + math.sin(s * math.pi) * L * 0.08))
        cv2.polylines(m, [np.array(pts, np.int32)], False, 1.0, max(2, int(w / 160)), cv2.LINE_AA)
        taper = np.clip(1 - np.abs((xx0 - x0) / (L * 0.55)), 0, 1)
        wm += blur(m, max(1.5, w / 260)) * taper * 0.35
    if wash.ghost:
        gx, gy, gw, gh, ga = wash.ghost
        rect = cv2.boxPoints(((gx, gy), (gw, gh), ga))
        g = poly_mask(h, w, rect, ss=1)
        wm -= blur(g, 3) * 0.24
        # stitch-hole ghost along the old pocket edge
        edge = cv2.morphologyEx((g > 0.5).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)).astype(np.float32)
        holes = (rng.random((h, w)) > 0.55).astype(np.float32)
        wm -= blur(edge * holes, 0.6) * 0.18
    if wash.phone:
        px, py, pw, ph = wash.phone
        m = np.zeros((h, w), np.float32)
        cv2.rectangle(m, (int(px), int(py)), (int(px + pw), int(py + ph)), 1.0, max(2, int(w / 120)), cv2.LINE_AA)
        wm += blur(m, 3) * 0.22
    for fn in wash.extra:
        wm = fn(wm, rng, h, w)

    wmS = cv2.resize(wm, (W, H), interpolation=cv2.INTER_LINEAR)

    # per-yarn variation (slubs) — each warp yarn varies along its length
    ncols = int(j.max() - j.min() + 2)
    nrows = int(i.max() - i.min() + 2)
    slub_w = cv2.resize(rng.normal(0, 1, (max(2, nrows // 9), ncols)).astype(np.float32),
                        (ncols, nrows), interpolation=cv2.INTER_LINEAR)
    jj = np.clip(j - j.min(), 0, ncols - 1)
    ii = np.clip(i - i.min(), 0, nrows - 1)
    slub = slub_w[ii, jj] * 0.07 + rng.normal(0, 1, ncols).astype(np.float32)[jj] * 0.035
    weft_var = rng.normal(0, 1, nrows).astype(np.float32)[ii] * 0.03

    prof_w = np.sin(np.pi * fu)            # warp yarn roundness
    prof_f = np.sin(np.pi * fv)            # weft yarn roundness
    lvl = np.clip(wmS + slub, 0, 1)
    warp = wash_color(lvl)
    # ring-dye: abraded yarn tops show the white core
    core = np.clip(lvl - 0.3, 0, 1) ** 1.3 * prof_w ** 3 * 0.55
    warp = warp + (ECRU - warp) * core[..., None]
    weft = (ECRU * 0.86 + FADED * 0.14)[None, None, :] * (0.92 + weft_var)[..., None]
    weft = weft * (0.97 - 0.12 * (1 - lvl))[..., None]
    twist = 0.92 + 0.08 * np.sin(2 * np.pi * (fu * 1.0 + v * 2.6))   # S-twist in the yarn
    shade_w = ((0.50 + 0.50 * prof_w) * twist)[..., None]
    shade_f = (0.30 + 0.32 * prof_f)[..., None]
    rgb = np.where(warp_top[..., None], warp * shade_w, weft * shade_f)
    height = np.where(warp_top, 0.6 + 0.4 * prof_w, 0.35 + 0.3 * prof_f)

    rgb = cv2.resize(rgb.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    height = cv2.resize(height.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA)
    # fibre fuzz
    fuzz = fbm(h, w, rng, scale=3, octaves=2)
    rgb = rgb * (0.93 + 0.12 * fuzz[..., None])
    return np.clip(rgb, 0, 1), height


# ───────────────────────────────────────────────────────────── surfaces

def concrete(h, w, seed=0, tone=1.0, smooth=False):
    rng = np.random.default_rng(seed)
    base = CONCRETE * 0.92 * tone
    big = fbm(h, w, rng, scale=max(h, w) / 2.5, octaves=5)
    mid = fbm(h, w, rng, scale=40, octaves=4)
    fine = rng.random((h, w)).astype(np.float32)
    lum = 0.82 + 0.28 * big + 0.12 * (mid - 0.5)
    if not smooth:
        lum += (fine - 0.5) * 0.10
        pores = (rng.random((h, w)) > 0.9965).astype(np.float32)
        lum -= blur(pores, 0.9) * 2.2
        agg = (rng.random((h, w)) > 0.9985).astype(np.float32)
        lum += blur(cv2.dilate(agg, np.ones((3, 3), np.uint8)), 1.0) * 0.4
    # stains / wet marks
    st = fbm(h, w, rng, scale=max(h, w) / 5, octaves=3)
    lum -= np.clip(st - 0.72, 0, 1) * 0.6
    img = base[None, None, :] * lum[..., None]
    # slight warm/cool variation
    img[..., 2] += (mid - 0.5) * 0.02
    return np.clip(img, 0, 1)


def plaster(h, w, seed=0):
    rng = np.random.default_rng(seed)
    base = STONE * 1.02
    big = fbm(h, w, rng, scale=max(h, w) / 2, octaves=5)
    fine = fbm(h, w, rng, scale=6, octaves=3)
    lum = 0.88 + 0.16 * big + 0.05 * (fine - 0.5)
    img = base[None, None, :] * lum[..., None]
    return np.clip(img, 0, 1)


def brick(h, w, seed=0, bh=30):
    """London stock brick: yellow-grey, soot-darkened, recessed mortar."""
    rng = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), np.float32)
    bw = int(bh * 3.0)
    mortar = max(2, bh // 7)
    stock = [hexrgb("#9C8B6A"), hexrgb("#8A7A5E"), hexrgb("#7B6E58"), hexrgb("#A39272"),
             hexrgb("#6E6352"), hexrgb("#B09A73"), hexrgb("#5E564A")]
    mcol = hexrgb("#9E978A")
    img[:] = mcol
    rows = h // bh + 2
    noise = fbm(h, w, rng, scale=6, octaves=3)
    for r in range(rows):
        off = (bw // 2) * (r % 2)
        y0 = r * bh
        for c in range(-1, w // bw + 2):
            x0 = c * bw + off + int(rng.normal(0, 1.5))
            col = stock[rng.integers(len(stock))] * rng.uniform(0.85, 1.08)
            if rng.random() < 0.12:
                col = col * 0.6 + hexrgb("#5B3A2A") * 0.4  # the odd red/burnt brick
            ya, yb = max(0, y0 + mortar), min(h, y0 + bh)
            xa, xb = max(0, x0 + mortar), min(w, x0 + bw)
            if ya < yb and xa < xb:
                img[ya:yb, xa:xb] = col
    # soot gradient & grime
    soot = fbm(h, w, rng, scale=max(h, w) / 3, octaves=4)
    img *= (0.55 + 0.6 * soot)[..., None]
    img *= (0.85 + 0.3 * noise)[..., None]
    # mortar recess shadow
    m = (np.abs(img - mcol).sum(-1) < 0.02).astype(np.float32)
    img *= (1 - blur(m, 1.2) * 0.25)[..., None]
    return np.clip(img, 0, 1)


def paper(h, w, seed=0, col=ECRU):
    rng = np.random.default_rng(seed)
    f = fbm(h, w, rng, scale=4, octaves=3)
    b = fbm(h, w, rng, scale=max(h, w) / 2, octaves=3)
    return np.clip(col[None, None, :] * (0.94 + 0.05 * f + 0.05 * b)[..., None], 0, 1)


# ───────────────────────────────────────────────────────────── light & grade

def flash(img, cx=0.5, cy=0.45, r0=0.55, floor=0.18, power=1.0):
    """Direct on-camera flash: bright centre, fast inverse-square-ish falloff."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx / w - cx) * (w / max(h, w))) ** 2 + ((yy / h - cy) * (h / max(h, w))) ** 2)
    L = floor + (1.15 - floor) / (1 + (d / r0) ** 2.6)
    return img * (L * power)[..., None]


def available(img, top=1.05, bottom=0.55, side_vignette=0.25, warm=0.02):
    """Strip light from above: soft gradient, slightly warm."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    L = top + (bottom - top) * (yy / h) ** 1.3
    L *= 1 - side_vignette * ((xx / w - 0.5) * 2) ** 2
    out = img * L[..., None]
    out[..., 0] *= 1 + warm
    out[..., 2] *= 1 - warm
    return out


def pool(img, cx, cy, r, floor=0.06, warm=0.04):
    """A pool of light (bench lamp) falling into darkness."""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx * w) ** 2 + (yy - cy * h) ** 2) / (r * max(h, w))
    L = floor + (1.1 - floor) * np.exp(-(d ** 2) * 1.4)
    out = img * L[..., None]
    out[..., 0] *= 1 + warm
    out[..., 2] *= 1 - warm * 0.8
    return out


def drop_shadow(bg, alpha, dx, dy, soft, strength):
    sh = np.roll(np.roll(alpha, int(dy), 0), int(dx), 1)
    sh = blur(sh, soft)
    return bg * (1 - sh * strength)[..., None]


def composite(bg, fg, alpha):
    return bg * (1 - alpha[..., None]) + fg * alpha[..., None]


def grade(img, seed=0, grain=0.035, halation=0.5, lift=0.05, cool=1.0, exposure=None, softness=0.6,
          vignette=0.22):
    """The house grade: cool lifted blacks, true denim, film grain, halation."""
    rng = np.random.default_rng(seed + 991)
    h, w = img.shape[:2]
    img = img.astype(np.float32)
    if exposure is None:
        exposure = rng.uniform(0.96, 1.06)
    img = img * exposure
    # film softness (lens + emulsion)
    img = blur(img, softness)
    lum = img @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    # halation: highlights bleed warm into the emulsion
    if halation:
        hm = np.clip((lum - 0.72) / 0.35, 0, 1)
        hb = blur(hm, max(h, w) / 140)
        img += hb[..., None] * np.array([0.22, 0.07, 0.03], np.float32) * halation
        img += blur(hm, max(h, w) / 600)[..., None] * 0.06
    # tone: gentle S, highlight roll-off
    img = np.clip(img, 0, 4)
    img = img / (1 + img * 0.18) * 1.18
    img = 0.5 + (img - 0.5) * 1.06
    # cool shadows, never orange-teal
    sh = np.clip(1 - lum * 1.6, 0, 1)[..., None] ** 2
    img += sh * np.array([-0.006, 0.0, 0.018], np.float32) * cool
    # lifted blacks
    img = lift + img * (1 - lift)
    # restrained saturation
    l2 = (img @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    img = l2 + (img - l2) * 0.9
    # vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2) * 2
    img *= (1 - vignette * d ** 1.4)[..., None]
    # grain: luminance-weighted, clumped (not per-pixel digital noise)
    g = rng.normal(0, 1, (h // 2 + 1, w // 2 + 1)).astype(np.float32)
    g = cv2.resize(g, (w, h), interpolation=cv2.INTER_LINEAR)
    g += rng.normal(0, 0.6, (h, w)).astype(np.float32)
    mid = 0.6 + 0.8 * (1 - np.abs(np.clip(l2[..., 0], 0, 1) - 0.45) * 1.6)
    img += (g * grain * mid)[..., None]
    chroma = rng.normal(0, grain * 0.25, (h // 3 + 1, w // 3 + 1, 3)).astype(np.float32)
    img += cv2.resize(chroma, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(img, 0, 1)


def save(img, path, quality=86):
    path.parent.mkdir(parents=True, exist_ok=True)
    im = Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))
    im.save(path, "JPEG", quality=quality, optimize=True, progressive=True, subsampling="4:2:0")
    return path

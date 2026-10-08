"""
Garment construction for placeholder photography.

Garments are described in centimetres as part polygons (body, sleeves,
collar…). Each part is split into panels — every panel is a piece of a
different first-life garment with its own wash — and every split becomes a
seam with flat-felled ridge and double topstitch. This mirrors the real
method: the panel map is the construction record.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import cv2
import numpy as np
from PIL import Image, ImageDraw
from shapely import affinity
from shapely.geometry import LineString, MultiLineString, Polygon
from shapely.ops import split

import core


@dataclass
class Part:
    name: str
    pts: list
    panels: int = 1
    bias: str = "any"          # "v" vertical seams, "h" horizontal, "any"
    hem: bool = True
    wash_shift: float = 0.0


@dataclass
class Garment:
    name: str
    parts: list
    seams: list = field(default_factory=list)       # extra seam polylines (cm)
    stitches: list = field(default_factory=list)    # single topstitch lines (cm)
    buttons: list = field(default_factory=list)     # (x, y, r) cm
    rivets: list = field(default_factory=list)
    patch: tuple | None = None                      # (x, y, w, h) cm
    selvedge: list = field(default_factory=list)    # polylines showing selvedge id
    loops: list = field(default_factory=list)       # belt loops (x, y)
    wash_range: tuple = (0.12, 0.72)
    sources: int = 5                                # first-life garments


def mirror(pts):
    return [(-x, y) for x, y in pts]


# ───────────────────────────────────────────────────────────── patterns

def trucker(view="front", length=56, sleeves=True, collar=True, panels=23, cropped=True):
    L = length
    body = [(-9, 0), (-24, 4), (-28, 22), (-27, L - 4), (27, L - 4), (28, 22), (24, 4), (9, 0), (0, 2)]
    band = [(-27, L - 4), (27, L - 4), (27, L + 1), (-27, L + 1)]
    parts = [Part("body", body, panels=max(3, panels - 10), bias="any"),
             Part("band", band, panels=3, bias="v")]
    if sleeves:
        sl = [(24, 4), (28, 22), (35, 64), (45.5, 61)]
        parts += [Part("sleeve_r", sl, panels=4, bias="h"), Part("sleeve_l", mirror(sl), panels=4, bias="h")]
        cuff = [(35, 64), (45.5, 61), (46.6, 65), (36, 68)]
        parts += [Part("cuff_r", cuff, 1), Part("cuff_l", mirror(cuff), 1)]
    if collar:
        parts.append(Part("collar", [(-9, 0), (-15, 1), (-17, 8), (-9, 6.5), (0, 4.5), (9, 6.5), (17, 8), (15, 1), (9, 0), (0, -1)],
                          panels=2, bias="v"))
    g = Garment("trucker", parts)
    if view == "front":
        g.seams.append([(0, 3), (0, L + 1)])
        g.stitches += [[(3.2, 4), (3.2, L + 1)]]
        for y in (10, 20, 30, 40):
            g.buttons.append((1.6, y, 0.85))
        g.buttons.append((1.6, L - 1.5, 0.85))
        for sx in (-1, 1):
            flap = [(sx * 6, 15), (sx * 20, 15), (sx * 20, 19), (sx * 13, 22.5), (sx * 6, 19)]
            g.parts.append(Part("flap", flap, 1, hem=True, wash_shift=-0.05))
            g.buttons.append((sx * 13, 19.5, 0.7))
            g.seams.append([(sx * 7, 22.5), (sx * 7, L - 4)])
            g.seams.append([(sx * 19, 22.5), (sx * 20, L - 4)])
            g.seams.append([(sx * 3, 13), (sx * 24, 12)])
    else:
        g.seams.append([(-27.5, 15), (0, 19), (27.5, 15)])  # pointed back yoke
        g.seams += [[(-10, 19), (-11, L - 4)], [(10, 19), (11, L - 4)]]
        g.patch = (14, L - 11, 9, 5.5)
    return g


def shirt(view="front", length=74, panels=20):
    L = length
    body = [(-9, 0), (-25, 5), (-27, 26), (-26, L - 6), (-20, L), (20, L), (26, L - 6), (27, 26), (25, 5), (9, 0), (0, 2)]
    sl = [(25, 5), (27, 26), (34, 78), (44, 75)]
    parts = [Part("body", body, panels=panels - 8, bias="any"),
             Part("sleeve_r", sl, 3, bias="h"), Part("sleeve_l", mirror(sl), 3, bias="h"),
             Part("collar", [(-9, 0), (-14, 1), (-18, 10), (-8, 7), (0, 5), (8, 7), (18, 10), (14, 1), (9, 0), (0, -1)], 1)]
    cuff = [(34, 78), (44, 75), (45.4, 81), (35.6, 84)]
    parts += [Part("cuff_r", cuff, 1), Part("cuff_l", mirror(cuff), 1)]
    g = Garment("shirt", parts)
    if view == "front":
        g.seams.append([(0, 3), (0, L)])
        g.stitches.append([(2.6, 4), (2.6, L)])
        for y in range(9, L - 4, 10):
            g.buttons.append((1.3, y, 0.6))
        for sx in (-1, 1):
            pocket = [(sx * 7, 16), (sx * 19, 16), (sx * 19, 28), (sx * 13, 31), (sx * 7, 28)]
            g.parts.append(Part("pocket", pocket, 1, wash_shift=0.05))
    else:
        g.seams.append([(-27, 12), (-9, 17), (0, 14), (9, 17), (27, 12)])
        g.patch = (15, L - 10, 7, 4.5)
    return g


def coat(view="front", length=80, panels=24):
    g = trucker(view, length=length, panels=panels, cropped=False)
    g.name = "coat"
    if view == "front":
        g.parts = [p for p in g.parts if p.name != "flap"]
        g.seams = [s for s in g.seams if not (len(s) == 2 and abs(s[0][1] - 22.5) < 0.1)]
        for sx in (-1, 1):
            g.parts.append(Part("pocket", [(sx * 6, 46), (sx * 22, 46), (sx * 22, 64), (sx * 6, 64)], 2, bias="h"))
            g.parts.append(Part("pocket", [(sx * 8, 16), (sx * 20, 16), (sx * 20, 28), (sx * 8, 28)], 1))
    return g


def gilet(view="front", length=58, panels=14):
    g = trucker(view, length=length, sleeves=False, panels=panels)
    g.name = "gilet"
    # wider armholes: swap body shape
    L = length
    g.parts[0].pts = [(-9, 0), (-21, 4), (-21, 14), (-27, 24), (-27, L - 4), (27, L - 4), (27, 24), (21, 14), (21, 4), (9, 0), (0, 2)]
    return g


def trousers(view="front", wide=False, panels=14, carpenter=False):
    hem = 31 if wide else 25
    L = 104
    outline = [(-21, 0), (21, 0), (23, 30), (hem, L), (2, L), (0, 34), (-2, L), (-hem, L), (-23, 30)]
    parts = [Part("legs", outline, panels=panels, bias="v")]
    parts.append(Part("waistband", [(-21.3, -4), (21.3, -4), (21.3, 0.2), (-21.3, 0.2)], 3, bias="v"))
    g = Garment("trousers", parts)
    g.loops = [(-17, -2), (-8, -2), (8, -2), (17, -2)] if view == "front" else [(-15, -2), (0, -2), (15, -2)]
    if view == "front":
        g.buttons.append((0.5, -2, 0.9))
        g.stitches.append([(-0.3, 0.5), (-4.2, 1), (-4.2, 16), (-2.5, 20), (-0.3, 22)])
        for sx in (-1, 1):
            g.seams.append([(sx * 10, 0.2), (sx * 13, 7), (sx * 22, 11)])
            g.rivets += [(sx * 10.4, 1.2), (sx * 21.7, 10)]
        if carpenter:
            g.parts.append(Part("tool", [(23.2, 34), (30.5, 52), (25, 54.5), (20.3, 38)], 1, wash_shift=0.08))
            g.parts.append(Part("loop", [(-24, 36), (-20.6, 36), (-19.8, 47), (-24.4, 47)], 1))
    else:
        g.seams.append([(-21.6, 8), (0, 14), (21.6, 8)])
        g.seams.append([(0, 0.2), (0, 34)])
        for sx in (-1, 1):
            pk = [(sx * 4, 15), (sx * 17, 13), (sx * 17.5, 28), (sx * 11, 31), (sx * 4.5, 28)]
            g.parts.append(Part("pocket", pk, 1, wash_shift=-0.06))
        g.patch = (11, -3.5, 8, 4.6)
    g.selvedge = [[(23.2, 32), (hem - 0.25, L - 3)]] if view == "front" else []
    return g


def skirt(view="front", panels=10):
    parts = [Part("skirt", [(-21, 0), (21, 0), (23, 10), (31, 64), (-31, 64), (-23, 10)], panels, bias="v"),
             Part("waistband", [(-21.3, -4), (21.3, -4), (21.3, 0.2), (-21.3, 0.2)], 2, bias="v")]
    g = Garment("skirt", parts)
    g.seams.append([(-23, 10), (0, 15), (23, 10)])
    g.buttons.append((0.5, -2, 0.9))
    g.loops = [(-15, -2), (15, -2)]
    if view == "back":
        g.patch = (11, -3.5, 8, 4.6)
    return g


def tote(view="front", panels=9):
    body = [(-22, 0), (22, 0), (22, 44), (-22, 44)]
    parts = [Part("bag", body, panels, bias="any")]
    # handles: two loops of re-used waistband
    hl = [(-15, 0.2), (-15, -12), (-12, -19), (-6, -21), (-3, -19), (-1, -12), (-1, 0.2),
          (-4, 0.2), (-4, -11), (-6, -16), (-9, -16.5), (-11, -14), (-12, -11), (-12, 0.2)]
    parts.append(Part("handle", hl, 1, hem=False, wash_shift=0.1))
    parts.append(Part("handle", [(-x, y) for x, y in hl], 1, hem=False, wash_shift=-0.08))
    g = Garment("tote", parts)
    if view == "back":
        g.patch = (-4, 34, 8, 4.6)
    return g


def waistband_bag(view="front"):
    parts = []
    for k in range(7):
        y = k * 4.2
        parts.append(Part(f"band{k}", [(-17, y), (17, y), (17, y + 4.2), (-17, y + 4.2)], 1, hem=True,
                          wash_shift=(k % 3 - 1) * 0.15))
    g = Garment("bag", parts, wash_range=(0.1, 0.8))
    for k in range(7):
        g.buttons.append(((-13 if k % 2 else 13), k * 4.2 + 2.1, 0.75))
        g.loops.append(((-4 if k % 2 else 5), k * 4.2 + 2.1))
    g.patch = (-4, 30.2, 8, 4.4) if view == "back" else None
    return g


def belt(view="front"):
    parts = []
    n = 8
    for k in range(n):
        x = -55 + k * 13.75
        parts.append(Part(f"seg{k}", [(x, 0), (x + 13.75, 0), (x + 13.75, 4), (x, 4)], 1, hem=True,
                          wash_shift=((k * 7) % 5 - 2) * 0.09))
    g = Garment("belt", parts, wash_range=(0.08, 0.85))
    g.buttons.append((51, 2, 0.95))
    g.patch = (-50, -0.3, 7, 4.6) if view == "back" else None
    return g


PATTERNS = {"trucker": trucker, "shirt": shirt, "coat": coat, "gilet": gilet, "trousers": trousers,
            "skirt": skirt, "tote": tote, "bag": waistband_bag, "belt": belt}


# ───────────────────────────────────────────────────────────── panelling

def split_part(poly: Polygon, n, rng, bias="any"):
    polys, seams = [poly], []
    tries = 0
    while len(polys) < n and tries < n * 12:
        tries += 1
        polys.sort(key=lambda p: p.area)
        p = polys.pop()
        minx, miny, maxx, maxy = p.bounds
        w, h = maxx - minx, maxy - miny
        if bias == "v":
            vertical = True
        elif bias == "h":
            vertical = False
        else:
            vertical = w > h * rng.uniform(0.7, 1.3)
        ang = (math.pi / 2 if vertical else 0) + rng.normal(0, 0.16)
        cx = minx + w * rng.uniform(0.35, 0.65)
        cy = miny + h * rng.uniform(0.35, 0.65)
        R = (w + h) * 2
        line = LineString([(cx - math.cos(ang) * R, cy - math.sin(ang) * R),
                           (cx + math.cos(ang) * R, cy + math.sin(ang) * R)])
        try:
            parts = [g for g in split(p, line).geoms if g.area > 1e-6]
        except Exception:
            parts = [p]
        if len(parts) < 2 or min(g.area for g in parts) < poly.area / (n * 4.5):
            polys.append(p)
            continue
        seams.append(p.intersection(line))
        polys.extend(parts)
    return polys, seams


def _lines(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, LineString):
        return [list(geom.coords)]
    if isinstance(geom, MultiLineString):
        return [list(g.coords) for g in geom.geoms]
    if hasattr(geom, "geoms"):
        out = []
        for g in geom.geoms:
            out += _lines(g)
        return out
    return []


# ───────────────────────────────────────────────────────────── drawing

def dashes(draw, pts, color, width, dash=5.0, gap=2.2, shadow=None, jitter=None, rng=None):
    """Topstitch: short dashes along a polyline (pixel coords)."""
    pos = 0.0
    on = True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg < 1e-6:
            continue
        dx, dy = (x1 - x0) / seg, (y1 - y0) / seg
        t = 0.0
        while t < seg:
            step = (dash if on else gap) - pos
            t1 = min(seg, t + step)
            if on:
                a = (x0 + dx * t, y0 + dy * t)
                b = (x0 + dx * t1, y0 + dy * t1)
                if jitter and rng is not None:
                    j = rng.normal(0, jitter, 2)
                    a = (a[0] + j[0], a[1] + j[1])
                if shadow is not None:
                    draw.line([(a[0] + width * 0.5, a[1] + width * 0.6), (b[0] + width * 0.5, b[1] + width * 0.6)],
                              fill=shadow, width=max(1, int(width)))
                draw.line([a, b], fill=color, width=max(1, int(round(width))))
            pos += t1 - t
            t = t1
            if pos >= (dash if on else gap) - 1e-6:
                pos = 0.0
                on = not on


def offset_line(pts, d):
    ls = LineString(pts)
    try:
        o = ls.offset_curve(d, join_style=2)
    except Exception:
        return pts
    ls2 = _lines(o)
    return ls2[0] if ls2 else pts


def render_garment(g: Garment, H, W, ppc, origin, seed=0, thread=None, ss=2, wash_bias=0.0,
                   grain_angle_jitter=0.25, fold=0.5):
    """Render a garment to RGB + alpha at (H, W). origin = pixel position of (0,0) cm."""
    rng = np.random.default_rng(seed)
    ox, oy = origin

    def P(pts):
        return [(ox + x * ppc, oy + y * ppc) for x, y in pts]

    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    height = np.zeros((H, W), np.float32)
    seam_lines = []
    hem_lines = []
    thread = thread or max(0.9, ppc * 0.035)
    lo, hi = g.wash_range
    src_levels = np.sort(rng.uniform(lo, hi, g.sources))
    src_levels[0], src_levels[-1] = lo + 0.02, hi - 0.02

    order = sorted(g.parts, key=lambda p: {"sleeve_r": 0, "sleeve_l": 0, "cuff_r": 0, "cuff_l": 0, "handle": 0}.get(p.name, 1))
    for part in order:
        poly = wobble(Polygon(P(part.pts)).buffer(0), ppc, rng)
        # this part lies on top of what is already there: cast a small shadow
        pm = core.poly_mask(H, W, list(poly.exterior.coords), ss=2)
        if alpha.max() > 0:
            shd = core.blur(np.roll(np.roll(pm, int(ppc * 0.25), 0), int(ppc * 0.18), 1), ppc * 0.3)
            rgb *= (1 - np.clip(shd - pm, 0, 1) * alpha * 0.55)[..., None]
        height += pm * 0.6
        panels, seams = split_part(poly, part.panels, rng, part.bias)
        for s in seams:
            seam_lines += _lines(s)
        if part.hem:
            hem_lines.append(list(poly.exterior.coords))
        for pnl in panels:
            minx, miny, maxx, maxy = [int(v) for v in pnl.bounds]
            minx, miny = max(0, minx - 2), max(0, miny - 2)
            maxx, maxy = min(W, maxx + 3), min(H, maxy + 3)
            bw, bh = maxx - minx, maxy - miny
            if bw < 3 or bh < 3:
                continue
            base = np.clip(src_levels[rng.integers(len(src_levels))] + rng.normal(0, 0.035) + part.wash_shift + wash_bias,
                           0.02, 0.95)
            wash = core.Wash(base=base, spread=rng.uniform(0.1, 0.24), seed=int(rng.integers(1e9)),
                             whiskers=int(rng.random() < 0.3) * int(rng.integers(1, 4)),
                             streaks=rng.uniform(0.3, 1.0))
            if rng.random() < 0.25 and bw > 40 and bh > 40:
                wash.ghost = (bw * rng.uniform(0.3, 0.7), bh * rng.uniform(0.3, 0.7),
                              bw * rng.uniform(0.3, 0.5), bh * rng.uniform(0.3, 0.45), rng.normal(0, 6))
            if rng.random() < 0.2 and bw > 40:
                wash.knee = (bw * rng.uniform(0.3, 0.7), bh * rng.uniform(0.3, 0.7), bw * 0.4, bh * 0.3)
            ang = rng.normal(0, grain_angle_jitter) + (math.pi / 2 if rng.random() < 0.12 else 0)
            tex, _ = core.denim(bh, bw, wash, thread=thread, angle=ang)
            m = core.poly_mask(bh, bw, [(x - minx, y - miny) for x, y in pnl.exterior.coords], ss=3)
            region = rgb[miny:maxy, minx:maxx]
            rgb[miny:maxy, minx:maxx] = region * (1 - m[..., None]) + tex * m[..., None]
            alpha[miny:maxy, minx:maxx] = np.maximum(alpha[miny:maxy, minx:maxx], m)

    # un-premultiply panel edges (avoids a dark fringe when composited)
    rgb = np.where(alpha[..., None] > 1e-3, rgb / np.maximum(alpha, 1e-3)[..., None], 0)
    # ── cloth relief: a height field lit from the light direction
    seam_m = np.zeros((H, W), np.float32)
    for ln in seam_lines + [P(s) for s in g.seams]:
        cv2.polylines(seam_m, [np.array(ln, np.int32)], False, 1.0, max(2, int(ppc * 0.7)), cv2.LINE_AA)
    for ln in hem_lines:
        cv2.polylines(seam_m, [np.array(ln, np.int32)], True, 0.7, max(2, int(ppc * 1.0)), cv2.LINE_AA)
    n1 = core.fbm(H, W, rng, scale=ppc * 16, octaves=2)
    ridges = (1 - np.abs(2 * n1 - 1)) ** 6
    n2 = core.fbm(H, W, rng, scale=ppc * 8, octaves=2)
    ridges2 = (1 - np.abs(2 * n2 - 1)) ** 8
    pucker = core.fbm(H, W, rng, scale=ppc * 0.8, octaves=2) * core.blur(seam_m, ppc * 0.8)
    hf = (core.blur(alpha, ppc * 1.6) * 0.45 + height * 0.3
          + core.fbm(H, W, rng, scale=ppc * 22, octaves=3) * 1.4
          + core.blur(ridges, ppc * 1.2) * 0.9 * fold + core.blur(ridges2, ppc * 0.7) * 0.25 * fold
          + core.blur(seam_m, ppc * 0.22) * 0.55 + pucker * 0.6) * alpha
    gy, gx = np.gradient(core.blur(hf, ppc * 0.12))
    lx, ly = -0.55, -0.75
    lit = 1 + (gx * lx + gy * ly) * ppc * 1.6
    ao = np.clip(core.blur(hf, ppc * 1.2) - hf, 0, 1)
    shade = np.clip(lit, 0.45, 1.5) * (1 - ao * 0.9)
    rgb *= shade[..., None]
    # edge roll: garment edges darken where the cloth turns under
    er = cv2.erode((alpha > 0.5).astype(np.uint8), np.ones((3, 3), np.uint8), iterations=max(1, int(ppc * 0.25)))
    edge = core.blur(alpha - er.astype(np.float32), ppc * 0.18)
    rgb *= (1 - np.clip(edge, 0, 1) * 0.35)[..., None]

    # seams, stitches, hardware on an overlay at ss
    ov = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    k = ppc * ss
    gold = tuple(int(c * 255) for c in core.THREAD_GOLD) + (235,)
    gold_sh = (10, 12, 20, 120)

    def S(pts):
        return [(x * ss, y * ss) for x, y in pts]

    extra = [P(s) for s in g.seams]
    for ln in seam_lines + extra:
        sp = S(ln)
        d.line(sp, fill=(5, 8, 18, 150), width=max(2, int(k * 0.32)))
        d.line(S(offset_line(ln, ppc * 0.16)), fill=(220, 225, 235, 46), width=max(1, int(k * 0.12)))
        for off in (0.35, 0.7):
            dashes(d, S(offset_line(ln, ppc * off)), gold, max(1.5, k * 0.075), dash=k * 0.32, gap=k * 0.1,
                   shadow=gold_sh, jitter=k * 0.01, rng=rng)
    for ln in [P(s) for s in g.stitches]:
        dashes(d, S(ln), gold, max(1.5, k * 0.075), dash=k * 0.32, gap=k * 0.1, shadow=gold_sh)
    for ln in hem_lines:
        poly = Polygon(ln)
        for inset in (0.45, 0.85):
            inner = poly.buffer(-ppc * inset, join_style=2)
            for li in _lines(inner.exterior if hasattr(inner, "exterior") else inner.boundary):
                dashes(d, S(li), gold, max(1.5, k * 0.07), dash=k * 0.32, gap=k * 0.1, shadow=gold_sh)
    for sl in g.selvedge:
        pts = S(P(sl))
        d.line(pts, fill=(236, 231, 220, 230), width=max(2, int(k * 0.35)))
        d.line(S(offset_line(P(sl), ppc * 0.06)), fill=(150, 40, 35, 220), width=max(1, int(k * 0.08)))
    for (x, y) in g.loops:
        cx, cy = ox + x * ppc, oy + y * ppc
        bx = [(cx - ppc * 0.6, cy - ppc * 2.3), (cx + ppc * 0.6, cy + ppc * 2.3)]
        d.rectangle([(bx[0][0] * ss, bx[0][1] * ss), (bx[1][0] * ss, bx[1][1] * ss)], fill=(40, 58, 92, 255),
                    outline=(10, 14, 28, 200), width=max(1, int(k * 0.06)))
        dashes(d, [(bx[0][0] * ss + k * 0.2, bx[0][1] * ss + k * 0.2), (bx[0][0] * ss + k * 0.2, bx[1][1] * ss - k * 0.2)],
               gold, max(1, k * 0.06), dash=k * 0.25, gap=k * 0.1)
    for (x, y, r) in g.buttons:
        _button(d, (ox + x * ppc) * ss, (oy + y * ppc) * ss, r * k)
    for (x, y) in g.rivets:
        _rivet(d, (ox + x * ppc) * ss, (oy + y * ppc) * ss, 0.38 * k)
    ov = ov.resize((W, H), Image.LANCZOS)
    o = np.asarray(ov, np.float32) / 255.0
    rgb = rgb * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]

    if g.patch:
        x, y, pw, ph = g.patch
        rgb, alpha = place_patch(rgb, alpha, ox + x * ppc, oy + y * ppc, pw * ppc, ph * ppc, seed=seed)
    return np.clip(rgb, 0, 1), alpha


def wobble(poly, ppc, rng, amp=0.07):
    """Cloth is never cut on a perfect line: densify and displace the outline."""
    try:
        p = poly.segmentize(ppc * 1.2)
    except Exception:
        return poly
    pts = np.array(p.exterior.coords)[:-1]
    n = len(pts)
    if n < 4:
        return poly
    noise = rng.normal(0, 1, n)
    k = max(3, n // 40)
    noise = np.convolve(np.concatenate([noise[-k:], noise, noise[:k]]), np.ones(k) / k, mode="same")[k:-k]
    c = np.array(p.centroid.coords[0])
    nrm = pts - c
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-6
    pts = pts + nrm * noise[:, None] * ppc * amp * 2.2
    out = Polygon(pts).buffer(0)
    return out if out.geom_type == "Polygon" else poly


def _button(d, cx, cy, r):
    steel = (154, 158, 163, 255)
    d.ellipse([cx - r * 1.12 + r * 0.18, cy - r * 1.12 + r * 0.25, cx + r * 1.12 + r * 0.18, cy + r * 1.12 + r * 0.25],
              fill=(5, 6, 12, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(98, 102, 108, 255))
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], fill=steel)
    d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(122, 126, 132, 255))
    d.ellipse([cx - r * 0.5, cy - r * 0.62, cx + r * 0.1, cy - r * 0.15], fill=(215, 220, 226, 200))
    d.ellipse([cx - r * 0.14, cy - r * 0.14, cx + r * 0.14, cy + r * 0.14], fill=(60, 62, 66, 255))


def _rivet(d, cx, cy, r):
    d.ellipse([cx - r + r * 0.2, cy - r + r * 0.3, cx + r + r * 0.2, cy + r + r * 0.3], fill=(5, 6, 12, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(116, 98, 70, 255))
    d.ellipse([cx - r * 0.55, cy - r * 0.6, cx + r * 0.1, cy - r * 0.05], fill=(205, 180, 130, 200))


def leather(h, w, seed=0):
    rng = np.random.default_rng(seed)
    g1 = core.fbm(h, w, rng, scale=2.5, octaves=3)
    g2 = core.fbm(h, w, rng, scale=max(h, w) / 2.5, octaves=3)
    img = core.TAN[None, None, :] * (0.86 + 0.14 * g1 + 0.12 * (g2 - 0.5))[..., None]
    img = img * 0.94 + core.SADDLE * 0.06
    return img


def patch_image(pw, ph, seed=0, piece="RR-014", text=True):
    """Debossed tan leather patch, stacked lockup with piece number."""
    pw, ph = int(pw), int(ph)
    img = leather(ph, pw, seed)
    if text and pw > 40:
        ss = 3
        mask = Image.new("L", (pw * ss, ph * ss), 0)
        d = ImageDraw.Draw(mask)
        fs = int(ph * 0.24 * ss)
        f = core.stamp(fs, 800)
        x0, y0 = pw * 0.11 * ss, ph * 0.13 * ss
        d.text((x0, y0), "RAW", font=f, fill=255)
        d.text((x0, y0 + fs * 1.0), "RETURN", font=f, fill=255)
        fm = core.mono(int(ph * 0.095 * ss), medium=True)
        d.text((x0, ph * 0.70 * ss), "RECLAIMED GARMENTS", font=fm, fill=255)
        d.text((x0, ph * 0.70 * ss + ph * 0.11 * ss), "RETURNED TO THE STREETS", font=fm, fill=255)
        tw = d.textlength(piece, font=fm)
        d.text((pw * ss - tw - pw * 0.08 * ss, ph * 0.13 * ss), piece, font=fm, fill=255)
        m = np.asarray(mask.resize((pw, ph), Image.LANCZOS), np.float32) / 255
        # deboss: pressed area darker (saddle), lit rim below-right, shadow above-left
        sh = np.roll(np.roll(m, -1, 0), -1, 1)
        hl = np.roll(np.roll(m, 1, 0), 1, 1)
        img = img * (1 - m[..., None] * 0.42) + core.SADDLE * m[..., None] * 0.15
        img = img * (1 - np.clip(sh - m, 0, 1)[..., None] * 0.35) + np.clip(hl - m, 0, 1)[..., None] * 0.1
    # stitched edge in dark thread
    ov = Image.new("RGBA", (pw * 2, ph * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    inset = min(pw, ph) * 0.07 * 2
    pts = [(inset, inset), (pw * 2 - inset, inset), (pw * 2 - inset, ph * 2 - inset), (inset, ph * 2 - inset), (inset, inset)]
    dashes(d, pts, (35, 24, 16, 230), max(1.5, ph * 0.02 * 2), dash=ph * 0.07 * 2, gap=ph * 0.035 * 2)
    o = np.asarray(ov.resize((pw, ph), Image.LANCZOS), np.float32) / 255
    img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
    # edge burnish
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    e = np.minimum(np.minimum(xx, pw - 1 - xx), np.minimum(yy, ph - 1 - yy))
    img *= (0.72 + 0.28 * np.clip(e / (min(pw, ph) * 0.05), 0, 1))[..., None]
    return np.clip(img, 0, 1)


def place_patch(rgb, alpha, x, y, pw, ph, seed=0, piece="RR-014"):
    pimg = patch_image(pw, ph, seed, piece)
    x, y = int(x), int(y)
    h, w = pimg.shape[:2]
    H, W = rgb.shape[:2]
    if x < 0 or y < 0 or x + w > W or y + h > H:
        return rgb, alpha
    # small contact shadow
    sh = np.zeros((H, W), np.float32)
    sh[y + 2:y + h + 3, x + 2:x + w + 2] = 1
    rgb = rgb * (1 - core.blur(sh, 2.5)[..., None] * 0.45)
    rgb[y:y + h, x:x + w] = pimg
    alpha[y:y + h, x:x + w] = 1
    return rgb, alpha

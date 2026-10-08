"""
Scene compositions. Two lights only, per the brand guideline:
  - available light at the bench (process, founder, piece)
  - direct flash outside (the return)
"""
from __future__ import annotations

import math

import cv2
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon

import core
import garments as G


# ───────────────────────────────────────────────────────────── object helpers

def place(canvas, rgb, alpha, x, y, angle=0.0, scale=1.0, shadow=(6, 9, 5, 0.5), dim=1.0):
    """Paste an RGBA object centred at (x, y), rotated (deg) and scaled, with a cast shadow."""
    h, w = alpha.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * sin + w * cos) + 2, int(h * cos + w * sin) + 2
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    r = cv2.warpAffine(rgb, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=0)
    a = cv2.warpAffine(alpha, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=0)
    H, W = canvas.shape[:2]
    x0, y0 = int(x - nw / 2), int(y - nh / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + nw), min(H, y0 + nh)
    if xa >= xb or ya >= yb:
        return canvas
    full_a = np.zeros((H, W), np.float32)
    full_a[ya:yb, xa:xb] = a[ya - y0:yb - y0, xa - x0:xb - x0]
    full_r = np.zeros((H, W, 3), np.float32)
    full_r[ya:yb, xa:xb] = r[ya - y0:yb - y0, xa - x0:xb - x0]
    if shadow:
        dx, dy, soft, st = shadow
        canvas = core.drop_shadow(canvas, full_a, dx, dy, soft, st)
    return core.composite(canvas, full_r * dim, full_a)


def panel_obj(pts_cm, ppc, wash, raw=True, hem_edges=(), holes_edges=(), loose=0, seed=0, thread=None):
    """A single cut denim panel with raw, fraying edges (top-down)."""
    rng = np.random.default_rng(seed)
    pts = np.array(pts_cm, np.float32) * ppc
    pts -= pts.min(0)
    pad = int(ppc * 1.2)
    pts += pad
    w, h = int(pts[:, 0].max() + pad), int(pts[:, 1].max() + pad)
    tex, _ = core.denim(h, w, wash, thread=thread or max(1.0, ppc * 0.045), angle=rng.normal(0, 0.05))
    poly = G.wobble(Polygon(pts), ppc, rng, amp=0.05)
    m = core.poly_mask(h, w, list(poly.exterior.coords), ss=3)
    ov = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    coords = list(poly.exterior.coords)
    if raw:  # frayed weft at cut edges
        ls = poly.exterior
        n = int(ls.length / 2.5)
        for k in range(n):
            p = ls.interpolate(k / n, normalized=True)
            q = ls.interpolate((k + 1) / n, normalized=True)
            tx, ty = q.x - p.x, q.y - p.y
            L = math.hypot(tx, ty) + 1e-6
            nx, ny = ty / L, -tx / L
            c = poly.centroid
            if (p.x - c.x) * nx + (p.y - c.y) * ny < 0:
                nx, ny = -nx, -ny
            ln = rng.uniform(0.5, 2.6) * ppc * 0.12
            col = (225, 220, 205, 210) if rng.random() < 0.6 else (60, 85, 125, 200)
            d.line([(p.x * 2, p.y * 2), ((p.x + nx * ln + rng.normal(0, 0.4)) * 2, (p.y + ny * ln + rng.normal(0, 0.4)) * 2)],
                   fill=col, width=1)
    gold = (201, 138, 58, 235)
    for ei in hem_edges:
        a, b = pts[ei], pts[(ei + 1) % len(pts)]
        ln = G.offset_line([tuple(a), tuple(b)], -ppc * 0.5)
        G.dashes(d, [(x * 2, y * 2) for x, y in ln], gold, max(1.5, ppc * 0.13), dash=ppc * 0.6, gap=ppc * 0.2,
                 shadow=(10, 12, 20, 120))
    for ei in holes_edges:  # stitch holes where a seam was unpicked
        a, b = pts[ei], pts[(ei + 1) % len(pts)]
        for off in (0.4, 0.75):
            ln = G.offset_line([tuple(a), tuple(b)], -ppc * off)
            (x0, y0), (x1, y1) = ln[0], ln[-1]
            L = math.hypot(x1 - x0, y1 - y0)
            for t in np.arange(0, L, ppc * 0.42):
                x, y = x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L
                r = ppc * 0.05
                d.ellipse([(x - r) * 2, (y - r) * 2, (x + r) * 2, (y + r) * 2], fill=(8, 10, 18, 190))
            # a few stubborn stitch ends
            for _ in range(int(L / (ppc * 3))):
                t = rng.uniform(0, L)
                x, y = x0 + (x1 - x0) * t / L, y0 + (y1 - y0) * t / L
                d.line([(x * 2, y * 2), ((x + rng.normal(0, ppc * 0.25)) * 2, (y + rng.normal(0, ppc * 0.25)) * 2)],
                       fill=gold, width=max(1, int(ppc * 0.1)))
    for _ in range(loose):  # loose threads
        c = poly.representative_point()
        x, y = c.x + rng.normal(0, w * 0.2), c.y + rng.normal(0, h * 0.2)
        path = [(x, y)]
        a = rng.uniform(0, 2 * math.pi)
        for _ in range(14):
            a += rng.normal(0, 0.5)
            x += math.cos(a) * ppc * 0.6
            y += math.sin(a) * ppc * 0.6
            path.append((x, y))
        d.line([(px * 2, py * 2) for px, py in path], fill=gold, width=max(2, int(ppc * 0.12)), joint="curve")
    ovn = np.asarray(ov.resize((w, h), Image.LANCZOS), np.float32) / 255
    alpha = np.clip(m + ovn[..., 3] * (1 - m), 0, 1)
    rgb = tex * m[..., None] + ovn[..., :3] * ovn[..., 3:4] * (1 - m[..., None])
    rgb = np.where(alpha[..., None] > 1e-3, rgb / np.maximum(alpha, 1e-3)[..., None], 0)
    inside = ovn[..., 3:4] * m[..., None]
    rgb = rgb * (1 - inside) + ovn[..., :3] * inside
    # cloth relief
    n1 = core.fbm(h, w, rng, scale=ppc * 14, octaves=2)
    hf = core.blur(m, ppc * 0.5) + n1 * 0.8 + core.blur((1 - np.abs(2 * n1 - 1)) ** 6, ppc) * 0.5
    gy, gx = np.gradient(core.blur(hf, ppc * 0.4))
    rgb *= np.clip(1 + (-0.55 * gx - 0.75 * gy) * ppc * 1.3, 0.7, 1.3)[..., None]
    return np.clip(rgb, 0, 1), alpha


def paper_obj(pts_cm, ppc, seed=0, label=None, grain=True, notches=(), col=None):
    """Pattern paper: thin ecru paper, pencil lines, notches, grain line, stamped label."""
    rng = np.random.default_rng(seed)
    pts = np.array(pts_cm, np.float32) * ppc
    pts -= pts.min(0)
    pad = int(ppc * 0.6)
    pts += pad
    w, h = int(pts[:, 0].max() + pad), int(pts[:, 1].max() + pad)
    rgb = core.paper(h, w, seed, col if col is not None else core.hexrgb("#E9E2D2"))
    m = core.poly_mask(h, w, [tuple(p) for p in pts], ss=3)
    ov = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pencil = (70, 70, 72, 150)
    # seam allowance line
    inner = Polygon(pts).buffer(-ppc * 1.0, join_style=2)
    if not inner.is_empty and inner.geom_type == "Polygon":
        d.line([(x * 2, y * 2) for x, y in inner.exterior.coords], fill=pencil, width=2)
    if grain:
        c = Polygon(pts).centroid
        L = min(w, h) * 0.32
        a = (c.x * 2, (c.y - L) * 2)
        b = (c.x * 2, (c.y + L) * 2)
        d.line([a, b], fill=pencil, width=2)
        for (px, py), sgn in ((a, 1), (b, -1)):
            d.line([(px, py), (px - ppc * 0.5, py + sgn * ppc * 0.9)], fill=pencil, width=2)
            d.line([(px, py), (px + ppc * 0.5, py + sgn * ppc * 0.9)], fill=pencil, width=2)
    for ei, t in notches:
        a, b = pts[ei], pts[(ei + 1) % len(pts)]
        x, y = a + (b - a) * t
        d.polygon([(x * 2 - ppc * 0.5, y * 2 - ppc * 0.5), (x * 2 + ppc * 0.5, y * 2 - ppc * 0.5), (x * 2, y * 2 + ppc * 0.6)],
                  fill=(30, 30, 30, 160))
    if label:
        f = core.mono(int(ppc * 1.1), medium=True)
        c = Polygon(pts).centroid
        for k, line in enumerate(label.split("\n")):
            d.text((c.x * 2 + ppc * 0.8, (c.y - ppc * 1.4 + k * ppc * 1.4) * 2), line, font=f, fill=(43, 43, 43, 200))
    ovn = np.asarray(ov.resize((w, h), Image.LANCZOS), np.float32) / 255
    rgb = rgb * (1 - ovn[..., 3:4]) + ovn[..., :3] * ovn[..., 3:4]
    # paper never lies flat
    n = core.fbm(h, w, rng, scale=ppc * 20, octaves=2)
    gy, gx = np.gradient(core.blur(n, ppc))
    rgb *= np.clip(1 + (-0.5 * gx - 0.8 * gy) * ppc * 2.5, 0.88, 1.08)[..., None]
    return np.clip(rgb, 0, 1), m * 0.97


def shears_obj(ppc, seed=0):
    """Tailor's shears, closed, top-down."""
    L = int(ppc * 26)
    Wd = int(ppc * 9)
    ss = 3
    im = Image.new("RGBA", (L * ss, Wd * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = ppc * ss
    blade = [(9 * k, 3.6 * k), (26 * k, 4.3 * k), (9 * k, 5.4 * k)]
    blade2 = [(9 * k, 4.2 * k), (25.5 * k, 4.6 * k), (9 * k, 6.0 * k)]
    d.polygon(blade2, fill=(120, 124, 130, 255))
    d.polygon(blade, fill=(168, 172, 178, 255))
    d.line([(9 * k, 4.2 * k), (25 * k, 4.35 * k)], fill=(225, 228, 232, 255), width=int(k * 0.15))
    # handles: black loops
    d.ellipse([0.5 * k, 0.6 * k, 7.6 * k, 4.8 * k], fill=(20, 20, 22, 255))
    d.ellipse([1.9 * k, 1.6 * k, 6.2 * k, 3.8 * k], fill=(0, 0, 0, 0))
    d.ellipse([0.2 * k, 4.6 * k, 6.4 * k, 8.4 * k], fill=(26, 26, 28, 255))
    d.ellipse([1.5 * k, 5.6 * k, 5.0 * k, 7.4 * k], fill=(0, 0, 0, 0))
    d.polygon([(6.6 * k, 2.2 * k), (9.5 * k, 3.5 * k), (9.5 * k, 6.1 * k), (5.6 * k, 6.6 * k)], fill=(24, 24, 26, 255))
    d.ellipse([8.6 * k, 4.2 * k, 9.8 * k, 5.4 * k], fill=(200, 202, 206, 255))
    a = np.asarray(im.resize((L, Wd), Image.LANCZOS), np.float32) / 255
    rgb, al = a[..., :3], a[..., 3]
    rgb = np.where(al[..., None] > 1e-3, rgb / np.maximum(al, 1e-3)[..., None], 0)
    return rgb, al


def tape_obj(ppc, length_cm=60, start=12, seed=0):
    """Cloth tape measure, ecru, printed in mono."""
    L = int(ppc * length_cm)
    Wd = int(ppc * 1.6)
    ss = 2
    im = Image.new("RGBA", (L * ss, Wd * ss), (232, 224, 205, 255))
    d = ImageDraw.Draw(im)
    k = ppc * ss
    f = core.mono(int(k * 0.62), medium=True)
    for mm in range(length_cm * 10):
        x = mm * k / 10
        cm = mm % 10 == 0
        hlen = 0.55 if cm else (0.35 if mm % 5 == 0 else 0.2)
        d.line([(x, 0), (x, hlen * k)], fill=(30, 30, 30, 255), width=max(1, int(k * (0.05 if cm else 0.025))))
        d.line([(x, Wd * ss), (x, Wd * ss - hlen * k)], fill=(30, 30, 30, 255), width=max(1, int(k * (0.05 if cm else 0.025))))
        if cm and mm:
            d.text((x - k * 0.35, k * 0.5), str(start + mm // 10), font=f, fill=(30, 30, 30, 255))
    a = np.asarray(im.resize((L, Wd), Image.LANCZOS), np.float32) / 255
    rng = np.random.default_rng(seed)
    rgb = a[..., :3] * (0.95 + 0.05 * core.fbm(Wd, L, rng, scale=4, octaves=2))[..., None]
    return rgb, np.ones((Wd, L), np.float32)


def spool_obj(ppc, col, seed=0):
    r = int(ppc * 2.8)
    s = r * 2 + 2
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2)
    alpha = np.clip(r - d, 0, 1)
    rgb = np.zeros((s, s, 3), np.float32)
    flange = (d > r * 0.82)
    thread = (d > r * 0.3) & ~flange
    rgb[flange] = core.CHARCOAL * 1.1
    rings = 0.8 + 0.2 * np.sin(d * 2.4)
    ang = np.arctan2(yy - r, xx - r)
    rgb[thread] = (col[None, :] * (rings * (0.85 + 0.15 * np.cos(ang - 2.2)))[..., None])[thread]
    hole = d < r * 0.12
    rgb[hole] = 0.05
    rgb[(d >= r * 0.12) & (d <= r * 0.3)] = core.STONE * 0.9
    return rgb, alpha


def pin_draw(d, x, y, ang, L, head=(30, 30, 32), k=1.0):
    x1, y1 = x + math.cos(ang) * L, y + math.sin(ang) * L
    d.line([(x + 2 * k, y + 3 * k), (x1 + 2 * k, y1 + 3 * k)], fill=(0, 0, 0, 90), width=max(1, int(1.5 * k)))
    d.line([(x, y), (x1, y1)], fill=(190, 194, 200, 255), width=max(1, int(1.4 * k)))
    r = 3.2 * k
    d.ellipse([x - r + 2 * k, y - r + 3 * k, x + r + 2 * k, y + r + 3 * k], fill=(0, 0, 0, 100))
    d.ellipse([x - r, y - r, x + r, y + r], fill=head + (255,))
    d.ellipse([x - r * 0.5, y - r * 0.6, x, y - r * 0.1], fill=(230, 230, 230, 160))


def chalk_lines(img, lines, width, seed=0, col=None):
    """Tailor's chalk: dry, broken lines (no lettering — handwriting is only ever the founder's own)."""
    rng = np.random.default_rng(seed)
    h, w = img.shape[:2]
    m = np.zeros((h, w), np.float32)
    for ln in lines:
        cv2.polylines(m, [np.array(ln, np.int32)], False, 1.0, int(width), cv2.LINE_AA)
    dry = core.fbm(h, w, rng, scale=2, octaves=2)
    dry2 = core.fbm(h, w, rng, scale=width * 3, octaves=2)
    m = m * np.clip((dry * 0.7 + dry2 * 0.6) * 1.5 - 0.35, 0, 1)
    dust = core.blur(m, width * 1.5) * 0.25 * (rng.random((h, w)) > 0.6)
    a = np.clip(m * 0.85 + dust, 0, 1)
    c = col if col is not None else np.array([0.90, 0.91, 0.93], np.float32)
    return img * (1 - a[..., None]) + c * a[..., None]


def ruler_obj(ppc, length_cm=40):
    L, Wd = int(ppc * length_cm), int(ppc * 3.2)
    ss = 2
    im = Image.new("RGBA", (L * ss, Wd * ss), (150, 154, 160, 255))
    d = ImageDraw.Draw(im)
    k = ppc * ss
    f = core.mono(int(k * 0.75), medium=True)
    for mm in range(length_cm * 10):
        x = k * 0.5 + mm * k / 10
        hl = 0.9 if mm % 10 == 0 else (0.6 if mm % 5 == 0 else 0.35)
        d.line([(x, 0), (x, hl * k)], fill=(25, 25, 28, 255), width=max(1, int(k * 0.035)))
        if mm % 10 == 0:
            d.text((x - k * 0.25, k * 1.05), str(mm // 10), font=f, fill=(25, 25, 28, 255))
    a = np.asarray(im.resize((L, Wd), Image.LANCZOS), np.float32) / 255
    rgb = a[..., :3]
    yy = np.linspace(0, 1, Wd)[:, None, None]
    rgb = rgb * (0.85 + 0.25 * np.exp(-((yy - 0.3) ** 2) * 30))   # brushed steel sheen
    return np.clip(rgb, 0, 1), np.ones((Wd, L), np.float32)


def card_obj(ppc, lines, w_cm=9, h_cm=13, seed=0, eyelet=True, title=None):
    """Heavy uncoated ecru board, printed in mono."""
    w, h = int(ppc * w_cm), int(ppc * h_cm)
    rgb = core.paper(h, w, seed, core.hexrgb("#EAE3D3"))
    ss = 3
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    k = ppc * ss
    y = k * 1.4
    if title:
        f = core.stamp(int(k * 0.95), 800)
        for tl in title:
            d.text((k * 0.8, y), tl, font=f, fill=(31, 42, 68, 255))
            y += k * 1.05
        y += k * 0.6
    fm = core.mono(int(k * 0.5))
    fmb = core.mono(int(k * 0.5), medium=True)
    for ln in lines:
        if ln == "---":
            G.dashes(d, [(k * 0.8, y + k * 0.3), (w * ss - k * 0.8, y + k * 0.3)], (201, 104, 47, 255), k * 0.05,
                     dash=k * 0.35, gap=k * 0.2)
            y += k * 0.8
            continue
        d.text((k * 0.8, y), ln, font=fmb if ln.isupper() and len(ln) < 14 else fm, fill=(43, 43, 43, 240))
        y += k * 0.72
    if eyelet:
        cx, cy, r = w * ss / 2, k * 0.8, k * 0.32
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(154, 158, 163, 255))
        d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=(0, 0, 0, 255))
    a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255
    rgb = rgb * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]
    # ink sits into uncoated board: slightly soft
    return np.clip(rgb, 0, 1), np.ones((h, w), np.float32)


# ───────────────────────────────────────────────────────────── surfaces

def bench_surface(H, W, seed):
    """Cutting table: worn grey board, knife scores, chalk dust."""
    rng = np.random.default_rng(seed)
    img = core.concrete(H, W, seed, tone=0.82, smooth=True)
    img = img * 0.7 + core.hexrgb("#6E6A63") * 0.3
    m = np.zeros((H, W), np.float32)
    for _ in range(60):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        a = rng.normal(0, 0.15) + (math.pi / 2 if rng.random() < 0.4 else 0)
        L = rng.uniform(0.05, 0.4) * W
        cv2.line(m, (int(x), int(y)), (int(x + math.cos(a) * L), int(y + math.sin(a) * L)), 1.0, 1, cv2.LINE_AA)
    img *= (1 - m * 0.18)[..., None]
    img += (np.roll(m, 1, 0) * 0.04)[..., None]
    return img


def night(H, W, seed, density=1.0):
    """London at night behind the subject: sodium and LED points, out of focus."""
    rng = np.random.default_rng(seed)
    img = np.zeros((H, W, 3), np.float32) + core.hexrgb("#07090F")
    img += core.fbm(H, W, rng, scale=W / 3, octaves=3)[..., None] * core.hexrgb("#0E1424") * 0.8
    pts = np.zeros((H, W, 3), np.float32)
    cols = [core.hexrgb("#F0A048"), core.hexrgb("#FFD9A0"), core.hexrgb("#DCE6FF"), core.hexrgb("#C8322A"),
            core.hexrgb("#F6F2E8")]
    for _ in range(int(45 * density)):
        x, y = rng.uniform(0, W), rng.uniform(0.05, 0.75) * H
        r = rng.uniform(0.008, 0.04) * W
        c = cols[rng.integers(len(cols))] * rng.uniform(0.3, 1.0)
        cv2.circle(pts, (int(x), int(y)), int(r), tuple(float(v) for v in c), -1, cv2.LINE_AA)
    pts = core.blur(pts, W * 0.004)
    img += pts * 0.55
    # wet pavement glints
    yy = np.linspace(0, 1, H)[:, None]
    glow = core.blur(pts, W * 0.02)
    img += np.flipud(glow) * (yy > 0.7)[..., None] * 0.25
    return img


# ───────────────────────────────────────────────────────────── scenes

def product(g, H, W, seed, ppc, origin, bg="concrete", light="flash", angle=0.0, wash_bias=0.0, tone=1.0):
    rgb, a = G.render_garment(g, H, W, ppc, origin, seed=seed, wash_bias=wash_bias)
    if bg == "concrete":
        base = core.concrete(H, W, seed + 100, tone=tone)
    elif bg == "plaster":
        base = core.plaster(H, W, seed + 100)
    else:
        base = core.paper(H, W, seed + 100, core.STONE)
    if light == "flash":
        base = core.drop_shadow(base, a, ppc * 0.9, ppc * 1.3, ppc * 0.25, 0.6)
    else:
        base = core.drop_shadow(base, a, ppc * 0.3, ppc * 0.9, ppc * 1.4, 0.5)
    img = core.composite(base, rgb, a)
    if angle:
        M = cv2.getRotationMatrix2D((W / 2, H / 2), angle, 1.04)
        img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if light == "flash":
        img = core.flash(img, cy=0.46, r0=0.62, floor=0.3)
    else:
        img = core.available(img, top=1.1, bottom=0.72)
    return img


def hung(g, H, W, seed, ppc, origin, wall="plaster", nightshot=False):
    """Hung on a wall from a steel hook: one hard light, shadow on the wall."""
    rgb, a = G.render_garment(g, H, W, ppc, origin, seed=seed)
    base = {"plaster": core.plaster, "brick": core.brick, "concrete": core.concrete}[wall](H, W, seed + 7)
    if wall == "plaster":
        base *= 0.86
    base = core.drop_shadow(base, a, ppc * 2.2, ppc * 1.6, ppc * 0.5, 0.7)
    img = core.composite(base, rgb, a)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    ox, oy = origin
    hx, hy = ox, oy - ppc * 7
    d.line([(hx + ppc * 2.2, hy + ppc * 1.6), (ox - ppc * 16 + ppc * 2.2, oy + ppc * 3 + ppc * 1.6)], fill=(0, 0, 0, 90), width=int(ppc * 0.4))
    d.line([(hx, hy + ppc * 2), (ox - ppc * 16, oy + ppc * 3)], fill=(150, 154, 160, 255), width=int(ppc * 0.35))
    d.line([(hx, hy + ppc * 2), (ox + ppc * 16, oy + ppc * 3)], fill=(150, 154, 160, 255), width=int(ppc * 0.35))
    d.arc([hx - ppc * 1.2, hy - ppc * 1.0, hx + ppc * 1.2, hy + ppc * 1.4], 180, 360 + 90, fill=(160, 164, 170, 255), width=int(ppc * 0.35))
    d.line([(hx, hy + ppc * 0.2), (hx, hy + ppc * 2)], fill=(150, 154, 160, 255), width=int(ppc * 0.35))
    o = np.asarray(ov, np.float32) / 255
    img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
    if nightshot:
        img = core.flash(img, cy=0.45, r0=0.42, floor=0.05, power=1.05)
    else:
        img = core.flash(img, cx=0.42, cy=0.38, r0=0.7, floor=0.3)
    return img


def macro_seam(H, W, seed, kind="seam"):
    """Construction close-up: two first-life garments meeting at a seam."""
    rng = np.random.default_rng(seed)
    thread = 3.4
    a, _ = core.denim(H, W, core.Wash(base=rng.uniform(0.15, 0.3), seed=seed, whiskers=1), thread=thread, angle=0.05)
    b, _ = core.denim(H, W, core.Wash(base=rng.uniform(0.55, 0.75), seed=seed + 1, knee=(W * 0.7, H * 0.4, W * 0.3, H * 0.3)),
                      thread=thread, angle=-0.4)
    ang = rng.uniform(-0.5, -0.2)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = (xx - W * 0.48) * math.cos(ang) + (yy - H * 0.5) * math.sin(ang)
    side = np.clip(dist / 1.5 + 0.5, 0, 1)
    img = a * (1 - side[..., None]) + b * side[..., None]
    k = W / 60
    # seam relief: raised fell, valley each side
    rel = np.exp(-((dist - k * 1.3) / (k * 1.1)) ** 2) * 0.25 - np.exp(-(dist / (k * 0.35)) ** 2) * 0.5
    img *= (1 + rel)[..., None]
    if kind == "ghost":
        g = np.zeros((H, W), np.float32)
        cv2.rectangle(g, (int(W * 0.58), int(H * 0.12)), (int(W * 0.95), int(H * 0.6)), 1.0, -1)
        g = core.blur(g, 6) * side
        img = img * (1 - g[..., None] * 0.35) + core.INDIGO * g[..., None] * 0.15
    ov = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    nx, ny = math.cos(ang), math.sin(ang)
    tx, ty = -ny, nx
    for off in (k * 0.9, k * 1.9):
        cx, cy = W * 0.48 + nx * off, H * 0.5 + ny * off
        pts = [((cx - tx * W) * 2, (cy - ty * W) * 2), ((cx + tx * W) * 2, (cy + ty * W) * 2)]
        G.dashes(d, pts, (204, 140, 62, 255), k * 0.55, dash=k * 1.6, gap=k * 0.45, shadow=(8, 10, 20, 150), jitter=k * 0.05, rng=rng)
    if kind == "selvedge":
        cx, cy = W * 0.48 - nx * k * 3, H * 0.5 - ny * k * 3
        d.line([((cx - tx * W) * 2, (cy - ty * W) * 2), ((cx + tx * W) * 2, (cy + ty * W) * 2)], fill=(236, 231, 220, 255), width=int(k * 2.4))
        cx2, cy2 = cx - nx * k * 0.6, cy - ny * k * 0.6
        d.line([((cx2 - tx * W) * 2, (cy2 - ty * W) * 2), ((cx2 + tx * W) * 2, (cy2 + ty * W) * 2)], fill=(160, 40, 36, 255), width=int(k * 0.5))
    o = np.asarray(ov.resize((W, H), Image.LANCZOS), np.float32) / 255
    # thread twist highlight
    img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
    if kind == "patch":
        pw, ph = int(W * 0.5), int(W * 0.3)
        pimg = G.patch_image(pw, ph, seed=seed)
        x0, y0 = int(W * 0.12), int(H * 0.55)
        sh = np.zeros((H, W), np.float32)
        sh[y0 + 4:y0 + ph + 6, x0 + 3:x0 + pw + 4] = 1
        img *= (1 - core.blur(sh, 4) * 0.5)[..., None]
        img[y0:y0 + ph, x0:x0 + pw] = pimg
    # shallow depth of field: focus band along the seam
    sharp = img
    soft = core.blur(img, W / 160)
    f = np.clip((np.abs(dist) - W * 0.12) / (W * 0.3), 0, 1)[..., None]
    if kind == "patch":
        f = f * 0.4
    img = sharp * (1 - f) + soft * f
    return core.available(img, top=1.08, bottom=0.7, side_vignette=0.3)


def chalk_macro(H, W, seed):
    rng = np.random.default_rng(seed)
    img, _ = core.denim(H, W, core.Wash(base=0.08, spread=0.08, seed=seed), thread=3.0, angle=0.02)
    # ruler across the top third
    ppc = W / 32
    r_rgb, r_a = ruler_obj(ppc, 40)
    img = place(img, r_rgb, r_a, W * 0.55, H * 0.22, angle=-4, shadow=(ppc * 0.2, ppc * 0.4, ppc * 0.3, 0.6))
    lines = []
    y0 = H * 0.36
    lines.append([(-10, y0 + 30), (W + 10, y0 - 25)])
    lines.append([(W * 0.18, H * 0.30), (W * 0.24, H * 1.05)])
    for k in range(5):  # notch ticks along the line
        x = W * (0.32 + k * 0.13)
        y = y0 + 30 - (x / W) * 55
        lines.append([(x, y - 18), (x, y + 18)])
    cx, cy = W * 0.62, H * 0.7
    lines.append([(cx - 30, cy - 30), (cx + 30, cy + 30)])
    lines.append([(cx - 30, cy + 30), (cx + 30, cy - 30)])
    curve = [(W * 0.3 + math.cos(t) * W * 0.5, H * 1.25 + math.sin(t) * H * 0.75) for t in np.linspace(-2.3, -1.2, 30)]
    lines.append(curve)
    img = chalk_lines(img, lines, max(3, W / 260), seed)
    sh_rgb, sh_a = shears_obj(W / 34)
    img = place(img, sh_rgb, sh_a, W * 0.78, H * 0.86, angle=158, shadow=(14, 20, 10, 0.55))
    return core.available(img, top=1.15, bottom=0.75, side_vignette=0.35)


def pile(H, W, seed, n=34, lit="available"):
    """The pile: a few hundred pairs; this is the top of it."""
    rng = np.random.default_rng(seed)
    img = core.concrete(H, W, seed, tone=0.7)
    for i in range(n):
        depth = i / n
        kind = rng.choice(["trousers", "trousers", "trousers", "trucker", "shirt"])
        g = G.PATTERNS[kind]("front" if rng.random() < 0.6 else "back")
        for p in g.parts:
            p.panels = 1
        g.seams = g.seams[:3]
        g.sources = 1
        lvl = rng.uniform(0.05, 0.8)
        g.wash_range = (lvl, lvl + 0.04)
        ppc = W / rng.uniform(70, 110)
        size_w = int(ppc * 64)
        size_h = int(ppc * 112) if kind == "trousers" else int(ppc * 80)
        rgb, a = G.render_garment(g, size_h, size_w, ppc, (size_w / 2, ppc * 6), seed=int(rng.integers(1e9)), fold=1.6)
        dim = 0.45 + 0.6 * depth
        img = place(img, rgb, a, rng.uniform(-0.05, 1.05) * W, rng.uniform(-0.05, 1.05) * H, angle=rng.uniform(0, 360),
                    scale=rng.uniform(0.85, 1.15), shadow=(ppc * 0.6, ppc * 1.0, ppc * 1.2, 0.75), dim=dim)
    if lit == "flash":
        return core.flash(img, cy=0.5, r0=0.55, floor=0.2)
    return core.available(img, top=1.2, bottom=0.65, side_vignette=0.4)


def bench(H, W, seed, nightshot=False, focus="trucker", wide=False):
    """The bench: a piece in work, pinned, chalked, with the tools that made it."""
    rng = np.random.default_rng(seed)
    img = bench_surface(H, W, seed)
    ppc = W / (100 if wide else 95)
    # pattern paper sheet underneath
    p_rgb, p_a = paper_obj([(0, 0), (58, 0), (60, 44), (2, 46)], ppc, seed, grain=False, col=core.hexrgb("#E4DCCB"))
    img = place(img, p_rgb, p_a, W * 0.33, H * 0.45, angle=-6, shadow=(4, 6, 6, 0.35))
    # half-built body: three panels pinned together
    for k, (pts, x, y, ang) in enumerate([
        ([(0, 0), (22, 0), (24, 30), (2, 33)], 0.28, 0.42, -4),
        ([(0, 0), (19, 2), (18, 31), (0, 29)], 0.42, 0.46, 3),
        ([(0, 0), (16, 0), (15, 18), (0, 20)], 0.36, 0.72, -8),
    ]):
        lvl = [0.18, 0.62, 0.38][k]
        pr, pa = panel_obj(pts, ppc, core.Wash(base=lvl, seed=seed + k, whiskers=k % 2, knee=None),
                           hem_edges=(0,) if k == 0 else (), holes_edges=(1,) if k == 1 else (), seed=seed + k)
        img = place(img, pr, pa, W * x, H * y, angle=ang, shadow=(ppc * 0.25, ppc * 0.4, ppc * 0.3, 0.6))
    # a sleeve, cut, waiting
    sr, sa = panel_obj([(0, 0), (16, 0), (12, 46), (2, 46)], ppc, core.Wash(base=0.5, seed=seed + 9, whiskers=2),
                       hem_edges=(2,), seed=seed + 9)
    img = place(img, sr, sa, W * 0.66, H * 0.42, angle=-72, shadow=(ppc * 0.25, ppc * 0.4, ppc * 0.3, 0.6))
    # pattern piece laid over it
    pp_rgb, pp_a = paper_obj([(0, 0), (14, 0), (11, 40), (3, 40)], ppc, seed + 3, label="RR-014\nL SLEEVE\nCUT 3",
                             notches=[(0, 0.5), (1, 0.4), (3, 0.6)])
    img = place(img, pp_rgb, pp_a, W * 0.7, H * 0.28, angle=-70, shadow=(3, 5, 4, 0.35))
    # chalk on the panels
    img = chalk_lines(img, [[(W * 0.2, H * 0.6), (W * 0.5, H * 0.56)], [(W * 0.47, H * 0.3), (W * 0.49, H * 0.62)]],
                      max(2, ppc * 0.18), seed)
    # pins along the join
    ov = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for t in np.linspace(0, 1, 7):
        x = (W * 0.36 + t * W * 0.01) * 2
        y = (H * 0.3 + t * H * 0.3) * 2
        pin_draw(d, x, y, rng.normal(0.15, 0.1), ppc * 3.2 * 2, head=(30, 30, 32) if t != 0.5 else (154, 158, 163), k=ppc * 0.18)
    o = np.asarray(ov.resize((W, H), Image.LANCZOS), np.float32) / 255
    img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
    # tools
    t_rgb, t_a = tape_obj(ppc, 70)
    img = place(img, t_rgb, t_a, W * 0.55, H * 0.88, angle=8, shadow=(2, 4, 3, 0.4))
    s_rgb, s_a = shears_obj(ppc)
    img = place(img, s_rgb, s_a, W * 0.82, H * 0.68, angle=-130, shadow=(ppc * 0.6, ppc * 1.0, ppc * 0.4, 0.6))
    sp_rgb, sp_a = spool_obj(ppc, core.THREAD_GOLD)
    img = place(img, sp_rgb, sp_a, W * 0.12, H * 0.2, shadow=(ppc * 0.4, ppc * 0.6, ppc * 0.4, 0.55))
    sp2_rgb, sp2_a = spool_obj(ppc * 0.9, core.INDIGO * 1.4)
    img = place(img, sp2_rgb, sp2_a, W * 0.17, H * 0.12, shadow=(ppc * 0.4, ppc * 0.6, ppc * 0.4, 0.55))
    # the one tan: the patch, not yet sewn
    pw, ph = int(ppc * 9), int(ppc * 5.4)
    patch = G.patch_image(pw, ph, seed=seed)
    img = place(img, patch, np.ones((ph, pw), np.float32), W * 0.86, H * 0.3, angle=12, shadow=(3, 5, 3, 0.5))
    if nightshot:
        return core.pool(img, 0.42, 0.5, 0.36 if wide else 0.42, floor=0.035)
    return core.available(img, top=1.15, bottom=0.68, side_vignette=0.3)


def unpicked(H, W, seed, label_prefix="01", zoom=1.0):
    """One pair of 501s taken apart, flat-laid as panels and numbered."""
    rng = np.random.default_rng(seed)
    img = core.concrete(H, W, seed, tone=0.9)
    ppc = min(W / 120, H * 0.78 / 100) * zoom
    lvl = 0.42
    pieces = [
        ([(0, 0), (24, 0), (27, 100), (5, 100), (0, 30)], (0.16, 0.38), 0),
        ([(0, 0), (24, 0), (24, 30), (21, 100), (0, 100)], (0.31, 0.38), 0),
        ([(0, 2), (28, 0), (25, 100), (2, 100), (-3, 32)], (0.47, 0.38), 0),
        ([(0, 0), (28, 2), (31, 32), (27, 100), (4, 100)], (0.63, 0.38), 0),
        ([(0, 0), (14, 0), (14, 15), (7, 18), (0, 15)], (0.8, 0.22), 1),
        ([(0, 0), (14, 0), (14, 15), (7, 18), (0, 15)], (0.9, 0.22), 1),
        ([(0, 0), (42, 0), (42, 4), (0, 4)], (0.3, 0.86), 2),
        ([(0, 0), (8, 0), (8, 9), (0, 9)], (0.85, 0.5), 3),
        ([(0, 0), (22, 0), (22, 6), (0, 9)], (0.6, 0.88), 2),
    ]
    tags = []
    for k, (pts, (x, y), kind) in enumerate(pieces):
        wash = core.Wash(base=lvl + rng.normal(0, 0.04), seed=seed + k, whiskers=2 if k < 4 else 0,
                         knee=(ppc * 12, ppc * 62, ppc * 10, ppc * 12) if k < 4 else None,
                         phone=(ppc * 5, ppc * 3, ppc * 9, ppc * 15) if k == 3 else None)
        pr, pa = panel_obj(pts, ppc, wash, holes_edges=tuple(range(len(pts))) if kind == 0 else (0, 1),
                           loose=2 if k % 3 == 0 else 0, seed=seed + k)
        img = place(img, pr, pa, W * x, H * y, angle=rng.normal(0, 1.5), shadow=(ppc * 0.3, ppc * 0.6, ppc * 0.5, 0.5))
        tags.append((W * x, H * y - pa.shape[0] / 2 + ppc * 3, k + 1))
    # ecru pocket bags (pocketing is cotton, not denim)
    for k, x in enumerate((0.8, 0.9)):
        pr, pa = paper_obj([(0, 0), (16, 0), (17, 22), (8, 26), (0, 20)], ppc, seed + 40 + k, grain=False,
                           col=core.hexrgb("#DCD5C4"))
        img = place(img, pr, pa, W * x, H * 0.78, angle=rng.normal(0, 3), shadow=(ppc * 0.2, ppc * 0.4, ppc * 0.4, 0.4))
        tags.append((W * x, H * 0.78 - ppc * 9, 10 + k))
    for (x, y, n) in tags:
        c_rgb, c_a = card_obj(ppc, [f"{label_prefix}.{n:02d}"], w_cm=5, h_cm=2.4, eyelet=False, seed=n)
        img = place(img, c_rgb, c_a, x, y, angle=rng.normal(0, 4), shadow=(2, 3, 2, 0.4))
    return core.available(img, top=1.12, bottom=0.78, side_vignette=0.28)


def record_card(H, W, seed, piece, lines):
    rng = np.random.default_rng(seed)
    img, _ = core.denim(H, W, core.Wash(base=0.22, seed=seed, whiskers=2), thread=1.6, angle=0.1)
    ppc = W / 26
    c_rgb, c_a = card_obj(ppc, lines, w_cm=11, h_cm=17, seed=seed, title=["RAW", "RETURN"])
    img = place(img, c_rgb, c_a, W * 0.47, H * 0.5, angle=-5, shadow=(ppc * 0.25, ppc * 0.45, ppc * 0.3, 0.6))
    # offcut swatch card
    o_rgb, o_a = panel_obj([(0, 0), (6, 0), (6, 6), (0, 6)], ppc, core.Wash(base=0.55, seed=seed + 2), seed=seed + 2)
    img = place(img, o_rgb, o_a, W * 0.82, H * 0.2, angle=14, shadow=(ppc * 0.15, ppc * 0.25, ppc * 0.2, 0.5))
    return core.flash(img, cy=0.45, r0=0.7, floor=0.35)


def failed_sleeves(H, W, seed):
    rng = np.random.default_rng(seed)
    img = core.plaster(H, W, seed)
    ppc = W / 70
    for k, x in enumerate((0.22, 0.5, 0.78)):
        pr, pa = panel_obj([(0, 0), (15, 0), (12, 52), (3, 52)], ppc,
                           core.Wash(base=[0.3, 0.55, 0.42][k], seed=seed + k, whiskers=2),
                           hem_edges=(1, 3) if k else (1,), holes_edges=(3,) if k == 0 else (), loose=1 if k == 1 else 0,
                           seed=seed + k)
        img = place(img, pr, pa, W * x, H * 0.55, angle=rng.normal(0, 1.5), shadow=(ppc * 1.6, ppc * 1.2, ppc * 1.2, 0.5))
        # bulldog clip
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        cx, cy = W * x, H * 0.55 - pa.shape[0] / 2 + ppc * 0.5
        d.rectangle([cx - ppc * 3, cy - ppc * 1.2, cx + ppc * 3, cy + ppc * 1.6], fill=(32, 32, 34, 255))
        d.line([(cx - ppc * 2, cy - ppc * 1.2), (cx, cy - ppc * 4)], fill=(170, 174, 180, 255), width=int(ppc * 0.3))
        d.line([(cx + ppc * 2, cy - ppc * 1.2), (cx, cy - ppc * 4)], fill=(170, 174, 180, 255), width=int(ppc * 0.3))
        d.ellipse([cx - ppc * 0.5, cy - ppc * 4.6, cx + ppc * 0.5, cy - ppc * 3.6], fill=(90, 90, 90, 255))
        o = np.asarray(ov, np.float32) / 255
        sh = core.blur(np.roll(np.roll(o[..., 3], int(ppc * 1.2), 0), int(ppc * 1.5), 1), ppc * 0.8)
        img *= (1 - sh * 0.4)[..., None]
        img = img * (1 - o[..., 3:4]) + o[..., :3] * o[..., 3:4]
        c_rgb, c_a = card_obj(ppc, [f"ATTEMPT {k + 1}", ["TOO SHORT", "PITCH WRONG", "KEPT"][k]], w_cm=8, h_cm=3.4,
                              eyelet=False, seed=seed + k)
        img = place(img, c_rgb, c_a, W * x + ppc * 4, H * 0.86, angle=rng.normal(0, 3), shadow=(ppc * 0.5, ppc * 0.5, ppc * 0.4, 0.4))
    return core.available(img, top=1.1, bottom=0.62, side_vignette=0.2, warm=0.03)


def street_back(g, H, W, seed, ppc_scale=1.0, crop_origin=(0.5, 0.3)):
    """Returned: the back of the piece, worn, in a crowd at night. Direct flash."""
    rng = np.random.default_rng(seed)
    ppc = W / 64 * ppc_scale
    rgb, a = G.render_garment(g, H, W, ppc, (W * crop_origin[0], H * crop_origin[1] + ppc * 6), seed=seed, fold=1.8)
    # body curvature: the back turns away at the sides
    xx = np.linspace(-1, 1, W)[None, :]
    curv = np.clip(1 - (xx * 0.85) ** 4, 0.25, 1)
    rgb *= curv[..., None]
    bg = night(H, W, seed)
    bg = cv2.GaussianBlur(cv2.blur(bg, (int(W * 0.04) | 1, 1)), (0, 0), 2)  # motion
    img = core.composite(bg, rgb, a)
    img = core.flash(img, cx=0.5 + rng.normal(0, 0.05), cy=0.58, r0=0.36, floor=0.06, power=1.15)
    # slight camera roll, imperfect framing
    M = cv2.getRotationMatrix2D((W / 2, H / 2), rng.uniform(-6, 6), 1.08)
    return cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)


def kerb(g, H, W, seed):
    """Folded on a London kerb at night: double yellow lines, wet asphalt, flash."""
    rng = np.random.default_rng(seed)
    img = core.concrete(H, W, seed, tone=0.48)
    img = img * 0.8 + core.hexrgb("#1A1C20") * 0.2
    # kerb stone
    k0 = int(H * 0.36)
    img[:k0] = core.concrete(k0, W, seed + 3, tone=0.95)[:k0]
    img[k0 - 6:k0 + 6] *= 0.45
    # double yellow lines on the asphalt
    yel = core.hexrgb("#D9A93A")
    for yo in (0.46, 0.53):
        y = int(H * yo)
        band = np.zeros((H, W), np.float32)
        band[y:y + int(H * 0.035)] = 1
        band *= np.clip(core.fbm(H, W, rng, scale=6, octaves=2) * 1.6 - 0.2, 0, 1)
        img = img * (1 - band[..., None] * 0.85) + yel * band[..., None] * 0.85
    ppc = W / 90
    rgb, a = G.render_garment(g, int(H * 0.9), int(W * 0.9), ppc, (W * 0.45, ppc * 8), seed=seed, fold=1.4)
    img = place(img, rgb, a, W * 0.5, H * 0.55, angle=rng.uniform(-14, 14), scale=0.75, shadow=(ppc * 1.0, ppc * 1.4, ppc * 0.4, 0.75))
    return core.flash(img, cy=0.55, r0=0.42, floor=0.06, power=1.1)


def brick_night(g, H, W, seed, ppc_div=80):
    ppc = W / ppc_div
    img = hung(g, H, W, seed, ppc, (W * 0.5, H * 0.2), wall="brick", nightshot=True)
    return img

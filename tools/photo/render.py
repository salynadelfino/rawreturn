"""
Render the Raw Return placeholder photography set.

    python3 tools/photo/render.py            # everything
    python3 tools/photo/render.py rr-014     # only files whose path contains "rr-014"

Output: src/assets/images/<category>/<name>.jpg — the exact paths the site
imports. Replace any file with real photography of the same name (any aspect
ratio works; the site crops with object-fit) and rebuild. Nothing else changes.
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import core  # noqa: E402
import garments as G  # noqa: E402
import scenes as SC  # noqa: E402

core.FONT_DIR = HERE / "fonts"
OUT = HERE.parent.parent / "src" / "assets" / "images"

# piece → (pattern, kwargs, status). Mirrors src/data/pieces.ts.
PIECES = {
    "rr-001": ("belt", {}, "returned"),
    "rr-002": ("trousers", {"panels": 6}, "returned"),
    "rr-003": ("bag", {}, "returned"),
    "rr-004": ("coat", {}, "returned"),
    "rr-005": ("skirt", {}, "returned"),
    "rr-006": ("gilet", {}, "returned"),
    "rr-007": ("shirt", {"panels": 14}, "available"),
    "rr-008": ("trousers", {"carpenter": True, "panels": 5}, "available"),
    "rr-009": ("shirt", {}, "returned"),
    "rr-010": ("trousers", {"wide": True, "panels": 6}, "available"),
    "rr-011": ("trucker", {"panels": 30}, "returned"),
    "rr-012": ("tote", {}, "returned"),
    "rr-013": ("shirt", {"panels": 12}, "returned"),
    "rr-014": ("trucker", {}, "available"),
    "rr-015": ("trousers", {"panels": 4}, "in-work"),
    "rr-016": ("belt", {}, "available"),
}

# cm framing per pattern: (cm across frame, origin y as fraction of height)
FRAME = {"trucker": (104, 0.17), "coat": (104, 0.08), "gilet": (90, 0.17), "shirt": (100, 0.1),
         "trousers": (118, 0.07), "skirt": (98, 0.17), "tote": (80, 0.38), "bag": (60, 0.32), "belt": (124, 0.48)}


def seed_of(key):
    return int(key.split("-")[1]) * 101


def jobs():
    J = []
    P, L, S = (1600, 2000), (2000, 1334), (1600, 1600)

    def add(path, size, fn, **grade):
        J.append((path, size, fn, grade))

    # ── hero & workshop (available light)
    add("hero/hero-bench-night.jpg", (2400, 1500), lambda W, H: SC.bench(H, W, 3, nightshot=True, wide=True),
        grain=0.045, halation=0.7)
    add("workshop/bench-day.jpg", L, lambda W, H: SC.bench(H, W, 21))
    add("workshop/the-pile.jpg", (2400, 1600), lambda W, H: SC.pile(H, W, 4, n=30), grain=0.04)
    add("workshop/the-pile-flash.jpg", P, lambda W, H: SC.pile(H, W, 44, n=24, lit="flash"), grain=0.045)
    add("workshop/chalk-on-indigo.jpg", L, lambda W, H: SC.chalk_macro(H, W, 6))
    add("workshop/topstitch-macro.jpg", S, lambda W, H: SC.macro_seam(H, W, 7))
    add("workshop/selvedge-macro.jpg", S, lambda W, H: SC.macro_seam(H, W, 17, kind="selvedge"))
    add("workshop/ghost-pocket-macro.jpg", S, lambda W, H: SC.macro_seam(H, W, 27, kind="ghost"))
    add("workshop/patch-macro.jpg", L, lambda W, H: SC.macro_seam(H, W, 8, kind="patch"))

    # ── process, in making order
    add("process/01-find.jpg", L, lambda W, H: SC.pile(H, W, 31, n=22))
    add("process/02-unpick.jpg", L, lambda W, H: SC.unpicked(H, W, 32, zoom=2.4))
    add("process/03-study.jpg", L, lambda W, H: SC.unpicked(H, W, 33))
    add("process/04-cut.jpg", L, lambda W, H: SC.chalk_macro(H, W, 34))
    add("process/05-rebuild.jpg", L, lambda W, H: SC.bench(H, W, 35))
    add("process/06-record.jpg", L, lambda W, H: SC.record_card(H, W, 36, "RR-014", RECORD_014))
    add("process/07-return.jpg", L, lambda W, H: SC.street_back(G.trucker("back"), H, W, seed_of("rr-014")), grain=0.05, halation=0.9, vignette=0.45)
    add("process/failed-sleeves.jpg", L, lambda W, H: SC.failed_sleeves(H, W, 10))

    # ── founder: the hand, not the face
    add("founder/founder-bench.jpg", P, lambda W, H: SC.bench(H, W, 51, nightshot=True))
    add("founder/founder-hands-chalk.jpg", P, lambda W, H: SC.chalk_macro(H, W, 52))

    # ── archive
    add("archive/rr-014-record.jpg", P, lambda W, H: SC.record_card(H, W, 61, "RR-014", RECORD_014))

    # ── pieces
    for key, (pat, kw, status) in PIECES.items():
        s = seed_of(key)
        cm, oy = FRAME[pat]

        def front(W, H, pat=pat, kw=kw, s=s, cm=cm, oy=oy, key=key):
            g = G.PATTERNS[pat]("front", **kw)
            ppc = W / cm
            if int(key[-2:]) % 2:
                return SC.product(g, H, W, s, ppc, (W / 2, H * oy), bg="concrete", light="flash")
            return SC.hung(g, H, W, s, ppc, (W / 2, H * max(oy, 0.14)), wall="plaster")

        def back(W, H, pat=pat, kw=kw, s=s, cm=cm, oy=oy):
            g = G.PATTERNS[pat]("back", **kw)
            return SC.product(g, H, W, s, W / cm, (W / 2, H * oy), bg="concrete", light="flash")

        add(f"products/{key}-front.jpg", P, front)
        if status in ("available", "in-work") or key in ("rr-011", "rr-013"):
            add(f"products/{key}-back.jpg", P, back)
            kind = ["seam", "ghost", "selvedge", "patch"][s % 4]
            add(f"products/{key}-detail.jpg", S, lambda W, H, s=s, kind=kind: SC.macro_seam(H, W, s + 3, kind=kind))
        if status != "in-work":
            if pat in ("trucker", "shirt", "coat", "gilet"):
                fn = (lambda W, H, pat=pat, kw=kw, s=s: SC.street_back(G.PATTERNS[pat]("back", **kw), H, W, s))
            elif pat in ("trousers", "skirt"):
                fn = (lambda W, H, pat=pat, kw=kw, s=s: SC.brick_night(G.PATTERNS[pat]("front", **kw), H, W, s, ppc_div=150))
            else:
                fn = (lambda W, H, pat=pat, kw=kw, s=s: SC.kerb(G.PATTERNS[pat]("front", **kw), H, W, s))
            add(f"street/{key}-returned.jpg", P, fn, grain=0.05, halation=0.9, vignette=0.45)

    # ── street (direct flash, night)
    add("street/night-kerb.jpg", L, lambda W, H: SC.kerb(G.trucker("front"), H, W, 71), grain=0.05, halation=0.9)
    add("street/brick-flash.jpg", P, lambda W, H: SC.brick_night(G.trucker("front"), H, W, 72), grain=0.05, halation=0.9)
    return J


RECORD_014 = ["RR-014 · 1/1", "---", "FIRST LIFE", "4 × LEVI'S 501", "1 × LEE 101J", "FOUND: WALTHAMSTOW E17",
              "DATE: 03.2026", "---", "SECOND LIFE", "PANEL TRUCKER", "23 PANELS", "HOURS: 38", "ATTEMPTS: 3 (L. SLEEVE)"]


JOBS = []


def _run(i):
    path, (W, H), fn, gr = JOBS[i]
    t = time.time()
    img = fn(W, H)
    img = core.grade(img, seed=i, **gr)
    core.save(img, OUT / path)
    return f"{path:44s} {W}×{H}  {time.time() - t:5.1f}s"


def main():
    import multiprocessing as mp

    flt = sys.argv[1] if len(sys.argv) > 1 else ""
    JOBS.extend(jobs())  # inherited by forked workers; lambdas never need pickling
    todo = [i for i, j in enumerate(JOBS) if not flt or flt in j[0]]
    # heaviest first so the pool stays busy
    todo.sort(key=lambda i: ("pile" not in JOBS[i][0], "hero" not in JOBS[i][0]))
    ctx = mp.get_context("fork")
    with ctx.Pool(max(1, min(4, mp.cpu_count()))) as pool:
        for line in pool.imap_unordered(_run, todo):
            print(line, flush=True)


if __name__ == "__main__":
    main()

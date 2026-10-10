"""Geostrophic wind and circulation, one animated figure → img/m-geo-wind.svg

One panel per hemisphere on the same chart: a LOW above, a HIGH below, both "stadium" shaped so the
isobars between them are truly straight and their ends are circular arcs.

Phase 1 (adjustment) — integrated step by step in the drawn pressure field:
    dv/dt = PGF + Coriolis - k (v·n) n        (n = unit vector across the isobars)
  The parcel starts at rest; PGF pushes it towards the LOW, Coriolis (right NH / left SH) turns it
  until it runs along the isobars. The damping acts only on motion ACROSS the isobars (it stands in
  for geostrophic adjustment, never pushes the air) and is not drawn.
Phase 2 (circulation) — the parcel follows the isobar round the LOW at the gradient-wind speed for
  the local curvature (isobars drawn as organic, slightly irregular rings):  V²/R + |f| V = |f| Vg.
  Straight isobars: V = Vg and Coriolis = PGF (geostrophic). Curved ends: V < Vg, so Coriolis < PGF
  and the difference is exactly the centripetal force V²/R that turns the air (gradient wind).
Arrows: PGF = alpha·|grad p| from the field, Coriolis = |f|·V, wind = V; same numbers as the motion.
Run: python3 tools/diagrams/geostrophic.py
"""
import math, os
import numpy as np
import contourpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.environ.get("OUT", os.path.join(ROOT, "img"))
FONT = 'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,"Helvetica Neue",Arial,sans-serif'
C_PGF, C_COR, C_WIND = "#e0483e", "#2f6fd6", "#1d2733"
C_L, C_H = "#d93a33", "#2a62c9"
PAPER, ISO = "#f6f3ea", "#6b7380"

W, H, PW = 1520, 760, 760
LX, LY, HX, HY, SIG = 245, 330, 560, 330, 92   # LOW left, HIGH right
F, ALPHA, K = 2.0, 2300.0, 4.5
LEVEL = 1008                        # the (drawn) isobar the parcel ends up circling
DT, FPS = 0.002, 10
PLAY = 0.72                         # playback time per physical second (same path and forces)
NEAR_STRAIGHT = 0.93                # V/Vg above this: "nearly straight", PGF ≈ Coriolis

def _rho(x, y, cx, cy, ph):
    """distance with a gentle angular wobble -> organic, hand-drawn-looking isobars"""
    dx, dy = x - cx, y - cy
    th = np.arctan2(dy, dx)
    return np.hypot(dx, dy) * (1 + 0.07 * np.sin(3 * th + ph) + 0.04 * np.sin(5 * th + 2 * ph))

def p(x, y):
    return (1012 - 16 * np.exp(-_rho(x, y, LX, LY, 0.6) ** 2 / (2 * SIG ** 2))
            + 16 * np.exp(-_rho(x, y, HX, HY, 2.1) ** 2 / (2 * (SIG * 0.9) ** 2)))

def grad(x, y, h=0.5):  # math coords (y up)
    return ((p(x + h, y) - p(x - h, y)) / (2 * h), -(p(x, y + h) - p(x, y - h)) / (2 * h))

def contours():
    xs = np.linspace(20, PW - 20, 420); ys = np.linspace(70, 640, 360)
    X, Y = np.meshgrid(xs, ys)
    gen = contourpy.contour_generator(X, Y, p(X, Y))
    return [(lev, ln) for lev in range(996, 1032, 4) for ln in gen.lines(lev)], gen

# ---------------------------------------------------------------- phase 1
def curvature(x, y, h=1.0):
    """Signed isobar curvature, kappa = div(grad p / |grad p|); > 0 round lower pressure (cyclonic)."""
    def n(xx, yy):
        gx, gy = grad(xx, yy); m = math.hypot(gx, gy) or 1e-12
        return gx / m, gy / m
    nxp, _ = n(x + h, y); nxm, _ = n(x - h, y)
    _, nyp = n(x, y - h); _, nym = n(x, y + h)          # math y up = screen y down
    return (nxp - nxm) / (2 * h) + (nyp - nym) / (2 * h)

def balanced_wind(x, y, f):
    """Gradient-wind velocity along the local isobar (= geostrophic where the isobars are straight)."""
    gx, gy = grad(x, y)
    vgx, vgy = (ALPHA / f) * -gy, (ALPHA / f) * gx
    Vg = math.hypot(vgx, vgy)
    if Vg < 1e-9: return 0.0, 0.0
    kap = curvature(x, y); fa = abs(f)
    if abs(kap) < 1e-6: V = Vg
    elif kap > 0:
        R = 1 / kap; V = (-fa * R + math.sqrt((fa * R) ** 2 + 4 * fa * R * Vg)) / 2
    else:
        R = -1 / kap; V = (fa * R - math.sqrt(max((fa * R) ** 2 - 4 * fa * R * Vg, 0.0))) / 2
    return vgx / Vg * V, vgy / Vg * V

def adjust(f, start, T=8.0):
    x, y = start; vx = vy = 0.0; out = []; t = 0.0
    while t <= T + 1e-9:
        gx, gy = grad(x, y)
        apx, apy = -ALPHA * gx, -ALPHA * gy
        acx, acy = f * vy, -f * vx
        out.append((t, x, y, vx, vy, apx, apy, acx, acy))
        # damp only the across-isobar part of the motion (never drives the air)
        m = math.hypot(gx, gy) or 1e-12; nx, ny = gx / m, gy / m
        vn = vx * nx + vy * ny
        ax = apx + acx - K * vn * nx; ay = apy + acy - K * vn * ny
        vx += ax * DT; vy += ay * DT; x += vx * DT; y -= vy * DT; t += DT
    return out

# ---------------------------------------------------------------- phase 2
def circulate(f, ring, x0, y0, t0):
    """Follow the closed isobar `ring` (screen coords) from the point nearest (x0, y0) for one lap."""
    ring = ring[:-1] if np.hypot(*(ring[0] - ring[-1])) < 1e-6 else ring
    area = 0.5 * np.sum(ring[:, 0] * np.roll(ring[:, 1], -1) - np.roll(ring[:, 0], -1) * ring[:, 1])  # >0 = clockwise on screen
    want_cw = f < 0                                   # NH anticlockwise round the LOW, SH clockwise
    if (area > 0) != want_cw: ring = ring[::-1]
    i0 = int(np.argmin(np.hypot(ring[:, 0] - x0, ring[:, 1] - y0)))
    ring = np.roll(ring, -i0, axis=0)
    seg = np.hypot(*np.diff(np.vstack([ring, ring[:1]]), axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)]); Ltot = s[-1]
    ss = np.linspace(0, Ltot, 1400)
    xs = np.interp(ss, s, np.append(ring[:, 0], ring[0, 0])); ys = np.interp(ss, s, np.append(ring[:, 1], ring[0, 1]))
    fa = abs(f)
    out = []; t = t0
    n = len(ss)
    for i in range(n - 1):
        x, y = xs[i], ys[i]
        a = np.array([xs[i - 6], ys[i - 6]]); b = np.array([x, y]); c = np.array([xs[(i + 6) % n], ys[(i + 6) % n]])
        cr = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
        den = np.linalg.norm(b - a) * np.linalg.norm(c - b) * np.linalg.norm(c - a)
        kap = 2 * cr / den if den > 0 else 0.0
        gx, gy = grad(x, y); P = ALPHA * math.hypot(gx, gy); Vg = P / fa
        if kap < 1e-4: V = Vg
        else:
            R = 1 / kap; V = (-fa * R + math.sqrt((fa * R) ** 2 + 4 * fa * R * Vg)) / 2
        tx, ty = xs[i + 1] - x, -(ys[i + 1] - y); m = math.hypot(tx, ty); tx, ty = tx / m, ty / m
        vx, vy = V * tx, V * ty
        out.append((t, x, y, vx, vy, -ALPHA * gx, -ALPHA * gy, f * vy, -f * vx, V / Vg))
        t += m / V * PLAY
    return out

def T(x, y, s, cls="lbl", a="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}" {extra}>{s}</text>'

STYLE = f"""<style>
text{{{FONT}}}
.hd{{font-size:21px;font-weight:700;fill:#1d2733}} .hs{{font-size:13.5px;fill:#5b6573}}
.lbl{{font-size:15px;font-weight:600;fill:#1d2733}} .lbw{{font-size:14.5px;font-weight:600;fill:#fff}}
.sm{{font-size:13px;fill:#3e4856}} .iso{{font-size:11.5px;font-weight:600;fill:#4a5361}}
.big{{font-size:38px;font-weight:800}}
.tag{{font-size:14px;font-weight:700;paint-order:stroke;stroke:{PAPER};stroke-width:4px;stroke-linejoin:round}}
</style>"""

def markers():
    return "".join(f'<marker id="a{n}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto">'
                   f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                   for n, c in (("p", C_PGF), ("c", C_COR), ("w", C_WIND), ("g", "#7d93ab")))

def run(sh, gen):
    f = -F if sh else F
    ring = max(gen.lines(LEVEL), key=len)
    y_start = LY + (55 if not sh else -55)        # NH air turns north (up) after leaving, SH south
    lo, hi = LX + 60, HX - 40                     # start x range (at rest, between the systems)
    for _ in range(30):
        mid = (lo + hi) / 2
        r = adjust(f, (mid, y_start))[-1]
        if p(r[1], r[2]) < LEVEL: lo = mid       # ended too deep in the low: start further out
        else: hi = mid
    ph1 = adjust(f, ((lo + hi) / 2, y_start))
    def aligned(r):
        gx, gy = grad(r[1], r[2]); vgx, vgy = (ALPHA / f) * -gy, (ALPHA / f) * gx
        ang = math.atan2(r[3] * vgy - r[4] * vgx, r[3] * vgx + r[4] * vgy)
        bx, by = balanced_wind(r[1], r[2], f); Vb = math.hypot(bx, by)
        return (abs(ang) < math.radians(6) and abs(p(r[1], r[2]) - LEVEL) < 0.2
                and abs(math.hypot(r[3], r[4]) - Vb) < 0.06 * Vb)
    cut = next((i for i, r in enumerate(ph1) if r[0] > 1.0 and aligned(r)), len(ph1) - 1)
    ph1 = [(r[0] * PLAY,) + tuple(r[1:]) for r in ph1[: cut + 1]]
    t1 = ph1[-1][0]
    ph2 = circulate(f, ring, ph1[-1][1], ph1[-1][2], t1)
    return ph1, ph2, t1

def panel(ox, sh, cons, gen):
    ph1, ph2, t1 = run(sh, gen)
    t_end = ph2[-1][0]
    dur = t_end + 1.6
    allf = [r[:9] for r in ph1] + [r[:9] for r in ph2]
    frames, nxt = [], 0.0
    for r in allf:
        if r[0] >= nxt - 1e-9: frames.append(r); nxt = r[0] + 1 / FPS
    if frames[-1] is not allf[-1]: frames.append(allf[-1])
    keyTimes = ";".join(f"{fr[0]/dur:.4f}" for fr in frames) + ";1"
    
    g = []
    g.append(f'<rect x="{ox+12}" y="12" width="{PW-24}" height="{H-24}" rx="18" fill="{PAPER}" stroke="#e2ddcf"/>')
    hdr = "Southern hemisphere" if sh else "Northern hemisphere"
    sub = ("Coriolis deflects LEFT · LOW clockwise, HIGH anticlockwise" if sh
           else "Coriolis deflects RIGHT · LOW anticlockwise, HIGH clockwise")
    g.append(T(ox + 34, 48, hdr, "hd") + T(ox + PW - 34, 48, sub, "hs", "end"))
    for lev, ln in cons:
        d = "M" + " L".join(f"{ox+a:.1f},{b:.1f}" for a, b in ln)
        closed = np.hypot(*(ln[0] - ln[-1])) < 3
        g.append(f'<path d="{d}" fill="none" stroke="{ISO}" stroke-width="1.5"/>')
        if closed and lev != 1012:
            around_L = lev < 1012
            area = 0.5 * np.sum(ln[:-1, 0] * ln[1:, 1] - ln[1:, 0] * ln[:-1, 1])
            want_cw = (not around_L) if not sh else around_L
            sign = -1 if (area > 0) == want_cw else 1
            col = C_L if around_L else C_H
            g.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-dasharray="9 33" opacity=".45">'
                     f'<animate attributeName="stroke-dashoffset" from="0" to="{sign*42}" dur="1.8s" repeatCount="indefinite"/></path>')
        i = int(np.argmin(ln[:, 0])) if lev < 1012 else int(np.argmax(ln[:, 0])) if lev > 1012 else int(np.argmin(ln[:, 1]))
        lx, ly = ox + min(max(ln[i, 0], 44), PW - 44), max(ln[i, 1], 76)
        g.append(f'<rect x="{lx-20}" y="{ly-9}" width="40" height="18" rx="6" fill="{PAPER}"/>' + T(lx, ly + 4, str(lev), "iso", "middle"))
    g.append(T(ox + LX, LY + 13, "L", "big", "middle", f'style="fill:{C_L}"'))
    g.append(T(ox + HX, HY + 13, "H", "big", "middle", f'style="fill:{C_H}"'))

    pts = [(ox + fr[1], fr[2]) for fr in frames]
    cum = [0.0]
    for (a, b), (c, d) in zip(pts, pts[1:]): cum.append(cum[-1] + math.hypot(c - a, d - b))
    Lt = cum[-1]
    vals = lambda arr: ";".join(f"{v:.1f}" for v in list(arr) + [arr[-1]])
    an = lambda attr, arr: f'<animate attributeName="{attr}" values="{vals(arr)}" keyTimes="{keyTimes}" dur="{dur:.2f}s" repeatCount="indefinite"/>'
    fade = f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;{(dur-0.4)/dur:.4f};1" dur="{dur:.2f}s" repeatCount="indefinite"/>'
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    g.append(f'<g>{fade}<polyline points="{poly}" fill="none" stroke="#e7a21a" stroke-width="3" stroke-linecap="round" '
             f'stroke-dasharray="{Lt:.1f} {Lt:.1f}">' + an("stroke-dashoffset", [Lt - c for c in cum]) + '</polyline>')
    g.append(f'<circle cx="{pts[0][0]:.1f}" cy="{pts[0][1]:.1f}" r="4" fill="#e7a21a"/>'
             + T(pts[0][0], pts[0][1] + 26, "air at rest", "sm", "middle"))
    Pref = np.mean([math.hypot(r[5], r[6]) for r in ph2])
    s_force = 54.0 / Pref                      # one scale for PGF and Coriolis: lengths compare honestly
    s_wind = 84.0 / (Pref / F)
    def vec(color, mk, comp, label, off):
        x1, y1, x2, y2, tx, ty = [], [], [], [], [], []
        for fr in frames:
            cx, cy = ox + fr[1], fr[2]
            dx, dy = comp(fr); ex, ey = cx + dx, cy - dy
            m = math.hypot(dx, dy) or 1
            x1.append(cx); y1.append(cy); x2.append(ex); y2.append(ey)
            tx.append(min(max(ex + dx / m * off, ox + 46), ox + PW - 46)); ty.append(min(max(ey - dy / m * off + 5, 70), H - 130))
        return (f'<line stroke="{color}" stroke-width="5" stroke-linecap="round" marker-end="url(#a{mk})">'
                + an("x1", x1) + an("y1", y1) + an("x2", x2) + an("y2", y2) + "</line>"
                + f'<text class="tag" text-anchor="middle" style="fill:{color}">{label}' + an("x", tx) + an("y", ty) + "</text>")
    g.append(vec(C_PGF, "p", lambda fr: (fr[5] * s_force, fr[6] * s_force), "PGF", 24))
    g.append(vec(C_COR, "c", lambda fr: (fr[7] * s_force, fr[8] * s_force), "Coriolis", 38))
    g.append(vec(C_WIND, "w", lambda fr: (fr[3] * s_wind, fr[4] * s_wind), "wind", 28))
    g.append('<circle r="9" fill="#f2b632" stroke="#fff" stroke-width="2.5">'
             + an("cx", [a for a, b in pts]) + an("cy", [b for a, b in pts]) + "</circle></g>")

    side = "RIGHT" if sh else "LEFT"          # where the LOW is (Buys Ballot)
    turn = "LEFT" if sh else "RIGHT"           # which way Coriolis deflects
    rot = "clockwise" if sh else "anticlockwise"
    def banner(text, spans):
        """visible during each (t0, t1) span"""
        kt, vv = [0.0], [0]
        for t0, t1_ in spans:
            k0, k1 = t0 / dur, t1_ / dur
            e = min(0.01, (k1 - k0) / 3)
            kt += [k0, k0 + e, k1 - e, k1]; vv += [0, 1, 1, 0]
        kt.append(1.0); vv.append(0)
        op = (f'<animate attributeName="opacity" values="{";".join(map(str, vv))}" '
              f'keyTimes="{";".join(f"{k:.4f}" for k in kt)}" dur="{dur:.2f}s" repeatCount="indefinite"/>')
        return (f'<g opacity="0">{op}<rect x="{ox+30}" y="{H-114}" width="{PW-60}" height="38" rx="19" fill="#1d2733"/>'
                + T(ox + PW / 2, H - 89.5, text, "lbw", "middle") + "</g>")
    # straight / curved spans from the isobar curvature along the lap
    spans = {True: [], False: []}
    cur, t_start = None, t1
    for r in ph2:
        c = r[9] < NEAR_STRAIGHT
        if cur is None: cur = c
        if c != cur:
            spans[cur].append((t_start, r[0])); cur, t_start = c, r[0]
    spans[cur].append((t_start, dur - 0.3))
    tb = t1 * 0.35
    g.append(banner("At rest: the PGF pushes the air from the HIGH towards the LOW", [(0.0, tb)]))
    g.append(banner(f"Moving air feels Coriolis, which turns it to the {turn}", [(tb, t1)]))
    g.append(banner(f"Nearly straight isobars: PGF ≈ Coriolis → geostrophic wind, LOW on its {side}", spans[False]))
    g.append(banner(f"Curved isobars: PGF > Coriolis → the air turns {rot} round the LOW (gradient wind)", spans[True]))
    bx, by = ox + PW / 2, H - 48
    g.append(f'<rect x="{bx-178}" y="{by-19}" width="356" height="38" rx="19" fill="#ffffff" stroke="#d9d3c3"/>')
    g.append(f'<g transform="translate({bx-150},{by})"><ellipse rx="12" ry="7.5" fill="#cfd8e3"/><circle cy="-1" r="5" fill="#f2b632"/>'
             f'<line x1="0" y1="22" x2="0" y2="11" stroke="#7d93ab" stroke-width="3" marker-end="url(#ag)"/></g>')
    g.append(T(bx + 12, by + 5.5, f"Back to the wind: LOW on your {side}", "lbl", "middle"))

    st = [math.hypot(r[7], r[8]) / math.hypot(r[5], r[6]) for r in ph2 if r[9] >= NEAR_STRAIGHT]
    cu = [math.hypot(r[7], r[8]) / math.hypot(r[5], r[6]) for r in ph2 if r[9] < NEAR_STRAIGHT]
    print(("SH" if sh else "NH"), f"adjust {t1:.1f}s, loop {t_end - t1:.1f}s · Coriolis/PGF straight {np.mean(st):.3f}, "
          f"bends {min(cu):.2f}-{max(cu):.2f} · start {ph1[0][1]:.0f},{ph1[0][2]:.0f}")
    return "".join(g)

def build():
    cons, gen = contours()
    parts = [panel(k * PW, sh, cons, gen) for k, sh in enumerate((False, True))]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Animation: geostrophic wind forming and circulating round a low, northern and southern hemispheres">'
           f'{STYLE}<defs>{markers()}</defs>{"".join(parts)}</svg>')
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "m-geo-wind.svg"), "w").write(svg)
    print("m-geo-wind.svg", len(svg) // 1024, "KB")

if __name__ == "__main__":
    build()

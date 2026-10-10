"""Geostrophic wind, two images (illustrated style, animated SVG):

img/m-geo-balance.svg     how the geostrophic wind forms: a parcel starts at rest, the PGF pushes it
                          towards the LOW, Coriolis deflects it (right NH / left SH) until the two
                          balance and the wind blows parallel to the isobars. NH and SH side by side.
img/m-geo-circulation.svg circulation round a LOW and a HIGH on a chart, NH vs SH, with flowing wind.

The parcel path is integrated, not hand-drawn: dv/dt = PGF + Coriolis - k (v - vg)
(the small damping stands in for the adjustment that, in the real atmosphere, leaves the wind
geostrophic above the friction layer).
Run: python3 tools/diagrams/geostrophic.py
"""
import math, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.environ.get("OUT", os.path.join(ROOT, "img"))

FONT = 'font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",Inter,"Helvetica Neue",Arial,sans-serif'
C_PGF, C_COR, C_WIND = "#e0483e", "#2f6fd6", "#1d2733"
C_L, C_H = "#d93a33", "#2a62c9"
PAPER, ISO = "#f6f3ea", "#5d6672"

def T(x, y, s, cls="lbl", a="start", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{a}" {extra}>{s}</text>'

STYLE = f"""<style>
text{{{FONT}}}
.hd{{font-size:21px;font-weight:700;fill:#1d2733}} .hs{{font-size:13.5px;fill:#5b6573}}
.lbl{{font-size:15px;font-weight:600;fill:#1d2733}} .lbw{{font-size:15px;font-weight:600;fill:#fff}} .sm{{font-size:13px;fill:#3e4856}}
.iso{{font-size:12px;font-weight:600;fill:#4a5361}}
.big{{font-size:40px;font-weight:800}}
.tag{{font-size:14px;font-weight:700;paint-order:stroke;stroke:{PAPER};stroke-width:4px;stroke-linejoin:round}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>"""

def arrowdefs():
    out = []
    for n, c in (("p", C_PGF), ("c", C_COR), ("w", C_WIND), ("g", "#8a94a3")):
        out.append(f'<marker id="a{n}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto">'
                   f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
    return "".join(out)

# ------------------------------------------------------------------ image 1: balance
def simulate(f=7.0, P=85 * 49.0, k=4.5, T=0.9, n=900):
    """math coords (y up), start at rest; NH Coriolis deflects to the right."""
    vg = P / f
    x = y = vx = vy = 0.0
    dt = T / n
    pts = [(0, 0, 0, 0)]
    for _ in range(n):
        ax = f * vy - k * (vx - vg)
        ay = P - f * vx - k * vy
        vx += ax * dt; vy += ay * dt
        x += vx * dt; y += vy * dt
        pts.append((x, y, vx, vy))
    return pts, vg, f, P

def balance_svg():
    W, H = 1520, 640
    PW = 760
    pts, vg, f, P = simulate()
    NF = 72
    step = (len(pts) - 1) // NF
    frames = pts[::step][: NF + 1]
    # scale arrows: final PGF = Coriolis = 64 px, final wind = 92 px
    A_P = 64.0
    s_cor = A_P / (f * vg)
    s_wind = 92.0 / vg
    iso_y = [150, 255, 360, 465]
    press = [1004, 1008, 1012, 1016]
    x0, y0 = 120, 438                     # NH start (svg coords), SH mirrored
    dur, move = 9.0, 6.0                  # seconds: motion then hold
    kt_move = [i / NF * move / dur for i in range(NF + 1)]
    keyTimes = ";".join(f"{t:.4f}" for t in kt_move + [1.0])

    def panel(ox, sh):
        sgn = -1 if sh else 1
        X = lambda px: ox + (x0 + px * 1.0 if not sh else PW - x0 - px)
        Y = lambda py: y0 - py
        g = []
        # background + isobars
        g.append(f'<rect x="{ox+14}" y="70" width="{PW-28}" height="{H-84}" rx="18" fill="{PAPER}" stroke="#e2ddcf"/>')
        for yy, p in zip(iso_y, press):
            g.append(f'<line x1="{ox+30}" y1="{yy}" x2="{ox+PW-30}" y2="{yy}" stroke="{ISO}" stroke-width="1.6"/>')
            lx = ox + (48 if not sh else PW - 92)
            g.append(f'<rect x="{lx-4}" y="{yy-10}" width="48" height="20" rx="6" fill="{PAPER}"/>' + T(lx + 20, yy + 4.5, str(p), "iso", "middle"))
        # LOW / HIGH
        g.append(T(ox + PW / 2, 128, "L", "big", "middle", f'fill="{C_L}"') + T(ox + PW / 2 + 34, 122, "LOW", "lbl", "start", f'style="fill:{C_L}"'))
        g.append(T(ox + PW / 2, 528, "H", "big", "middle", f'fill="{C_H}"') + T(ox + PW / 2 + 34, 522, "HIGH", "lbl", "start", f'style="fill:{C_H}"'))
        # heading
        hdr = "Southern hemisphere" if sh else "Northern hemisphere"
        sub = "Coriolis deflects to the LEFT" if sh else "Coriolis deflects to the RIGHT"
        g.append(T(ox + 36, 104, hdr, "hd") + T(ox + PW - 36, 104, sub, "hs", "end"))
        # trail
        tp = [(X(px), Y(py)) for px, py, _, _ in frames]
        cum = [0.0]
        for (a, b), (c, d) in zip(tp, tp[1:]):
            cum.append(cum[-1] + math.hypot(c - a, d - b))
        Ltot = cum[-1]
        poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in tp)
        offs = ";".join(f"{Ltot - c:.1f}" for c in cum) + f";{0:.1f}"
        g.append(f'<polyline points="{poly}" fill="none" stroke="#e7a21a" stroke-width="3" stroke-linecap="round" stroke-dasharray="{Ltot:.1f} {Ltot:.1f}" stroke-dashoffset="{Ltot:.1f}">'
                 f'<animate attributeName="stroke-dashoffset" values="{offs}" keyTimes="{keyTimes}" dur="{dur}s" repeatCount="indefinite" calcMode="linear"/></polyline>')
        # start marker
        g.append(f'<circle cx="{tp[0][0]:.1f}" cy="{tp[0][1]:.1f}" r="4" fill="#e7a21a" opacity=".6"/>'
                 + T(tp[0][0] + (14 if not sh else -14), tp[0][1] + 24, "air at rest", "sm", "start" if not sh else "end"))
        # moving vectors
        def anim_line(cls_color, mk, getter, label, lab_off):
            xs1, ys1, xs2, ys2, tx, ty = [], [], [], [], [], []
            for (px, py, vx, vy) in frames:
                cx, cy = X(px), Y(py)
                dx, dy = getter(vx, vy)               # math coords
                if sh: dx = -dx
                ex, ey = cx + dx, cy - dy
                xs1.append(cx); ys1.append(cy); xs2.append(ex); ys2.append(ey)
                m = math.hypot(dx, dy) or 1
                tx.append(ex + dx / m * lab_off); ty.append(ey - dy / m * lab_off + 5)
            def vals(a): return ";".join(f"{v:.1f}" for v in a + [a[-1]])
            an = lambda attr, a: f'<animate attributeName="{attr}" values="{vals(a)}" keyTimes="{keyTimes}" dur="{dur}s" repeatCount="indefinite"/>'
            s = (f'<line stroke="{cls_color}" stroke-width="5" stroke-linecap="round" marker-end="url(#a{mk})">'
                 + an("x1", xs1) + an("y1", ys1) + an("x2", xs2) + an("y2", ys2) + "</line>")
            s += (f'<text class="tag" text-anchor="middle" fill="{cls_color}">{label}' + an("x", tx) + an("y", ty) + "</text>")
            return s
        g.append(anim_line(C_PGF, "p", lambda vx, vy: (0, A_P), "PGF", 26))
        g.append(anim_line(C_COR, "c", lambda vx, vy: (s_cor * f * vy, -s_cor * f * vx), "Coriolis", 40))
        g.append(anim_line(C_WIND, "w", lambda vx, vy: (s_wind * vx, s_wind * vy), "wind", 30))
        # parcel
        cxs = ";".join(f"{X(px):.1f}" for px, *_ in frames) + f";{X(frames[-1][0]):.1f}"
        cys = ";".join(f"{Y(py):.1f}" for _, py, *_ in frames) + f";{Y(frames[-1][1]):.1f}"
        g.append(f'<circle r="9" fill="#f2b632" stroke="#fff" stroke-width="2.5">'
                 f'<animate attributeName="cx" values="{cxs}" keyTimes="{keyTimes}" dur="{dur}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="cy" values="{cys}" keyTimes="{keyTimes}" dur="{dur}s" repeatCount="indefinite"/></circle>')
        # result banner (fades in during the hold)
        res = "Balanced: PGF = Coriolis · wind ∥ isobars · LOW on its " + ("RIGHT" if sh else "LEFT")
        op = f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;{move/dur*0.92:.3f};{move/dur:.3f};0.97;1" dur="{dur}s" repeatCount="indefinite"/>'
        g.append(f'<g opacity="0">{op}<rect x="{ox+PW/2-262}" y="{H-62}" width="524" height="36" rx="18" fill="#1d2733"/>'
                 + T(ox + PW / 2, H - 38.5, res, "lbw", "middle") + "</g>")
        return "".join(g)

    body = panel(0, False) + panel(PW, True)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {56} {W} {H-56+4}" width="{W}" height="{H-52}" role="img" '
           f'aria-label="Animation: geostrophic wind forming in the northern and southern hemispheres">{STYLE}'
           f'<defs>{arrowdefs()}</defs>{body}</svg>')
    return svg

# ------------------------------------------------------------------ image 2: circulation
def ring(cx, cy, rx, ry, wob, seed, n=72):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = 1 + wob * (math.sin(3 * a + seed) * 0.6 + math.sin(5 * a + seed * 2) * 0.4)
        pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(n):
        p0, p1 = pts[i], pts[(i + 1) % n]
        d += f" L{p1[0]:.1f},{p1[1]:.1f}"
    return d + "Z"

def circulation_svg():
    W, H = 1520, 600
    PW = 760
    parts = []
    def system(cx, cy, kind, cw, base_p, seed):
        """cw = True: clockwise flow on screen."""
        g = []
        sizes = [(70, 54), (128, 100), (186, 146), (244, 190)]
        for i, (rx, ry) in enumerate(sizes):
            d = ring(cx, cy, rx * 0.62, ry * 0.68, 0.05, seed + i)
            g.append(f'<path d="{d}" fill="none" stroke="{ISO}" stroke-width="1.5"/>')
            # flowing wind: dashes moving along the isobar (path direction is clockwise on screen)
            dirn = -1 if cw else 1
            g.append(f'<path d="{d}" fill="none" stroke="{C_L if kind=="L" else C_H}" stroke-width="3.2" stroke-linecap="round" '
                     f'stroke-dasharray="10 34" opacity=".75"><animate attributeName="stroke-dashoffset" from="0" to="{dirn*44*(1)}" '
                     f'dur="{1.4+0.25*i:.2f}s" repeatCount="indefinite"/></path>')
            p = base_p + (4 * (i + 1) if kind == "L" else -4 * (i + 1))
            lx, ly = cx + rx * 0.62 * 1.0, cy - 4
            g.append(f'<rect x="{lx-21}" y="{ly-10}" width="42" height="19" rx="6" fill="{PAPER}"/>' + T(lx, ly + 4.5, str(p), "iso", "middle"))
        col = C_L if kind == "L" else C_H
        g.append(T(cx, cy + 14, kind, "big", "middle", f'fill="{col}"'))
        # one big direction arrow on the outer ring (top), screen direction
        y_top = cy - 190 * 0.68 - 18
        a1, a2 = (cx - 60, cx + 60) if cw else (cx + 60, cx - 60)
        g.append(f'<path d="M{a1},{y_top+8} Q{cx},{y_top-14} {a2},{y_top+8}" fill="none" stroke="{col}" stroke-width="4" marker-end="url(#a{"p" if kind=="L" else "c"})"/>')
        return "".join(g)
    for k, sh in enumerate((False, True)):
        ox = k * PW
        parts.append(f'<rect x="{ox+14}" y="14" width="{PW-28}" height="{H-28}" rx="18" fill="{PAPER}" stroke="#e2ddcf"/>')
        hdr = "Southern hemisphere" if sh else "Northern hemisphere"
        sub = "LOW clockwise · HIGH anticlockwise" if sh else "LOW anticlockwise · HIGH clockwise"
        parts.append(T(ox + 36, 50, hdr, "hd") + T(ox + PW - 36, 50, sub, "hs", "end"))
        # NH: low anticlockwise (cw False), high clockwise
        parts.append(system(ox + 200, 300, "L", sh, 1000, 1.0 + k))
        parts.append(system(ox + 560, 300, "H", not sh, 1032, 2.5 + k))
        # Buys Ballot badge
        bx, by = ox + 380, H - 70
        parts.append(f'<rect x="{bx-170}" y="{by-26}" width="340" height="52" rx="26" fill="#1d2733"/>')
        parts.append(f'<g transform="translate({bx-136},{by})"><ellipse cx="0" cy="0" rx="13" ry="8" fill="#e8edf3"/><circle cx="0" cy="-1" r="5.5" fill="#f2b632"/>'
                     f'<line x1="0" y1="26" x2="0" y2="12" stroke="#9fb3c8" stroke-width="3" marker-end="url(#ag)"/></g>')
        side = "RIGHT" if sh else "LEFT"
        parts.append(T(bx + 14, by + 5.5, f"Back to the wind: LOW on your {side}", "lbw", "middle"))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Circulation round lows and highs in the northern and southern hemispheres">{STYLE}'
           f'<defs>{arrowdefs()}</defs>{"".join(parts)}</svg>')
    return svg

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("m-geo-balance.svg", balance_svg), ("m-geo-circulation.svg", circulation_svg)):
        s = fn()
        open(os.path.join(OUT, name), "w").write(s)
        print(name, len(s) // 1024, "KB")

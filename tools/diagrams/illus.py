"""Illustrated-style toolkit: clean vector clouds with cel shading (pure SVG, no raster).

cumulus(): union of circles, flat base, lit top-left, shaded bottom-right.
stratus(): flat grey layer with gently undulating edges.
cirrus():  thin hooked filaments (Ci uncinus) drawn as tapered strokes.
"""
import math, random

def _circles_cu(x, base, w, h, rnd):
    """Circles making a cumulus: a bottom row resting on the flat base plus a domed crown."""
    cs = []
    rb = h * 0.36
    nb = max(3, int((w - rb) / (rb * 0.85)) + 1)
    for i in range(nb):
        cx = x + rb * 0.7 + (w - rb * 1.4) * i / (nb - 1)
        cs.append((cx, base - rb * 0.45 + rnd.uniform(-2, 2), rb * rnd.uniform(0.9, 1.05), 0))
    # interior core so shrunken highlight layers leave no holes
    for tt in (0.25, 0.4, 0.5, 0.6, 0.75):
        bump = math.sin(math.pi * tt)
        cs.append((x + tt * w, base - h * (0.3 + 0.32 * bump), h * (0.22 + 0.12 * bump), 1))
    t = 0.08
    while t < 0.93:
        bump = math.sin(math.pi * t)
        r = h * (0.12 + 0.13 * bump) * rnd.uniform(0.8, 1.15)
        prof = h * (0.42 + 0.58 * bump ** 1.3)
        cs.append((x + t * w, base - prof + r, r, 1))
        t += (r * 0.75) / w
    for _ in range(4 + int(w > 180) * 2):
        tt = rnd.uniform(0.28, 0.72); r = h * rnd.uniform(0.10, 0.17)
        cs.append((x + tt * w, base - h + r * 0.95, r, 1))
    return cs

def cumulus(id, x, base, w, h, seed=1, lit="#ffffff", mid="#eef2f7", shade="#c3ccd8", line="#93a0b2"):
    """x = left edge, base = flat cloud base y, w/h = size. Returns SVG string."""
    rnd = random.Random(seed)
    cs = _circles_cu(x, base, w, h, rnd)
    def U(off=(0, 0), k=1.0, fill="#000", crown=False):
        return "".join(f'<circle cx="{cx+off[0]:.1f}" cy="{cy+off[1]:.1f}" r="{r*k:.1f}" fill="{fill}"/>'
                       for cx, cy, r, c in cs if c or not crown)
    top = min(cy - r for cx, cy, r, c in cs) - 4
    clip = (f'<clipPath id="{id}c"><rect x="{x-w:.0f}" y="{top-20:.0f}" width="{w*3:.0f}" height="{base-top+20:.1f}"/></clipPath>'
            f'<clipPath id="{id}u">{U(k=0.955)}</clipPath>'
            f'<linearGradient id="{id}g" x1="0" y1="{top:.0f}" x2="0" y2="{base:.0f}" gradientUnits="userSpaceOnUse">'
            f'<stop offset=".55" stop-color="{shade}" stop-opacity="0"/><stop offset="1" stop-color="#8592a4" stop-opacity=".8"/></linearGradient>'
            f'<filter id="{id}s1" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="1.1"/></filter>'
            f'<filter id="{id}s2" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="{max(2.0, w/90):.1f}"/></filter>')
    body = (f'<g clip-path="url(#{id}c)">'
            f'<g filter="url(#{id}s1)" opacity=".7">{U(k=1.0, fill=line)}</g>'   # soft outline
            f'{U(k=0.955, fill=shade)}'                                     # shadow tone
            f'<g filter="url(#{id}s2)">{U(off=(-w*0.008, -h*0.02), k=0.9, fill=mid)}</g>'   # mid tone, blended
            f'<g opacity=".95" filter="url(#{id}s2)">{U(off=(-w*0.018, -h*0.05), k=0.72, fill=lit)}</g>'  # sunlit body, blended
            f'<g filter="url(#{id}s1)" opacity=".35">{U(off=(w*0.004, h*0.012), k=0.98, fill=shade, crown=True)}</g>'  # lobe rims
            f'<g filter="url(#{id}s1)" opacity=".9">{U(off=(-w*0.012, -h*0.03), k=0.8, fill=lit, crown=True)}</g>'  # lobe highlights
            f'<rect x="{x-w*0.1:.0f}" y="{top:.0f}" width="{w*1.2:.0f}" height="{base-top:.1f}" fill="url(#{id}g)" clip-path="url(#{id}u)"/>'  # grey base
            f'</g>')
    return clip, body

def stratus(x0, x1, base, top, seed=2, fill="#b8c1cc", dark="#9aa5b2", line="#7f8b99"):
    rnd = random.Random(seed)
    n = int((x1 - x0) / 40) + 2
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    tp = [top + rnd.uniform(-5, 5) for _ in xs]
    bt = [base + rnd.uniform(-3, 4) for _ in xs]
    def smooth(pts):
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for i in range(1, len(pts)):
            px, py = pts[i - 1]; cx, cy = pts[i]
            d += f" Q{px:.1f},{py:.1f} {(px+cx)/2:.1f},{(py+cy)/2:.1f}"
        return d + f" L{pts[-1][0]:.1f},{pts[-1][1]:.1f}"
    up = list(zip(xs, tp)); dn = list(zip(xs[::-1], bt[::-1]))
    d = smooth(up) + " " + smooth(dn).replace("M", "L", 1) + " Z"
    # inner darker lower band
    mid = [(x, (t + b) / 2 + 3) for x, t, b in zip(xs, tp, bt)]
    d2 = smooth(mid) + " " + smooth(dn).replace("M", "L", 1) + " Z"
    fid = f"st{seed}"
    return (f'<filter id="{fid}" x="-5%" y="-40%" width="110%" height="180%"><feGaussianBlur stdDeviation="1.3"/></filter>'
            f'<linearGradient id="{fid}g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d3dae2"/><stop offset="1" stop-color="{fill}"/></linearGradient>'
            f'<g filter="url(#{fid})"><path d="{d}" fill="url(#{fid}g)" stroke="{line}" stroke-width="1" stroke-opacity=".6" stroke-linejoin="round"/>'
            f'<path d="{d2}" fill="{dark}" opacity=".5"/></g>')

def cirrus(x, y, length, seed=3, n=5, col="#ffffff"):
    """Hooked filaments: a curving streak ending in an upward tuft (Ci uncinus)."""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        sx = x + rnd.uniform(0, length * 0.5); sy = y + rnd.uniform(-14, 14)
        L = length * rnd.uniform(0.45, 0.8)
        ex, ey = sx + L, sy + rnd.uniform(-6, 6)
        d = (f"M{sx:.1f},{sy+L*0.10:.1f} C{sx+L*0.25:.1f},{sy+L*0.02:.1f} {sx+L*0.6:.1f},{ey+4:.1f} {ex:.1f},{ey:.1f}"
             f" q{8:.1f},{-2:.1f} {10:.1f},{-12:.1f}")
        for wdt, op in ((7, .18), (3.2, .4), (1.2, .85)):
            out.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{wdt}" stroke-linecap="round" opacity="{op * rnd.uniform(.7, 1):.2f}"/>')
    fid = f"ci{seed}"
    return (f'<filter id="{fid}" x="-5%" y="-50%" width="110%" height="200%"><feGaussianBlur stdDeviation="0.9"/></filter>'
            f'<g filter="url(#{fid})">' + "".join(out) + "</g>")

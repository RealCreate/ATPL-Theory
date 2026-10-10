"""Warm front vertical cross-section → img/warmfront.svg (animated) + img/warmfront.jpg (static).

Geometry follows the usual ATPL / Met Office figures: frontal slope ≈ 1:150,
Ci up to ≈ 1000 km ahead at 8–10 km, Cs ≈ 600–850 km, As ≈ 300–650 km,
Ns and the rain belt within ≈ 300 km (≈ 200 nm) of the surface front;
St/Sc and drizzle in the warm sector behind.
Run:  python3 tools/diagrams/warmfront.py
"""
import base64, io, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
sys.path.insert(0, os.path.dirname(__file__))
from scene import Scene, smooth, to_img

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W, HDR, SH, FTR = 1520, 72, 748, 172          # svg units: header, scene, footer
H = HDR + SH + FTR
FX, KX = 340, 1.1                             # front at x=340, 1.1 units per km
G, KY = 690, 56                               # ground (scene-local) and units per km altitude
xk = lambda km: FX + km * KX
yh = lambda h: G - h * KY
SLOPE = 150.0
front = lambda km: np.maximum(km, 0) / SLOPE   # frontal surface altitude (km)

S = Scene(W, SH, xk, yh, scale=2, seed=7)
KM, ALT = S.KM, S.ALT

# ---------------- clouds ----------------
# One continuous frontal cloud body in the warm air above the frontal surface:
# dense, amorphous Ns near the surface front -> layered As -> thin fibrous Cs veil ahead.
def ramp(x, xp, fp): return np.interp(x, xp, fp).astype(np.float32)
k = KM
base = np.maximum(front(k) + 0.15, 0.3)
top = ramp(k, [-170, -90, -30, 40, 150, 400, 650, 900, 1000], [1.3, 2.6, 4.6, 6.1, 6.8, 6.9, 7.4, 7.9, 8.0])
th = np.maximum(top - base, 1e-3)
u = (ALT - base) / th
nb = S.noise(18, 9, 6, 0.6, seed=101)        # ragged base
nt = S.noise(8, 6, 5, 0.5, seed=102)         # gently undulating top
t_ns = S.noise(14, 20, 6, 0.62, seed=103)    # amorphous
t_as = S.noise(5, 42, 6, 0.6, seed=104)      # layered
t_cs = S.noise(3, 90, 6, 0.6, seed=105)      # fibrous
w_ns = smooth((330 - k) / 120)
w_cs = smooth((k - 560) / 160)
w_as = np.clip(1 - w_ns - w_cs, 0, 1)
tex = w_ns * (0.74 + 0.75 * (t_ns - .5)) + w_as * (0.52 + 1.1 * (t_as - .5)) + w_cs * (0.30 + 1.0 * (t_cs - .5))
edge = 0.16 + 0.25 * w_cs
m = smooth((ALT - base + (nb - .5) * (1.0 * w_ns + 0.5)) / (0.35 + 0.5 * w_cs)) * smooth((1 - u + (nt - .5) * 0.35) / edge)
dk = ramp(k, [-180, -80, 0, 280, 450, 650, 850, 930], [0, 0.55, 1, 1, 0.8, 0.5, 0.32, 0])
S.add_density(m * np.clip(tex, 0, 1) * dk, albedo=0.9)
# warm sector: St / Sc sheet with a few breaks, drizzle beneath
cell = S.noise(46, 9, 5, 0.5, seed=41); n1 = S.noise(20, 6, 4, 0.5, seed=42)
u2 = (ALT - 0.42) / 0.95
m2 = smooth((u2 + (n1 - .5) * 0.5) / 0.3) * smooth((1 - u2 + (cell - .5) * 0.45) / 0.3)
S.add_density(m2 * np.clip(0.58 + (cell - .5) * 2.0, 0, 1) * smooth((-k + 10) / 50) * 0.8, albedo=0.66)
# cold air under the Ns: St fractus / frontal fog in the rain
S.add_layer(5, 220, lambda k: 0.0 + 0 * k, lambda k: 0.8 + 0 * k,
            kind="fractus", edge=0.45, fade=45, dens=1.0, seed=53, albedo=0.85)
S.light(sigma=0.016, slope=0.35)
crgb, ca = S.cloud_rgba()

# cirrus layer baked separately (it drifts in the SVG)
CI = Scene(W, SH, xk, yh, scale=2, seed=9)
CI.add_layer(720, 1075, lambda k: 8.5 + 0 * k, lambda k: 10.1 + 0 * k,
             kind="ci", edge=0.45, fade=95, dens=0.9, seed=61)
CI.T = np.ones_like(CI.dens); CI.Ta = np.ones_like(CI.dens)
cirgb, cia = CI.cloud_rgba(opac=3.2)

# ---------------- sky / air ----------------
h, w = S.h, S.w
t = np.clip(S.Y / SH, 0, 1)[..., None]
zen, hor = np.array([.27, .45, .72], np.float32), np.array([.78, .85, .91], np.float32)
sky = zen + (hor - zen) * (t ** 1.35)
# warm air a touch warmer / hazier, cold wedge cooler and greyer
cold = smooth((front(KM) - ALT) / 0.25) * (KM > -5)
sky = sky * (1 - 0.16 * cold[..., None]) + np.array([.60, .66, .72], np.float32) * 0.16 * cold[..., None]
# rain & low cloud dim the air: shadow from the sun march plus extra murk in the rain zone
shade = (0.86 + 0.14 * gaussian_filter(S.T, 10)) * (0.58 + 0.42 * gaussian_filter(np.where(S.dens > 0.05, 1.0, S.Ta), 45))
rainzone = smooth((KM + 10) / 30) * smooth((300 - KM) / 60) * (ALT < front(KM) + 0.4) * 1.0
murk = gaussian_filter(rainzone.astype(np.float32), 6)
sky = sky * shade[..., None]
sky = sky * (1 - 0.25 * murk[..., None]) + np.array([.42, .45, .50], np.float32) * 0.25 * murk[..., None]

# ---------------- rain shafts (baked soft streaks) ----------------
streak = S.noise(240, 3, 4, 0.5, seed=5)
streak = np.roll(streak, 0, axis=1)
# slant the streaks slightly (falling into the wind)
sl = np.zeros_like(streak)
for y in range(h):
    sl[y] = np.roll(streak[y], int(y * 0.12))
nsbase = np.maximum(front(KM) + 0.12, 0.35)
rmask = smooth((KM + 15) / 25) * smooth((310 - KM) / 70) * (ALT < nsbase + 0.2) * (ALT > -0.05)
heavy = 1 - 0.55 * smooth(KM / 300)                     # heavier near the front
rain = rmask * heavy * np.clip(0.35 + (sl - .5) * 2.0, 0, 1)
# virga under the As (evaporating before the ground)
vmask = smooth((KM - 290) / 30) * smooth((470 - KM) / 60) * (ALT < front(KM) + 0.45) * smooth((ALT - front(KM) + 1.1) / 0.9)
rain += vmask * 0.45 * np.clip(0.3 + (sl - .5) * 2.2, 0, 1)
# drizzle in the warm sector
dmask = smooth((-KM - 10) / 40) * (ALT < 0.5) * 0.35
rain += dmask * np.clip(0.4 + (sl - .5) * 1.8, 0, 1)
rain = gaussian_filter(rain, (1.5, 0.6))
rcol = np.array([.33, .36, .41], np.float32)
ra = np.clip(rain * 0.8, 0, 0.7)[..., None]
img = sky * (1 - ra) + rcol * ra

# ---------------- clouds over sky ----------------
img = img * (1 - ca[..., None]) + crgb * ca[..., None]

# ---------------- terrain ----------------
xs = np.arange(w) / 2
r = np.random.default_rng(3)
def ridge(cells, amp, seed):
    g = np.random.default_rng(seed).random(cells + 4)
    z = np.interp(np.linspace(1, cells + 1, w), np.arange(cells + 4), g)
    return gaussian_filter(z, w / cells / 3) * amp
far = G - 10 - ridge(28, 26, 4) - ridge(90, 6, 5)
near = G + 6 - ridge(18, 16, 6) - ridge(120, 4, 7)
Yp = S.Y
farm = smooth((Yp - far[None, :]) * 2)
nearm = smooth((Yp - near[None, :]) * 2)

gi = (np.clip((near * 2).astype(int), 0, h - 1), np.arange(w))
gT = ((0.6 + 0.4 * gaussian_filter(S.T[gi], 30)) * (0.62 + 0.38 * gaussian_filter(S.Ta[gi], 30)))[None, :, None]
haze = np.array([.55, .62, .66], np.float32)
farc = (np.array([.34, .42, .36], np.float32) * 0.55 + haze * 0.45) * gT
img = img * (1 - farm[..., None]) + farc * farm[..., None]
gtex = S.noise(160, 30, 5, 0.55, seed=8)
nearc = np.stack([.24 + .08 * gtex, .32 + .08 * gtex, .19 + .05 * gtex], -1) * gT
depth = smooth((Yp - near[None, :]) / 50)[..., None]
nearc = nearc * (1 - 0.35 * depth)
wet = (smooth((KM + 10) / 20) * smooth((300 - KM) / 40))[..., None]
nearc = nearc * (1 - 0.12 * wet) + np.array([.20, .23, .24], np.float32) * 0.12 * wet
img = img * (1 - nearm[..., None]) + nearc * nearm[..., None]
# low mist hugging the ground in rain / drizzle
mist = gaussian_filter((smooth((KM + 330) / 30) * smooth((310 - KM) / 60)).astype(np.float32) * smooth((G + 4 - Yp) / 26) * smooth((Yp - G + 60) / 40), 20)
img = img * (1 - 0.35 * mist[..., None]) + np.array([.62, .65, .68], np.float32) * 0.35 * mist[..., None]

# film grain + very soft vignette so it reads as a photograph, not a gradient
grain = np.random.default_rng(1).normal(0, 0.012, (h, w, 1)).astype(np.float32)
vy, vx = (S.Y / SH - .5), (S.X / W - .5)
vig = 1 - 0.10 * (vx ** 2 * 1.2 + vy ** 2)
img = np.clip(img * vig[..., None] + grain, 0, 1)

base = to_img(img)
vis = (1 - smooth((S.dens - 0.08) / 0.35)) * smooth((KM + 6) / 14) * smooth((305 - KM) / 50) * (ALT < front(KM) + 1.6)
vis = gaussian_filter(vis.astype(np.float32), 3) * (1 - nearm)
rvis = Image.fromarray((np.clip(vis, 0, 1) * 255).astype(np.uint8), "L").resize((W, SH), Image.LANCZOS)
ci = Image.fromarray(np.dstack([(np.clip(cirgb, 0, 1) * 255).astype(np.uint8),
                                (np.clip(cia, 0, 1) * 235).astype(np.uint8)]), "RGBA")
# crop the cirrus to its bounding box to keep the file small
bb = ci.getbbox()
ci_c = ci.crop(bb)
OUT = os.environ.get("OUT", os.path.join(ROOT, "img"))
os.makedirs(OUT, exist_ok=True)

def b64(im, fmt, **kw):
    bio = io.BytesIO(); im.save(bio, fmt, **kw); return base64.b64encode(bio.getvalue()).decode()

bg64 = b64(base, "JPEG", quality=84, optimize=True, progressive=True)
ci64 = b64(ci_c, "PNG", optimize=True)
rv64 = b64(rvis, "PNG", optimize=True)
cix, ciy, ciw, cih = bb[0] / 2, bb[1] / 2, (bb[2] - bb[0]) / 2, (bb[3] - bb[1]) / 2

# ---------------- vector overlay ----------------
Y0 = HDR
def P(km, hkm): return xk(km), Y0 + yh(hkm)
def pts(seq): return " ".join(f"{x:.1f},{y:.1f}" for x, y in seq)

fs_end = 1072
fx0, fy0 = P(0, 0); fx1, fy1 = P(fs_end, fs_end / SLOPE)
ang = np.degrees(np.arctan2(fy1 - fy0, fx1 - fx0))

# warm-air streamlines: rising gently over the wedge, parallel-ish to the frontal surface
streams = []
for i, (off, kend) in enumerate([(0.9, 560), (2.5, 800), (4.1, 940)]):
    seq = []
    for k in np.linspace(-300, kend, 70):
        lift = (np.log1p(np.exp((k + 60) / 60)) * 60) / SLOPE    # soft ramp onto the frontal slope
        seq.append(P(k, off + lift))
    streams.append(seq)

# rain streak field (animated) clipped to rain belt
rng = np.random.default_rng(12)
drops = []
for _ in range(1100):
    k = rng.uniform(-8, 300) ** 1.0
    if rng.random() < 0.55 * (k / 300): continue
    x, y = xk(k) + rng.uniform(-4, 4), Y0 + rng.uniform(yh(k / SLOPE + 1.7) - 60, G)
    drops.append((x, y))
rain_top = [P(-8, 0.35), P(0, 0.35)] + [P(k, max(k / SLOPE + 0.12, 0.35)) for k in range(0, 311, 10)]
rain_clip = pts(rain_top + [P(310, -0.3), P(-8, -0.3)])

lens = rng.uniform(7, 14, len(drops))
def drop_lines(dy):
    return "".join(f'<line x1="{x:.1f}" y1="{y+dy:.1f}" x2="{x-1.3:.1f}" y2="{y+dy+L:.1f}"/>' for (x, y), L in zip(drops, lens))

T = lambda x, y, s, cls="lbl", anchor="start", extra="": f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{s}</text>'

ticks = []
for hkm in range(2, 12, 2):
    y = Y0 + yh(hkm)
    ft = int(round(hkm * 3280.84 / 500) * 500)
    ticks.append(f'<line x1="22" y1="{y:.1f}" x2="34" y2="{y:.1f}" class="tick"/>'
                 + T(40, y + 4, f"{hkm} km", "ax") + T(40, y + 18, f"{ft:,} ft".replace(",", " "), "axs"))
xt = []
for km in (-200, 0, 300, 600, 900):
    x = xk(km)
    xt.append(f'<line x1="{x:.1f}" y1="{HDR+SH:.1f}" x2="{x:.1f}" y2="{HDR+SH+8:.1f}" class="tickd"/>'
              + T(x, HDR + SH + 24, ("+" if km > 0 else "") + f"{km} km", "axd", "middle"))

trop_y = Y0 + yh(11)
# surface front = the single point where the frontal surface meets the ground (x = 0 km)
semis = (f'<line x1="{xk(-24):.1f}" y1="{Y0+G:.1f}" x2="{xk(24):.1f}" y2="{Y0+G:.1f}" class="wfl"/>'
         + "".join(f'<path d="M{xk(k)-6:.1f},{Y0+G-1:.1f} a6,6 0 0 1 12,0 z" class="wf"/>' for k in (-14, 0, 14)))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Warm front vertical cross-section">
<title>Warm front · vertical cross-section</title>
<style>
  text{{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Inter","Helvetica Neue",Arial,sans-serif}}
  .h1{{font-size:24px;font-weight:600;fill:#14171c;letter-spacing:-.2px}}
  .sub{{font-size:14px;fill:#6b7280}}
  .lbl{{font-size:16px;font-weight:600;fill:#fff;paint-order:stroke;stroke:rgba(15,20,30,.55);stroke-width:3.2px;stroke-linejoin:round}}
  .sm{{font-size:13px;font-weight:500;fill:#f3f5f8;paint-order:stroke;stroke:rgba(15,20,30,.55);stroke-width:3px;stroke-linejoin:round}}
  .big{{font-size:21px;font-weight:700;fill:#fff;letter-spacing:.3px;paint-order:stroke;stroke:rgba(15,20,30,.45);stroke-width:3.5px}}
  .ax{{font-size:12.5px;font-weight:600;fill:#fff;paint-order:stroke;stroke:rgba(15,20,30,.5);stroke-width:3px}}
  .axs{{font-size:10.5px;fill:#e8edf3;paint-order:stroke;stroke:rgba(15,20,30,.5);stroke-width:2.6px}}
  .axd{{font-size:13px;fill:#4b5563}} .cap{{font-size:13.5px;fill:#374151}} .capb{{font-size:14px;font-weight:600;fill:#111827}}
  .src{{font-size:11.5px;fill:#9ca3af}}
  .tick{{stroke:#fff;stroke-width:1.5;opacity:.85}} .tickd{{stroke:#9ca3af;stroke-width:1.2}}
  .fs{{fill:none;stroke:#fff;stroke-width:2.2;stroke-dasharray:10 7;opacity:.95}}
  .trop{{fill:none;stroke:#fff;stroke-width:1.2;stroke-dasharray:3 6;opacity:.55}}
  .flow{{fill:none;stroke:#ffe9c7;stroke-width:2.6;stroke-linecap:round;stroke-dasharray:7 34;opacity:.7;animation:flow 2.6s linear infinite}}
  .flow2{{animation-duration:3.1s}} .flow3{{animation-duration:3.6s}}
  @keyframes flow{{to{{stroke-dashoffset:-41}}}}
  .rain line{{stroke:#d5dde6;stroke-width:.8;opacity:.42;stroke-linecap:round}}
  .rainA{{animation:fall .9s linear infinite}}
  @keyframes fall{{from{{transform:translate(0,-60px)}}to{{transform:translate(-7px,0)}}}}
  .ci{{animation:drift 40s ease-in-out infinite alternate}}
  @keyframes drift{{from{{transform:translate(-4px,0)}}to{{transform:translate(16px,0)}}}}
  .wf{{fill:#d9363e}} .wfl{{stroke:#d9363e;stroke-width:4}}
  .mv{{fill:none;stroke:#fff;stroke-width:2.4}}
  .mvp{{animation:nudge 3s ease-in-out infinite}}
  @keyframes nudge{{0%,100%{{transform:translate(0,0)}}50%{{transform:translate(6px,0)}}}}
  @media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<defs>
  <clipPath id="sc"><rect x="0" y="{HDR}" width="{W}" height="{SH}"/></clipPath>
  <mask id="rm" maskUnits="userSpaceOnUse" x="0" y="{HDR}" width="{W}" height="{SH}"><image x="0" y="{HDR}" width="{W}" height="{SH}" preserveAspectRatio="none" xlink:href="data:image/png;base64,{rv64}" href="data:image/png;base64,{rv64}"/></mask>
  <marker id="ah" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ffe9c7"/></marker>
  <marker id="aw" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="4.5" markerHeight="4.5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#fff"/></marker>
</defs>
<rect width="{W}" height="{H}" fill="#fff"/>
{T(36, 44, "Warm front · vertical cross-section", "h1")}
{T(W-36, 44, f"Front moving left → right · vertical scale exaggerated ≈ {round(KY/KX):d}×", "sub", "end")}
<g clip-path="url(#sc)">
  <image x="0" y="{HDR}" width="{W}" height="{SH}" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{bg64}" href="data:image/jpeg;base64,{bg64}"/>
  <g class="ci"><image x="{cix:.1f}" y="{HDR+ciy:.1f}" width="{ciw:.1f}" height="{cih:.1f}" xlink:href="data:image/png;base64,{ci64}" href="data:image/png;base64,{ci64}"/></g>
  <g mask="url(#rm)"><g class="rain rainA">{drop_lines(0)}{drop_lines(-60)}</g></g>
  <line x1="0" y1="{trop_y:.1f}" x2="{W}" y2="{trop_y:.1f}" class="trop"/>
  {T(W-30, trop_y-8, "Tropopause ≈ 11 km", "sm", "end", 'opacity=".85"')}
  {"".join(f'<polyline points="{pts(s)}" class="flow flow{i+1}" marker-end="url(#ah)"/>' for i, s in enumerate(streams))}
  <line x1="{fx0:.1f}" y1="{fy0:.1f}" x2="{fx1:.1f}" y2="{fy1:.1f}" class="fs"/>
  {semis}
  {"".join(ticks)}
  {T(xk(-270), Y0+yh(8.6), "WARM AIR (mT)", "big")}
  {T(xk(-270), Y0+yh(8.6)+22, "warm, moist, stable — slides up over the cold wedge", "sm")}
  {T(xk(860), Y0+yh(2.1), "COLD AIR (mP)", "big", "middle")}
  {T(xk(860), Y0+yh(2.1)+22, "denser air: a shallow wedge the front climbs over", "sm", "middle")}
  {T(xk(930), Y0+yh(10.55), "Ci · Cirrus", "lbl", "middle")}
  {T(xk(930), Y0+yh(10.55)+18, "first sign · up to ≈ 1 000 km ahead", "sm", "middle")}
  {T(xk(735), Y0+yh(7.55), "Cs · Cirrostratus (halo)", "lbl", "middle")}
  {T(xk(470), Y0+yh(6.95), "As · Altostratus", "lbl", "middle")}
  {T(xk(470), Y0+yh(6.95)+18, "watery sun · virga beneath", "sm", "middle")}
  {T(xk(120), Y0+yh(4.1), "Ns · Nimbostratus", "lbl", "middle")}
  {T(xk(120), Y0+yh(4.1)+18, "thick, dark · base often below 1 000 ft", "sm", "middle")}
  {T(xk(-150), Y0+yh(2.05), "St / Sc · drizzle", "lbl", "start")}
  {T(xk(-150), Y0+yh(2.05)+18, "warm sector: low cloud, poor vis", "sm", "start")}
  {T(xk(232), Y0+yh(0.55), "St fractus · frontal fog", "sm", "middle")}
  {T(xk(160), Y0+yh(2.75), "Rain belt ≈ 300 km (≈ 200 nm)", "sm", "middle")}
  {T(xk(420), Y0+yh(2.15), "FZRA risk where rain falls into", "sm", "middle")}
  {T(xk(420), Y0+yh(2.15)+16, "sub-zero air in the wedge", "sm", "middle")}
  <g transform="translate({(fx0+fx1)/2+40:.1f},{(fy0+fy1)/2+22:.1f}) rotate({ang:.2f})">{T(0, 0, "Frontal surface · slope ≈ 1:150", "sm", "middle")}</g>
  <g class="mvp"><line x1="{xk(88):.1f}" y1="{Y0+G+27:.1f}" x2="{xk(132):.1f}" y2="{Y0+G+27:.1f}" class="mv" marker-end="url(#aw)"/></g>
  {T(xk(0), Y0+G+32, "Surface warm front", "lbl", "middle")}
</g>
<line x1="0" y1="{HDR+SH}" x2="{W}" y2="{HDR+SH}" stroke="#e5e7eb"/>
{"".join(xt)}
{T(W-36, HDR+SH+46, "distance from the surface front (warm sector ← | → ahead)", "src", "end")}
{T(36, HDR+SH+72, "Passage sequence (observer ahead of the front):", "capb")}
{T(36, HDR+SH+94, "Ci → Cs (halo) → As (watery sun) → Ns with steady rain, lowering base, poor visibility · pressure falls steadily, wind backs and freshens.", "cap")}
{T(36, HDR+SH+114, "At passage: wind veers, temperature and dew point rise, rain eases to drizzle, pressure fall stops · warm sector: St/Sc, drizzle, haze.", "cap")}
{T(36, HDR+SH+148, "Typical values: slope ≈ 1:150 · rain belt ≈ 300 km (≈ 200 nm) ahead · cirrus up to ≈ 1 000 km ahead · moves ≈ 10–15 kt. Cf. Met Office “Weather fronts”; Penn State METEO 3, warm fronts.", "src")}
</svg>'''

with open(os.path.join(OUT, "warmfront.svg"), "w") as f:
    f.write(svg)
print("svg", len(svg) // 1024, "KB")

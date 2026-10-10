"""Shared toolkit for the realistic weather scenes.

The heavy, textured parts of a scene (sky, terrain, clouds, rain shafts) are
rendered here with numpy: clouds are noise-based density fields lit by a
simple 2-D light march, so bases darken and tops catch the sun the way real
clouds do. The result is baked to an image that the animated SVG embeds;
labels, lines and motion stay as crisp vectors on top.
"""
import numpy as np
from scipy.ndimage import zoom, gaussian_filter

def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)

class Scene:
    def __init__(self, W, H, x_of_km, y_of_h, scale=2, seed=1):
        """W,H in SVG units; x_of_km / y_of_h map km / altitude-km to SVG units."""
        self.W, self.H, self.s = W, H, scale
        self.w, self.h = W * scale, H * scale
        self.rng = np.random.default_rng(seed)
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.X = xs / scale            # SVG units
        self.Y = ys / scale
        self.xk, self.yh = x_of_km, y_of_h
        # inverse maps (linear)
        a0, a1 = x_of_km(0), x_of_km(1)
        b0, b1 = y_of_h(0), y_of_h(1)
        self.KM = (self.X - a0) / (a1 - a0)          # km along section
        self.ALT = (self.Y - b0) / (b1 - b0)         # altitude km
        self.dens = np.zeros((self.h, self.w), np.float32)
        self.albedo = np.ones((self.h, self.w), np.float32)

    # ---------- noise ----------
    def noise(self, cx, cy, oct=5, pers=0.5, lac=2.0, seed=None):
        """fBm value noise in [0,1]; cx,cy = number of cells across W,H at the base octave."""
        rng = np.random.default_rng(seed) if seed is not None else self.rng
        out = np.zeros((self.h, self.w), np.float32)
        amp, tot = 1.0, 0.0
        for o in range(oct):
            gx, gy = max(2, int(cx * lac ** o)) + 3, max(2, int(cy * lac ** o)) + 3
            g = rng.random((gy, gx)).astype(np.float32)
            z = zoom(g, (self.h / (gy - 3), self.w / (gx - 3)), order=3, mode="reflect", grid_mode=False)
            out += amp * z[: self.h, : self.w]
            tot += amp
            amp *= pers
        out /= tot
        out = (out - out.mean()) / (out.std() + 1e-6)
        return np.clip(0.5 + out * 0.18, 0, 1)

    # ---------- clouds ----------
    def add_layer(self, x0, x1, base, top, kind="st", edge=0.25, fade=60,
                  dens=1.0, seed=0, albedo=1.0):
        """Add a cloud between x0..x1 km, base(km)->alt, top(km)->alt (vectorised callables)."""
        KM, ALT = self.KM, self.ALT
        b, t = base(KM), top(KM)
        th = np.maximum(t - b, 1e-3)
        rng = np.random.default_rng(seed)
        if kind == "ns":      # amorphous, heavy, ragged base
            n1 = self.noise(16, 8, 6, 0.6, seed=rng.integers(1e9))
            n2 = self.noise(10, 6, 5, 0.5, seed=rng.integers(1e9))
            tex = self.noise(14, 22, 6, 0.62, seed=rng.integers(1e9))
            u = (ALT - b) / th
            m = smooth((u + (n1 - .5) * 0.75) / edge) * smooth((1 - u + (n2 - .5) * 0.28) / edge)
            d = m * (0.72 + 0.7 * (tex - .5))
        elif kind == "as":    # grey layered sheet, fibrous-smooth
            n1 = self.noise(8, 10, 5, 0.5, seed=rng.integers(1e9))
            n2 = self.noise(9, 12, 5, 0.5, seed=rng.integers(1e9))
            tex = self.noise(6, 46, 6, 0.6, seed=rng.integers(1e9))
            u = (ALT - b) / th
            m = smooth((u + (n1 - .5) * 0.35) / edge) * smooth((1 - u + (n2 - .5) * 0.35) / edge)
            d = m * np.clip(0.5 + 1.0 * (tex - .5), 0, 1)
        elif kind == "cs":    # thin translucent veil with faint fibres
            n1 = self.noise(10, 3, 4, 0.5, seed=rng.integers(1e9))
            fib = self.noise(4, 70, 6, 0.6, seed=rng.integers(1e9))
            u = (ALT - b) / th
            m = smooth((u + (n1 - .5) * 0.6) / edge) * smooth((1 - u + (n1[::-1] - .5) * 0.6) / edge)
            d = m * np.clip(0.18 + 1.2 * (fib - .5), 0, 1)
        elif kind == "ci":    # fibrous streaks / mares' tails
            fib = self.noise(22, 120, 6, 0.6, seed=rng.integers(1e9))
            fine = self.noise(60, 300, 4, 0.6, seed=rng.integers(1e9))
            blob = self.noise(9, 30, 4, 0.5, seed=rng.integers(1e9))
            # shear: fibres trail down-left like mares' tails
            def shear(a, k=1.4):
                a2 = np.concatenate([a, a[:, ::-1]], axis=1)   # mirrored: no seam when sheared
                out = np.zeros_like(a)
                for y in range(a.shape[0]):
                    out[y] = np.roll(a2[y], -(int(y * k) % a2.shape[1]))[: a.shape[1]]
                return out
            sh = shear(fib * 0.65 + fine * 0.35)
            blob = shear(blob, 2.2)
            u = (ALT - b) / th
            m = smooth(u / edge) * smooth((1 - u) / edge)
            d = m * np.clip((sh - .46) * 6, 0, 1) ** 1.2 * np.clip((blob - .44) * 4, 0, 1)
        elif kind == "sc":    # broken cellular low cloud
            cell = self.noise(60, 10, 5, 0.5, seed=rng.integers(1e9))
            n1 = self.noise(30, 6, 4, 0.5, seed=rng.integers(1e9))
            u = (ALT - b) / th
            m = smooth((u + (n1 - .5) * 0.6) / edge) * smooth((1 - u + (cell - .5) * 1.2) / edge)
            d = m * np.clip((cell - 0.42) * 3.2, 0, 1)
        elif kind == "fractus":  # ragged low scud / fog patches
            n = self.noise(50, 14, 5, 0.6, seed=rng.integers(1e9))
            n1 = self.noise(20, 6, 4, 0.5, seed=rng.integers(1e9))
            u = (ALT - b) / th
            m = smooth((u + (n1 - .5)) / edge) * smooth((1 - u + (n1 - .5)) / edge)
            d = m * np.clip((n - 0.4) * 2.4, 0, 1)
        # horizontal taper
        xm = smooth((KM - x0) / fade) * smooth((x1 - KM) / fade)
        d = np.clip(d, 0, 1) * xm * dens
        self.dens = np.maximum(self.dens, d.astype(np.float32))
        self.albedo = np.where(d > 0.02, np.minimum(self.albedo, albedo), self.albedo)
        return d

    def add_density(self, d, albedo=1.0):
        d = np.clip(d, 0, 1).astype(np.float32)
        self.dens = np.maximum(self.dens, d)
        if not np.isscalar(albedo) or albedo != 1.0:
            self.albedo = np.where(d > 0.02, np.minimum(self.albedo, albedo), self.albedo).astype(np.float32)

    def light(self, sigma=0.022, slope=0.8):
        """Optical depth toward a sun at upper right (slope px-right per px-down)."""
        d = self.dens
        acc = np.zeros_like(d)
        av = np.zeros_like(d)
        k = slope
        xs = np.arange(self.w, dtype=np.float32)
        for y in range(1, self.h):
            prev = np.interp(xs + k, xs, acc[y - 1], right=0.0)
            acc[y] = prev + d[y]
            av[y] = av[y - 1] + d[y]
        self.T = np.exp(-sigma * acc).astype(np.float32)      # direct sun
        self.Ta = np.exp(-sigma * 0.35 * av).astype(np.float32)  # sky light from above
        return self.T

    def cloud_rgba(self, sun=(1.0, .985, .955), amb=(.56, .62, .72), dark=(.26, .28, .32), opac=4.0):
        T, Ta = self.T, self.Ta
        sun, amb, dark = map(lambda c: np.array(c, np.float32), (sun, amb, dark))
        lit = T[..., None] * sun * 0.7 + (0.35 + 0.65 * Ta[..., None]) * amb * 0.7
        rgb = dark + (lit - dark * 0.4) * 0.9
        rgb = np.clip(rgb * (0.75 + 0.25 * self.albedo[..., None]), 0, 1)
        a = 1 - np.exp(-opac * self.dens)
        return rgb, a

def to_img(rgb):
    from PIL import Image
    return Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8))

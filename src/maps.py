"""Parsomen tarzinda tarihi haritalar (kara/deniz maskesi: global_land_mask)."""
import math
import os

import numpy as np
import skia
from global_land_mask import globe
from scipy import ndimage

from gfx import (OUT, W, H, ROOT, circle, ease_in_out, ease_out, fill, font, label_tag, lin_grad, poly, pop,
                 rad_grad, rgb, rrect, shade, smooth, stroke, text, clamp, blur_paint)

CACHE = os.path.join(os.environ.get("ZK_WORK", "/home/user/work"), "mapcache")
os.makedirs(CACHE, exist_ok=True)
MS = 1.6  # harita goruntusu ekranin 1.6 kati cozunurlukte
COSL = math.cos(math.radians(38))

PLACES = {
    "Roma": (41.90, 12.50), "Atina": (37.98, 23.73), "Korint": (37.91, 22.88), "Antakya": (36.20, 36.16),
    "Efes": (37.94, 27.34), "Bergama": (39.12, 27.18), "Smyrna": (38.42, 27.14), "Afrodisias": (37.71, 28.72),
    "Halikarnassos": (37.04, 27.42), "Amastris": (41.75, 32.39), "Kartaca": (36.85, 10.32),
    "İskenderiye": (31.20, 29.92), "Pompeii": (40.75, 14.49), "Olympia": (37.64, 21.63), "Kibyra": (37.08, 29.49),
    "Ankyra": (39.93, 32.86),
}

RIVERS = {}


class MapView:
    def __init__(self, lon_c, lat_c, span_lat):
        self.lon_c, self.lat_c, self.span = lon_c, lat_c, span_lat
        self.h_deg = span_lat
        self.w_deg = span_lat * (W / H) / COSL

    def xy(self, lat, lon):
        x = (lon - self.lon_c) / self.w_deg * W + W / 2
        y = (self.lat_c - lat) / self.h_deg * H + H / 2
        return x, y


def _render_raster(view, key):
    path = os.path.join(CACHE, key + ".png")
    if os.path.exists(path):
        return skia.Image.open(path)
    pw, ph = int(W * MS), int(H * MS)
    lons = view.lon_c + (np.arange(pw) / pw - 0.5) * view.w_deg
    lats = view.lat_c - (np.arange(ph) / ph - 0.5) * view.h_deg
    LO, LA = np.meshgrid(lons, lats)
    land = globe.is_land(LA, LO).astype(np.float32)
    sm = ndimage.gaussian_filter(land, 2.0) > 0.5
    # cok kucuk adaciklari temizle
    lab, n = ndimage.label(sm)
    if n > 0:
        sizes = ndimage.sum(sm, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = sizes > 60
        sm = keep[lab]
    dist_in = ndimage.distance_transform_edt(sm)
    dist_out = ndimage.distance_transform_edt(~sm)
    rng = np.random.default_rng(3)
    noise = ndimage.gaussian_filter(rng.standard_normal((ph, pw)).astype(np.float32), 3) * 6
    img = np.zeros((ph, pw, 3), np.float32)
    sea = np.array([126, 166, 170], np.float32)
    sea_deep = np.array([96, 136, 146], np.float32)
    landc = np.array([234, 214, 168], np.float32)
    landd = np.array([196, 160, 104], np.float32)
    fsea = np.clip(dist_out / 260, 0, 1)[..., None]
    img[:] = sea * (1 - fsea) + sea_deep * fsea
    # kiyi cizgileri (dalga konturleri)
    rings = ((dist_out % 22) < 2.2) & (dist_out < 90) & (dist_out > 6)
    img[rings] = img[rings] * 0.86
    fl = np.clip(dist_in / 40, 0, 1)[..., None]
    lc = landd * (1 - fl) + landc * fl
    img = np.where(sm[..., None], lc, img)
    img += noise[..., None]
    coast = (dist_out > 0) & (dist_out < 3.2)
    img[coast] = np.array([92, 62, 36])
    # parsomen lekeleri
    big = ndimage.gaussian_filter(rng.standard_normal((ph // 8, pw // 8)).astype(np.float32), 6)
    big = np.kron(big, np.ones((8, 8), np.float32))[:ph, :pw]
    img *= (1 + big[..., None] * 0.6)
    yy, xx = np.mgrid[0:ph, 0:pw]
    vig = 1 - 0.35 * (((xx / pw - 0.5) * 1.6) ** 2 + ((yy / ph - 0.5) * 1.6) ** 2)
    img *= vig[..., None]
    img = np.clip(img, 0, 255).astype(np.uint8)
    rgba = np.concatenate([img, np.full((ph, pw, 1), 255, np.uint8)], axis=2)
    im = skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.kRGBA_8888_ColorType)
    im.save(path, skia.kPNG)
    return skia.Image.open(path)


_imgs = {}


def map_image(view, key):
    if key not in _imgs:
        _imgs[key] = _render_raster(view, key)
    return _imgs[key]


def draw_map_base(cv, view, key, rivers=True, rivers_a=255):
    img = map_image(view, key)
    cv.drawImageRect(img, skia.Rect.MakeWH(W, H), skia.SamplingOptions(skia.FilterMode.kLinear,
                                                                       skia.MipmapMode.kNone))
    if rivers:
        for name, pts in RIVERS.items():
            xy = [view.xy(a, b) for a, b in pts]
            p = smooth(xy, closed=False)
            cv.drawPath(p, stroke("#4f7f96", 5.5, rivers_a))
            cv.drawPath(p, stroke("#86b4c4", 2.5, rivers_a))


def place(cv, view, name, t=1.0, t0=0.0, size=34, dot="#b01818", dx=0, dy=-26, star=False, label=None):
    s = pop(t - t0, 0.35)
    if s <= 0:
        return
    lat, lon = PLACES[name]
    x, y = view.xy(lat, lon)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    if star:
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            r = 22 if k % 2 == 0 else 9
            pts.append((math.cos(a) * r, math.sin(a) * r))
        cv.drawPath(poly(pts), fill("#f6c64a"))
        cv.drawPath(poly(pts), stroke(OUT, 3))
    else:
        cv.drawPath(circle(0, 0, 10), fill(dot))
        cv.drawPath(circle(0, 0, 10), stroke(OUT, 3))
    f = font("black", size)
    text(cv, label or name, dx, dy, f, "#2a1a10", oc="#f6ead0", ow=5)
    cv.restore()


def region_label(cv, view, s, lat, lon, size=44, col="#6a3a1a", a=255, rot=0, spacing=True):
    x, y = view.xy(lat, lon)
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    f = font("deco", size)
    text(cv, s, 0, 0, f, col, a=a, oc="#f3e3bf", ow=3)
    cv.restore()


def route(cv, view, pts, t, t0, dur, col="#b01818", w=10, dashed=True, head=True, a=255):
    """pts: [(lat,lon)] animasyonlu ok"""
    f = clamp((t - t0) / dur)
    if f <= 0:
        return
    xy = [view.xy(a_, b_) for a_, b_ in pts]
    path = smooth(xy, closed=False) if len(xy) > 2 else poly(xy, closed=False)
    meas = skia.PathMeasure(path, False)
    L = meas.getLength()
    seg = skia.Path()
    meas.getSegment(0, L * ease_in_out(f), seg, True)
    p_out = stroke(OUT, w + 6, a)
    p_in = stroke(col, w, a)
    if dashed:
        p_in.setPathEffect(skia.DashPathEffect.Make([w * 2.4, w * 1.4], 0))
    cv.drawPath(seg, p_out)
    cv.drawPath(seg, p_in)
    if head and f > 0.02:
        pos, tan = meas.getPosTan(L * ease_in_out(f))
        ang = math.atan2(tan.y(), tan.x())
        hx, hy = pos.x(), pos.y()
        tri = poly([(hx + math.cos(ang) * 30, hy + math.sin(ang) * 30),
                    (hx + math.cos(ang + 2.4) * 24, hy + math.sin(ang + 2.4) * 24),
                    (hx + math.cos(ang - 2.4) * 24, hy + math.sin(ang - 2.4) * 24)])
        cv.drawPath(tri, fill(col, a))
        cv.drawPath(tri, stroke(OUT, 3.5, a))


def battle_icon(cv, x, y, t, t0, s=1.0, label=None, year=None):
    sc = pop(t - t0, 0.4)
    if sc <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(sc * s, sc * s)
    cv.drawPath(circle(0, 0, 40), fill("#fbf3df"))
    cv.drawPath(circle(0, 0, 40), stroke(OUT, 4))
    for sg in (-1, 1):
        cv.save()
        cv.rotate(sg * 45)
        cv.drawPath(rrect(-5, -30, 10, 46, 3), fill("#c9d0d6"))
        cv.drawPath(rrect(-5, -30, 10, 46, 3), stroke(OUT, 2.5))
        cv.drawPath(rrect(-14, 12, 28, 7, 3), fill("#c9a040"))
        cv.drawPath(rrect(-4, 18, 8, 12, 3), fill("#6a4424"))
        cv.restore()
    if label:
        text(cv, label, 0, 78, font("black", 36), "#2a1a10", oc="#f6ead0", ow=5)
    if year:
        text(cv, year, 0, 116, font("slab", 32), "#a01818", oc="#f6ead0", ow=5)
    cv.restore()


def mountains(cv, view, lat, lon, n=5, s=1.0, seed=0):
    import random
    r = random.Random(seed)
    x0, y0 = view.xy(lat, lon)
    for k in range(n):
        x = x0 + r.uniform(-90, 90) * s
        y = y0 + r.uniform(-30, 30) * s
        hh = r.uniform(30, 50) * s
        p = poly([(x - hh * 0.9, y), (x, y - hh), (x + hh * 0.9, y)])
        cv.drawPath(p, fill("#b89a6a"))
        cv.drawPath(poly([(x, y - hh), (x + hh * 0.9, y), (x + hh * 0.2, y)]), fill("#9a7a4a"))
        cv.drawPath(p, stroke("#5a3a1a", 2.5))

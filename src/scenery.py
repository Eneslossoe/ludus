"""Arka planlar ve dekor ogeleri."""
import math
import random

import numpy as np
import skia

from gfx import (OUT, P, W, H, blur_paint, capsule, circle, ellipse, fill, lin_grad, mix, noise1, poly,
                 rad_grad, rgb, rrect, shade, shape, smooth, stroke, tint)


# ------------------------------------------------------------------ gokyuzu
def sky(cv, w, h, cols, pos=None, horizon=None):
    horizon = horizon or h
    cv.drawRect(skia.Rect.MakeWH(w, h), lin_grad((0, 0), (0, horizon), cols, pos))


def sun(cv, x, y, r, col="#fff6d0", glow="#ffd27a", ga=150):
    cv.drawPath(circle(x, y, r * 3.2), rad_grad((x, y), r * 3.2, [rgb(glow, ga), rgb(glow, 0)]))
    cv.drawPath(circle(x, y, r), fill(col))


def moon(cv, x, y, r):
    cv.drawPath(circle(x, y, r * 3), rad_grad((x, y), r * 3, [rgb("#cfe0ff", 90), rgb("#cfe0ff", 0)]))
    cv.drawPath(circle(x, y, r), fill("#f4f1e4"))
    cv.drawPath(circle(x + r * 0.35, y - r * 0.2, r * 0.85), fill("#0d1530", 255))


def stars(cv, w, h, n, seed=3, maxy=None):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(0, maxy or h * 0.6)
        s = r.uniform(0.8, 2.6)
        cv.drawPath(circle(x, y, s), fill("#ffffff", r.randint(120, 255)))


def clouds(cv, w, h, n, seed=5, col="#ffffff", a=200, ymax=0.35):
    r = random.Random(seed)
    for _ in range(n):
        x, y = r.uniform(0, w), r.uniform(h * 0.05, h * ymax)
        s = r.uniform(0.6, 1.4)
        for k in range(5):
            cv.drawPath(ellipse(x + (k - 2) * 40 * s, y - (abs(k - 2) < 1) * 18 * s, 50 * s, 26 * s),
                        fill(col, a))


# ------------------------------------------------------------------ arazi
def ridge(cv, w, h, base_y, amp, freq, col, seed=0, top_col=None, to_y=None, outline=False, rough=0.0):
    pts = [(0, h)]
    n = 60
    for i in range(n + 1):
        x = i / n * w
        y = base_y - amp * (noise1(x * freq / 100.0, seed) * 0.8 + noise1(x * freq / 30.0, seed + 7) * 0.2 * rough
                            + math.sin(x * freq / 300 + seed) * 0.2)
        pts.append((x, y))
    pts.append((w, h))
    p = poly(pts)
    if top_col:
        cv.drawPath(p, lin_grad((0, base_y - amp), (0, to_y or h), [top_col, col]))
    else:
        cv.drawPath(p, fill(col))
    if outline:
        cv.drawPath(p, stroke(shade(col, 0.7), 3))
    return pts


def dunes(cv, w, h, horizon, palette, seed=1):
    """palette: uzak->yakin renk listesi"""
    n = len(palette)
    for i, c in enumerate(palette):
        y = horizon + (h - horizon) * (i / n) * 0.75
        amp = 40 + i * 25
        ridge(cv, w, h, y + amp * 0.5, amp, 1.2 + i * 0.4, c, seed=seed + i * 11, top_col=shade(c, 1.12),
              to_y=y + 200)


def sand_ripples(cv, w, h, y0, col, seed=9, n=40):
    r = random.Random(seed)
    for _ in range(n):
        x = r.uniform(0, w)
        y = r.uniform(y0, h)
        l = r.uniform(30, 90) * (0.6 + (y - y0) / (h - y0 + 1))
        p = P()
        p.moveTo(x - l, y)
        p.quadTo(x, y - 8, x + l, y)
        cv.drawPath(p, stroke(col, 2.5, 120))


def rock(cv, x, y, s, col="#9a7a5a"):
    pts = [(-60, 0), (-50, -40), (-20, -62), (20, -58), (52, -30), (64, 0)]
    p = smooth([(x + a * s, y + b * s) for a, b in pts] + [(x, y + 4)], tension=0.3)
    shape(cv, p, col, w=3)
    cv.drawPath(smooth([(x + a * s, y + b * s) for a, b in [(0, -55), (40, -32), (50, -4), (10, -10)]]),
                fill(shade(col, 0.8), 160))


def palm(cv, x, y, s=1.0, lean=8, seed=0):
    r = random.Random(seed)
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    # govde
    segs = 9
    tx, ty = 0, 0
    pts = []
    for i in range(segs + 1):
        f = i / segs
        pts.append((math.sin(f * 1.2) * lean * 6, -f * 300))
    for i in range(segs):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        wdt = 22 - i * 1.0
        shape(cv, poly([(x0 - wdt, y0), (x1 - wdt + 2, y1 + 2), (x1 + wdt - 2, y1 + 2), (x0 + wdt, y0)]), "#8a6a44",
              w=3)
    topx, topy = pts[-1]
    # yapraklar
    for k in range(8):
        a = math.radians(-170 + k * 24 + r.uniform(-8, 8))
        L = r.uniform(120, 160)
        ex, ey = topx + math.cos(a) * L, topy + math.sin(a) * L * 0.6 + 50
        mx, my = topx + math.cos(a) * L * 0.5, topy - 30 + math.sin(a) * L * 0.2
        p = P()
        p.moveTo(topx, topy)
        p.quadTo(mx, my - 20, ex, ey)
        p.quadTo(mx, my + 14, topx, topy)
        shape(cv, p, "#3f7a32" if k % 2 else "#4f8f3a", w=3)
    for k in range(4):
        cv.drawPath(circle(topx - 14 + k * 9, topy + 14 + (k % 2) * 6, 8), fill("#9a4a1a"))
    cv.restore()


def olive(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    shape(cv, poly([(-10, 0), (-14, -70), (-30, -110), (-4, -90), (10, -120), (12, -70), (14, 0)]), "#6a5038", w=3)
    for (cx, cy, r) in ((-40, -130, 46), (20, -150, 52), (50, -115, 40), (-10, -170, 40)):
        shape(cv, circle(cx, cy, r), "#6f8a4a", w=3)
    cv.restore()


def bush(cv, x, y, s=1.0, col="#7a8a4a"):
    for k, (dx, r) in enumerate(((-20, 22), (0, 30), (22, 22))):
        shape(cv, circle(x + dx * s, y - r * s * 0.8, r * s), shade(col, 1 - 0.08 * k), w=3)


# ------------------------------------------------------------------ cadirlar
def bedouin_tent(cv, x, y, s=1.0, col="#2e2622"):
    """kil cadir: alcak, genis, birkac tepe"""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    for sx in (-1, 1):
        cv.drawLine(sx * 160, -110, sx * 240, 0, stroke("#c9b48a", 2.5))
    roof = smooth([(-190, -40), (-170, -120), (-90, -100), (0, -150), (90, -100), (170, -120), (190, -40)],
                  closed=False)
    body = P()
    body.moveTo(-200, 0)
    body.lineTo(-190, -40)
    body.addPath(roof)
    body.lineTo(200, 0)
    body.close()
    shape(cv, body, col, w=3.5)
    cv.save()
    cv.clipPath(body, skia.ClipOp.kIntersect, True)
    for k in range(-190, 200, 26):
        cv.drawLine(k, -160, k + 10, 0, stroke(shade(col, 1.4), 3, 120))
    cv.drawRect(skia.Rect.MakeLTRB(-60, -80, 60, 0), fill("#120e0c"))
    cv.restore()
    shape(cv, body, None, w=3.5)
    for px in (-170, 0, 170):
        cv.drawLine(px, -140 if px == 0 else -116, px, 0, stroke("#7a5a3a", 5))
    shape(cv, rrect(-40, -40, 80, 40, 4), "#a8282b", w=2.5)
    cv.restore()


def army_tent(cv, x, y, s=1.0, col="#f2ece0", stripe="#b02a2a"):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = poly([(-90, 0), (-70, -90), (0, -170), (70, -90), (90, 0)])
    shape(cv, body, col, w=3.5)
    cv.save()
    cv.clipPath(body, skia.ClipOp.kIntersect, True)
    for k in range(-90, 100, 36):
        cv.drawPath(poly([(k, 0), (0, -170), (k + 14, 0)]), fill(stripe))
    cv.drawPath(poly([(-24, 0), (0, -70), (24, 0)]), fill("#2a1a12"))
    cv.restore()
    shape(cv, body, None, w=3.5)
    cv.drawLine(0, -170, 0, -200, stroke("#6a4a2a", 4))
    cv.drawPath(poly([(0, -200), (30, -192), (0, -184)]), fill(stripe))
    cv.restore()


def campfire(cv, x, y, t, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.drawPath(ellipse(0, 0, 260, 90), rad_grad((0, 0), 260, [rgb("#ff9a3a", 90), rgb("#ff9a3a", 0)]))
    for a in (-20, 20, 0):
        cv.save()
        cv.rotate(a)
        shape(cv, rrect(-50, -8, 100, 16, 7), "#5a3a22", w=3)
        cv.restore()
    for k in range(5):
        ph = t * 7 + k * 1.7
        hgt = 70 + 25 * math.sin(ph) + 10 * math.sin(ph * 2.3)
        xo = (k - 2) * 14
        f = smooth([(xo - 22, -4), (xo - 14, -hgt * 0.5), (xo + 4 * math.sin(ph), -hgt), (xo + 14, -hgt * 0.45),
                    (xo + 22, -4)], tension=0.5)
        cv.drawPath(f, fill("#ff7a1a" if k % 2 else "#ffb020", 230))
    for k in range(3):
        ph = t * 9 + k * 2.1
        hgt = 40 + 12 * math.sin(ph)
        xo = (k - 1) * 12
        f = smooth([(xo - 12, -4), (xo - 6, -hgt * 0.5), (xo + 3 * math.sin(ph), -hgt), (xo + 8, -hgt * 0.4),
                    (xo + 12, -4)])
        cv.drawPath(f, fill("#fff2a0", 240))
    # kivilcimlar
    for k in range(8):
        ph = (t * 0.7 + k * 0.137) % 1.0
        ex = math.sin(k * 3.3 + t) * 30 * ph + (k - 4) * 4
        ey = -60 - ph * 180
        cv.drawPath(circle(ex, ey, 3 * (1 - ph)), fill("#ffd080", int(255 * (1 - ph))))
    cv.restore()


# ------------------------------------------------------------------ yapilar
def mud_house(cv, x, y, w_, h_, col="#c9a274", seed=0, door=True):
    r = random.Random(seed)
    shape(cv, rrect(x, y - h_, w_, h_, 6), col, w=3.5)
    cv.drawRect(skia.Rect.MakeLTRB(x + w_ * 0.7, y - h_ + 3, x + w_ - 3, y - 3), fill(shade(col, 0.85), 160))
    cv.drawLine(x - 6, y - h_ + 2, x + w_ + 6, y - h_ + 2, stroke(shade(col, 0.7), 8))
    for k in range(int(w_ // 40)):
        cv.drawLine(x + 20 + k * 40, y - h_ + 10, x + 20 + k * 40, y - h_ - 6, stroke("#7a5a3a", 5))
    if door:
        shape(cv, rrect(x + w_ * 0.35, y - h_ * 0.55, w_ * 0.22, h_ * 0.55, 10), "#5a3a22", w=3)
    for k in range(r.randint(1, 2)):
        wx = x + w_ * (0.12 + 0.55 * k) + r.uniform(0, 10)
        shape(cv, rrect(wx, y - h_ * 0.8, 22, 22, 4), "#2a1a12", w=2.5)


def stone_wall(cv, x0, x1, y, h_, col="#c8b89a", crenel=True, seed=0):
    shape(cv, poly([(x0, y), (x0, y - h_), (x1, y - h_), (x1, y)]), col, w=4)
    cv.save()
    cv.clipPath(poly([(x0, y), (x0, y - h_), (x1, y - h_), (x1, y)]), skia.ClipOp.kIntersect, True)
    row = 0
    for yy in np.arange(y - h_, y, 34):
        off = 30 if row % 2 else 0
        cv.drawLine(x0, yy, x1, yy, stroke(shade(col, 0.75), 2.4))
        for xx in np.arange(x0 + off, x1, 60):
            cv.drawLine(xx, yy, xx, yy + 34, stroke(shade(col, 0.75), 2.4))
        row += 1
    cv.drawRect(skia.Rect.MakeLTRB(x0, y - h_, x1, y - h_ + 14), fill(shade(col, 1.1), 120))
    cv.restore()
    if crenel:
        for xx in np.arange(x0 + 6, x1 - 20, 44):
            shape(cv, rrect(xx, y - h_ - 26, 26, 30, 2), col, w=3.5)


def tower(cv, x, y, w_, h_, col="#c8b89a", roof=None):
    stone_wall(cv, x - w_ / 2, x + w_ / 2, y, h_, col)
    shape(cv, rrect(x - 10, y - h_ * 0.7, 20, 40, 10), "#2a1a12", w=2.5)
    if roof:
        shape(cv, poly([(x - w_ / 2 - 10, y - h_ - 26), (x, y - h_ - 26 - w_ * 0.8), (x + w_ / 2 + 10, y - h_ - 26)]),
              roof, w=3.5)


def gate(cv, x, y, w_, h_, open_=0.0, col="#6a4424"):
    arch = P()
    arch.moveTo(x - w_ / 2, y)
    arch.lineTo(x - w_ / 2, y - h_ + w_ / 2)
    arch.arcTo(skia.Rect.MakeLTRB(x - w_ / 2, y - h_, x + w_ / 2, y - h_ + w_), 180, 180, False)
    arch.lineTo(x + w_ / 2, y)
    arch.close()
    shape(cv, arch, "#1a120c", w=4)
    if open_ < 1:
        cv.save()
        cv.clipPath(arch, skia.ClipOp.kIntersect, True)
        dw = w_ / 2 * (1 - open_)
        for sx in (-1, 1):
            x0 = x + sx * w_ / 2
            x1 = x0 - sx * dw
            cv.drawRect(skia.Rect.MakeLTRB(min(x0, x1), y - h_, max(x0, x1), y), fill(col))
            for k in range(1, 4):
                xx = x0 - sx * dw * k / 4
                cv.drawLine(xx, y - h_, xx, y, stroke(shade(col, 0.7), 3))
        cv.restore()
        shape(cv, arch, None, w=4)


def dome_building(cv, x, y, w_, h_, col="#e8dcc4", dome="#b8a57a", cross=True, seed=0):
    shape(cv, rrect(x - w_ / 2, y - h_, w_, h_, 4), col, w=3.5)
    for k in range(3):
        wx = x - w_ / 2 + w_ * (0.2 + 0.3 * k)
        a = P()
        a.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(wx - 10, y - h_ * 0.75, 20, 40), 10, 10))
        shape(cv, a, "#2a1a12", w=2.4)
    d = P()
    d.moveTo(x - w_ * 0.36, y - h_)
    d.cubicTo(x - w_ * 0.36, y - h_ - w_ * 0.5, x + w_ * 0.36, y - h_ - w_ * 0.5, x + w_ * 0.36, y - h_)
    d.close()
    shape(cv, d, dome, w=3.5)
    if cross:
        ty = y - h_ - w_ * 0.38
        cv.drawLine(x, ty, x, ty - 40, stroke("#d9a83a", 5))
        cv.drawLine(x - 12, ty - 28, x + 12, ty - 28, stroke("#d9a83a", 5))


def column(cv, x, y, h_, col="#e8e0cc"):
    shape(cv, rrect(x - 12, y - h_, 24, h_, 3), col, w=3)
    shape(cv, rrect(x - 20, y - h_ - 12, 40, 14, 3), col, w=3)
    shape(cv, rrect(x - 18, y - 12, 36, 12, 3), col, w=3)


def city_skyline(cv, x0, x1, y, seed=0, roman=True, scale=1.0, col="#cdbb98"):
    r = random.Random(seed)
    x = x0
    while x < x1:
        w_ = r.uniform(70, 150) * scale
        h_ = r.uniform(60, 160) * scale
        kind = r.random()
        if roman and kind < 0.18:
            dome_building(cv, x + w_ / 2, y, w_, h_ * 0.8, col=shade(col, 1.05), dome="#a89a7a", cross=True)
        elif roman and kind < 0.4:
            shape(cv, rrect(x, y - h_, w_, h_, 3), shade(col, r.uniform(0.9, 1.08)), w=3)
            shape(cv, poly([(x - 6, y - h_), (x + w_ / 2, y - h_ - 34 * scale), (x + w_ + 6, y - h_)]),
                  "#a8503a", w=3)
        else:
            mud_house(cv, x, y, w_, h_, col=shade(col, r.uniform(0.88, 1.08)), seed=r.randint(0, 999),
                      door=False)
        x += w_ * r.uniform(0.75, 1.0)


def ravine(cv, x0, x1, y_top, depth, col="#9a7048"):
    """derin vadi (yarik) - uclarinda ucurum"""
    gap = poly([(x0, y_top), (x0 + 60, y_top + depth * 0.5), (x0 + 30, y_top + depth), (x1 - 30, y_top + depth),
                (x1 - 60, y_top + depth * 0.5), (x1, y_top)])
    cv.drawPath(gap, lin_grad((0, y_top), (0, y_top + depth), ["#4a3020", "#1c120c"]))
    cv.drawPath(gap, stroke(OUT, 4))


def grave(cv, x, y, s=1.0, col="#8a7a60"):
    shape(cv, ellipse(x, y, 60 * s, 18 * s), "#7a6448", w=3)
    shape(cv, rrect(x - 10 * s, y - 50 * s, 20 * s, 44 * s, 6 * s), col, w=3)


def banner_pole(cv, x, y, t, h_=300, col="#1d1b1a", size=1.0, cross=False, sym=None):
    cv.drawLine(x, y, x, y - h_, stroke(OUT, 9))
    cv.drawLine(x, y, x, y - h_, stroke("#8a5a2e", 5))
    pts = []
    n = 8
    fw, fh = 140 * size, 90 * size
    for i in range(n + 1):
        f = i / n
        wy = math.sin(t * 5 - f * 4) * 10 * f * size
        pts.append((x + f * fw, y - h_ + 4 + wy))
    for i in range(n, -1, -1):
        f = i / n
        wy = math.sin(t * 5 - f * 4) * 10 * f * size
        pts.append((x + f * fw, y - h_ + 4 + fh + wy))
    p = poly(pts)
    shape(cv, p, col, w=3.5)
    if cross:
        cx, cy = x + fw * 0.45, y - h_ + 4 + fh / 2 + math.sin(t * 5 - 1.8) * 4
        cv.drawLine(cx - 18, cy, cx + 18, cy, stroke("#f0c040", 7))
        cv.drawLine(cx, cy - 24, cx, cy + 24, stroke("#f0c040", 7))


def scroll_shape(cv, x, y, w_, h_, open_=1.0, col="#f2e2b8"):
    hh = h_ * open_
    shape(cv, rrect(x - w_ / 2, y - hh / 2, w_, hh, 6), col, w=4)
    for sy in (-1, 1):
        shape(cv, rrect(x - w_ / 2 - 20, y + sy * hh / 2 - 16, w_ + 40, 32, 16), shade(col, 0.85), w=4)


def coin(cv, x, y, r=22, col="#f0c040", label=None):
    shape(cv, circle(x + 2, y + 3, r), (0, 0, 0), None, a=60) if False else None
    cv.drawPath(circle(x, y, r), rad_grad((x - r * 0.3, y - r * 0.3), r * 1.4, ["#fff3b0", col, shade(col, 0.7)]))
    cv.drawPath(circle(x, y, r), stroke(OUT, 3))
    cv.drawPath(circle(x, y, r * 0.72), stroke(shade(col, 0.65), 2))


def chest(cv, x, y, s=1.0, open_=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    shape(cv, rrect(-80, -90, 160, 90, 8), "#7a4a22", w=4)
    for xx in (-60, 60):
        cv.drawRect(skia.Rect.MakeLTRB(xx - 8, -90, xx + 8, 0), fill("#c9a040"))
    lid = rrect(-84, -130, 168, 44, 16)
    cv.save()
    if open_ > 0:
        cv.translate(0, -90)
        cv.rotate(-open_ * 60)
        cv.translate(0, 90)
    shape(cv, lid, "#8a5a2a", w=4)
    cv.restore()
    shape(cv, rrect(-12, -100, 24, 26, 4), "#c9a040", w=3)
    cv.restore()


def waterskin(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    p = smooth([(-20, -90), (-60, -40), (-62, 20), (-30, 50), (30, 50), (62, 20), (58, -40), (20, -90)], tension=0.5)
    shape(cv, p, "#8a5a30")
    cv.drawPath(ellipse(-20, -10, 18, 30), fill("#b08050", 150))
    shape(cv, rrect(-14, -110, 28, 26, 6), "#5a3a22", w=3)
    cv.restore()


def date_pile(cv, x, y, s=1.0):
    for k, (dx, dy) in enumerate(((-30, 0), (0, 0), (30, 0), (-15, -24), (15, -24), (0, -46))):
        cv.save()
        cv.translate(x + dx * s, y + dy * s)
        cv.rotate(k * 23)
        shape(cv, ellipse(0, 0, 14 * s, 22 * s), "#6a2e12" if k % 2 else "#7a3a18", w=3)
        cv.drawPath(ellipse(-4 * s, -6 * s, 4 * s, 8 * s), fill("#c07040", 140))
        cv.restore()


def flour_sack(cv, x, y, s=1.0):
    p = smooth([(x - 50 * s, y), (x - 56 * s, y - 70 * s), (x - 30 * s, y - 110 * s), (x + 30 * s, y - 110 * s),
                (x + 56 * s, y - 70 * s), (x + 50 * s, y)])
    shape(cv, p, "#e8dcc0")
    cv.drawLine(x - 30 * s, y - 96 * s, x + 30 * s, y - 96 * s, stroke("#8a6a40", 5))


def meat(cv, x, y, s=1.0):
    for k in range(3):
        p = smooth([(x - 40 * s + k * 30 * s, y), (x - 50 * s + k * 30 * s, y - 70 * s),
                    (x - 34 * s + k * 30 * s, y - 80 * s), (x - 24 * s + k * 30 * s, y - 6 * s)])
        shape(cv, p, "#8a2a1a" if k % 2 else "#a0402a", w=3)
    cv.drawLine(x - 60 * s, y - 80 * s, x + 50 * s, y - 80 * s, stroke("#6a4a2a", 5))


def mail_shirt(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    p = poly([(-50, -120), (-90, -100), (-80, -60), (-55, -70), (-55, 0), (55, 0), (55, -70), (80, -60), (90, -100),
              (50, -120), (20, -110), (-20, -110)])
    cv.drawPath(p, fill("#8d949c"))
    cv.save()
    cv.clipPath(p, skia.ClipOp.kIntersect, True)
    for yy in range(-124, 4, 9):
        for xx in range(-96, 96, 10):
            cv.drawPath(circle(xx + ((yy // 9) % 2) * 5, yy, 4.2), stroke("#5f666e", 1.7))
    cv.restore()
    cv.drawPath(p, stroke(OUT, 4))
    cv.restore()


def bow_item(cv, x, y, s=1.0):
    p = P()
    p.moveTo(x - 10 * s, y - 100 * s)
    p.quadTo(x + 60 * s, y, x - 10 * s, y + 100 * s)
    cv.drawPath(p, stroke(OUT, 12 * s))
    cv.drawPath(p, stroke("#7a4a22", 7 * s))
    cv.drawLine(x - 10 * s, y - 100 * s, x - 10 * s, y + 100 * s, stroke("#efe6d0", 2.5))


def skull(cv, x, y, s=1.0, a=255):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    shape(cv, smooth([(-30, 0), (-34, -40), (0, -62), (34, -40), (30, 0), (18, 10), (-18, 10)]), "#efe8d8", a=a)
    for sx in (-1, 1):
        cv.drawPath(ellipse(sx * 13, -24, 9, 11), fill("#2a1a12", a))
    cv.drawPath(poly([(0, -10), (-5, 0), (5, 0)]), fill("#2a1a12", a))
    cv.restore()


def book(cv, x, y, w_, h_, open_=1.0):
    shape(cv, rrect(x - w_ / 2 - 10, y - h_ / 2 - 8, w_ + 20, h_ + 16, 8), "#6a2a1a", w=4)
    for sx in (-1, 1):
        pg = rrect(x if sx > 0 else x - w_ / 2, y - h_ / 2, w_ / 2, h_, 4)
        shape(cv, pg, "#f4e8c8", w=3)
    cv.drawLine(x, y - h_ / 2, x, y + h_ / 2, stroke(shade("#f4e8c8", 0.7), 3))


def ship(cv, x, y, s=1.0, t=0.0):
    cv.save()
    cv.translate(x, y + math.sin(t * 1.5) * 4 * s)
    cv.scale(s, s)
    cv.rotate(math.sin(t * 1.2) * 2)
    hull = smooth([(-160, -40), (160, -40), (130, 10), (-130, 10)], tension=0.2)
    shape(cv, hull, "#6a4424")
    cv.drawLine(0, -40, 0, -230, stroke(OUT, 9))
    cv.drawLine(0, -40, 0, -230, stroke("#8a5a2e", 5))
    sail = poly([(-90, -210), (90, -210), (110, -70), (-110, -70)])
    shape(cv, sail, "#efe2c4")
    cv.drawLine(-100, -140, 100, -140, stroke("#c0262b", 14))
    for k in range(-120, 140, 40):
        cv.drawLine(k, -30, k - 20, 20, stroke("#4a2a14", 4))
    cv.restore()


def sea(cv, w, y, h, t, col="#2f6f9a"):
    cv.drawRect(skia.Rect.MakeLTRB(0, y, w, h), lin_grad((0, y), (0, h), [shade(col, 1.2), shade(col, 0.7)]))
    for k in range(18):
        yy = y + 20 + k * (h - y) / 18
        p = P()
        off = (t * 30 * (1 + k * 0.1)) % 120
        p.moveTo(-120 + off, yy)
        for xx in range(-120, int(w) + 120, 60):
            p.quadTo(xx + off + 15, yy - 6, xx + off + 30, yy)
            p.quadTo(xx + off + 45, yy + 6, xx + off + 60, yy)
        cv.drawPath(p, stroke(shade(col, 1.35), 2.5, 120))

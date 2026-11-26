"""Parcacik ve atmosfer efektleri (toz, kum firtinasi, ok yagmuru, kan, kivilcim...)."""
import math
import random

import skia

from gfx import (OUT, P, W, H, blur_paint, circle, ellipse, fill, lin_grad, poly, rad_grad, rgb, shade, smooth,
                 stroke)


def dust_cloud(cv, x, y, t, s=1.0, col="#d8c098", a=170, seed=0, n=9):
    r = random.Random(seed)
    for k in range(n):
        ph = (t * 0.25 + r.random()) % 1.0
        dx = r.uniform(-1, 1) * 140 * s + ph * 60 * s * (1 if k % 2 else -1)
        dy = -ph * 80 * s - r.uniform(0, 40) * s
        rr = (40 + 70 * ph) * s * r.uniform(0.7, 1.3)
        al = a * math.sin(ph * math.pi)
        cv.drawPath(circle(x + dx, y + dy, rr), blur_paint(col, rr * 0.35, al))


def ground_dust(cv, x0, x1, y, t, col="#d8c098", a=120, seed=1, density=12):
    r = random.Random(seed)
    for k in range(density):
        bx = r.uniform(x0, x1)
        ph = (t * r.uniform(0.15, 0.35) + r.random()) % 1.0
        rr = r.uniform(50, 120) * (0.6 + ph)
        cv.drawPath(circle(bx + ph * 80, y - ph * 50, rr), blur_paint(col, rr * 0.4, a * math.sin(ph * math.pi)))


def sandstorm(cv, t, strength=1.0, col="#d9b27a", seed=7, w=W, h=H, direction=1):
    cv.drawRect(skia.Rect.MakeWH(w, h), fill(col, int(110 * strength)))
    r = random.Random(seed)
    for k in range(int(70 * strength)):
        sp = r.uniform(600, 1400)
        y = r.uniform(0, h)
        x = (r.uniform(0, w + 400) + t * sp * direction) % (w + 400) - 200
        l = r.uniform(40, 160)
        cv.drawLine(x, y, x - l * direction, y + r.uniform(-6, 6), stroke(shade(col, 1.2), r.uniform(1.5, 3.5),
                                                                          int(160 * strength)))
    for k in range(int(10 * strength)):
        x = (r.uniform(0, w + 800) + t * 500 * direction) % (w + 800) - 400
        y = r.uniform(0, h)
        rr = r.uniform(150, 320)
        cv.drawPath(circle(x, y, rr), blur_paint(shade(col, 1.1), rr * 0.5, int(90 * strength)))


def heat_shimmer_overlay(cv, t, y0, y1, a=40):
    for k in range(6):
        yy = y0 + (y1 - y0) * k / 6 + math.sin(t * 2 + k) * 6
        cv.drawLine(0, yy, W, yy + math.sin(t + k) * 4, stroke("#ffffff", 14, a))


def arrow(cv, x, y, ang, s=1.0, a=255):
    r = math.radians(ang)
    dx, dy = math.cos(r), math.sin(r)
    L = 90 * s
    x0, y0 = x - dx * L, y - dy * L
    cv.drawLine(x0, y0, x, y, stroke(OUT, 5 * s, a))
    cv.drawLine(x0, y0, x, y, stroke("#a8784a", 3 * s, a))
    nx, ny = -dy, dx
    tip = poly([(x + dx * 14 * s, y + dy * 14 * s), (x + nx * 6 * s, y + ny * 6 * s), (x - nx * 6 * s, y - ny * 6 * s)])
    cv.drawPath(tip, fill("#9aa3ab", a))
    for sg in (-1, 1):
        cv.drawLine(x0 + dx * 4 * s, y0 + dy * 4 * s, x0 - dx * 10 * s + nx * sg * 8 * s,
                    y0 - dy * 10 * s + ny * sg * 8 * s, stroke("#e8e0d0", 4 * s, a))


def arrow_volley(cv, t, x0, y0, x1, y1, n=40, dur=1.6, seed=3, s=0.8, spread=300, start=0.0, loop=None):
    """x0,y0 -> x1,y1 parabolik ok yagmuru"""
    r = random.Random(seed)
    for k in range(n):
        off = r.uniform(0, dur * 0.8)
        tt = t - start - off
        if loop:
            tt = tt % loop
        if tt < 0 or tt > dur:
            continue
        f = tt / dur
        sx = x0 + r.uniform(-spread, spread) * 0.4
        ex = x1 + r.uniform(-spread, spread)
        sy = y0 + r.uniform(-40, 40)
        ey = y1 + r.uniform(-60, 60)
        x = sx + (ex - sx) * f
        hgt = r.uniform(250, 420)
        y = sy + (ey - sy) * f - math.sin(f * math.pi) * hgt
        # turev
        dxv = ex - sx
        dyv = (ey - sy) - math.cos(f * math.pi) * math.pi * hgt
        ang = math.degrees(math.atan2(dyv, dxv))
        arrow(cv, x, y, ang, s)


def blood_splat(cv, x, y, t, t0, s=1.0, seed=0, a=230):
    """t0 aninda patlayan kan damlalari (cizgi film)"""
    tt = t - t0
    if tt < 0:
        return
    r = random.Random(seed)
    for k in range(14):
        ang = r.uniform(-math.pi * 0.95, -math.pi * 0.05)
        sp = r.uniform(200, 520) * s
        g = 1400 * s
        px = x + math.cos(ang) * sp * tt
        py = y + math.sin(ang) * sp * tt + 0.5 * g * tt * tt
        rr = r.uniform(5, 12) * s
        if tt > 0.9:
            continue
        cv.drawPath(circle(px, py, rr), fill("#b0141a", a))
        cv.drawPath(circle(px - rr * 0.3, py - rr * 0.3, rr * 0.35), fill("#ff6a6a", a * 0.7))


def blood_pool(cv, x, y, s=1.0, a=200, seed=0):
    r = random.Random(seed)
    pts = []
    for k in range(10):
        ang = k / 10 * math.tau
        rr = r.uniform(0.7, 1.2)
        pts.append((x + math.cos(ang) * 60 * s * rr, y + math.sin(ang) * 16 * s * rr))
    cv.drawPath(smooth(pts), fill("#8a0c10", a))


def sparks(cv, x, y, t, t0, s=1.0, seed=0, n=16):
    tt = t - t0
    if tt < 0 or tt > 0.5:
        return
    r = random.Random(seed)
    f = tt / 0.5
    cv.drawPath(circle(x, y, 60 * s * (1 - f)), blur_paint("#fff3b0", 20 * s, int(255 * (1 - f))))
    for k in range(n):
        ang = r.uniform(0, math.tau)
        sp = r.uniform(80, 260) * s
        px, py = x + math.cos(ang) * sp * f, y + math.sin(ang) * sp * f
        cv.drawLine(px, py, px - math.cos(ang) * 16 * s, py - math.sin(ang) * 16 * s,
                    stroke("#ffe07a", 3 * s, int(255 * (1 - f))))


def impact_star(cv, x, y, t, t0, s=1.0, col="#fff6c0"):
    tt = t - t0
    if tt < 0 or tt > 0.35:
        return
    f = tt / 0.35
    pts = []
    for k in range(16):
        ang = k / 16 * math.tau
        rr = (70 if k % 2 == 0 else 30) * s * (0.6 + f)
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    cv.drawPath(poly(pts), fill(col, int(255 * (1 - f))))
    cv.drawPath(poly(pts), stroke(OUT, 3, int(255 * (1 - f))))


def embers(cv, t, n=30, seed=4, col="#ffb050", w=W, h=H):
    r = random.Random(seed)
    for k in range(n):
        sp = r.uniform(40, 120)
        x = (r.uniform(0, w) + math.sin(t * r.uniform(0.5, 1.5) + k) * 40) % w
        y = h - ((t * sp + r.uniform(0, h)) % (h + 100))
        rr = r.uniform(2, 5)
        cv.drawPath(circle(x, y, rr * 2.5), blur_paint(col, rr, 120))
        cv.drawPath(circle(x, y, rr * 0.7), fill("#fff0c0", 220))


def light_rays(cv, x, y, t, n=10, col="#fff2c0", a=60, length=1400, spread=70, base_ang=90):
    for k in range(n):
        ang = math.radians(base_ang - spread / 2 + spread * k / (n - 1) + math.sin(t * 0.5 + k) * 2)
        w = 30 + 20 * math.sin(k * 1.7)
        dx, dy = math.cos(ang), math.sin(ang)
        nx, ny = -dy, dx
        pth = poly([(x, y), (x + dx * length + nx * w, y + dy * length + ny * w),
                    (x + dx * length - nx * w, y + dy * length - ny * w)])
        p = lin_grad((x, y), (x + dx * length, y + dy * length), [rgb(col, a), rgb(col, 0)])
        cv.drawPath(pth, p)


def fog(cv, t, y, h_, col="#e8dcc8", a=90, seed=2):
    r = random.Random(seed)
    for k in range(10):
        x = (r.uniform(0, W + 600) + t * r.uniform(10, 30)) % (W + 600) - 300
        rr = r.uniform(200, 380)
        cv.drawPath(ellipse(x, y + r.uniform(-h_, h_), rr, rr * 0.35), blur_paint(col, 60, a))


def flash(cv, t, t0, dur=0.25, col="#ffffff", a=200):
    tt = t - t0
    if 0 <= tt <= dur:
        cv.drawRect(skia.Rect.MakeWH(W, H), fill(col, int(a * (1 - tt / dur))))


def film_grain(cv, t, a=14):
    r = random.Random(int(t * 30))
    for k in range(60):
        x, y = r.uniform(0, W), r.uniform(0, H)
        cv.drawPath(circle(x, y, r.uniform(0.6, 1.6)), fill("#000000" if k % 2 else "#ffffff", a))


def plague_miasma(cv, t, a=70):
    r = random.Random(11)
    for k in range(14):
        x = (r.uniform(0, W + 600) + t * r.uniform(8, 25)) % (W + 600) - 300
        y = r.uniform(H * 0.3, H)
        rr = r.uniform(150, 300)
        cv.drawPath(circle(x, y, rr), blur_paint("#7a9a5a", rr * 0.45, a))


def speed_lines(cv, t, cx, cy, a=90, n=40, seed=8):
    r = random.Random(seed + int(t * 12))
    for k in range(n):
        ang = r.uniform(0, math.tau)
        r0 = r.uniform(500, 700)
        r1 = r0 + r.uniform(200, 500)
        cv.drawLine(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, cx + math.cos(ang) * r1,
                    cy + math.sin(ang) * r1, stroke("#ffffff", r.uniform(2, 6), a))

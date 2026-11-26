"""Sahne arka planlari (statik kisimlar; engine.bg ile onbellege alinir).

Antik Yunan / Roma Anadolusu: arena, tunel, tiyatro, tapinak, Izmir limani, Bergama, ludus avlusu,
hucre, yemekhane, Galenos'un odasi, gece ziyafeti, Efes kazisi.
"""
import math
import random

import skia

import scenery as S
from gfx import (OUT, W, H, P, blur_paint, circle, ellipse, fill, lin_grad, mix, poly, rad_grad, rgb, rrect, shade,
                 smooth, stroke, tint, shape)

SKIES = {
    "golden": (["#5f8fc4", "#a9c3d6", "#f4d9a0", "#f3b56a"], [0, 0.35, 0.8, 1]),
    "day": (["#3f86d0", "#86bde6", "#d8ecf6"], [0, 0.6, 1]),
    "hot": (["#5f98d0", "#cfe0e6", "#f7e2b0"], [0, 0.55, 1]),
    "dawn": (["#2a3a6a", "#7a6a9a", "#e8a07a", "#f6d08a"], [0, 0.35, 0.75, 1]),
    "sunset": (["#3a2a5a", "#a8506a", "#f08a4a", "#ffd08a"], [0, 0.4, 0.75, 1]),
    "dusk": (["#1a1f40", "#4a3a6a", "#b0607a", "#f0a070"], [0, 0.45, 0.8, 1]),
    "night": (["#070b1e", "#0f1a3a", "#1d2c55"], [0, 0.6, 1]),
}

GROUND = {
    "golden": ["#c9a86a", "#b08a50", "#8a6a3a"],
    "day": ["#b8b070", "#9a9a58", "#7a7a42"],
    "hot": ["#e8c88a", "#d8b070", "#c09050"],
    "dawn": ["#8a7a6a", "#6a5a4a", "#4a3a30"],
    "sunset": ["#b07a4a", "#8a5a34", "#5a3a22"],
    "dusk": ["#6a5050", "#4a3a3a", "#2a2028"],
    "night": ["#2a2a40", "#1e1e30", "#141420"],
}

MARBLE = "#efe8d8"
MARBLE2 = "#d9cfba"
ROOF = "#b8553a"
SAND = "#e6c98e"


def sky_for(cv, v, horizon=620):
    cols, pos = SKIES[v]
    S.sky(cv, W, H, cols, pos, horizon=horizon)
    if v == "night":
        S.stars(cv, W, H, 260, maxy=horizon)
        S.moon(cv, 1500, 170, 46)
    elif v == "dusk":
        S.stars(cv, W, H, 80, maxy=horizon * 0.5)
    elif v == "golden":
        S.sun(cv, 1450, 330, 70, glow="#ffc870", ga=170)
    elif v == "sunset":
        S.sun(cv, 1500, 520, 90, col="#ffe0a0", glow="#ff9a4a", ga=200)
    elif v == "dawn":
        S.sun(cv, 300, 600, 80, col="#ffe8b0", glow="#ffb07a", ga=170)
    elif v in ("day", "hot"):
        S.sun(cv, 1600, 150, 60)
        S.clouds(cv, W, H, 4, seed=2, a=150, ymax=0.25)


def studio(cv, col="#f0d9a8", col2="#c89a58"):
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H * 0.45), 1300, [shade(col, 1.08), col, col2]))
    r = random.Random(4)
    for _ in range(26):
        x, y = r.uniform(0, W), r.uniform(0, H)
        rr = r.uniform(60, 200)
        cv.drawPath(circle(x, y, rr), fill("#ffffff", 14))
    cv.drawPath(ellipse(W / 2, 1010, 820, 70), fill(shade(col2, 0.8), 120))


def dark_studio(cv, col="#3a2a22", col2="#120c08"):
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H * 0.45), 1300, [shade(col, 1.2), col, col2]))
    cv.drawPath(ellipse(W / 2, 1010, 820, 70), fill("#000000", 90))


# ================================================================== mimari ogeler
def greek_column(cv, x, y, h_, w_=26, col=MARBLE):
    shape(cv, rrect(x - w_ / 2, y - h_, w_, h_, 3), col, w=3)
    for k in (-1, 0, 1):
        cv.drawLine(x + k * w_ * 0.25, y - h_ + 14, x + k * w_ * 0.25, y - 12, stroke(shade(col, 0.82), 2))
    shape(cv, rrect(x - w_ * 0.85, y - h_ - 12, w_ * 1.7, 14, 3), col, w=3)
    shape(cv, rrect(x - w_ * 0.75, y - 12, w_ * 1.5, 12, 3), col, w=3)


def temple(cv, x, y, w_, h_, col=MARBLE, n=6, roof_col=None):
    """on cepheden Yunan tapinagi: basamaklar, sutunlar, alinlik"""
    shape(cv, rrect(x - w_ / 2 - 20, y - 14, w_ + 40, 14, 2), shade(col, 0.92), w=3)
    shape(cv, rrect(x - w_ / 2 - 10, y - 26, w_ + 20, 14, 2), col, w=3)
    ch = h_ * 0.62
    cv.drawRect(skia.Rect.MakeLTRB(x - w_ / 2 + 10, y - 26 - ch, x + w_ / 2 - 10, y - 26), fill(shade(col, 0.6)))
    for k in range(n):
        cx = x - w_ / 2 + 22 + k * (w_ - 44) / (n - 1)
        greek_column(cv, cx, y - 26, ch, w_=max(14, w_ / n * 0.42), col=col)
    shape(cv, rrect(x - w_ / 2 - 6, y - 26 - ch - 30, w_ + 12, 22, 2), col, w=3)
    ped = poly([(x - w_ / 2 - 14, y - 26 - ch - 30), (x, y - 26 - ch - 30 - h_ * 0.26),
                (x + w_ / 2 + 14, y - 26 - ch - 30)])
    shape(cv, ped, roof_col or col, w=3)
    shape(cv, poly([(x - w_ / 2 + 20, y - 26 - ch - 36), (x, y - 26 - ch - 30 - h_ * 0.26 + 16),
                    (x + w_ / 2 - 20, y - 26 - ch - 36)]), shade(col, 0.9), w=2)


def house(cv, x, y, w_, h_, col="#f0e6d2", roof=ROOF, door=True, win=True, seed=0):
    shape(cv, rrect(x, y - h_, w_, h_, 3), col, w=3)
    shape(cv, poly([(x - 10, y - h_ + 2), (x + w_ / 2, y - h_ - w_ * 0.22), (x + w_ + 10, y - h_ + 2)]), roof, w=3)
    for k in range(int(w_ / 22)):
        xx = x - 4 + k * 22
        cv.drawLine(xx, y - h_ - 2, xx + w_ * 0.05, y - h_ - 2 - w_ * 0.06, stroke(shade(roof, 0.75), 2))
    if door:
        shape(cv, rrect(x + w_ * 0.4, y - h_ * 0.5, w_ * 0.2, h_ * 0.5, 3), "#6a4424", w=2.5)
    if win and h_ > 70:
        shape(cv, rrect(x + w_ * 0.12, y - h_ * 0.82, w_ * 0.16, h_ * 0.18, 2), "#3a2a20", w=2)
        shape(cv, rrect(x + w_ * 0.72, y - h_ * 0.82, w_ * 0.16, h_ * 0.18, 2), "#3a2a20", w=2)


def town(cv, x0, x1, y, seed=0, scale=1.0, temples=1):
    r = random.Random(seed)
    x = x0
    k = 0
    while x < x1:
        w_ = r.uniform(70, 130) * scale
        h_ = r.uniform(60, 120) * scale
        house(cv, x, y + r.uniform(-4, 4) * scale, w_, h_, col=mix("#f4ecda", "#e2cfa8", r.random()),
              roof=mix(ROOF, "#9a4a32", r.random()), door=r.random() < 0.5, win=True)
        x += w_ * r.uniform(0.8, 1.0)
        k += 1


def amphora(cv, x, y, s=1.0, col="#b86a3a"):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = smooth([(-14, -110), (-30, -86), (-34, -40), (-16, 0), (16, 0), (34, -40), (30, -86), (14, -110)],
                  tension=0.5)
    shape(cv, body, col, w=3)
    for sx in (-1, 1):
        hnd = P()
        hnd.moveTo(sx * 12, -108)
        hnd.quadTo(sx * 40, -112, sx * 28, -86)
        cv.drawPath(hnd, stroke(OUT, 7))
        cv.drawPath(hnd, stroke(col, 3))
    shape(cv, rrect(-14, -124, 28, 16, 4), shade(col, 0.9), w=3)
    cv.drawLine(-30, -66, 30, -66, stroke("#2a1a12", 4))
    cv.drawLine(-32, -56, 32, -56, stroke("#2a1a12", 2))
    cv.restore()


def pot(cv, x, y, s=1.0, col="#c07040", black=False):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = smooth([(-20, -70), (-40, -40), (-30, 0), (30, 0), (40, -40), (20, -70)], tension=0.5)
    shape(cv, body, col if not black else "#2a1a12", w=3)
    shape(cv, rrect(-24, -82, 48, 14, 5), shade(col, 0.9), w=3)
    if black:
        cv.drawPath(ellipse(0, -36, 18, 14), fill(col))
    else:
        cv.drawLine(-38, -40, 38, -40, stroke("#2a1a12", 4))
    cv.restore()


def torch_holder(cv, x, y, s=1.0):
    shape(cv, rrect(x - 6 * s, y - 70 * s, 12 * s, 70 * s, 4), "#5a3a22", w=3)
    shape(cv, poly([(x - 16 * s, y - 70 * s), (x + 16 * s, y - 70 * s), (x + 10 * s, y - 90 * s),
                    (x - 10 * s, y - 90 * s)]), "#4a4a4a", w=3)


def flame(cv, x, y, t, s=1.0, seed=0):
    cv.drawPath(circle(x, y - 20 * s, 70 * s), rad_grad((x, y - 20 * s), 70 * s, [rgb("#ffb040", 110),
                                                                                    rgb("#ffb040", 0)]))
    for k in range(3):
        ph = t * 8 + k * 2.1 + seed
        hh = (38 + 10 * math.sin(ph)) * s
        xo = (k - 1) * 7 * s
        f = smooth([(x + xo - 12 * s, y), (x + xo - 8 * s, y - hh * 0.5), (x + xo + 3 * math.sin(ph) * s, y - hh),
                    (x + xo + 8 * s, y - hh * 0.45), (x + xo + 12 * s, y)], tension=0.5)
        cv.drawPath(f, fill("#ff8a1a" if k != 1 else "#ffd040", 235))


def stone_wall_bg(cv, x0, y0, x1, y1, col="#9a8a72", seed=0, bw=120, bh=56):
    cv.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), fill(col))
    r = random.Random(seed)
    row = 0
    y = y0
    while y < y1:
        off = (row % 2) * bw / 2
        x = x0 - off
        while x < x1:
            ww = bw * r.uniform(0.85, 1.15)
            c2 = shade(col, r.uniform(0.86, 1.1))
            cv.drawRect(skia.Rect.MakeLTRB(x + 3, y + 3, x + ww - 3, y + bh - 3), fill(c2))
            x += ww
        cv.drawLine(x0, y, x1, y, stroke(shade(col, 0.6), 3))
        y += bh
        row += 1


def pergamon_hill(cv, x, y, s=1.0, col="#9aa27a", far=False):
    """Bergama akropolu: dik tepe, yamacta tiyatro, tepede tapinaklar"""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    hill = smooth([(-560, 0), (-420, -120), (-260, -300), (-100, -392), (120, -404), (300, -396), (420, -280),
                   (520, -130), (620, 0)], closed=False)
    hill.lineTo(620, 40)
    hill.lineTo(-520, 40)
    hill.close()
    cv.drawPath(hill, fill(col))
    cv.drawPath(hill, stroke(shade(col, 0.7), 3))
    # tiyatro (yamacta yelpaze)
    th = P()
    th.moveTo(-180, -150)
    th.quadTo(-120, -290, 20, -300)
    th.lineTo(30, -140)
    th.close()
    cv.drawPath(th, fill(shade(MARBLE2, 0.95) if not far else shade(col, 1.15)))
    for k in range(7):
        p_ = P()
        p_.moveTo(-170 + k * 6, -160 - k * 18)
        p_.quadTo(-110 + k * 10, -180 - k * 16, 24, -150 - k * 21)
        cv.drawPath(p_, stroke(shade(MARBLE2, 0.75), 2))
    # surlar + tapinaklar
    cv.drawRect(skia.Rect.MakeLTRB(-90, -404, 300, -380), fill(shade(MARBLE2, 0.85)))
    temple(cv, 20, -380, 160, 120, col=MARBLE if not far else shade(MARBLE, 0.92), n=6)
    temple(cv, 210, -384, 110, 90, col=MARBLE if not far else shade(MARBLE, 0.92), n=4)
    for k in range(4):
        house(cv, 300 + k * 60, -392 + k * 50 + (k > 1) * 20, 56, 40, col="#e8dcc4", door=False, win=False)
    cv.restore()


def crowd_band(cv, x0, x1, y, scale, seed, curve=0.0, density=1.0, cols=None, dark=1.0):
    """bir oturma sirasi boyunca kalabalik (kafa + omuz)"""
    r = random.Random(seed)
    cols = cols or ["#b8423a", "#3a6a9a", "#e8dcc0", "#6a8a4a", "#c9a040", "#8a5a8a", "#d8d0c0", "#5a4a3a",
                    "#a86a3a", "#f0e8d8"]
    skins = ["#e9b991", "#dba479", "#c98e62", "#f1c8a0", "#b07a4a"]
    hairs = ["#2a1a12", "#4a2a1a", "#1a120c", "#6a4a2a", "#cfc8be", "#8a5a2a"]
    sp = 30 * scale / density
    x = x0
    while x < x1:
        yy = y - curve * ((x - W / 2) / (W / 2)) ** 2
        c = shade(r.choice(cols), dark)
        sk = shade(r.choice(skins), dark)
        hb = r.uniform(-3, 3) * scale
        cv.drawPath(rrect(x - 13 * scale, yy - 8 * scale + hb, 26 * scale, 26 * scale, 9 * scale), fill(c))
        cv.drawPath(circle(x, yy - 16 * scale + hb, 10 * scale), fill(sk))
        if r.random() < 0.75:
            cv.drawPath(ellipse(x, yy - 22 * scale + hb, 10 * scale, 6 * scale), fill(shade(r.choice(hairs), dark)))
        x += sp * r.uniform(0.85, 1.15)


# ================================================================== ARENA
def arena(cv, v="day", tribunal=True):
    """Arenaya donusturulmus stadyum: kalabalik tribunler, podyum duvari, kum."""
    sky_for(cv, "day" if v == "day" else v, horizon=300)
    # velarium (gunes perdesi) serit
    for k in range(9):
        x = k * 240 - 40
        shape(cv, poly([(x, -10), (x + 230, -10), (x + 200, 70 + (k % 2) * 16), (x + 30, 70 + (k % 2) * 16)]),
              "#e8d8b8" if k % 2 else "#c8482a", w=3)
    # tribunler
    top = 90
    rows = 14
    for i in range(rows):
        y0 = top + i * 34
        band = poly([(0, y0 - 40), (W, y0 - 40), (W, y0 + 40), (0, y0 + 40)])
        cv.drawRect(skia.Rect.MakeLTRB(0, y0, W, y0 + 34), fill(shade(MARBLE2, 0.82 + i * 0.012)))
        cv.drawLine(0, y0, W, y0, stroke(shade(MARBLE2, 0.6), 2))
        crowd_band(cv, -20, W + 20, y0 + 30, 0.62 + i * 0.03, seed=100 + i, curve=-30 * (1 - i / rows),
                   dark=0.86 + i * 0.008)
    # merdiven bolumleri
    for x in range(160, W, 400):
        cv.drawRect(skia.Rect.MakeLTRB(x - 14, top, x + 14, top + rows * 34), fill(shade(MARBLE2, 0.72)))
    # podyum duvari
    py0, py1 = 590, 690
    cv.drawRect(skia.Rect.MakeLTRB(0, py0 - 14, W, py0), fill(shade(MARBLE, 0.95)))
    cv.drawRect(skia.Rect.MakeLTRB(0, py0, W, py1), lin_grad((0, py0), (0, py1), ["#c8b48e", "#a8946e"]))
    for k in range(12):
        x = 40 + k * 162
        col = ["#8a2a22", "#2f5a7a", "#6a7a3a"][k % 3]
        cv.drawPath(rrect(x, py0 + 16, 120, py1 - py0 - 32, 6), fill(col, 200))
        cv.drawPath(rrect(x, py0 + 16, 120, py1 - py0 - 32, 6), stroke("#e2c47a", 3))
    cv.drawLine(0, py0, W, py0, stroke(OUT, 4))
    cv.drawLine(0, py1, W, py1, stroke(OUT, 4))
    # ag/korkuluk (hayvanlara karsi)
    for x in range(0, W, 26):
        cv.drawLine(x, py0 - 60, x, py0 - 14, stroke("#5a4a3a", 2, 150))
    cv.drawLine(0, py0 - 60, W, py0 - 60, stroke("#5a4a3a", 3, 160))
    if tribunal:
        # baskanlik locasi
        tx = W / 2
        shape(cv, rrect(tx - 190, 380, 380, 210, 6), "#7a2a5a", w=4)
        cv.drawRect(skia.Rect.MakeLTRB(tx - 180, 390, tx + 180, 470), fill("#5a1a40"))
        for k in range(5):
            greek_column(cv, tx - 170 + k * 85, 590, 200, 22)
        shape(cv, poly([(tx - 210, 384), (tx, 320), (tx + 210, 384)]), MARBLE, w=3)
        for k in range(8):
            cv.drawLine(tx - 180 + k * 51, 470, tx - 154 + k * 51, 540, stroke("#e2c47a", 2, 150))
    # kum
    cv.drawRect(skia.Rect.MakeLTRB(0, py1, W, H), lin_grad((0, py1), (0, H), ["#e8cf98", SAND, "#d6b276"]))
    r = random.Random(9)
    for _ in range(200):
        x, y = r.uniform(0, W), r.uniform(py1 + 10, H)
        cv.drawPath(ellipse(x, y, r.uniform(4, 14), r.uniform(1.5, 3)), fill("#b89458", 90))
    cv.drawPath(ellipse(W / 2, py1 + 14, 1100, 20), fill("#000000", 40))


def arena_crowd_overlay(cv, t, x0=0, x1=W, y0=110, y1=560, n=70, seed=3, excite=0.5):
    """kalabaliktan kalkan kollar (animasyon)"""
    r = random.Random(seed)
    for k in range(n):
        x = r.uniform(x0, x1)
        y = r.uniform(y0, y1)
        ph = r.uniform(0, 6.28)
        sp = r.uniform(5, 9)
        up = max(0.0, math.sin(t * sp + ph)) * excite
        if up < 0.05:
            continue
        s = 0.6 + (y - y0) / (y1 - y0) * 0.5
        sk = r.choice(["#e9b991", "#dba479", "#c98e62"])
        for sx in (-1, 1):
            cv.drawLine(x + sx * 10 * s, y, x + sx * (14 + 6 * up) * s, y - 30 * up * s, stroke(OUT, 7 * s))
            cv.drawLine(x + sx * 10 * s, y, x + sx * (14 + 6 * up) * s, y - 30 * up * s, stroke(sk, 4 * s))


def tunnel(cv, light=0.0):
    """arenaya acilan karanlik tonoz ve demir kapi; arka planda parlak arena"""
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#1c1410"))
    # uzak arena (kapinin ardi)
    gx0, gx1, gy0, gy1 = 620, 1300, 250, 900
    cv.save()
    arch = P()
    arch.moveTo(gx0, gy1)
    arch.lineTo(gx0, gy0 + 220)
    arch.cubicTo(gx0, gy0 - 40, gx1, gy0 - 40, gx1, gy0 + 220)
    arch.lineTo(gx1, gy1)
    arch.close()
    cv.clipPath(arch, skia.ClipOp.kIntersect, True)
    cv.drawRect(skia.Rect.MakeLTRB(gx0, gy0 - 100, gx1, gy1), lin_grad((0, gy0), (0, gy1),
                                                                         ["#fff6dc", "#ffe2a0", "#f0c070"]))
    for i in range(6):
        crowd_band(cv, gx0 - 20, gx1 + 20, gy0 + 120 + i * 40, 0.6 + i * 0.05, seed=300 + i, dark=0.55)
    cv.drawRect(skia.Rect.MakeLTRB(gx0, gy0 + 400, gx1, gy0 + 460), fill("#8a7a5a"))
    cv.drawRect(skia.Rect.MakeLTRB(gx0, gy0 + 460, gx1, gy1), fill("#f0d8a0"))
    cv.restore()
    # tonoz taslari
    stone = P()
    stone.addRect(skia.Rect.MakeWH(W, H))
    hole = P()
    hole.moveTo(gx0, gy1)
    hole.lineTo(gx0, gy0 + 220)
    hole.cubicTo(gx0, gy0 - 40, gx1, gy0 - 40, gx1, gy0 + 220)
    hole.lineTo(gx1, gy1)
    hole.close()
    wall = skia.Op(stone, hole, skia.PathOp.kDifference_PathOp)
    cv.save()
    cv.clipPath(wall, skia.ClipOp.kIntersect, True)
    stone_wall_bg(cv, 0, 0, W, H, col="#4a3c30", seed=4, bw=150, bh=70)
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, 560), 900, [rgb("#000000", 0), rgb("#000000", 200)]))
    cv.restore()
    cv.drawPath(hole, stroke(OUT, 8))
    # zemin
    cv.drawRect(skia.Rect.MakeLTRB(0, 900, W, H), lin_grad((0, 900), (0, H), ["#3a2e24", "#120c08"]))
    cv.drawPath(poly([(gx0, 900), (gx1, 900), (gx1 + 300, H), (gx0 - 300, H)]), fill("#ffe2a0", 40))


def portcullis(cv, x0, x1, y0, y1, lift=0.0):
    """demir parmaklikli kapi; lift 0..1 yukari kalkar"""
    dy = -(y1 - y0) * lift
    cv.save()
    cv.translate(0, dy)
    for x in range(int(x0) + 20, int(x1), 56):
        cv.drawLine(x, y0 - 40, x, y1, stroke(OUT, 16))
        cv.drawLine(x, y0 - 40, x, y1, stroke("#4a4a4e", 10))
        cv.drawLine(x - 2, y0 - 40, x - 2, y1, stroke("#7a7a80", 2))
        shape(cv, poly([(x - 10, y1), (x + 10, y1), (x, y1 + 22)]), "#4a4a4e", w=3)
    for y in range(int(y0) + 40, int(y1), 120):
        cv.drawLine(x0, y, x1, y, stroke(OUT, 14))
        cv.drawLine(x0, y, x1, y, stroke("#55555a", 8))
    cv.restore()


# ================================================================== TIYATRO / TAPINAK
def theater(cv):
    """Efes tipi Yunan tiyatrosu (yamaca oyulmus), sahne binasi"""
    sky_for(cv, "day", horizon=500)
    S.ridge(cv, W, H, 420, 120, 0.8, "#8a9a6a", seed=5)
    # cavea
    cx, cy = W / 2, 980
    for i in range(18):
        rr = 380 + i * 38
        p_ = P()
        p_.addArc(skia.Rect.MakeLTRB(cx - rr * 1.5, cy - rr, cx + rr * 1.5, cy + rr), 180, 180)
        cv.drawPath(p_, stroke(shade(MARBLE2, 0.95 - i * 0.012), 36, cap="butt"))
        cv.drawPath(p_, stroke(shade(MARBLE2, 0.7), 2))
    for a in range(200, 345, 24):
        rad = math.radians(a)
        cv.drawLine(cx + math.cos(rad) * 570, cy + math.sin(rad) * 380, cx + math.cos(rad) * 1590,
                    cy + math.sin(rad) * 1060, stroke(shade(MARBLE2, 0.7), 10))
    # orkestra ve sahne
    cv.drawPath(ellipse(cx, cy + 20, 520, 160), fill("#d8c8a0"))
    cv.drawPath(ellipse(cx, cy + 20, 520, 160), stroke(OUT, 3))
    cv.drawRect(skia.Rect.MakeLTRB(0, 1000, W, H), fill("#c8b48e"))


def olympia(cv):
    sky_for(cv, "day", horizon=640)
    S.ridge(cv, W, H, 560, 90, 0.9, "#9aa27a", seed=2)
    S.ridge(cv, W, H, 620, 50, 1.4, "#8a9a62", seed=6)
    temple(cv, 1380, 700, 520, 360)
    for x in (180, 330, 1780):
        S.olive(cv, x, 720, 1.1)
    cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), lin_grad((0, 700), (0, H), ["#e2c890", "#c8a870"]))
    for k in range(3):
        cv.drawLine(0, 860 + k * 70, W, 860 + k * 70, stroke("#f6ecd4", 5, 160))


# ================================================================== IZMIR / SEHIR
def harbor(cv, v="day"):
    sky_for(cv, v, horizon=600)
    # Pagos tepesi + kale
    S.ridge(cv, W, H, 430, 160, 0.7, "#8a9a72", seed=3)
    cv.drawRect(skia.Rect.MakeLTRB(1180, 300, 1520, 340), fill("#cbbd9c"))
    for x in range(1180, 1520, 30):
        cv.drawRect(skia.Rect.MakeLTRB(x, 288, x + 16, 300), fill("#cbbd9c"))
    cv.drawRect(skia.Rect.MakeLTRB(1180, 300, 1520, 340), stroke(OUT, 3))
    for i in range(4):
        town(cv, -40 + i * 30, W + 40, 520 + i * 48, seed=20 + i, scale=0.7 + i * 0.12)
    temple(cv, 1500, 560, 240, 190)
    # deniz
    cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), lin_grad((0, 700), (0, H), ["#3f8ab8", "#2a5a80"]))
    for k in range(14):
        yy = 720 + k * 26
        for x in range(-60, W, 140):
            cv.drawLine(x + (k % 2) * 70, yy, x + 60 + (k % 2) * 70, yy, stroke("#8fc8e8", 3, 120))
    # iskele
    cv.drawRect(skia.Rect.MakeLTRB(0, 860, 820, 900), fill("#8a6a44"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 860, 820, 900), stroke(OUT, 4))
    for x in range(20, 820, 80):
        cv.drawRect(skia.Rect.MakeLTRB(x, 900, x + 16, 1000), fill("#5a4028"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 900, 820, H), fill("#7a6040"))
    for k, x in enumerate((90, 160, 520, 600)):
        amphora(cv, x, 860, 0.7, col=["#b86a3a", "#c07a48"][k % 2])


def shop(cv):
    """comlekci dukkani (ic mekan, acik on cephe)"""
    cv.drawRect(skia.Rect.MakeWH(W, H), lin_grad((0, 0), (0, H), ["#c8a478", "#a88054", "#7a5a3a"]))
    stone_wall_bg(cv, 0, 0, W, 760, col="#c2a47c", seed=7, bw=180, bh=80)
    tint(cv, "#5a3a20", 50)
    # raflar
    for y in (300, 520):
        cv.drawRect(skia.Rect.MakeLTRB(80, y, 1840, y + 22), fill("#6a4424"))
        cv.drawRect(skia.Rect.MakeLTRB(80, y, 1840, y + 22), stroke(OUT, 3))
    r = random.Random(4)
    x = 120
    while x < 1800:
        if r.random() < 0.5:
            pot(cv, x, 300, r.uniform(0.7, 1.0), col=r.choice(["#c07040", "#b86a3a", "#d08850"]),
                black=r.random() < 0.3)
        else:
            amphora(cv, x, 300, r.uniform(0.6, 0.8))
        x += r.uniform(90, 140)
    x = 140
    while x < 1800:
        pot(cv, x, 520, r.uniform(0.8, 1.1), col=r.choice(["#c07040", "#b86a3a"]), black=r.random() < 0.4)
        x += r.uniform(110, 170)
    cv.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), lin_grad((0, 760), (0, H), ["#8a6a44", "#5a4028"]))
    cv.drawLine(0, 760, W, 760, stroke(OUT, 5))
    # comlekci carki
    shape(cv, ellipse(1500, 830, 130, 30), "#6a4424", w=4)
    shape(cv, rrect(1490, 830, 20, 120, 4), "#5a3a22", w=3)
    pot(cv, 1500, 820, 0.9, col="#c88a58")


def street(cv, v="day"):
    """sehir sokagi: ilan yazilabilir sivali duvar"""
    sky_for(cv, v, horizon=420)
    town(cv, -40, W + 40, 300, seed=33, scale=0.9)
    cv.drawRect(skia.Rect.MakeLTRB(0, 250, W, 820), fill("#efe2c8"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 250, W, 820), stroke(OUT, 4))
    shape(cv, rrect(-10, 220, W + 20, 40, 4), ROOF, w=4)
    r = random.Random(3)
    for _ in range(30):
        cv.drawPath(ellipse(r.uniform(0, W), r.uniform(280, 800), r.uniform(30, 90), r.uniform(8, 20)),
                    fill("#c8b48e", 60))
    cv.drawRect(skia.Rect.MakeLTRB(0, 820, W, H), lin_grad((0, 820), (0, H), ["#b8a888", "#8a7a60"]))
    for x in range(-40, W, 130):
        for yy in (860, 940, 1020):
            cv.drawPath(rrect(x + (yy // 80 % 2) * 60, yy, 118, 66, 10), stroke("#6a5a44", 3, 150))


def road(cv, v="day"):
    sky_for(cv, v, horizon=620)
    S.ridge(cv, W, H, 560, 100, 0.8, "#a8b088", seed=11)
    pergamon_hill(cv, 1380, 640, 0.95, col="#8f9a6e")
    S.ridge(cv, W, H, 660, 50, 1.4, "#9aa26a", seed=12)
    cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), lin_grad((0, 700), (0, H), ["#b0aa6a", "#8a8a4a"]))
    rd = poly([(860, 700), (1000, 700), (1500, H), (300, H)])
    cv.drawPath(rd, fill("#d8c08a"))
    cv.drawPath(rd, stroke("#a08a5a", 3))
    for x, y, s in ((200, 760, 1.0), (420, 720, 0.7), (1700, 790, 1.2), (1500, 730, 0.75), (80, 900, 1.4)):
        S.olive(cv, x, y, s)


# ================================================================== LUDUS
def ludus_court(cv, v="day"):
    """sutunlu revakla cevrili kumlu avlu; arkada Bergama akropolu"""
    sky_for(cv, v, horizon=420)
    pergamon_hill(cv, 1300, 420, 0.7, col="#8f9a6e", far=True)
    # arka revak
    cv.drawRect(skia.Rect.MakeLTRB(0, 300, W, 700), fill("#cbb894"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 300, W, 330), fill(MARBLE2))
    cv.drawRect(skia.Rect.MakeLTRB(0, 300, W, 330), stroke(OUT, 3))
    shape(cv, poly([(-20, 300), (W + 20, 300), (W + 20, 270), (-20, 270)]), ROOF, w=3)
    # hucre kapilari
    for k in range(9):
        x = 60 + k * 215
        shape(cv, rrect(x + 50, 470, 90, 220, 6), "#5a3a22", w=3)
        for j in range(3):
            cv.drawLine(x + 62 + j * 30, 490, x + 62 + j * 30, 560, stroke("#2a1a10", 6))
        cv.drawLine(x + 60, 520, x + 130, 520, stroke("#2a1a10", 5))
    for k in range(10):
        greek_column(cv, k * 215 - 10, 700, 370, 30, col=MARBLE)
    cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, 730), fill(shade(MARBLE2, 0.9)))
    cv.drawLine(0, 700, W, 700, stroke(OUT, 3))
    # kum avlu
    cv.drawRect(skia.Rect.MakeLTRB(0, 730, W, H), lin_grad((0, 730), (0, H), ["#e8cf98", SAND, "#d2ac70"]))
    r = random.Random(5)
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(740, H)
        cv.drawPath(ellipse(x, y, r.uniform(4, 12), r.uniform(1.5, 3)), fill("#b89458", 80))


def palus_post(cv, x, y, s=1.0, hit=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.rotate(hit * 4)
    cv.drawPath(ellipse(0, 4, 40, 10), fill("#000000", 60))
    shape(cv, rrect(-22, -230, 44, 236, 10), "#8a5a2e", w=4)
    for k in range(5):
        cv.drawLine(-18, -200 + k * 40, 16, -196 + k * 40, stroke("#6a4424", 3))
    for (yy, ln) in ((-180, 18), (-120, 22), (-80, 14)):
        cv.drawLine(-14, yy, -14 + ln, yy + 6, stroke("#4a2a14", 2.4))
    cv.restore()


def cell(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#2a2018"))
    stone_wall_bg(cv, 0, 0, W, 780, col="#5a4a3a", seed=12, bw=170, bh=80)
    # kucuk pencere
    shape(cv, rrect(1260, 150, 200, 110, 6), "#1a2a4a", w=5)
    for k in range(4):
        cv.drawLine(1290 + k * 46, 150, 1290 + k * 46, 260, stroke("#2a2a2a", 9))
    S.stars(cv, W, H, 0)
    cv.drawRect(skia.Rect.MakeLTRB(0, 780, W, H), lin_grad((0, 780), (0, H), ["#4a3a2c", "#2a2018"]))
    cv.drawLine(0, 780, W, 780, stroke(OUT, 5))
    # saman yatak
    shape(cv, rrect(160, 830, 700, 110, 30), "#c8a858", w=4)
    r = random.Random(2)
    for _ in range(80):
        x = r.uniform(180, 840)
        y = r.uniform(840, 930)
        a = r.uniform(-0.4, 0.4)
        cv.drawLine(x, y, x + math.cos(a) * 30, y + math.sin(a) * 30, stroke("#a88838", 2))
    # kapi
    shape(cv, rrect(1500, 330, 300, 450, 8), "#4a3020", w=5)
    for k in range(4):
        cv.drawLine(1540 + k * 70, 330, 1540 + k * 70, 780, stroke("#2a1a10", 5))
    for y in (420, 640):
        shape(cv, rrect(1490, y, 320, 24, 4), "#3a3a3e", w=3)
    shape(cv, rrect(1590, 430, 120, 80, 6), "#1a120c", w=3)
    for k in range(3):
        cv.drawLine(1610 + k * 40, 430, 1610 + k * 40, 510, stroke("#55555a", 6))
    tint(cv, "#0a0a20", 70)


def mess(cv):
    """yemekhane: uzun masa, kazanlar"""
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#7a5a3a"))
    stone_wall_bg(cv, 0, 0, W, 700, col="#a8906a", seed=17, bw=200, bh=90)
    tint(cv, "#3a2010", 60)
    for x in (360, 1560):
        torch_holder(cv, x, 360)
    cv.drawRect(skia.Rect.MakeLTRB(0, 700, W, H), lin_grad((0, 700), (0, H), ["#6a4a2e", "#3a2818"]))
    cv.drawLine(0, 700, W, 700, stroke(OUT, 5))
    # kazan
    shape(cv, ellipse(1640, 760, 170, 40), "#3a3a3a", w=4)
    shape(cv, smooth([(1470, 760), (1490, 880), (1640, 920), (1790, 880), (1810, 760)], closed=True), "#4a4a4e",
          w=4)
    cv.drawPath(ellipse(1640, 760, 150, 30), fill("#e8d8a8"))


def clinic(cv):
    """Galenos'un odasi: raflar, tomarlar, ilac kaplari, sedir"""
    cv.drawRect(skia.Rect.MakeWH(W, H), lin_grad((0, 0), (0, H), ["#d8c8a8", "#c0a880", "#8a7050"]))
    for x in range(0, W, 200):
        cv.drawRect(skia.Rect.MakeLTRB(x, 0, x + 6, 760), fill("#b8a078", 120))
    # raflar
    for y in (260, 440):
        cv.drawRect(skia.Rect.MakeLTRB(1100, y, 1820, y + 18), fill("#6a4424"))
        cv.drawRect(skia.Rect.MakeLTRB(1100, y, 1820, y + 18), stroke(OUT, 3))
    r = random.Random(8)
    for k in range(9):
        x = 1140 + k * 76
        if k % 3 == 0:
            for j in range(3):
                shape(cv, rrect(x - 16 + j * 6, 200 + j * 6, 26, 60, 10), "#efe2c0", w=2.4)
        else:
            pot(cv, x, 260, 0.55, col=r.choice(["#5a7a9a", "#c07040", "#6a8a5a"]))
    for k in range(8):
        x = 1150 + k * 86
        pot(cv, x, 440, 0.5, col=r.choice(["#b86a3a", "#e0d0b0", "#7a6a8a"]))
    # Asklepios asasi (yilanli) duvarda
    cv.drawLine(420, 140, 420, 520, stroke(OUT, 14))
    cv.drawLine(420, 140, 420, 520, stroke("#8a5a2e", 9))
    snk = P()
    snk.moveTo(420, 500)
    for k in range(6):
        snk.quadTo(420 + (40 if k % 2 == 0 else -40), 470 - k * 55, 420, 445 - k * 55)
    cv.drawPath(snk, stroke(OUT, 12))
    cv.drawPath(snk, stroke("#5f8f3a", 7))
    cv.drawRect(skia.Rect.MakeLTRB(0, 760, W, H), lin_grad((0, 760), (0, H), ["#9a7a52", "#6a4e32"]))
    cv.drawLine(0, 760, W, 760, stroke(OUT, 5))
    # muayene sediri
    shape(cv, rrect(560, 760, 760, 70, 14), "#8a5a2e", w=4)
    shape(cv, rrect(580, 730, 720, 40, 16), "#e8dcc0", w=4)
    for x in (600, 1260):
        shape(cv, rrect(x, 830, 24, 120, 4), "#6a4424", w=3)


def banquet(cv):
    """dovus oncesi gece ziyafeti: avlu, mesaleler, uzun masa"""
    sky_for(cv, "night", horizon=420)
    pergamon_hill(cv, 1400, 430, 0.6, col="#2a3048", far=True)
    cv.drawRect(skia.Rect.MakeLTRB(0, 330, W, 720), fill("#4a3a3a"))
    for k in range(10):
        greek_column(cv, k * 215 - 10, 720, 390, 30, col="#8a7a70")
    cv.drawRect(skia.Rect.MakeLTRB(0, 720, W, H), lin_grad((0, 720), (0, H), ["#5a4636", "#2a2018"]))
    tint(cv, "#101030", 50)


def table(cv, x0, x1, y, food=True, seed=0):
    shape(cv, rrect(x0, y - 20, x1 - x0, 34, 6), "#7a4a24", w=4)
    shape(cv, rrect(x0 - 10, y - 30, x1 - x0 + 20, 16, 6), "#efe6d2", w=3)
    for x in (x0 + 20, x1 - 40):
        shape(cv, rrect(x, y + 14, 20, 90, 3), "#5a3a1a", w=3)
    if food:
        r = random.Random(seed)
        x = x0 + 30
        while x < x1 - 30:
            k = r.random()
            if k < 0.3:
                shape(cv, ellipse(x, y - 36, 34, 14), "#c9963a", w=3)
                shape(cv, ellipse(x, y - 46, 22, 16), "#a0402a", w=3)
            elif k < 0.55:
                amphora(cv, x, y - 28, 0.45)
            elif k < 0.8:
                for j in range(4):
                    cv.drawPath(circle(x - 12 + j * 8, y - 40 - (j % 2) * 8, 8), fill("#6a2a6a"))
                    cv.drawPath(circle(x - 12 + j * 8, y - 40 - (j % 2) * 8, 8), stroke(OUT, 2))
            else:
                shape(cv, ellipse(x, y - 40, 28, 12), "#e0b060", w=3)
            x += r.uniform(70, 110)


def dig(cv):
    """Efes kazisi: kazi alani, ip grid, kemikler"""
    sky_for(cv, "hot", horizon=420)
    S.ridge(cv, W, H, 380, 80, 1.0, "#a8a070", seed=21)
    # uzakta Efes (Celsus Kutuphanesi benzeri cephe yerine sade sutunlar)
    for k in range(6):
        greek_column(cv, 1280 + k * 60, 420, 120, 18, col="#e8dcc4")
    cv.drawRect(skia.Rect.MakeLTRB(1250, 286, 1620, 300), fill("#e8dcc4"))
    cv.drawRect(skia.Rect.MakeLTRB(0, 420, W, H), lin_grad((0, 420), (0, H), ["#c8a878", "#a88a5a"]))
    pit = poly([(300, 540), (1620, 540), (1720, 1000), (200, 1000)])
    cv.drawPath(pit, lin_grad((0, 540), (0, 1000), ["#8a6a44", "#a8885a"]))
    cv.drawPath(pit, stroke(OUT, 4))
    for k in range(1, 6):
        x = 300 + k * 220
        cv.drawLine(x, 540, x - 20 + k * 4, 1000, stroke("#efe2c0", 3, 200))
    for k in range(1, 4):
        y = 540 + k * 115
        cv.drawLine(250 - k * 10, y, 1650 + k * 18, y, stroke("#efe2c0", 3, 200))


# ================================================================== diger
def map_parchment(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H / 2), 1200, ["#f1dfb4", "#d8b97c", "#8a6a3a"]))


def museum(cv):
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, 380), 1100, ["#4a4440", "#24201c", "#0e0c0a"]))
    cv.drawPath(ellipse(W / 2, 980, 760, 60), fill("#000000", 120))
    cv.drawPath(poly([(W / 2 - 160, -10), (W / 2 + 160, -10), (W / 2 + 520, 1000), (W / 2 - 520, 1000)]),
                fill("#fff2d0", 22))

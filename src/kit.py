"""Sahnelerde tekrar kullanilan kucuk grafik parcalari."""
import math
import random

import skia

import characters as C
import engine as E
from gfx import (OUT, W, H, big_number, blur_paint, circle, clamp, ease_in_out, ease_out, ellipse, fill, font,
                 label_tag, lerp, lin_grad, pop, poly, rad_grad, rgb, ribbon, rrect, shade, shape, smooth, stroke,
                 text, wrap_lines)


def popped(cv, t, t0, x, y, dur=0.4, rot=0.0):
    """pop olcegiyle cv'yi hazirlar; cizim yapilacaksa olcegi dondurur (cagiran restore etmeli)"""
    s = pop(t - t0, dur)
    if s <= 0:
        return 0.0
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    if rot:
        cv.rotate(rot)
    return s


def tag(cv, s, x, y, t, t0, size=40, rot=-4, bg="#fbf6ea", fg="#2a1a10", t1=None):
    if t1 is not None and t > t1:
        a = 1 - clamp((t - t1) / 0.3)
        if a <= 0:
            return
    if popped(cv, t, t0, x, y):
        label_tag(cv, s, 0, 0, size, rot=rot, bg=bg, fg=fg)
        cv.restore()


def rib(cv, s, x, y, t, t0, size=56, color="#c8202a", rot=-2, maxw=None, t1=None):
    if t1 is not None and t > t1 + 0.3:
        return
    if popped(cv, t, t0, x, y, 0.45):
        a = 255 if t1 is None else int(255 * (1 - clamp((t - t1) / 0.3)))
        ribbon(cv, s, 0, 0, size, color=color, rot=rot, maxw=maxw, a=a)
        cv.restore()


def num(cv, s, x, y, t, t0, size=150, rot=-3):
    if popped(cv, t, t0, x, y, 0.45):
        big_number(cv, s, 0, 0, size, rot=rot)
        cv.restore()


def txt(cv, s, x, y, t, t0, size=44, col="#2a1a10", fnt="xb", oc=None, ow=0, align="center"):
    a = clamp((t - t0) / 0.35)
    if a <= 0:
        return
    text(cv, s, x, y, font(fnt, size), col, align=align, oc=oc, ow=ow, a=int(255 * a))


def vs_badge(cv, x, y, t, t0, s=1.0):
    if popped(cv, t, t0, x, y, 0.4, rot=-8):
        cv.scale(s, s)
        cv.drawPath(circle(0, 0, 70), fill("#c8202a"))
        cv.drawPath(circle(0, 0, 70), stroke(OUT, 6))
        text(cv, "VS", 0, 22, font("slab", 66), "#ffffff", oc=OUT, ow=4)
        cv.restore()


def panel(cv, x, y, w, h, col="#fbf3df", a=255, r=26):
    cv.drawPath(rrect(x - w / 2 + 6, y - h / 2 + 9, w, h, r), fill((0, 0, 0), 70 * a / 255))
    cv.drawPath(rrect(x - w / 2, y - h / 2, w, h, r), fill(col, a))
    cv.drawPath(rrect(x - w / 2, y - h / 2, w, h, r), stroke(OUT, 5, a))


def portrait_card(cv, x, y, w, h, t, t0, name, title=None, col="#fbf3df", bgcol="#e8d0a0", pose=None,
                  ps_scale=1.0, dy=0, f=1, rot=0, **kw):
    """icinde karakter olan kart"""
    s = popped(cv, t, t0, x, y, 0.45, rot=rot)
    if not s:
        return
    panel(cv, 0, 0, w, h, col)
    cv.save()
    cv.clipPath(rrect(-w / 2 + 10, -h / 2 + 10, w - 20, h - 20, 20), skia.ClipOp.kIntersect, True)
    cv.drawRect(skia.Rect.MakeLTRB(-w / 2, -h / 2, w / 2, h / 2), rad_grad((0, -h * 0.2), h, [shade(bgcol, 1.15),
                                                                                         bgcol]))
    ps = dict(pose or {})
    ps.setdefault("blink", E.blink(t, hash(name) % 7))
    ps.setdefault("bob", math.sin(t * 2.2) * 1.5)
    c = C.preset(name, **kw)
    C.draw_person(cv, c, C.pose(**ps), 0, h / 2 + 30 + dy, ps_scale, f)
    cv.restore()
    if title:
        label_tag(cv, title, 0, h / 2 - 6, 34, rot=-2)
    cv.restore()


def oil_lamp(cv, x, y, s=1.0, t=0.0, relief=False):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = smooth([(-70, -10), (-60, -46), (0, -60), (60, -46), (110, -36), (120, -20), (100, -6), (60, 0),
                   (-60, 0)], tension=0.45)
    shape(cv, body, "#c07a4a", w=4)
    cv.drawPath(ellipse(-4, -40, 44, 14), fill("#a8623a"))
    cv.drawPath(ellipse(-4, -40, 44, 14), stroke(OUT, 3))
    shape(cv, smooth([(-70, -24), (-104, -40), (-110, -20), (-74, -10)]), "#b06a3a", w=3)
    if relief:
        cv.save()
        cv.save()
        cv.clipPath(ellipse(-4, -40, 44, 14), skia.ClipOp.kIntersect, True)
        cv.translate(-4, -22)
        cv.scale(0.1, 0.1)
        p = skia.Paint()
        p.setColorFilter(skia.ColorFilters.Blend(rgb("#6a3a1a"), skia.BlendMode.kSrcIn))
        cv.saveLayer(None, p)
        C.draw_person(cv, C.preset("thraex"), C.pose(arm_a=-20, arm_b=70, wpn=80), -120, 140, 1.0, 1)
        C.draw_person(cv, C.preset("murmillo"), C.pose(arm_a=-20, arm_b=70, wpn=80), 120, 140, 1.0, -1)
        cv.restore()
        cv.restore()
        cv.restore()
    fx, fy = 118, -34
    cv.drawPath(circle(fx, fy - 10, 40), rad_grad((fx, fy - 10), 40, [rgb("#ffc860", 140), rgb("#ffc860", 0)]))
    hh = 26 + 5 * math.sin(t * 9)
    fl = smooth([(fx - 7, fy), (fx - 5, fy - hh * 0.5), (fx + 2 * math.sin(t * 7), fy - hh), (fx + 6, fy - hh * 0.4),
                 (fx + 7, fy)], tension=0.5)
    cv.drawPath(fl, fill("#ffb030"))
    cv.drawPath(smooth([(fx - 3, fy), (fx, fy - hh * 0.55), (fx + 3, fy)]), fill("#fff3b0"))
    cv.restore()


def net_shape(cv, cx, cy, rx, ry, a=255, rot=0.0, col="#d8c8a0"):
    cv.save()
    cv.translate(cx, cy)
    cv.rotate(rot)
    pts = []
    for k in range(16):
        ang = k / 16 * math.tau
        rr = 1 + 0.08 * math.sin(k * 2.7)
        pts.append((math.cos(ang) * rx * rr, math.sin(ang) * ry * rr))
    pth = smooth(pts)
    cv.drawPath(pth, fill(col, int(a * 0.25)))
    cv.save()
    cv.clipPath(pth, skia.ClipOp.kIntersect, True)
    step = max(12, rx / 7)
    k = -rx * 2
    while k < rx * 2:
        cv.drawLine(k, -ry * 1.2, k + ry * 0.8, ry * 1.2, stroke("#7a6440", 3, a))
        cv.drawLine(k, ry * 1.2, k + ry * 0.8, -ry * 1.2, stroke("#7a6440", 3, a))
        k += step
    cv.restore()
    cv.drawPath(pth, stroke("#5a4a2a", 5, a))
    for k in range(10):
        ang = k / 10 * math.tau
        cv.drawPath(circle(math.cos(ang) * rx, math.sin(ang) * ry, 7), fill("#6a6a70", a))
        cv.drawPath(circle(math.cos(ang) * rx, math.sin(ang) * ry, 7), stroke(OUT, 2, a))
    cv.restore()


def hand(cv, x, y, s=1.0, finger=0.0, skin="#e9b991", glove=False):
    """yumruk; finger 0..1 isaret parmagi kalkar"""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    capsule_w = 70
    cv.drawLine(0, 120, 0, 320, stroke(OUT, capsule_w + 8))
    cv.drawLine(0, 120, 0, 320, stroke("#e6dcc4" if glove else skin, capsule_w))
    if glove:
        for k in range(6):
            cv.drawLine(-36, 140 + k * 30, 36, 140 + k * 30, stroke("#9a8a6a", 3))
    fist = rrect(-62, -20, 124, 140, 40)
    shape(cv, fist, skin, w=5)
    for k in range(3):
        shape(cv, rrect(-50 + k * 34, -4, 30, 60, 14), shade(skin, 0.95), w=3)
    fl = 150 * ease_out(finger)
    shape(cv, rrect(30 - 4, -10 - fl, 34, 60 + fl, 16), skin, w=4)
    shape(cv, smooth([(-62, 50), (-90, 20), (-78, -6), (-50, 20)]), skin, w=4)
    cv.restore()


def thumb_icon(cv, x, y, s=1.0, down=False, q=True):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, -s if down else s)
    shape(cv, rrect(-40, -20, 80, 80, 24), "#e9b991", w=4)
    shape(cv, rrect(-14, -90, 30, 84, 14), "#e9b991", w=4)
    for k in range(3):
        cv.drawLine(-36, 4 + k * 18, 30, 4 + k * 18, stroke(OUT, 2.4))
    cv.restore()
    if q:
        text(cv, "?", x + 70 * s, y - 30 * s, font("slab", 90 * s), "#ffd23a", oc=OUT, ow=5)


def skull_holes(cv, x, y, s=1.0, holes=0.0, a=255):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    sk = smooth([(-110, 30), (-124, -70), (-80, -150), (0, -176), (80, -150), (124, -70), (110, 30), (70, 60),
                 (40, 96), (-40, 96), (-70, 60)], tension=0.5)
    cv.drawPath(sk, lin_grad((-100, -170), (100, 90), ["#f6efdc", "#e0d4b4", "#b8a880"]))
    cv.drawPath(sk, stroke(OUT, 6, a))
    for sx in (-1, 1):
        shape(cv, ellipse(sx * 46, -10, 32, 36), "#2a1a12", w=4)
    shape(cv, poly([(0, 30), (-16, 60), (16, 60)]), "#2a1a12", w=3)
    for k in range(5):
        cv.drawLine(-40 + k * 20, 80, -40 + k * 20, 100, stroke(OUT, 3))
    cv.drawLine(-80, -120, -20, -80, stroke(shade("#b8a880", 0.8), 3))
    if holes > 0:
        for k in range(3):
            hs = clamp((holes - k * 0.15) / 0.3)
            if hs > 0:
                hx, hy = -50 + k * 50, -120 + (abs(k - 1)) * 8
                cv.drawPath(circle(hx, hy, 11 * hs), fill("#1a0e08"))
                cv.drawPath(circle(hx, hy, 14 * hs), stroke("#8a6a3a", 3))
    cv.restore()


def stele(cv, x, y, s=1.0, relief=None, lines=4, col="#d8ccb0", title=None):
    """mezar tasi: ustte alinlik, ortada kabartma, altta yazi satirlari"""
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    body = rrect(-180, -620, 360, 620, 10)
    cv.drawPath(rrect(-170, -606, 360, 620, 10), fill((0, 0, 0), 90))
    cv.drawPath(body, lin_grad((-180, 0), (180, 0), [shade(col, 0.85), shade(col, 1.08), shade(col, 0.9)]))
    cv.drawPath(body, stroke(OUT, 5))
    shape(cv, poly([(-200, -620), (0, -720), (200, -620)]), col, w=5)
    cv.drawPath(circle(0, -650, 22), stroke(shade(col, 0.7), 4))
    shape(cv, rrect(-150, -580, 300, 330, 6), shade(col, 0.88), w=3)
    if relief:
        cv.save()
        cv.clipPath(rrect(-150, -580, 300, 330, 6), skia.ClipOp.kIntersect, True)
        stone_layer(cv, lambda c: relief(c), col)
        cv.restore()
    for k in range(lines):
        yy = -200 + k * 40
        cv.drawLine(-130, yy, 130 - (k == lines - 1) * 80, yy, stroke(shade(col, 0.55), 5))
    if title:
        text(cv, title, 0, -210 - 6, font("bold", 30), shade(col, 0.45))
    cv.restore()


def stone_layer(cv, drawfn, col="#d8ccb0"):
    """cizimi tas kabartma rengine boyar (gri ton + golge)"""
    r, g, b = int(col[1:3], 16) / 255, int(col[3:5], 16) / 255, int(col[5:7], 16) / 255
    m = [0.30 * r, 0.55 * r, 0.12 * r, 0, 0.05 * r * 0,
         0.30 * g, 0.55 * g, 0.12 * g, 0, 0,
         0.30 * b, 0.55 * b, 0.12 * b, 0, 0,
         0, 0, 0, 1, 0]
    sh = skia.Paint()
    sh.setColorFilter(skia.ColorFilters.Blend(rgb("#3a3020", 150), skia.BlendMode.kSrcIn))
    cv.save()
    cv.translate(5, 6)
    cv.saveLayer(None, sh)
    drawfn(cv)
    cv.restore()
    cv.restore()
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Matrix(m))
    cv.saveLayer(None, p)
    drawfn(cv)
    cv.restore()


def lying(cv, name, x, y, s, t, ang=-90, seed=0, **kw):
    """yere uzanmis karakter (ayaklar x,y'de; ang ile doner)"""
    cv.save()
    cv.translate(x, y)
    cv.rotate(ang)
    c = C.preset(name, **{k: kw.pop(k) for k in list(kw) if k in C.preset(name) and k != "expr"})
    kw.setdefault("blink", E.blink(t, seed))
    C.draw_person(cv, c, C.pose(**kw), 0, 0, s, 1)
    cv.restore()


def arrow_line(cv, x0, y0, x1, y1, t, t0, dur=0.5, col="#c8202a", w=12):
    f = ease_in_out(clamp((t - t0) / dur))
    if f <= 0:
        return
    xe, ye = lerp(x0, x1, f), lerp(y0, y1, f)
    cv.drawLine(x0, y0, xe, ye, stroke(OUT, w + 6))
    cv.drawLine(x0, y0, xe, ye, stroke(col, w))
    ang = math.atan2(ye - y0, xe - x0)
    tri = poly([(xe + math.cos(ang) * 26, ye + math.sin(ang) * 26),
                (xe + math.cos(ang + 2.4) * 24, ye + math.sin(ang + 2.4) * 24),
                (xe + math.cos(ang - 2.4) * 24, ye + math.sin(ang - 2.4) * 24)])
    cv.drawPath(tri, fill(col))
    cv.drawPath(tri, stroke(OUT, 3))


def bar(cv, x, y, w, h, frac, col, label, t, t0, vertical=True, val=None):
    f = ease_out(clamp((t - t0) / 0.8)) * frac
    if t < t0:
        return
    if vertical:
        cv.drawPath(rrect(x - w / 2, y - h, w, h, 12), fill("#000000", 40))
        cv.drawPath(rrect(x - w / 2, y - h * f, w, h * f, 12), fill(col))
        cv.drawPath(rrect(x - w / 2, y - h * f, w, h * f, 12), stroke(OUT, 4))
        text(cv, label, x, y + 50, font("black", 36), "#2a1a10")
        if val:
            text(cv, val, x, y - h * f - 20, font("slab", 44), "#2a1a10")
    else:
        cv.drawPath(rrect(x, y - h / 2, w, h, 12), fill("#000000", 40))
        cv.drawPath(rrect(x, y - h / 2, w * f, h, 12), fill(col))
        cv.drawPath(rrect(x, y - h / 2, w * f, h, 12), stroke(OUT, 4))
        text(cv, label, x - 24, y + 14, font("black", 38), "#2a1a10", align="right")


def coins_pile(cv, x, y, n, t, t0, s=1.0, seed=0):
    import scenery as S
    r = random.Random(seed)
    for k in range(n):
        tt = t - t0 - k * 0.06
        if tt < 0:
            break
        fy = min(1.0, tt / 0.35)
        cx = x + r.uniform(-60, 60) * s
        cy = y - k * 7 * s
        yy = lerp(cy - 300, cy, ease_out(fy))
        S.coin(cv, cx, yy, 22 * s)


def sweat_drops(cv, x, y, t, s=1.0):
    for k in range(3):
        ph = (t * 1.5 + k * 0.33) % 1.0
        dx = (k - 1) * 40 * s
        yy = y + ph * 60 * s
        shape(cv, smooth([(x + dx, yy - 12 * s), (x + dx + 7 * s, yy + 4 * s), (x + dx, yy + 10 * s),
                          (x + dx - 7 * s, yy + 4 * s)]), "#9fd4ff", w=2, a=int(255 * (1 - ph)))


def chains(cv, x0, y0, x1, y1, s=1.0):
    n = int(math.hypot(x1 - x0, y1 - y0) / (22 * s)) + 1
    for k in range(n):
        f = k / max(n - 1, 1)
        x, y = lerp(x0, x1, f), lerp(y0, y1, f) + math.sin(f * math.pi) * 30 * s
        if k % 2:
            cv.drawPath(ellipse(x, y, 13 * s, 8 * s), stroke(OUT, 7 * s))
            cv.drawPath(ellipse(x, y, 13 * s, 8 * s), stroke("#8a8a90", 4 * s))
        else:
            cv.drawPath(ellipse(x, y, 7 * s, 12 * s), stroke(OUT, 7 * s))
            cv.drawPath(ellipse(x, y, 7 * s, 12 * s), stroke("#8a8a90", 4 * s))


def hearts(cv, t, t0, x, y, n=6, seed=0):
    r = random.Random(seed)
    for k in range(n):
        tt = t - t0 - k * 0.2
        if tt < 0 or tt > 2.2:
            continue
        hx = x + r.uniform(-260, 260) + math.sin(tt * 3 + k) * 20
        hy = y - tt * 160
        a = int(255 * (1 - tt / 2.2))
        s = r.uniform(0.7, 1.2)
        hp = skia.Path()
        hp.moveTo(hx, hy + 22 * s)
        hp.cubicTo(hx - 40 * s, hy - 6 * s, hx - 18 * s, hy - 34 * s, hx, hy - 14 * s)
        hp.cubicTo(hx + 18 * s, hy - 34 * s, hx + 40 * s, hy - 6 * s, hx, hy + 22 * s)
        cv.drawPath(hp, fill("#e0304a", a))
        cv.drawPath(hp, stroke(OUT, 3, a))

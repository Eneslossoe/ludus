"""Sahne motoru: kamera, onbellekler, kalabalik ordular, ortak katmanlar."""
import math
import random

import skia

import characters as ch
from gfx import (OUT, W, H, SAMPLING, big_number, clamp, draw_image, ease_in_out, ease_out, fill, font, lerp,
                 lin_grad, pop, rad_grad, rgb, ribbon, rrect, shade, stroke, text, label_tag, vignette, wrap_lines,
                 blur_paint, circle, poly)

BG_SCALE = 1.5
_bg = {}
_spr = {}


# ------------------------------------------------------------------ kamera
def camera(cv, t, d, z0=1.0, z1=1.08, c0=(960, 540), c1=None, ease=True):
    c1 = c1 or c0
    f = ease_in_out(t / max(d, 1e-6)) if ease else clamp(t / max(d, 1e-6))
    z = lerp(z0, z1, f)
    cx, cy = lerp(c0[0], c1[0], f), lerp(c0[1], c1[1], f)
    if z >= 1.0:
        hw, hh = W / (2 * z), H / (2 * z)
        cx = min(max(cx, hw), W - hw)
        cy = min(max(cy, hh), H - hh)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-cx, -cy)
    return z


def shake(cv, t, amp=8.0, freq=23.0):
    if amp <= 0:
        return
    cv.translate(math.sin(t * freq) * amp, math.cos(t * freq * 1.3) * amp * 0.7)


# ------------------------------------------------------------------ arka plan onbellegi
def bg(key, fn, w=W, h=H):
    if key not in _bg:
        s = skia.Surface(int(w * BG_SCALE), int(h * BG_SCALE))
        c = s.getCanvas()
        c.scale(BG_SCALE, BG_SCALE)
        fn(c)
        _bg[key] = s.makeImageSnapshot()
    return _bg[key]


def draw_bg(cv, key, fn, x=0, y=0, w=W, h=H):
    img = bg(key, fn, w, h)
    draw_image(cv, img, x, y, w, h)


# ------------------------------------------------------------------ sprite onbellegi
def person_sprite(name, facing=1, expr="neutral", scale=0.5, seed=0, **kw):
    key = ("p", name, facing, expr, round(scale, 3), seed, tuple(sorted(kw.items())))
    if key not in _spr:
        c = ch.preset(name, **kw)
        r = random.Random(seed)
        ps = ch.pose(expr=expr, look=(0.4 * facing * 0 + 0.4, 0), arm_b=r.uniform(8, 24),
                     wpn=r.uniform(0, 16), arm_a=r.uniform(10, 20))
        sc = scale * 2  # 2x cozunurluk
        wpx, hpx = int(420 * sc), int(560 * sc)
        s = skia.Surface(max(wpx, 4), max(hpx, 4))
        cv = s.getCanvas()
        cv.clear(skia.ColorTRANSPARENT)
        ch.draw_person(cv, c, ps, x=wpx / 2, y=hpx - 40 * sc, scale=sc, facing=facing)
        _spr[key] = (s.makeImageSnapshot(), wpx / 2, hpx - 40 * sc)
    return _spr[key]


def horse_sprite(rider_name, facing=1, scale=0.5, color="#7a4a2a", armored=False, phase=0.0, gallop=1.0,
                 expr="shout"):
    key = ("h", rider_name, facing, round(scale, 3), color, armored, round(phase, 2), gallop, expr)
    if key not in _spr:
        sc = scale * 2
        wpx, hpx = int(760 * sc), int(640 * sc)
        s = skia.Surface(max(wpx, 4), max(hpx, 4))
        cv = s.getCanvas()
        cv.clear(skia.ColorTRANSPARENT)
        rider = ch.preset(rider_name) if rider_name else None
        ch.draw_horse(cv, wpx / 2, hpx - 30 * sc, sc, facing, phase=phase, gallop=gallop, color=color,
                      armored=armored, rider=rider, rider_pose=ch.pose(expr=expr, arm_b=60, wpn=60))
        _spr[key] = (s.makeImageSnapshot(), wpx / 2, hpx - 30 * sc)
    return _spr[key]


def blit(cv, spr, x, y, a=255, sx=1.0):
    img, ox, oy = spr
    w, h = img.width() / 2 * sx, img.height() / 2 * sx
    draw_image(cv, img, x - ox / 2 * sx, y - oy / 2 * sx, w, h, a)


# ------------------------------------------------------------------ ordular
MUSLIM_MIX = ["arab_soldier", "arab_soldier2", "zeyd", "arab_archer", "arab_soldier"]
ROMAN_MIX = ["roman", "roman", "roman_archer", "roman", "armenian_archer"]


def army(cv, t, rows, facing=1, mix=None, march=0.0, charge=0.0, seed=1, bob=True, expr="neutral", jitter=1.0,
         alpha=255):
    """rows: [(y, scale, x0, x1, spacing)] arkadan one sirala.
    march: yuruyus hizi (px/sn), charge: x ofseti"""
    mix = mix or MUSLIM_MIX
    r = random.Random(seed)
    for (y, sc, x0, x1, sp) in rows:
        x = x0
        i = 0
        while x < x1:
            name = mix[r.randrange(len(mix))]
            vseed = r.randrange(3)
            spr = person_sprite(name, facing, expr, sc, seed=vseed)
            ph = r.uniform(0, 6.28)
            by = -abs(math.sin(t * 6 + ph)) * 6 * sc if (march or charge) else math.sin(t * 2 + ph) * 2 * sc
            xx = x + r.uniform(-8, 8) * jitter * sc + march * t * facing + charge * facing
            blit(cv, spr, xx, y + by + r.uniform(-4, 4) * sc, a=alpha)
            x += sp * r.uniform(0.85, 1.15)
            i += 1


def cavalry(cv, t, rows, facing=1, rider="arab_soldier", color_mix=("#7a4a2a", "#5a3a22", "#a07850", "#e8e0d4"),
            armored=False, speed=0.0, seed=2, x_off=0.0):
    r = random.Random(seed)
    for (y, sc, x0, x1, sp) in rows:
        x = x0
        while x < x1:
            col = color_mix[r.randrange(len(color_mix))]
            ph0 = r.uniform(0, 6.28)
            phase = (t * 9 + ph0) % 6.283
            phq = round(phase / 6.283 * 8) % 8 * 6.283 / 8
            spr = horse_sprite(rider, facing, sc, col, armored, phq, 1.0 if speed else 0.0)
            blit(cv, spr, x + speed * t * facing + x_off * facing + r.uniform(-10, 10) * sc, y + r.uniform(-6, 6) * sc)
            x += sp * r.uniform(0.85, 1.15)


# ------------------------------------------------------------------ yazi katmanlari
def caption(cv, s, t, t0, t1, y=960, size=52, col="#ffffff", box=True, maxw=1500):
    a = 255
    if t < t0 or t > t1:
        return
    a = int(255 * min(1, (t - t0) / 0.25, (t1 - t) / 0.25))
    f = font("black", size)
    lines = wrap_lines(s, f, maxw)
    lh = size * 1.2
    if box:
        tw = max(f.measureText(l) for l in lines)
        hh = lh * len(lines) + size * 0.6
        cv.drawPath(rrect(W / 2 - tw / 2 - 30, y - hh + size * 0.35, tw + 60, hh, 18), fill((10, 8, 6), int(a * 0.6)))
    for i, l in enumerate(lines):
        yy = y - lh * (len(lines) - 1 - i)
        text(cv, l, W / 2, yy, f, col, oc=OUT, ow=4, a=a, shadow=(3, 4, 0, 120))


def year_stamp(cv, s, t, t0=0.2, x=1700, y=170, size=110, rot=-4):
    sc = pop(t - t0, 0.45)
    if sc <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(sc, sc)
    big_number(cv, s, 0, 0, size, rot=rot)
    cv.restore()


def chapter_card(cv, t, d, num, title, sub=None, bgcol="#2a1a10"):
    """Bolum karti: parsomen + kirmizi serit"""
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H / 2), 1200, ["#f1dfb4", "#d8b97c", "#8a6a3a"]))
    r = random.Random(num)
    for _ in range(140):
        x, y = r.uniform(0, W), r.uniform(0, H)
        cv.drawPath(circle(x, y, r.uniform(2, 10)), fill("#7a5a2a", r.randint(8, 30)))
    # ince cerceve
    cv.drawPath(rrect(60, 60, W - 120, H - 120, 20), stroke("#6a4a22", 6, 160))
    cv.drawPath(rrect(80, 80, W - 160, H - 160, 14), stroke("#6a4a22", 2, 140))
    s1 = pop(t - 0.05, 0.45)
    cv.save()
    cv.translate(W / 2, 400)
    cv.scale(s1, s1)
    f = font("deco", 72)
    roman = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][num]
    text(cv, f"BÖLÜM {roman}", 0, 0, f, "#5a1a10", oc=None, a=255)
    cv.restore()
    s2 = pop(t - 0.25, 0.5)
    if s2 > 0:
        cv.save()
        cv.translate(W / 2, 560)
        cv.scale(s2, s2)
        ribbon(cv, title, 0, 0, size=78, rot=-1.5, maxw=1600)
        cv.restore()
    if sub:
        a = int(255 * clamp((t - 0.6) / 0.4))
        text(cv, sub, W / 2, 720, font("xb", 44), "#4a2a14", a=a)
    vignette(cv, 120)


def lower_third(cv, s, t, t0, t1, x=120, y=930, size=46, col="#c8202a"):
    a = clamp(min((t - t0) / 0.3, (t1 - t) / 0.3))
    if a <= 0:
        return
    f = font("black", size)
    tw = f.measureText(s)
    slide = (1 - ease_out(clamp((t - t0) / 0.4))) * -60
    cv.save()
    cv.translate(slide, 0)
    cv.drawPath(rrect(x, y - size * 1.05, tw + 60, size * 1.5, 10), fill(col, int(230 * a)))
    cv.drawPath(rrect(x, y - size * 1.05, tw + 60, size * 1.5, 10), stroke(OUT, 4, int(255 * a)))
    text(cv, s, x + 30, y, f, "#ffffff", align="left", a=int(255 * a), shadow=(2, 3, 0, 120))
    cv.restore()


def icon_card(cv, x, y, w, h, title, drawfn, t, t0, col="#fbf3df", tcol="#2a1a10", tsize=40):
    s = pop(t - t0, 0.4)
    if s <= 0:
        return
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.rotate((1 - s) * -8)
    cv.drawPath(rrect(-w / 2 + 6, -h / 2 + 8, w, h, 24), fill((0, 0, 0), 80))
    cv.drawPath(rrect(-w / 2, -h / 2, w, h, 24), fill(col))
    cv.drawPath(rrect(-w / 2, -h / 2, w, h, 24), stroke(OUT, 5))
    cv.save()
    cv.translate(0, -h * 0.08)
    drawfn(cv)
    cv.restore()
    f = font("black", tsize)
    while f.measureText(title) > w - 30 and tsize > 20:
        tsize -= 2
        f = font("black", tsize)
    text(cv, title, 0, h / 2 - tsize * 0.6, f, tcol)
    cv.restore()


def cross_out(cv, x0, y0, x1, y1, t, t0, col="#d01818", w=14):
    f = clamp((t - t0) / 0.3)
    if f <= 0:
        return
    for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x0, y1, x1, y0)):
        cv.drawLine(ax, ay, ax + (bx - ax) * f, ay + (by - ay) * f, stroke(OUT, w + 6))
        cv.drawLine(ax, ay, ax + (bx - ax) * f, ay + (by - ay) * f, stroke(col, w))


def check_mark(cv, x, y, s, t, t0, col="#2a9a3a"):
    f = clamp((t - t0) / 0.3)
    if f <= 0:
        return
    pts = [(x - 30 * s, y), (x - 8 * s, y + 24 * s), (x + 36 * s, y - 30 * s)]
    p = skia.Path()
    p.moveTo(*pts[0])
    if f < 0.4:
        g = f / 0.4
        p.lineTo(pts[0][0] + (pts[1][0] - pts[0][0]) * g, pts[0][1] + (pts[1][1] - pts[0][1]) * g)
    else:
        p.lineTo(*pts[1])
        g = (f - 0.4) / 0.6
        p.lineTo(pts[1][0] + (pts[2][0] - pts[1][0]) * g, pts[1][1] + (pts[2][1] - pts[1][1]) * g)
    cv.drawPath(p, stroke(OUT, 16 * s))
    cv.drawPath(p, stroke(col, 10 * s))


def quote_card(cv, s, who, t, t0, y=880, size=46):
    a = clamp((t - t0) / 0.35)
    if a <= 0:
        return
    f = font("xb", size)
    lines = wrap_lines("“" + s + "”", f, 1400)
    lh = size * 1.25
    hh = lh * len(lines) + size * 1.6
    top = y - hh
    cv.drawPath(rrect(W / 2 - 760, top, 1520, hh + 20, 22), fill("#1a120c", int(200 * a)))
    cv.drawPath(rrect(W / 2 - 760, top, 1520, hh + 20, 22), stroke("#d9a83a", 4, int(255 * a)))
    for i, l in enumerate(lines):
        text(cv, l, W / 2, top + size * 1.1 + lh * i, f, "#fff4d6", a=int(255 * a))
    text(cv, "— " + who, W / 2 + 600, top + hh, font("bold", 34), "#d9a83a", align="right", a=int(255 * a))


def line_t(p, i):
    """anlatim satiri i'nin sahne ici (baslangic, bitis) zamani"""
    ls = p.get("_lines", [])
    if not ls:
        return (0.0, p.get("_dur", 5.0))
    i = max(0, min(i, len(ls) - 1))
    return ls[i]


def talking(t, p, speaker_lines=None):
    """anlatici konusurken agiz hareketi icin 0..1"""
    for k, (a, b) in enumerate(p.get("_lines", [])):
        if speaker_lines is not None and k not in speaker_lines:
            continue
        if a <= t <= b:
            return 0.5 + 0.5 * math.sin(t * 22) * math.sin(t * 7.3)
    return 0.0


def blink(t, seed=0):
    ph = (t + seed * 1.37) % 3.7
    return 1.0 if ph < 0.12 else 0.0

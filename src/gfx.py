"""Temel cizim yardimcilari (skia tabanli).

Tum gorseller bu dosyadaki ilkel fonksiyonlarla kodla uretilir.
"""
import math
import os
import random

import numpy as np
import skia

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

W, H = 1920, 1080
FPS = 30

OUT = (40, 26, 18)          # karakter kontur rengi
OUTW = 4.0


# ---------------------------------------------------------------- renk
def rgb(c, a=255):
    """'#rrggbb' veya (r,g,b[,a]) -> skia Color int"""
    if isinstance(c, str):
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        if len(c) == 8:
            a = int(c[6:8], 16)
    elif len(c) == 4:
        r, g, b, a = c
    else:
        r, g, b = c
    return skia.Color(int(r), int(g), int(b), int(max(0, min(255, a))))


def tup(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        if len(c) == 3:
            c = "".join(ch * 2 for ch in c)
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    return tuple(c[:3])


def shade(c, f):
    """f<1 koyulastir, f>1 acar"""
    r, g, b = tup(c)
    if f < 1:
        return (int(r * f), int(g * f), int(b * f))
    k = f - 1
    return (int(r + (255 - r) * k), int(g + (255 - g) * k), int(b + (255 - b) * k))


def mix(c1, c2, t):
    a, b = tup(c1), tup(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------------------------------------------------------------- boya
def fill(c, a=255):
    return skia.Paint(Color=rgb(c, a), AntiAlias=True, Style=skia.Paint.kFill_Style)


def stroke(c, w, a=255, cap="round"):
    p = skia.Paint(Color=rgb(c, a), AntiAlias=True, Style=skia.Paint.kStroke_Style,
                   StrokeWidth=w)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
    return p


def blur_paint(c, sigma, a=255):
    p = fill(c, a)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


def lin_grad(p0, p1, colors, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear(
        points=[skia.Point(*p0), skia.Point(*p1)],
        colors=[rgb(c) if not isinstance(c, int) else c for c in colors],
        positions=pos))
    return p


def rad_grad(center, r, colors, pos=None):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(
        center=skia.Point(*center), radius=r,
        colors=[rgb(c) if not isinstance(c, int) else c for c in colors],
        positions=pos))
    return p


# ---------------------------------------------------------------- yollar
def P():
    return skia.Path()


def ellipse(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def circle(cx, cy, r):
    return ellipse(cx, cy, r, r)


def rrect(x, y, w, h, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r))
    return p


def poly(pts, closed=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if closed:
        p.close()
    return p


def smooth(pts, closed=True, tension=0.5):
    """Catmull-Rom -> kubik bezier ile yumusak yol"""
    n = len(pts)
    p = skia.Path()
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[(i + 1) % n]
        t = tension / 3.0 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 2, p1[1] + (p2[1] - p0[1]) * t / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 2, p2[1] - (p3[1] - p1[1]) * t / 2)
        p.cubicTo(*c1, *c2, *p2)
    if closed:
        p.close()
    return p


def shape(cv, path, fc, oc=OUT, w=OUTW, a=255):
    if fc is not None:
        cv.drawPath(path, fill(fc, a))
    if oc is not None and w > 0:
        cv.drawPath(path, stroke(oc, w, a))


def line(cv, x0, y0, x1, y1, c, w, a=255):
    cv.drawLine(x0, y0, x1, y1, stroke(c, w, a))


def capsule(cv, x0, y0, x1, y1, w, fc, oc=OUT, ow=OUTW):
    """kalin yuvarlak uclu cubuk (kol, bacak)"""
    if oc is not None:
        cv.drawLine(x0, y0, x1, y1, stroke(oc, w + ow * 2))
    cv.drawLine(x0, y0, x1, y1, stroke(fc, w))


# ---------------------------------------------------------------- yazi
_fonts = {}
FONT_FILES = {
    "slab": "AlfaSlabOne-Regular.ttf",
    "black": "Inter-Black.otf",
    "xb": "Inter-ExtraBold.otf",
    "bold": "Inter-Bold.otf",
    "deco": "CinzelDecorative-Black.ttf",
    "bevan": "Bevan-Regular.ttf",
}


def font(name, size):
    if name not in _fonts:
        _fonts[name] = skia.Typeface.MakeFromFile(os.path.join(FONT_DIR, FONT_FILES[name]))
    f = skia.Font(_fonts[name], size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    f.setSubpixel(True)
    return f


def text_w(s, f):
    return f.measureText(s)


def text(cv, s, x, y, f, c="#ffffff", align="center", oc=None, ow=0, shadow=None, a=255,
         grad=None):
    """y = taban cizgisi. shadow=(dx,dy,sigma,alpha)"""
    w = f.measureText(s)
    if align == "center":
        x0 = x - w / 2
    elif align == "right":
        x0 = x - w
    else:
        x0 = x
    blob = skia.TextBlob.MakeFromString(s, f)
    if shadow:
        dx, dy, sg, sa = shadow
        sp = fill((0, 0, 0), sa * a / 255)
        if sg > 0:
            sp.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sg))
        if oc is not None and ow > 0:
            p2 = stroke((0, 0, 0), ow * 2, sa * a / 255)
            if sg > 0:
                p2.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sg))
            cv.drawTextBlob(blob, x0 + dx, y + dy, p2)
        cv.drawTextBlob(blob, x0 + dx, y + dy, sp)
    if oc is not None and ow > 0:
        cv.drawTextBlob(blob, x0, y, stroke(oc, ow * 2, a))
    if grad is not None:
        gp = lin_grad((0, y - f.getSize() * 0.75), (0, y + f.getSize() * 0.05), grad)
        gp.setAlphaf(a / 255)
        cv.drawTextBlob(blob, x0, y, gp)
    else:
        cv.drawTextBlob(blob, x0, y, fill(c, a))
    return w


def wrap_lines(s, f, maxw):
    words = s.split()
    lines, cur = [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if f.measureText(t) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def pop(t, dur=0.35):
    """0'dan 1'e zıplayarak gelen olcek"""
    if t <= 0:
        return 0.0
    if t >= dur:
        return 1.0
    return ease_out_back(t / dur, 2.2)


def fade_window(t, t0, t1, fin=0.3, fout=0.3):
    if t < t0 or t > t1:
        return 0.0
    a = 1.0
    if fin > 0:
        a = min(a, (t - t0) / fin)
    if fout > 0:
        a = min(a, (t1 - t) / fout)
    return clamp(a)


def noise1(x, seed=0):
    """basit 1B deger gurultusu (yumusak)"""
    i = math.floor(x)
    f = x - i

    def h(n):
        n = (n * 374761393 + seed * 668265263) & 0xFFFFFFFF
        n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0

    u = f * f * (3 - 2 * f)
    return h(i) * (1 - u) + h(i + 1) * u


# ---------------------------------------------------------------- yuzey
def new_surface(w=W, h=H):
    return skia.Surface(w, h)


def snapshot(surface):
    return surface.makeImageSnapshot()


SAMPLING = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def draw_image(cv, img, x, y, w=None, h=None, a=255):
    if w is None:
        w, h = img.width(), img.height()
    p = skia.Paint(AntiAlias=True)
    if a < 255:
        p.setAlphaf(a / 255)
    cv.drawImageRect(img, skia.Rect.MakeXYWH(x, y, w, h), SAMPLING, p)


def make_sprite(draw_fn, w, h, ox, oy, scale=1.0):
    """draw_fn(canvas) yerel koordinatlarda cizer; (ox,oy) yerel orijinin sprite icindeki yeri"""
    s = skia.Surface(int(w), int(h))
    cv = s.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    cv.translate(ox, oy)
    cv.scale(scale, scale)
    draw_fn(cv)
    return s.makeImageSnapshot()


# ---------------------------------------------------------------- ortak grafik ogeleri
def label_tag(cv, s, x, y, size=34, rot=-4, bg="#fbf6ea", fg="#2a1a10", a=255):
    """Kanal stilindeki kucuk beyaz isim etiketi"""
    f = font("black", size)
    tw = f.measureText(s)
    pw, ph = tw + size * 0.9, size * 1.35
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    path = rrect(-pw / 2, -ph / 2, pw, ph, size * 0.25)
    sh = rrect(-pw / 2 + 4, -ph / 2 + 5, pw, ph, size * 0.25)
    cv.drawPath(sh, fill((0, 0, 0), 90 * a / 255))
    cv.drawPath(path, fill(bg, a))
    cv.drawPath(path, stroke(OUT, max(3, size * 0.1), a))
    text(cv, s, 0, size * 0.36, f, fg, a=a)
    cv.restore()


def ribbon(cv, s, x, y, size=46, color="#c8202a", fg="#ffffff", rot=-2, a=255, maxw=None):
    """kanal kucuk resimlerindeki kirmizi serit"""
    f = font("black", size)
    tw = f.measureText(s)
    if maxw and tw + size * 1.6 > maxw:
        f = font("black", size * maxw / (tw + size * 1.6))
        size = f.getSize()
        tw = f.measureText(s)
    pw, ph = tw + size * 1.3, size * 1.45
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    dark = shade(color, 0.6)
    # kuyruklar
    for sgn in (-1, 1):
        tail = poly([(sgn * pw / 2 - sgn * 10, -ph / 2 + 14), (sgn * (pw / 2 + ph * 0.55), -ph / 2 + 14),
                     (sgn * (pw / 2 + ph * 0.3), ph / 2 * 0.45 + 14), (sgn * (pw / 2 + ph * 0.55), ph / 2 + 14),
                     (sgn * pw / 2 - sgn * 10, ph / 2 + 14)])
        cv.drawPath(tail, fill(dark, a))
        cv.drawPath(tail, stroke(OUT, 4, a))
    body = poly([(-pw / 2, -ph / 2), (pw / 2, -ph / 2), (pw / 2, ph / 2), (-pw / 2, ph / 2)])
    cv.drawPath(rrect(-pw / 2 + 5, -ph / 2 + 7, pw, ph, 4), fill((0, 0, 0), 80 * a / 255))
    cv.drawPath(body, lin_grad((0, -ph / 2), (0, ph / 2), [shade(color, 1.15), color, shade(color, 0.85)]))
    cv.drawPath(body, stroke(OUT, 4.5, a))
    cv.drawLine(-pw / 2 + 8, -ph / 2 + 8, pw / 2 - 8, -ph / 2 + 8, stroke(shade(color, 1.4), 3, 140 * a / 255))
    text(cv, s, 0, size * 0.37, f, fg, a=a, shadow=(2, 3, 0, 120))
    cv.restore()


def big_number(cv, s, x, y, size=200, a=255, rot=0):
    """altin renkli kalin rakam (kanal stili)"""
    f = font("slab", size)
    cv.save()
    cv.translate(x, y)
    cv.rotate(rot)
    text(cv, s, 0, 0, f, oc=OUT, ow=size * 0.07, a=a, shadow=(6, 10, 4, 140),
         grad=["#fff3b0", "#f6c64a", "#c9851e"])
    cv.restore()


def vignette(cv, strength=160, w=W, h=H):
    p = rad_grad((w / 2, h / 2), math.hypot(w, h) * 0.62,
                 [rgb((0, 0, 0), 0), rgb((0, 0, 0), 0), rgb((0, 0, 0), strength)], [0, 0.55, 1])
    cv.drawRect(skia.Rect.MakeWH(w, h), p)


def tint(cv, c, a, w=W, h=H, mode=None):
    p = fill(c, a)
    if mode:
        p.setBlendMode(mode)
    cv.drawRect(skia.Rect.MakeWH(w, h), p)


def speech_bubble(cv, s, x, y, tail_x, tail_y, maxw=560, size=36, a=255, fg="#2a1a10", bg="#fffdf6"):
    f = font("xb", size)
    lines = wrap_lines(s, f, maxw)
    lh = size * 1.25
    tw = max(f.measureText(l) for l in lines)
    pw, ph = tw + size * 1.4, lh * len(lines) + size * 0.9
    bx, by = x - pw / 2, y - ph / 2
    body = rrect(bx, by, pw, ph, size * 0.8)
    tail = poly([(x - pw * 0.12, y + ph / 2 - 4), (tail_x, tail_y), (x + pw * 0.06, y + ph / 2 - 4)])
    path = skia.Op(body, tail, skia.PathOp.kUnion_PathOp)
    cv.save()
    cv.translate(5, 7)
    cv.drawPath(path, fill((0, 0, 0), 70 * a / 255))
    cv.restore()
    cv.drawPath(path, fill(bg, a))
    cv.drawPath(path, stroke(OUT, 4.5, a))
    for i, l in enumerate(lines):
        text(cv, l, x, by + size * 0.45 + lh * (i + 0.8), f, fg, a=a)


def rng(seed):
    return random.Random(seed)

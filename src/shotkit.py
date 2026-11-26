"""Sahne yazarken kullanilan kisa yardimcilar."""
import math

import skia

import backgrounds as B
import characters as C
import engine as E
from gfx import clamp, lerp, ease_in_out, W, H


def bgk(cv, key, fn, *a, **k):
    E.draw_bg(cv, key, lambda c: fn(c, *a, **k))


_PKEYS = set(C.preset("demetrios").keys())


def person(cv, name, x, y, s=1.0, f=1, t=0.0, seed=0, talk=0.0, breathe=True, **kw):
    over = {k: kw.pop(k) for k in list(kw) if k in _PKEYS and k != "expr"}
    c = C.preset(name, **over) if isinstance(name, str) else dict(name, **over)
    ps = C.pose(**kw)
    if "blink" not in kw:
        ps["blink"] = E.blink(t, seed)
    ps["mouth"] = max(ps.get("mouth", 0.0), talk)
    if breathe and "bob" not in kw:
        ps["bob"] = math.sin(t * 2.2 + seed) * 1.6
    C.draw_person(cv, c, ps, x, y, s, f)


def walk_x(t, t0, t1, x0, x1):
    f = clamp((t - t0) / max(t1 - t0, 1e-6))
    moving = 0 < f < 1
    return lerp(x0, x1, f), moving


def lt(p, i):
    return E.line_t(p, i)[0]


def le(p, i):
    return E.line_t(p, i)[1]


def lf(p, i, frac):
    a, b = E.line_t(p, i)
    return a + (b - a) * frac


def nlines(p):
    return len(p.get("_lines", []))


def talk_on(t, p, idx):
    """belirli satirlar sirasinda agiz hareketi"""
    for k in idx:
        a, b = E.line_t(p, k)
        if a <= t <= b:
            return 0.45 + 0.45 * math.sin(t * 21) * math.sin(t * 6.7 + 1)
    return 0.0


def xfade_layers(cv, t, t_switch, dur, draw_a, draw_b):
    """iki gorunum arasinda gecis (t_switch etrafinda)"""
    f = clamp((t - t_switch) / dur)
    if f <= 0:
        draw_a(cv)
    elif f >= 1:
        draw_b(cv)
    else:
        draw_a(cv)
        cv.saveLayerAlpha(None, int(255 * f))
        draw_b(cv)
        cv.restore()


def phase(t, p, i):
    """t satir i baslangicindan sonra mi"""
    return t >= lt(p, i)

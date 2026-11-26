"""Tum ses miksaji: anlatim + fon muzigi + efektler + ortam sesleri -> soundtrack.wav"""
import json
import os

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

import music
import synth as Y
from synth import SR, pan, place

WORK = os.environ.get("ZK_WORK", "/home/user/work")


def load_tl():
    with open(os.path.join(WORK, "timeline.json")) as f:
        return json.load(f)


class Shot:
    def __init__(self, s):
        self.s = s
        self.t0 = s["start"]
        self.d = s["dur"]
        self.L = [(l["start"], l["end"]) for l in s["lines"]]

    def lt(self, i):
        return self.L[min(i, len(self.L) - 1)][0] if self.L else 0.0

    def le(self, i):
        return self.L[min(i, len(self.L) - 1)][1] if self.L else self.d

    def lf(self, i, fr):
        a, b = (self.lt(i), self.le(i))
        return a + (b - a) * fr


# ------------------------------------------------------------------ anlatim
def narration(tl, n):
    out = np.zeros((n, 2))
    for s in tl["shots"]:
        for l in s["lines"]:
            a, sr = sf.read(l["wav"], dtype="float32")
            a = resample_poly(a, 320, 147).astype(np.float64)  # 22050 -> 48000
            a = Y.hp(a, 75)
            a = a + Y.bp(a, 2500, 5000) * 0.25 + Y.lp(a, 250) * 0.15
            env = np.sqrt(np.maximum(Y.lp(a ** 2, 8), 0) + 1e-9)
            g = np.minimum(1.0, (0.12 / (env + 1e-9)) ** 0.35)
            a = a * g
            a = a / (np.abs(a).max() + 1e-9) * 0.82
            if l["voice"] == "q":
                a = a * 0.95
            place(out, np.stack([a, a], axis=1), s["start"] + l["start"])
    return Y.reverb(out, 0.06, seconds=0.9, damp=7.0, bright=5000)


def speech_mask(tl, n):
    m = np.zeros(n)
    for s in tl["shots"]:
        for l in s["lines"]:
            a = int((s["start"] + l["start"] - 0.15) * SR)
            b = int((s["start"] + l["end"] + 0.25) * SR)
            m[max(a, 0):min(b, n)] = 1.0
    k = int(0.25 * SR)
    c = np.concatenate([[0.0], np.cumsum(m)])
    idx = np.arange(n)
    lo = np.clip(idx - k // 2, 0, n)
    hi = np.clip(idx + k // 2, 0, n)
    return np.clip((c[hi] - c[lo]) / k, 0, 1)


# ------------------------------------------------------------------ muzik
def soundtrack_music(tl, n):
    segs = []
    cur = None
    for s in tl["shots"]:
        m = s["params"].get("music")
        if m and m != cur:
            segs.append([s["start"], m])
            cur = m
    out = np.zeros((n, 2))
    xf = 1.6
    for i, (t0, m) in enumerate(segs):
        t1 = segs[i + 1][0] if i + 1 < len(segs) else n / SR
        dur = t1 - t0 + xf
        cp = os.path.join(WORK, "music_cache", f"{i:02d}_{m}_{dur:.2f}.npy")
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        if os.path.exists(cp):
            y = np.load(cp)
        else:
            y = music.gen(m, dur, seed=100 + i)
            np.save(cp, y.astype(np.float32))
        L = len(y)
        e = np.ones(L)
        fi = int(0.6 * SR)
        e[:fi] = np.linspace(0, 1, fi)
        fo = int(xf * SR)
        if i + 1 < len(segs):
            e[-fo:] *= np.linspace(1, 0, fo)
        y = y * e[:, None]
        print(f"  muzik {m:12s} {t0:7.2f}s  {dur:6.1f}s", flush=True)
        place(out, y, t0)
    k = int(4 * SR)
    out[-k:] *= np.linspace(1, 0, k)[:, None]
    return out


# ------------------------------------------------------------------ efektler
def cues(tl):
    """(mutlak zaman, stereo ses, kazanc) listesi"""
    C = []
    rng = np.random.default_rng(7)
    S = {s["id"]: Shot(s) for s in tl["shots"]}

    def add(t, x, g=1.0, p=0.0):
        if x.ndim == 1:
            x = pan(x, p)
        C.append((t, x, g))

    def amb(sh, x, g, t0=0.0, t1=None, fade=0.5):
        t1 = sh.d if t1 is None else t1
        if x.ndim == 1:
            x = np.stack([x, x], axis=1)
        L = int((t1 - t0) * SR)
        if L <= 0:
            return
        x = x[:L]
        if len(x) < L:
            x = np.pad(x, ((0, L - len(x)), (0, 0)))
        f = min(int(fade * SR), L // 2)
        e = np.ones(L)
        if f > 0:
            e[:f] = np.linspace(0, 1, f)
            e[-f:] = np.linspace(1, 0, f)
        add(sh.t0 + t0, x * e[:, None], g)

    def pops(sh, times, g=0.55, f=600):
        for k, t in enumerate(times):
            add(sh.t0 + t, Y.ui_pop(1.0, f + k * 60), g)

    def muffled(x):
        return np.stack([Y.lp(x[:, 0], 600), Y.lp(x[:, 1], 600)], axis=1)

    def crowd(sh, g=0.25, t0=0.0, t1=None, seed=0, density=0.6, clashes=False):
        t1 = sh.d if t1 is None else t1
        amb(sh, Y.crowd_roar(t1 - t0, 1.0, seed, shouts=True, clashes=clashes, density=density), g, t0, t1)

    def clacks(sh, g=0.22, t0=0.0, t1=None, seed=0, rate=0.45):
        t1 = sh.d if t1 is None else t1
        r = np.random.default_rng(seed)
        tt = t0 + r.uniform(0, rate)
        while tt < t1:
            add(sh.t0 + tt, Y.wood_clack(r.uniform(0.4, 1.0), int(r.integers(0, 1e6))), g, float(r.uniform(-0.7, 0.7)))
            tt += rate * r.uniform(0.6, 1.4)

    # ---- giris
    sh = S["s01"]
    amb(sh, muffled(Y.crowd_roar(sh.d, 1.0, 1, shouts=True, clashes=False, density=0.8)), 0.45)
    amb(sh, Y.wind(sh.d, 1.0, 2, bright=500), 0.25)
    add(sh.t0 + 0.5, Y.impact(0.6), 0.45)
    add(sh.t0 + 1.0, Y.chain_rattle(0.8, 1.0, 1), 0.4, -0.4)
    hb = sh.lf(2, 0.6)
    k = 0
    while hb + k * 0.85 < sh.d:
        add(sh.t0 + hb + k * 0.85, Y.heartbeat(1.0), 0.55)
        k += 1
    pops(sh, [sh.lf(2, f) for f in (0.08, 0.3, 0.42)])
    sh = S["s02"]
    crowd(sh, 0.28, seed=2)
    pops(sh, [sh.lf(0, 0.16), sh.lf(0, 0.32), sh.lf(0, 0.66), sh.lf(0, 0.82)])
    for fr in (0.16, 0.32):
        add(sh.t0 + sh.lf(0, fr) + 0.35, Y.buzz(1.0), 0.4)
    add(sh.t0 + 1.2, Y.whoosh(0.6, 1.0, 300, 1800, 3), 0.25)
    sh = S["s03"]
    add(sh.t0 + 0.15, Y.impact(0.8), 0.5)
    add(sh.t0 + 0.45, Y.whoosh(0.5, 1.0, 400, 3000, 2), 0.45)
    t2 = sh.lt(1)
    for k in range(int((sh.d - t2) / 0.85)):
        add(sh.t0 + t2 + k * 0.85, Y.heartbeat(1.0), 0.55)
    pops(sh, [t2 + 0.5 + k * 0.18 for k in range(6)], 0.35, 800)
    add(sh.t0 + sh.d - 2.2, Y.riser(2.2), 0.5)
    sh = S["s04"]
    add(sh.t0 + 0.05, Y.impact(1.0), 0.7)
    add(sh.t0 + 0.9, Y.whoosh(0.5, 1.0, 300, 3000, 3), 0.4)
    # ---- bolum 1
    sh = S["s06"]
    t1 = sh.lt(1)
    amb(sh, Y.wind(t1, 1.0, 4), 0.2, 0, t1)
    amb(sh, Y.murmur(t1, 1.0, 5), 0.25, 0, t1)
    pops(sh, [0.3, sh.lf(0, 0.25), sh.lf(0, 0.55), sh.lf(0, 0.7), sh.lf(0, 0.84)])
    add(sh.t0 + sh.lf(0, 0.25) + 0.5, Y.buzz(1.0), 0.4)
    amb(sh, Y.fire(sh.d - t1, 1.0, 1), 0.45, t1, sh.d)
    add(sh.t0 + t1, Y.impact(0.5), 0.35)
    tc = t1 + 0.4
    k = 0
    while tc < sh.d - 0.3:
        add(sh.t0 + tc, Y.sword_clash(0.7, 50 + k), 0.3, (k % 2 - 0.5) * 0.6)
        tc += 0.98
        k += 1
    sh = S["s07"]
    add(sh.t0, Y.paper(1.0, 0.8, 1), 0.5)
    t1, t2 = sh.lt(1), sh.lt(2)
    for tt in (0.9, 2.3, t1):
        add(sh.t0 + tt, Y.whoosh(0.9, 1.0, 300, 1600, int(tt * 10)), 0.3)
    pops(sh, [0.3, 2.0, 2.2, 3.2, 3.4, t1 + 1.1, t1 + 1.3, t1 + 1.8])
    add(sh.t0 + sh.lf(2, 0.3), Y.gasp(1.0, 1), 0.35)
    add(sh.t0 + sh.lf(2, 0.55), Y.murmur(1.6, 1.0, 2), 0.3)
    add(sh.t0 + sh.lf(2, 0.8), Y.crowd_roar(2.0, 1.0, 3, shouts=True, clashes=False, density=2.0), 0.35)
    pops(sh, [sh.lf(2, f) for f in (0.3, 0.55, 0.8)], 0.4, 700)
    sh = S["s08"]
    t1 = sh.lt(1)
    add(sh.t0, Y.paper(1.0, 0.6, 2), 0.4)
    pops(sh, [sh.lf(0, f) for f in (0.42, 0.55, 0.68, 0.82)])
    crowd(sh, 0.25, t1 - 0.3, sh.d, seed=4, clashes=True)
    pops(sh, [t1 + 0.3])
    add(sh.t0 + sh.lf(1, 0.45), Y.impact(0.5), 0.35)
    sh = S["s09"]
    t1 = sh.lt(1)
    amb(sh, Y.murmur(t1 + 0.5, 1.0, 6), 0.25, 0, t1 + 0.5)
    crowd(sh, 0.4, t1 - 0.2, sh.d, seed=7, density=1.5)
    add(sh.t0 + t1, Y.whoosh(0.5, 1.0, 400, 3000, 9), 0.35)
    pops(sh, [t1 + 0.3, t1 + 0.4])
    # ---- bolum 2
    sh = S["s11"]
    t1 = sh.lt(1)
    amb(sh, Y.sea_waves(sh.d, 1.0, 1), 0.5)
    amb(sh, Y.wind(sh.d, 1.0, 8), 0.12)
    amb(sh, Y.steps(2.2, 1.0, 1, 0.42, sand=False), 0.6, t1 - 0.2, t1 + 2.0)
    pops(sh, [0.4, t1 + 1.2, sh.lf(1, 0.6)])
    sh = S["s12"]
    t1 = sh.lt(1)
    amb(sh, Y.steps(1.5, 1.0, 2, 0.5, sand=False), 0.6, sh.lf(0, 0.45), sh.lf(0, 0.75))
    tb = sh.lf(0, 0.62)
    pops(sh, [tb + k * 0.12 for k in range(6)], 0.4, 500)
    add(sh.t0 + tb + 0.4, Y.impact(0.5), 0.35)
    for k in range(3):
        add(sh.t0 + t1 + 0.1 + k * 0.28, Y.thunk(1.0, k), 0.6)
    amb(sh, Y.steps(1.0, 1.0, 3, 0.5, sand=False), 0.5, t1 + 0.2, t1 + 1.2)
    sh = S["s13"]
    pops(sh, [0.3, sh.lf(1, 0.05), sh.lf(1, 0.38), sh.lf(1, 0.72), sh.lf(2, 0.35), sh.lf(2, 0.6)])
    for fr in (0.05, 0.38, 0.72):
        add(sh.t0 + sh.lf(1, fr) + 0.3, Y.chain_rattle(0.6, 1.0, int(fr * 100)), 0.5)
    add(sh.t0 + sh.lf(2, 0.4), Y.ding(1.0), 0.4)
    add(sh.t0 + sh.lf(2, 0.62), Y.coins(6, 1.0, 1, 0.3), 0.5)
    sh = S["s14"]
    add(sh.t0 + 0.2, Y.paper(1.0, 0.6, 3), 0.5)
    pops(sh, [0.2, 0.5, sh.lf(0, 0.18), sh.lf(0, 0.3), sh.lf(0, 0.45)])
    add(sh.t0 + sh.lf(0, 0.72), Y.impact(0.5), 0.35)
    add(sh.t0 + sh.lf(0, 0.75), Y.coins(14, 1.0, 2, 1.0), 0.6)
    sh = S["s15"]
    t1 = sh.lt(1)
    amb(sh, Y.sea_waves(sh.d, 1.0, 2), 0.4)
    amb(sh, Y.steps(1.6, 1.0, 4, 0.55, sand=False), 0.6, 0.2, 1.8)
    pops(sh, [sh.lf(0, 0.35), t1 + 0.2, sh.lf(1, 0.3), sh.lf(1, 0.75)])
    add(sh.t0 + t1 + 0.6, Y.coins(6, 1.0, 3, 0.4), 0.5)
    sh = S["s16"]
    t1, t2 = sh.lt(1), sh.lt(2)
    amb(sh, Y.fire(sh.d, 1.0, 2), 0.55)
    a, b = sh.lt(1), sh.le(1)
    fxs = [Y.whoosh(0.6, 1.0, 200, 1500, 4), Y.chain_rattle(0.8, 1.0, 5), Y.whip_crack(1.0, 6),
           Y.metal_clang(1.0, 7)]
    for k, fr in enumerate((0.02, 0.25, 0.5, 0.72)):
        add(sh.t0 + a + (b - a) * fr, Y.ui_pop(1.0, 500), 0.4)
        add(sh.t0 + a + (b - a) * fr + 0.05, fxs[k], 0.5)
    add(sh.t0 + t1 - 0.1, Y.impact(0.6), 0.4)
    add(sh.t0 + t2 + 0.3, Y.impact(0.8), 0.45)
    pops(sh, [sh.lf(2, 0.5)], 0.5, 400)
    # ---- bolum 3
    sh = S["s18"]
    t1 = sh.lt(1)
    amb(sh, Y.wind(sh.d, 1.0, 10), 0.25)
    amb(sh, Y.steps(sh.d, 1.0, 5, 0.4, sand=False), 0.55)
    pops(sh, [0.6, t1 + 0.3, sh.lf(1, 0.55)])
    sh = S["s19"]
    t1 = sh.lt(1)
    clacks(sh, 0.25, seed=1)
    amb(sh, Y.murmur(sh.d, 1.0, 11), 0.12)
    pops(sh, [0.6, sh.lf(0, 0.55), sh.lf(0, 0.8), sh.lf(1, 0.35)])
    add(sh.t0 + sh.lf(1, 0.6), Y.buzz(1.0), 0.45)
    sh = S["s20"]
    t1 = sh.lt(1)
    amb(sh, Y.crickets(sh.d - t1 + 1.0, 1.0, 1), 0.8, t1 - 1.0, sh.d)
    amb(sh, Y.wind(sh.d, 1.0, 12, bright=400), 0.15)
    pops(sh, [sh.lf(0, f) for f in (0.2, 0.45, 0.62, 0.82)], 0.45)
    sh = S["s21"]
    t1 = sh.lt(1)
    clacks(sh, 0.18, seed=2, rate=0.6)
    pops(sh, [0.4] + [sh.lf(1, f) for f in (0.05, 0.22, 0.4)])
    add(sh.t0 + sh.lf(1, 0.7), Y.impact(0.7), 0.45)
    add(sh.t0 + sh.lf(1, 0.7) - 0.3, Y.whoosh(0.4, 1.0, 400, 3000, 12), 0.35)
    sh = S["s22"]
    pops(sh, [0.3, 0.55, 0.8, sh.lf(1, 0.45)])
    add(sh.t0 + sh.lf(1, 0.45) + 0.2, Y.ding(1.0), 0.4)
    # ---- bolum 4
    sh = S["s24"]
    t1 = sh.lt(1)
    amb(sh, Y.wind(sh.d, 1.0, 13, bright=500), 0.15)
    k = 0
    while t1 + 0.75 * (k + 0.25) < sh.d:
        add(sh.t0 + t1 + 0.75 * (k + 0.25), Y.wood_clack(1.0, k), 0.55)
        add(sh.t0 + t1 + 0.75 * (k + 0.25), Y.thunk(0.6, k), 0.3)
        k += 1
    pops(sh, [sh.lf(0, 0.72), sh.lf(1, 0.08), sh.lf(1, 0.35)])
    sh = S["s25"]
    t1 = sh.lt(1)
    clacks(sh, 0.15, seed=3, rate=0.5)
    k = 0
    while k * 1.6 < t1:
        add(sh.t0 + k * 1.6, Y.whip_crack(1.0, k), 0.5)
        k += 1
    pops(sh, [0.6, 1.2, sh.lf(0, 0.4), sh.lf(1, 0.5)])
    sh = S["s26"]
    pops(sh, [0.3, sh.lf(1, 0.02), sh.lf(1, 0.55), sh.lf(2, 0.02), sh.lf(3, 0.08)])
    for k, tt in enumerate((sh.lf(1, 0.02), sh.lf(1, 0.55), sh.lf(2, 0.02), sh.lf(3, 0.08))):
        add(sh.t0 + tt + 0.05, Y.metal_clang(0.6, 20 + k), 0.25)
    sh = S["s27"]
    a, b = sh.lt(0), sh.le(0)
    pops(sh, [0.3])
    for fr in (0.45, 0.72):
        t0 = a + (b - a) * (fr - 0.25)
        pops(sh, [t0])
        add(sh.t0 + t0 + 0.3, Y.impact(0.5), 0.35)
        add(sh.t0 + t0 + 0.35, Y.sword_clash(0.8, int(fr * 100)), 0.35)
    sh = S["s28"]
    t1 = sh.lt(1)
    tm = sh.lf(0, 0.25)
    add(sh.t0 + tm, Y.whoosh(0.5, 1.0, 1500, 300, 14), 0.4)
    add(sh.t0 + tm + 0.5, Y.metal_clang(1.0, 30), 0.55)
    pops(sh, [sh.lf(0, 0.5)])
    amb(sh, Y.steps(t1 - sh.lf(0, 0.7), 1.0, 6, 0.3), 0.5, sh.lf(0, 0.7), t1)
    add(sh.t0 + t1, Y.whoosh(0.7, 1.0, 200, 2000, 15), 0.4)
    amb(sh, Y.breath(sh.d - t1, 1.0, 0.8, 1), 0.7, t1, sh.d)
    pops(sh, [sh.lf(1, f) for f in (0.12, 0.4, 0.75)])
    # ---- bolum 5
    sh = S["s30"]
    t1 = sh.lt(1)
    amb(sh, Y.fire(sh.d, 1.0, 3), 0.25)
    amb(sh, Y.murmur(sh.d, 1.0, 12), 0.1)
    for k in range(int(sh.d / 1.3)):
        add(sh.t0 + 0.4 + k * 1.3 + rng.uniform(0, 0.4), Y.ding(0.4), 0.12, float(rng.uniform(-0.6, 0.6)))
    tm = sh.lf(0, 0.25)
    pops(sh, [tm, sh.lf(0, 0.55)] + [sh.lf(1, 0.05 + k * 0.12) for k in range(3)] + [sh.lf(1, 0.6)])
    add(sh.t0 + tm + 0.3, Y.buzz(1.0), 0.4)
    sh = S["s31"]
    t1, t2 = sh.lt(1), sh.lt(2)
    amb(sh, Y.wind(t1, 1.0, 14), 0.3, 0, t1)
    add(sh.t0 + 0.5, Y.impact(0.6), 0.4)
    pops(sh, [1.0, t1 + 0.1, t1 + 0.4, t1 + 0.6, sh.lf(1, 0.5), sh.lf(1, 0.8)])
    add(sh.t0 + sh.lf(1, 0.5) + 0.3, Y.ding(1.0), 0.35)
    amb(sh, Y.hiss(sh.d - t2, 1.0, 1), 0.6, t2, sh.d)
    add(sh.t0 + t2 + 0.2, Y.pour(1.2, 1.0, 1), 0.4)
    pops(sh, [t2 + 0.3, sh.lf(2, 0.5)])
    sh = S["s32"]
    t1, t2 = sh.lt(1), sh.lt(2)
    pops(sh, [sh.lf(0, 0.75), sh.lf(1, 0.2), sh.lf(1, 0.65), t2 + 0.2, t2 + 1.4])
    add(sh.t0 + t1 + 0.4, Y.pour(1.4, 1.0, 2), 0.4)
    add(sh.t0 + t2 + 0.5, Y.ding(0.8), 0.3)
    add(sh.t0 + t2 + 0.9, Y.ding(1.0), 0.35)
    sh = S["s33"]
    a, b = sh.lt(0), sh.le(0)
    add(sh.t0 + a + (b - a) * 0.3, Y.coins(18, 1.0, 4, 1.1), 0.6)
    pops(sh, [a + (b - a) * 0.4, a + (b - a) * 0.72])
    add(sh.t0 + a + (b - a) * 0.72 + 0.1, Y.buzz(1.0), 0.45)
    # ---- bolum 6
    sh = S["s35"]
    t1 = sh.lt(1)
    pops(sh, [0.3, sh.lf(0, 0.55), sh.lf(0, 0.7)])
    for k in range(6):
        add(sh.t0 + sh.lf(0, 0.2) + k * 0.2, Y.ding(0.5), 0.15, float(rng.uniform(-0.5, 0.5)))
    amb(sh, Y.scribble(2.8, 1.0, 2), 0.5, t1, t1 + 2.8)
    pops(sh, [t1 + 0.2, sh.lf(1, 0.6)])
    for k in range(8):
        add(sh.t0 + sh.lf(1, 0.6) + 0.3 + k * 0.2, Y.ding(0.5), 0.15, float(rng.uniform(-0.5, 0.5)))
    sh = S["s36"]
    a, b = sh.lt(0), sh.le(0)
    pops(sh, [a + (b - a) * (0.25 + k * 0.15) for k in range(4)])
    add(sh.t0 + a + (b - a) * 0.85, Y.buzz(1.0), 0.4)
    sh = S["s37"]
    a, b = sh.lt(0), sh.le(0)
    amb(sh, Y.wind(sh.d, 1.0, 15, bright=400), 0.2)
    add(sh.t0 + 0.2, Y.stone(1.0, 1), 0.5)
    pops(sh, [a + (b - a) * 0.4, a + (b - a) * 0.75])
    sh = S["s38"]
    t1 = sh.lt(1)
    add(sh.t0 + 0.3, Y.stone(1.0, 2), 0.55)
    pops(sh, [sh.lf(0, 0.35), t1 + 0.6])
    add(sh.t0 + t1 + 0.6, Y.ding(1.0), 0.4)
    # ---- bolum 7
    sh = S["s40"]
    t1 = sh.lt(1)
    amb(sh, Y.murmur(sh.d, 1.0, 16), 0.12)
    amb(sh, Y.scribble(sh.lf(0, 0.95) - sh.lf(0, 0.05), 1.0, 3), 0.6, sh.lf(0, 0.05), sh.lf(0, 0.95))
    for k in range(3):
        pops(sh, [sh.lf(1, 0.05 + k * 0.25)])
    add(sh.t0 + sh.lf(1, 0.05), Y.roar(1.0, 1), 0.45)
    add(sh.t0 + sh.lf(1, 0.55), Y.metal_clang(0.8, 40), 0.3)
    sh = S["s41"]
    t1 = sh.lt(1)
    amb(sh, Y.fire(sh.d, 1.0, 4), 0.35)
    amb(sh, Y.murmur(sh.d, 1.0, 17), 0.22)
    amb(sh, Y.crickets(sh.d, 1.0, 2), 0.4)
    for k in range(int(sh.d / 1.5)):
        add(sh.t0 + 0.5 + k * 1.5 + rng.uniform(0, 0.5), Y.ding(0.5), 0.12, float(rng.uniform(-0.6, 0.6)))
    pops(sh, [0.4, sh.lf(1, 0.05), sh.lf(1, 0.22), sh.lf(1, 0.4), sh.lf(1, 0.55)])
    sh = S["s42"]
    t1 = sh.lt(1)
    crowd(sh, 0.3, seed=18)
    add(sh.t0 + sh.lf(0, 0.1) + 0.3, Y.roar(1.0, 2), 0.4)
    pops(sh, [0.3, sh.lf(0, 0.1), sh.lf(0, 0.55), t1 + 0.3])
    add(sh.t0 + t1 + 0.3, Y.impact(0.7), 0.4)
    add(sh.t0 + t1 + 0.4, Y.crowd_roar(2.5, 1.0, 19, shouts=True, clashes=False, density=2.0), 0.35)
    tc = t1 + 0.8
    k = 0
    while tc < sh.d - 0.2:
        add(sh.t0 + tc, Y.sword_clash(0.7, 60 + k), 0.3, (k % 2 - 0.5) * 0.5)
        tc += 1.05
        k += 1
    sh = S["s43"]
    t1 = sh.lt(1)
    crowd(sh, 0.22, seed=20, density=0.8)
    amb(sh, Y.steps(t1, 1.0, 7, 0.36), 0.5, 0, t1)
    for k, dg in enumerate((0, 4, 7, 4, 12)):
        add(sh.t0 + 0.3 + k * 0.3, Y.cornu(Y.D4 / 2 * 2 ** (dg / 12), 0.45 if k < 4 else 1.2, 0.8), 0.35)
    pops(sh, [sh.lf(0, 0.3), sh.lf(0, 0.6), t1 + 0.4])
    add(sh.t0 + t1, Y.whoosh(0.5, 1.0, 300, 3000, 16), 0.35)
    for fr in (0.45, 0.62):
        pops(sh, [sh.lf(1, fr)])
        add(sh.t0 + sh.lf(1, fr) + 0.25, Y.ding(1.0), 0.4)
    add(sh.t0 + sh.lf(1, 0.85), Y.metal_clang(0.7, 41), 0.35)
    # ---- bolum 8
    sh = S["s45"]
    t1 = sh.lt(1)
    tg = sh.lf(0, 0.45)
    amb(sh, muffled(Y.crowd_roar(tg + 0.4, 1.0, 21, shouts=True, clashes=False, density=1.0)), 0.45, 0, tg + 0.4)
    add(sh.t0 + sh.lf(0, 0.12), Y.gate_creak(1.8, 1.0, 1), 0.6)
    add(sh.t0 + tg, Y.riser(0.5, 1.0), 0.3)
    add(sh.t0 + tg + 0.4, Y.impact(1.0), 0.55)
    crowd(sh, 0.4, tg + 0.4, sh.d, seed=22, density=1.4)
    amb(sh, Y.steps(1.6, 1.0, 8, 0.4), 0.6, tg + 0.4, tg + 2.0)
    pops(sh, [sh.lf(1, f) for f in (0.05, 0.2, 0.5, 0.62, 0.85)])
    sh = S["s46"]
    t1 = sh.lt(1)
    crowd(sh, 0.38, seed=23, density=1.2)
    amb(sh, Y.steps(sh.d, 1.0, 9, 0.28), 0.55)
    amb(sh, Y.breath(t1, 1.0, 1.4, 2), 0.6, 0, t1)
    th = sh.lf(1, 0.08) + 0.25
    add(sh.t0 + th - 0.25, Y.whoosh(0.35, 1.0, 800, 3000, 17), 0.45)
    add(sh.t0 + th, Y.metal_clang(1.0, 50), 0.6)
    add(sh.t0 + th, Y.sword_clash(1.0, 51), 0.5)
    add(sh.t0 + th, Y.impact(0.6), 0.4)
    add(sh.t0 + th + 0.2, Y.gasp(1.0, 2), 0.4)
    sl = sh.lf(1, 0.55) + 0.1
    add(sh.t0 + sl, Y.whoosh(0.4, 1.0, 600, 3500, 18), 0.55)
    add(sh.t0 + sl + 0.3, Y.crowd_roar(2.0, 1.0, 24, shouts=True, clashes=False, density=2.5), 0.4)
    add(sh.t0 + sh.lf(0, 0.18), Y.ui_pop(1.0, 600), 0.4)
    sh = S["s47"]
    t1 = sh.lt(1)
    throw = sh.lf(0, 0.05)
    crowd(sh, 0.38, seed=25, density=1.3)
    add(sh.t0 + throw, Y.whoosh(0.8, 1.0, 200, 900, 19), 0.6)
    add(sh.t0 + throw + 0.8, Y.thunk(1.0, 3), 0.5)
    add(sh.t0 + throw + 0.8, Y.gasp(1.0, 3), 0.45)
    fall = sh.lf(0, 0.72) + 0.45
    add(sh.t0 + fall, Y.thud(1.0, 1), 0.7)
    add(sh.t0 + fall, Y.impact(0.7), 0.45)
    add(sh.t0 + fall + 0.05, Y.metal_clang(0.7, 52), 0.35)
    amb(sh, Y.steps(0.8, 1.0, 10, 0.3), 0.6, t1, t1 + 0.8)
    pops(sh, [throw + 0.2])
    sh = S["s48"]
    t1 = sh.lt(1)
    amb(sh, muffled(Y.murmur(t1, 1.0, 26)), 0.5, 0, t1)
    add(sh.t0 + sh.lf(0, 0.62) + 0.3, Y.ding(1.0), 0.45)
    pops(sh, [sh.lf(0, 0.3), t1 + 0.2, sh.lf(1, 0.45), sh.lf(1, 0.75)])
    amb(sh, Y.murmur(sh.d - t1, 1.0, 27), 0.35, t1, sh.d)
    sh = S["s49"]
    t1 = sh.lt(1)
    crowd(sh, 0.3, seed=28, density=1.5)
    amb(sh, Y.crowd_chant(t1 + 0.8, 1.0, 1, beat=0.38), 0.55, 0.3, t1 + 1.1)
    m_t = sh.lf(1, 0.55)
    add(sh.t0 + m_t, Y.impact(0.8), 0.5)
    add(sh.t0 + m_t + 0.1, Y.crowd_roar(3.0, 1.0, 29, shouts=True, clashes=False, density=3.0), 0.5)
    add(sh.t0 + m_t + 0.1, Y.ding(1.0), 0.4)
    sh = S["s50"]
    t1 = sh.lt(1)
    amb(sh, Y.wind(sh.d, 1.0, 30, bright=500), 0.35)
    add(sh.t0 + sh.lf(0, 0.45), Y.impact(0.6), 0.35)
    add(sh.t0 + t1, Y.stone(1.0, 3), 0.5)
    for k in range(3):
        add(sh.t0 + sh.lf(1, 0.3) + k * 0.15, Y.thunk(1.0, 10 + k), 0.5)
    add(sh.t0 + sh.lf(1, 0.7), Y.whoosh(0.5, 1.0, 300, 1500, 20), 0.35)
    pops(sh, [t1 + 0.2, sh.lf(1, 0.55)])
    # ---- bolum 9
    sh = S["s52"]
    t1, t2 = sh.lt(1), sh.lt(2)
    pops(sh, [0.3, sh.lf(0, 0.55), t1 + 0.1] + [sh.lf(1, 0.45) + k * 0.07 for k in range(10)], 0.35, 700)
    add(sh.t0 + sh.lf(1, 0.8), Y.buzz(1.0), 0.4)
    pops(sh, [sh.lf(1, 0.85), t2 + 0.4, sh.lf(2, 0.5)])
    add(sh.t0 + t2 + 0.2, Y.whoosh(0.5, 1.0, 300, 2500, 21), 0.4)
    for k in range(2):
        add(sh.t0 + t2 + 0.4 + k * 0.3, Y.buzz(0.8), 0.3)
    sh = S["s53"]
    t1 = sh.lt(1)
    add(sh.t0 + 0.2, Y.stone(1.0, 4), 0.5)
    pops(sh, [0.6, sh.lf(1, 0.7)])
    add(sh.t0 + t1, Y.impact(0.5), 0.35)
    sh = S["s54"]
    t1 = sh.lt(1)
    crowd(sh, 0.3, 0, t1, seed=31, density=1.2)
    give = sh.lf(0, 0.3) + 0.8
    add(sh.t0 + give, Y.ding(1.0), 0.45)
    add(sh.t0 + give, Y.crowd_roar(2.5, 1.0, 32, shouts=True, clashes=False, density=2.5), 0.4)
    pops(sh, [give + 0.1, t1 + 0.1, sh.lf(1, 0.45)])
    add(sh.t0 + sh.lf(1, 0.6), Y.coins(10, 1.0, 5, 0.6), 0.5)
    sh = S["s55"]
    amb(sh, Y.sea_waves(sh.d, 1.0, 3), 0.45)
    amb(sh, Y.steps(3.3, 1.0, 11, 0.5, sand=False), 0.5, 0.2, 3.5)
    a, b = sh.lt(0), sh.le(0)
    pops(sh, [a + (b - a) * 0.55, a + (b - a) * 0.8])
    for k in range(6):
        add(sh.t0 + 4.3 + k * 0.2, Y.ding(0.5), 0.15, float(rng.uniform(-0.5, 0.5)))
    sh = S["s56"]
    t1 = sh.lt(1)
    a, b = sh.lt(0), sh.le(0)
    pops(sh, [0.3] + [a + (b - a) * fr for fr in (0.4, 0.62, 0.86)], 0.55)
    add(sh.t0 + t1 + 0.1, Y.impact(0.6), 0.35)
    add(sh.t0 + t1 + 1.0, Y.ui_pop(1.0, 500), 0.5)
    add(sh.t0 + t1 + 3.2, Y.tek(1.0, 3500), 0.5)
    add(sh.t0 + t1 + 3.25, Y.ding(1.0), 0.45)
    # bolum kartlari
    for sid, sh in S.items():
        if sh.s["fn"] == "chapter":
            add(sh.t0, Y.whoosh(0.7, 1.0, 200, 2500, int(sid[1:])), 0.6)
            add(sh.t0 + 0.28, Y.impact(0.6), 0.45)
            add(sh.t0 + 0.05, Y.paper(1.0, 0.7, int(sid[1:])), 0.5)
    return C


def build():
    tl = load_tl()
    total = tl["total"]
    n = int((total + 0.5) * SR)
    print("anlatim...", flush=True)
    nar = narration(tl, n)
    print("muzik...", flush=True)
    mus = soundtrack_music(tl, n)
    mask = speech_mask(tl, n)
    mus *= (1.0 - 0.7 * mask)[:, None]
    print("efektler...", flush=True)
    fx = np.zeros((n, 2))
    for t, x, g in cues(tl):
        place(fx, x, t, g)
    fxm = (1.0 - 0.5 * mask)[:, None]
    for nm, arr in (("anlatim", nar), ("muzik", mus), ("efekt", fx)):
        bad = ~np.isfinite(arr)
        if bad.any():
            print("UYARI: NaN/Inf ->", nm, int(bad.sum()))
            arr[bad] = 0.0
    mix = nar * 1.0 + mus * 0.45 + fx * 0.52 * fxm
    print("tepe:", round(float(np.abs(mix).max()), 3))
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    sf.write(os.path.join(WORK, "soundtrack.wav"), mix.astype(np.float32), SR, subtype="FLOAT")
    sf.write(os.path.join(WORK, "stem_narration.wav"), nar.astype(np.float32), SR, subtype="FLOAT")
    sf.write(os.path.join(WORK, "stem_music.wav"), (mus * 0.45).astype(np.float32), SR, subtype="FLOAT")
    sf.write(os.path.join(WORK, "stem_fx.wav"), (fx * 0.52 * fxm).astype(np.float32), SR, subtype="FLOAT")
    print("yazildi:", os.path.join(WORK, "soundtrack.wav"), round(n / SR, 2), "sn")


if __name__ == "__main__":
    build()

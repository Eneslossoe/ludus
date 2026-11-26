"""Prosedurel ses sentezi: enstrumanlar (lir, aulos, def, su orgu, kornu, koro) ve efektler.

Hicbir hazir ses dosyasi kullanilmaz; her sey numpy ile matematiksel olarak uretilir.
"""
import math

import numpy as np
from scipy import signal

SR = 48000
RNG = np.random.default_rng(1234)


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2, sr=SR):
    a_, d_, r_ = int(a * sr), int(d * sr), int(r * sr)
    s_ = max(0, n - a_ - d_ - r_)
    e = np.concatenate([np.linspace(0, 1, max(a_, 1)), np.linspace(1, s, max(d_, 1)), np.full(s_, s),
                        np.linspace(s, 0, max(r_, 1))])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def noise(n, rng=None):
    return (rng or RNG).standard_normal(n)


def pink(n, rng=None):
    w = (rng or RNG).standard_normal(n)
    b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
    return signal.lfilter(b, a, w) * 4


def brown(n, rng=None):
    w = (rng or RNG).standard_normal(n)
    x = np.cumsum(w)
    x = signal.lfilter([1, -1], [1, -0.995], x)
    return x / (np.abs(x).max() + 1e-9)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), 0.99)], btype="band", output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    sos = signal.butter(order, min(f / (SR / 2), 0.99), btype="low", output="sos")
    return signal.sosfilt(sos, x)


def hp(x, f, order=2):
    sos = signal.butter(order, f / (SR / 2), btype="high", output="sos")
    return signal.sosfilt(sos, x)


def pan(x, p):
    """p: -1 sol, +1 sag"""
    a = (p + 1) * math.pi / 4
    return np.stack([x * math.cos(a), x * math.sin(a)], axis=1)


def place(buf, x, t0, gain=1.0):
    """buf: (N,2); x: (n,) veya (n,2); t0 saniye"""
    i = int(t0 * SR)
    if i >= len(buf):
        return
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    if i < 0:
        x = x[-i:]
        i = 0
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * gain


_IR = {}


def reverb_ir(seconds=2.4, damp=3.2, seed=7, bright=6000):
    key = (seconds, damp, seed, bright)
    if key not in _IR:
        r = np.random.default_rng(seed)
        n = int(seconds * SR)
        t = np.arange(n) / SR
        irs = []
        for ch in range(2):
            w = r.standard_normal(n) * np.exp(-t * damp)
            w = lp(w, bright)
            w[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
            irs.append(w / np.sqrt((w ** 2).sum()))
        _IR[key] = np.stack(irs, axis=1)
    return _IR[key]


def reverb(x, wet=0.25, seconds=2.4, damp=3.2, bright=6000):
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    ir = reverb_ir(seconds, damp, bright=bright)
    y = np.zeros((len(x) + len(ir) - 1, 2))
    for c in range(2):
        y[:, c] = signal.fftconvolve(x[:, c], ir[:, c])
    y = y[:len(x)]
    return x * (1 - wet) + y * wet * 1.6


# ================================================================== ENSTRUMANLAR
def hz(semi_from_a4):
    return 440.0 * 2 ** (semi_from_a4 / 12)


D4 = hz(-7)
HICAZ = [0, 1, 4, 5, 7, 8, 10]  # D Eb F# G A Bb C


def scale_f(deg, base=D4, sc=HICAZ):
    o, k = divmod(deg, len(sc))
    return base * 2 ** ((sc[k] + 12 * o) / 12)


def oud(f, dur=1.2, vel=0.8, bright=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, 14):
        fk = f * k * (1 + 0.0004 * k * k)
        if fk > SR / 2.2:
            break
        amp = (1.0 / k ** 1.1) * (1.0 if k > 1 else 1.3) * (math.sin(math.pi * k * 0.18) + 0.25)
        dec = 2.2 + 0.9 * k / bright
        y += amp * np.sin(2 * np.pi * fk * t + RNG.uniform(0, 6.28)) * np.exp(-t * dec)
    pick = noise(min(n, 400)) * np.exp(-np.arange(min(n, 400)) / 60)
    y[:len(pick)] += pick * 0.3
    y = signal.lfilter(*signal.iirpeak(min(320 / (SR / 2), 0.99), 3), y) * 0.4 + y
    att = np.minimum(1, t / 0.003)
    return y * att * vel * 0.22


def kanun(f, dur=0.9, vel=0.6):
    return oud(f * 2, dur, vel, bright=1.8) * 0.8


def ney(f, dur=1.5, vel=0.7, vib=0.006):
    n = int(dur * SR)
    t = np.arange(n) / SR
    glide = 1 - 0.03 * np.exp(-t / 0.06)
    vibr = 1 + vib * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.25) / 0.3, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * glide * vibr) / SR
    y = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    br = bp(noise(n), f * 1.2, min(f * 5, 9000)) * 0.35
    y = y + br
    e = env_adsr(n, 0.12, 0.2, 0.85, min(0.35, dur * 0.4))
    return y * e * vel * 0.2


def saw_add(f, t, nh=14, detune=0.0):
    y = np.zeros(len(t))
    for k in range(1, nh + 1):
        if f * k > SR / 2.5:
            break
        y += np.sin(2 * np.pi * f * k * t * (1 + detune)) / k
    return y


def pad(freqs, dur, vel=0.5, att=0.8, rel=1.2, bright=2200, nh=12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        for dt in (-0.004, 0.0, 0.0045):
            y += saw_add(f, t, nh, dt)
    y = lp(y, bright)
    e = env_adsr(n, att, 0.3, 0.9, rel)
    return y * e * vel * 0.05


def choir(freqs, dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in freqs:
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t + RNG.uniform(0, 6))
        ph = 2 * np.pi * np.cumsum(f * vib) / SR
        for k in range(1, 30):
            if f * k > 8000:
                break
            y += np.sin(k * ph) / k
    out = bp(y, 650, 1000) * 1.0 + bp(y, 1050, 1350) * 0.6 + bp(y, 2600, 3200) * 0.25
    e = env_adsr(n, 0.6, 0.3, 0.9, 1.0)
    return out * e * vel * 0.12


def drone(f, dur, vel=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = saw_add(f, t, 20) + saw_add(f * 1.5, t, 12, 0.002) * 0.5 + saw_add(f * 0.5, t, 20, -0.001) * 0.7
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t)
    y = lp(y, 500) * (0.7 + 0.3 * lfo)
    e = env_adsr(n, 1.5, 0.5, 1.0, 1.5)
    return y * e * vel * 0.06


def brass(f, dur, vel=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    c = 0.9 - 0.6 * np.exp(-t / 0.08)
    for k in range(1, 16):
        if f * k > 9000:
            break
        y += np.sin(2 * np.pi * f * k * t) / k * np.exp(-k * (1 - c) * 0.6)
    e = env_adsr(n, 0.04, 0.2, 0.7, 0.25)
    return y * e * vel * 0.15


def big_drum(vel=1.0, f0=110, f1=45, dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.35)
    y += lp(noise(n), 1200) * np.exp(-t / 0.04) * 0.5
    return y * vel * 0.7


def dum(vel=1.0):
    return big_drum(vel * 0.7, 140, 75, 0.45)


def tek(vel=1.0, f=1900):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    y = hp(noise(n), 2500) * np.exp(-t / 0.018) * 0.7
    y += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.03) * 0.4
    return y * vel * 0.5


def jingle(vel=1.0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    y = hp(noise(n), 6000) * np.exp(-t / 0.06)
    for f in (5200, 6900, 8300):
        y += np.sin(2 * np.pi * f * t) * np.exp(-t / 0.08) * 0.15
    return y * vel * 0.25


def bell(f=220, dur=5.0, vel=0.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for r, a, d in ((0.56, 1.0, 1.2), (0.92, 0.7, 1.6), (1.19, 0.6, 2.0), (1.71, 0.5, 2.6), (2.0, 0.6, 3.0),
                    (2.74, 0.35, 4.0), (3.0, 0.3, 4.5), (3.76, 0.25, 5.5), (4.07, 0.2, 6.0)):
        y += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d / 2.5)
    return y * vel * 0.15


# ================================================================== EFEKTLER
def sword_clash(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in r.uniform(1800, 9000, 7):
        y += np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t * r.uniform(5, 14)) * r.uniform(0.3, 1)
    y += hp(noise(n, r), 3000) * np.exp(-t / 0.01) * 1.5
    y += lp(noise(n, r), 800) * np.exp(-t / 0.03) * 0.6
    return y * vel * 0.25


def whoosh(dur=0.5, vel=1.0, f0=300, f1=3000, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n, r)
    out = np.zeros(n)
    steps = 12
    for i in range(steps):
        a, b = int(i * n / steps), int((i + 1) * n / steps)
        f = f0 * (f1 / f0) ** (i / steps)
        out[a:b] = bp(x, f * 0.7, f * 1.4)[a:b]
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return out * e * vel * 0.6


def arrow_whiz(vel=1.0, seed=0):
    return whoosh(0.35, vel, 2500, 900, seed) * 0.7


def thunk(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    y = lp(noise(n, r), 900) * np.exp(-t / 0.02) + np.sin(2 * np.pi * 160 * t) * np.exp(-t / 0.05) * 0.5
    return y * vel * 0.5


def hoof(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.2 * SR)
    t = np.arange(n) / SR
    y = lp(noise(n, r), 600) * np.exp(-t / 0.02) * 0.8 + np.sin(2 * np.pi * 70 * t) * np.exp(-t / 0.04) * 0.6
    return y * vel * 0.5


def gallop(dur, n_horses=6, vel=1.0, seed=0, tempo=0.42):
    r = np.random.default_rng(seed)
    out = np.zeros((int(dur * SR) + SR, 2))
    for h in range(n_horses):
        off = r.uniform(0, tempo)
        p = r.uniform(-0.7, 0.7)
        t0 = off
        while t0 < dur:
            for k, dt in enumerate((0.0, 0.09, 0.19)):
                place(out, pan(hoof(r.uniform(0.6, 1.0), int(r.integers(0, 1e6))), p), t0 + dt)
            t0 += tempo * r.uniform(0.95, 1.05)
    return out[:int(dur * SR)] * vel


def shout(f0=180, dur=0.8, vowel="a", vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    fcurve = f0 * (1 + 0.15 * np.sin(np.pi * t / dur)) * (1 + 0.01 * np.sin(2 * np.pi * 6 * t))
    ph = 2 * np.pi * np.cumsum(fcurve) / SR
    y = np.zeros(n)
    for k in range(1, 40):
        if f0 * k > 7000:
            break
        y += np.sin(k * ph) / k
    y += noise(n, r) * 0.15
    F = {"a": (800, 1200, 2600), "o": (500, 900, 2500), "e": (500, 1800, 2600)}[vowel]
    out = bp(y, F[0] * 0.8, F[0] * 1.2) + 0.6 * bp(y, F[1] * 0.85, F[1] * 1.15) + 0.3 * bp(y, F[2] * 0.9, F[2] * 1.1)
    e = env_adsr(n, 0.05, 0.1, 0.8, 0.3)
    return out * e * vel * 0.5


def crowd_roar(dur, vel=1.0, seed=0, shouts=True, clashes=True, density=1.0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    base = pink(n, r)
    y = bp(base, 300, 900) * 0.8 + bp(base, 1000, 1800) * 0.5 + bp(base, 2200, 3200) * 0.2
    mod = lp(r.standard_normal(n), 2.0)
    mod = 0.6 + 0.4 * mod / (np.abs(mod).max() + 1e-9)
    y *= mod
    out = pan(y * 0.25, 0)
    out[:, 0] += bp(pink(n, r), 300, 1500)[:n] * 0.06
    out[:, 1] += bp(pink(n, r), 300, 1500)[:n] * 0.06
    if shouts:
        for _ in range(int(dur * 4 * density)):
            s = shout(r.uniform(140, 300), r.uniform(0.4, 1.1), r.choice(["a", "o", "e"]), r.uniform(0.15, 0.4),
                      int(r.integers(0, 1e6)))
            place(out, pan(s, r.uniform(-0.8, 0.8)), r.uniform(0, dur))
    if clashes:
        for _ in range(int(dur * 2.2 * density)):
            place(out, pan(sword_clash(r.uniform(0.2, 0.55), int(r.integers(0, 1e6))), r.uniform(-0.9, 0.9)),
                  r.uniform(0, dur))
    return out * vel


def wind(dur, vel=1.0, seed=0, bright=900):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    x = brown(n, r) * 0.6 + pink(n, r) * 0.05
    mod = lp(r.standard_normal(n), 0.6)
    mod = 0.5 + 0.5 * mod / (np.abs(mod).max() + 1e-9)
    y = lp(x, bright) * (0.4 + 0.6 * mod)
    y2 = bp(pink(n, r), 600, 2200) * mod * 0.1
    return np.stack([y + y2, np.roll(y, 800) + y2], axis=1) * vel * 0.5


def fire(dur, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = lp(brown(n, r), 300) * 0.3
    for _ in range(int(dur * 14)):
        i = int(r.uniform(0, n - 600))
        k = int(r.uniform(80, 400))
        out[i:i + k] += hp(noise(k, r), 2000) * np.exp(-np.arange(k) / (k / 5)) * r.uniform(0.1, 0.5)
    return out * vel


def sea_waves(dur, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    sw = 0.5 + 0.5 * np.sin(2 * np.pi * t / 6.5 + 1) ** 2
    y = lp(pink(n, r), 1500) * sw * 0.5
    return np.stack([y, np.roll(y, 2400)], axis=1) * vel


def coins(n_coins=10, vel=1.0, seed=0, spread=1.0):
    r = np.random.default_rng(seed)
    out = np.zeros((int((spread + 1) * SR), 2))
    for _ in range(n_coins):
        m = int(0.4 * SR)
        t = np.arange(m) / SR
        y = np.zeros(m)
        for f in r.uniform(3000, 7500, 4):
            y += np.sin(2 * np.pi * f * t) * np.exp(-t * r.uniform(12, 30))
        place(out, pan(y * 0.12, r.uniform(-0.5, 0.5)), r.uniform(0, spread))
    return out * vel


def ui_pop(vel=1.0, f=600):
    n = int(0.14 * SR)
    t = np.arange(n) / SR
    fr = f * (1 + 1.2 * t / 0.14)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.04)
    return y * vel * 0.3


def ding(vel=1.0):
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t / 0.25)
    return y * vel * 0.18


def buzz(vel=1.0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    y = signal.sawtooth(2 * np.pi * 110 * t) * np.exp(-t / 0.15)
    return lp(y, 1500) * vel * 0.2


def heartbeat(vel=1.0):
    out = np.zeros(int(0.8 * SR))
    for dt, v in ((0.0, 1.0), (0.22, 0.7)):
        b = big_drum(v, 70, 40, 0.4)
        i = int(dt * SR)
        out[i:i + len(b)] += b[:len(out) - i]
    return lp(out, 200) * vel


def impact(vel=1.0):
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    f = 35 + 60 * np.exp(-t / 0.08)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)
    y += lp(noise(n), 2500) * np.exp(-t / 0.08) * 0.6
    return y * vel * 0.8


def riser(dur=2.0, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = noise(n)
    out = np.zeros(n)
    steps = 16
    for i in range(steps):
        a, b = int(i * n / steps), int((i + 1) * n / steps)
        f = 300 * (12 ** (i / steps))
        out[a:b] = bp(x, f * 0.7, min(f * 1.4, 20000))[a:b]
    e = (t / dur) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(200 * 4 ** (t / dur)) / SR) * 0.3
    return (out + tone) * e * vel * 0.5


def paper(vel=1.0, dur=0.6, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    y = bp(noise(n, r), 1500, 7000)
    mod = np.abs(lp(r.standard_normal(n), 20))
    return y * mod / (mod.max() + 1e-9) * vel * 0.3


def scribble(dur=2.0, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = bp(noise(n, r), 2500, 6000)
    mod = (np.sin(2 * np.pi * 7 * t + np.sin(2 * np.pi * 1.3 * t) * 3) > 0.2).astype(float)
    return lp(mod, 60) * y * vel * 0.12


def caw(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 900 - 300 * t / 0.35
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + noise(n, r) * 0.4
    y = bp(y, 800, 2500)
    return y * np.sin(np.pi * t / 0.35) * vel * 0.12


def camel_steps(dur, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((int(dur * SR), 2))
    t0 = 0.0
    while t0 < dur:
        y = lp(noise(int(0.15 * SR), r), 700) * np.exp(-np.arange(int(0.15 * SR)) / (0.03 * SR))
        place(out, pan(y * 0.25, r.uniform(-0.2, 0.2)), t0)
        t0 += 0.5 * r.uniform(0.9, 1.1)
    return out * vel


# ================================================================== ANTIK YUNAN / ROMA ENSTRUMANLARI
DORIAN = [0, 2, 3, 5, 7, 9, 10]      # D E F G A B C  (sicak, halk ezgisi)
PHRYG = [0, 1, 3, 5, 7, 8, 10]       # D Eb F G A Bb C (karanlik, gergin)
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def lyre(f, dur=1.4, vel=0.8):
    """kithara / lir: parlak, kisa sonumlu telli"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(1, 16):
        fk = f * k * (1 + 0.0002 * k * k)
        if fk > SR / 2.2:
            break
        amp = (1.0 / k ** 1.25) * (math.sin(math.pi * k * 0.12) + 0.3)
        y += amp * np.sin(2 * np.pi * fk * t + RNG.uniform(0, 6.28)) * np.exp(-t * (1.6 + 1.3 * k))
    pk = min(n, 300)
    y[:pk] += noise(pk) * np.exp(-np.arange(pk) / 40) * 0.25
    return y * np.minimum(1, t / 0.002) * vel * 0.24


def aulos(f, dur=1.2, vel=0.7, vib=0.008):
    """aulos: cift kamisli, genizden gelen sert ton"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    glide = 1 - 0.02 * np.exp(-t / 0.05)
    vibr = 1 + vib * np.sin(2 * np.pi * 5.6 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * glide * vibr) / SR
    y = np.zeros(n)
    for k in range(1, 18):
        if f * k > 9000:
            break
        y += np.sin(k * ph) / k * (1.0 if k % 2 else 0.45)
    y = bp(y, 500, 3800) * 1.4 + lp(y, 500) * 0.3
    y += bp(noise(n), 1500, 5000) * 0.05
    e = env_adsr(n, 0.05, 0.15, 0.85, min(0.25, dur * 0.3))
    return y * e * vel * 0.16


def aulos_drone(f, dur, vel=0.4):
    return aulos(f, dur, vel, vib=0.002) * 0.6


def tympanon(vel=1.0, low=True):
    """def / tympanon"""
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    if low:
        fq = 90 + 80 * np.exp(-t / 0.03)
        y = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.12)
        y += lp(noise(n), 1500) * np.exp(-t / 0.02) * 0.4
    else:
        y = bp(noise(n), 800, 4000) * np.exp(-t / 0.03) * 0.8
        y += np.sin(2 * np.pi * 320 * t) * np.exp(-t / 0.04) * 0.3
    return y * vel * 0.55


def krotala(vel=1.0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    y = bp(noise(n), 2000, 6000) * np.exp(-t / 0.008)
    y += np.sin(2 * np.pi * 1700 * t) * np.exp(-t / 0.02) * 0.4
    return y * vel * 0.35


def organ(freqs, dur, vel=0.5):
    """hydraulis: su orgu (boru sesi, hafif titresim)"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    trem = 1 + 0.03 * np.sin(2 * np.pi * 6.0 * t)
    for f in freqs:
        for k, a in ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.25), (6, 0.12), (8, 0.08)):
            y += a * np.sin(2 * np.pi * f * k * t * (1 + 0.0007 * k))
    y += bp(noise(n), 1000, 4000) * 0.03
    e = env_adsr(n, 0.06, 0.1, 0.9, 0.3)
    return y * trem * e * vel * 0.05


def cornu(f, dur, vel=0.8):
    """kornu: genis, kalin pirinç boru"""
    return (brass(f, dur, vel) + brass(f * 0.5, dur, vel * 0.5)) * 1.1


# ================================================================== EK EFEKTLER
def wood_clack(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in r.uniform(500, 1400, 3):
        y += np.sin(2 * np.pi * f * t) * np.exp(-t * r.uniform(30, 60))
    y += bp(noise(n, r), 800, 4000) * np.exp(-t / 0.006) * 1.2
    return y * vel * 0.35


def metal_clang(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for f in r.uniform(400, 2600, 6):
        y += np.sin(2 * np.pi * f * t + r.uniform(0, 6)) * np.exp(-t * r.uniform(3, 8)) * r.uniform(0.3, 1)
    y += lp(noise(n, r), 2000) * np.exp(-t / 0.015) * 1.0
    return y * vel * 0.25


def whip_crack(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    w = whoosh(0.25, 0.6, 400, 4000, seed)
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    c = hp(noise(n, r), 2000) * np.exp(-t / 0.004) * 2.0
    out = np.zeros(len(w) + n)
    out[:len(w)] += w
    out[len(w) - 200:len(w) - 200 + n] += c
    return out * vel * 0.5


def chain_rattle(dur=0.8, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n + SR // 2)
    k = 0
    tt = 0.0
    while tt < dur:
        m = int(0.12 * SR)
        t = np.arange(m) / SR
        y = np.zeros(m)
        for f in r.uniform(2500, 7000, 3):
            y += np.sin(2 * np.pi * f * t) * np.exp(-t * r.uniform(30, 70))
        i = int(tt * SR)
        out[i:i + m] += y * r.uniform(0.3, 1.0)
        tt += r.uniform(0.02, 0.07)
        k += 1
    return out[:n] * vel * 0.12


def gate_creak(dur=1.8, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 70 + 20 * np.sin(2 * np.pi * 0.7 * t) + 8 * lp(r.standard_normal(n), 5) * 40
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) * 0.4
    y = bp(y, 120, 1500) + lp(noise(n, r), 300) * 0.3
    y *= env_adsr(n, 0.1, 0.1, 1.0, 0.3)
    return (y + chain_rattle(dur, 0.8, seed)) * vel * 0.6


def breath(dur=2.0, vel=1.0, rate=0.9, seed=0):
    """migfer icinde nefes"""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    env = np.clip(np.sin(2 * np.pi * rate * t), 0, 1) ** 1.5 + 0.6 * np.clip(-np.sin(2 * np.pi * rate * t), 0, 1) ** 2
    y = bp(noise(n, r), 300, 2400) * env
    y = y + bp(y, 700, 1000) * 1.5
    return y * vel * 0.35


def crickets(dur, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((n, 2))
    for c in range(3):
        f = r.uniform(4200, 5200)
        p = r.uniform(-0.6, 0.6)
        tt = r.uniform(0, 0.5)
        while tt < dur:
            m = int(0.03 * SR)
            t = np.arange(m) / SR
            for j in range(3):
                y = np.sin(2 * np.pi * f * t) * np.sin(np.pi * t / 0.03) * 0.05
                place(out, pan(y, p), tt + j * 0.045)
            tt += r.uniform(0.5, 0.9)
    return out * vel


def steps(dur, vel=1.0, seed=0, rate=0.45, sand=True):
    r = np.random.default_rng(seed)
    out = np.zeros((int(dur * SR) + SR, 2))
    tt = 0.0
    while tt < dur:
        m = int(0.12 * SR)
        y = (bp(noise(m, r), 300, 2500) if sand else lp(noise(m, r), 900)) * np.exp(-np.arange(m) / (0.02 * SR))
        place(out, pan(y * 0.3, r.uniform(-0.2, 0.2)), tt)
        tt += rate * r.uniform(0.9, 1.1)
    return out[:int(dur * SR)] * vel


def murmur(dur, vel=1.0, seed=0):
    return crowd_roar(dur, vel * 0.5, seed, shouts=False, clashes=False)


def crowd_chant(dur, vel=1.0, seed=0, beat=0.55):
    """'Bi-rak o-nu!' benzeri ritmik toplu bagiris"""
    r = np.random.default_rng(seed)
    out = np.zeros((int(dur * SR) + SR, 2))
    tt = 0.0
    k = 0
    while tt < dur:
        for v in range(10):
            f0 = r.uniform(130, 260) * (1.12 if k % 4 in (0, 2) else 1.0)
            s = shout(f0, beat * 0.8, ["a", "a", "o", "e"][k % 4], r.uniform(0.3, 0.6), int(r.integers(0, 1e6)))
            place(out, pan(s, r.uniform(-0.8, 0.8)), tt + r.uniform(-0.03, 0.03))
        tt += beat if k % 4 != 3 else beat * 2
        k += 1
    return out[:int(dur * SR)] * vel


def gasp(vel=1.0, seed=0):
    """kalabaligin 'oooh' sesi"""
    r = np.random.default_rng(seed)
    out = np.zeros((int(1.6 * SR), 2))
    for v in range(14):
        s = shout(r.uniform(150, 320), 1.3, "o", r.uniform(0.2, 0.45), int(r.integers(0, 1e6)))
        place(out, pan(s, r.uniform(-0.8, 0.8)), r.uniform(0, 0.15))
    return out * vel


def hiss(dur=1.5, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    return hp(noise(n, r), 3000) * np.sin(np.pi * t / dur) * vel * 0.08


def pour(dur=1.2, vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = bp(noise(n, r), 400, 2500) * 0.15
    for _ in range(int(dur * 30)):
        i = int(r.uniform(0, n - 2000))
        m = 1500
        f = r.uniform(600, 1800)
        tt = np.arange(m) / SR
        out[i:i + m] += np.sin(2 * np.pi * f * (1 + tt * 8) * tt) * np.exp(-tt / 0.01) * 0.2
    return out * np.sin(np.pi * np.arange(n) / n) * vel


def thud(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.8 * SR)
    t = np.arange(n) / SR
    f = 50 + 70 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.18)
    y += lp(noise(n, r), 1200) * np.exp(-t / 0.05) * 0.8
    return y * vel * 0.7


def stone(vel=1.0, seed=0):
    r = np.random.default_rng(seed)
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    y = lp(noise(n, r), 600) * np.exp(-t / 0.08) + np.sin(2 * np.pi * 60 * t) * np.exp(-t / 0.1) * 0.6
    return y * vel * 0.6


def roar(vel=1.0, seed=0, dur=1.6):
    """aslan kukremesi (alcak, puruzlu)"""
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 90 + 40 * np.sin(np.pi * t / dur) + 10 * lp(r.standard_normal(n), 30) * 20
    y = signal.sawtooth(2 * np.pi * np.cumsum(f) / SR) + noise(n, r) * 0.6
    y = bp(y, 150, 1200) * env_adsr(n, 0.15, 0.2, 0.8, 0.5)
    return y * vel * 0.4

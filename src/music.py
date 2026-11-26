"""Prosedurel fon muzigi: antik Yunan / Roma renkleri.

Lir (kithara), aulos (cift kamisli), tympanon (def), krotala (zil), su orgu (hydraulis), kornu ve koro.
Modlar: Dor (sicak), Frig (gergin), majör (zafer/rahatlama).
"""
import numpy as np

import synth as Y
from synth import SR, pan, place, scale_f

D2, D3, D4, D5 = Y.D4 / 4, Y.D4 / 2, Y.D4, Y.D4 * 2

# 8'lik vuruslarla ritim kaliplari (D=def dusuk, T=def yuksek, K=krotala, B=buyuk davul, .=bos)
PAT = {
    "dance": "D.TKD.TK",
    "dance2": "D.KTD.TT",
    "march": "B.T.D.T.",
    "battle": "BKTKBTBKBKTKBTTT",
    "battle_pre": "B...B...B.B.B...",
    "soft": "D...K...",
    "train": "D.T.DKT.",
    "festival": "B.TKB.TKBKTKB.TT",
}

MOODS = {
    "intro": dict(bpm=76, pat="battle_pre", scale="phryg", drone=True, cornu=True, choir=True, aulos=0.5, wet=0.35),
    "greek": dict(bpm=92, pat="dance", scale="dorian", lyre=True, aulos=0.75, drone=True, wet=0.3),
    "greek2": dict(bpm=84, pat="soft", scale="dorian", lyre=True, aulos=0.6, drone=True, wet=0.32),
    "sad": dict(bpm=66, pat=None, scale="phryg", drone=True, pad_dark=True, aulos=0.9, lyre_sparse=True, wet=0.5),
    "dark": dict(bpm=60, pat="soft", scale="phryg", drone=True, pad_dark=True, choir=True, heart=True, wet=0.55),
    "ludus": dict(bpm=104, pat="train", scale="dorian", lyre=True, drone=True, aulos=0.4, cornu=True, wet=0.28),
    "feast": dict(bpm=112, pat="dance2", scale="dorian", lyre=True, aulos=0.8, drone=True, wet=0.3),
    "festival": dict(bpm=100, pat="festival", scale="major", organ=True, cornu=True, drone=True, wet=0.32),
    "arena_pre": dict(bpm=84, pat="battle_pre", scale="phryg", drone=True, choir=True, cornu=True, organ=True,
                      wet=0.35),
    "arena": dict(bpm=132, pat="battle", scale="phryg", drone=True, choir=True, cornu=True, ostinato=True,
                  organ_stab=True, wet=0.28),
    "heartbeat": dict(bpm=72, pat=None, scale="phryg", drone=True, heart=True, aulos=0.5, wet=0.6),
    "relief": dict(bpm=80, pat="soft", scale="major", pad_major=True, choir=True, lyre=True, wet=0.45),
    "epic_end": dict(bpm=88, pat="soft", scale="dorian", drone=True, pad_major=True, aulos=0.8, lyre=True, wet=0.4),
    "outro": dict(bpm=104, pat="dance", scale="dorian", lyre=True, aulos=0.5, drone=True, wet=0.28),
}

SCALES = {"dorian": Y.DORIAN, "phryg": Y.PHRYG, "major": Y.MAJOR}

LYRE_RIFFS = [[0, 2, 4, 2, 7, 4, 2, 4], [0, 4, 7, 4, 3, 4, 2, 1], [5, 4, 2, 4, 0, 2, 4, 2],
              [0, None, 4, 7, 6, None, 4, 2]]


def melody_phrase(r, n=5, lo=-1, hi=8):
    deg = int(r.integers(0, 5))
    notes = []
    for i in range(n):
        step = int(r.choice([-2, -1, -1, 1, 1, 2, 0]))
        deg = int(np.clip(deg + step, lo, hi))
        notes.append(deg)
    notes[-1] = int(r.choice([0, 4, 7]))
    return notes


def gen(mood, dur, seed=0):
    cfg = MOODS[mood]
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros((n + SR * 4, 2))
    beat = 60.0 / cfg["bpm"]
    eighth = beat / 2
    sc = SCALES[cfg.get("scale", "dorian")]
    major = cfg.get("scale") == "major"

    def f(deg, base=D4):
        return scale_f(deg, base, sc)

    if cfg.get("drone"):
        seg = 12.0
        t0 = 0.0
        while t0 < dur:
            d = min(seg + 2, dur - t0 + 2)
            place(out, pan(Y.drone(D2, d, 0.5), -0.2), t0)
            place(out, pan(Y.drone(D2 * 1.5, d, 0.22), 0.25), t0)
            t0 += seg
    if cfg.get("pad_dark"):
        t0, k = 0.0, 0
        chords = [[D3, D3 * 1.5], [D3 * 2 ** (1 / 12), D3 * 2 ** (8 / 12)], [D3, D3 * 2 ** (5 / 12)]]
        while t0 < dur:
            place(out, pan(Y.pad(chords[k % 3], 8.5, 0.6, att=2.0, rel=2.5, bright=900), 0), t0)
            t0 += 8.0
            k += 1
    if cfg.get("pad_major"):
        t0, k = 0.0, 0
        st = lambda *ss: [D3 * 2 ** (x / 12) for x in ss]
        chords = [st(0, 4, 7), st(5, 9, 12), st(0, 4, 7), st(7, 11, 14)] if major else \
            [st(0, 3, 7), st(5, 9, 12), st(3, 7, 10), st(7, 10, 14)]
        while t0 < dur:
            place(out, pan(Y.pad(chords[k % 4], 6.5, 0.7, att=1.5, rel=2.0, bright=2400), 0), t0)
            t0 += 6.0
            k += 1
    if cfg.get("choir"):
        t0, k = 0.0, 0
        ch = [[D3, D3 * 1.5, D4], [D3 * 2 ** (1 / 12), D3 * 2 ** (8 / 12), D4 * 2 ** (1 / 12)]] if not major else \
            [[D3, D3 * 1.26, D3 * 1.5], [D3 * 4 / 3, D3 * 5 / 3, D4]]
        while t0 < dur:
            place(out, pan(Y.choir(ch[k % 2], beat * 8 + 1.0, 0.5), 0), t0)
            t0 += beat * 8
            k += 1
    if cfg.get("organ"):
        t0, k = 0.0, 0
        st = lambda *ss: [D3 * 2 ** (x / 12) for x in ss]
        prog = [st(0, 4, 7, 12), st(5, 9, 12), st(7, 11, 14), st(0, 4, 7)] if major else \
            [st(0, 3, 7, 12), st(1, 5, 8), st(0, 3, 7), st(-2, 3, 7)]
        while t0 < dur:
            place(out, pan(Y.organ(prog[k % 4], beat * 4, 0.7), 0.15), t0)
            t0 += beat * 4
            k += 1
    pat = PAT.get(cfg.get("pat")) if cfg.get("pat") else None
    if pat:
        step = eighth if len(pat) == 8 else beat / 4
        i = 0
        t0 = 0.0
        while t0 < dur:
            c = pat[i % len(pat)]
            v = r.uniform(0.75, 1.0)
            if c == "D":
                place(out, pan(Y.tympanon(v, True), -0.1), t0)
            elif c == "T":
                place(out, pan(Y.tympanon(v * 0.7, False), 0.2), t0)
            elif c == "K":
                place(out, pan(Y.krotala(v * 0.7), 0.35), t0)
            elif c == "B":
                place(out, pan(Y.big_drum(v), 0), t0)
            t0 += step
            i += 1
            if mood in ("arena", "arena_pre", "intro") and i % (len(pat) * 4) == 0:
                for k in range(6):
                    place(out, pan(Y.big_drum(0.5 + k * 0.08, 130, 60, 0.6), 0), t0 - beat + k * beat / 6)
    if cfg.get("lyre"):
        t0 = 0.0
        bar = 0
        while t0 < dur:
            riff = LYRE_RIFFS[(bar // 2) % len(LYRE_RIFFS)]
            for j, dg in enumerate(riff):
                if dg is None:
                    continue
                place(out, pan(Y.lyre(f(dg, D3 * 2), 1.4, r.uniform(0.55, 0.85)), -0.35), t0 + j * eighth)
            t0 += eighth * 8
            bar += 1
    if cfg.get("lyre_sparse"):
        t0 = 1.5
        while t0 < dur:
            for j, dg in enumerate((0, 4, 7)):
                place(out, pan(Y.lyre(f(dg, D3 * 2), 2.0, 0.5), -0.3), t0 + j * 0.35)
            t0 += beat * 8
    if cfg.get("ostinato"):
        t0, k = 0.0, 0
        seq = [0, 0, 1, 0, 3, 0, 1, 0]
        while t0 < dur:
            dg = seq[k % 8]
            nn = Y.pad([f(dg, D3)], beat / 2 * 0.9, 0.9, att=0.005, rel=0.05, bright=3000, nh=10)
            place(out, pan(nn, 0.3 if k % 2 else -0.3), t0)
            t0 += beat / 2
            k += 1
    if cfg.get("organ_stab"):
        t0 = beat * 4
        while t0 < dur:
            place(out, pan(Y.organ([D3, D3 * 2 ** (1 / 12) * 2, D3 * 1.5], beat * 0.9, 0.8), 0.1), t0)
            t0 += beat * 8
    if cfg.get("cornu"):
        t0, k = beat * 2, 0
        notes = [0, 1, 0, -1] if not major else [0, 2, 4, 2]
        while t0 < dur:
            dg = notes[k % len(notes)]
            place(out, pan(Y.cornu(f(dg, D3), beat * 1.5, 0.7), 0.0), t0)
            place(out, pan(Y.cornu(f(dg + 4, D3), beat * 1.5, 0.45), 0.1), t0)
            t0 += beat * 8
            k += 1
    if cfg.get("heart"):
        t0 = 0.0
        while t0 < dur:
            place(out, pan(Y.heartbeat(0.9), 0), t0)
            t0 += 0.85
    av = cfg.get("aulos", 0)
    if av:
        slow = mood in ("sad", "heartbeat", "dark")
        t0 = beat * 4 if not slow else 1.0
        while t0 < dur:
            if r.random() < 0.85:
                ph = melody_phrase(r, int(r.integers(3, 6)))
                durs = r.choice([[1, 1, 2, 1, 3], [0.5, 0.5, 1, 2, 2], [2, 1, 1, 4, 2], [1.5, 0.5, 2, 2, 2]])
                tt = t0
                for dg, dd in zip(ph, durs):
                    ln = dd * beat * (1.6 if slow else 1.0)
                    place(out, pan(Y.aulos(f(dg, D4), ln + 0.15, av * 0.9), 0.15), tt)
                    tt += ln
                t0 = tt + beat * r.choice([2, 4])
            else:
                t0 += beat * 4
    out = out[:n]
    out = Y.reverb(out, cfg.get("wet", 0.3), seconds=2.8, damp=2.6)
    pk = np.abs(out).max() + 1e-9
    return out / pk * 0.5

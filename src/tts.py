"""Yerel Piper TTS ile Turkce seslendirme + zaman cizelgesi (timeline.json).

ElevenLabs KULLANILMAZ. Sesler tamamen yerel, acik kaynak Piper modelleriyle uretilir.
"""
import hashlib
import json
import os
import sys
import wave

import numpy as np
import soundfile as sf

from script import SHOTS, SUB_FIX

WORK = os.environ.get("ZK_WORK", "/home/user/work")
MODELS = os.path.join(WORK, "models")
CACHE = os.path.join(WORK, "tts_cache")
os.makedirs(CACHE, exist_ok=True)

VOICES = {
    "n": ("dfki", dict(length_scale=1.04, noise_scale=0.6, noise_w_scale=0.75)),       # anlatici
    "q": ("fahrettin", dict(length_scale=1.12, noise_scale=0.55, noise_w_scale=0.7)),  # alintilar
}
_loaded = {}


def voice(v):
    from piper import PiperVoice
    name = VOICES[v][0]
    if name not in _loaded:
        d = f"{MODELS}/vits-piper-tr_TR-{name}-medium"
        _loaded[name] = PiperVoice.load(f"{d}/tr_TR-{name}-medium.onnx", config_path=f"{d}/tr_TR-{name}-medium.onnx.json")
    return _loaded[name]


def synth(text, v):
    from piper import SynthesisConfig
    name, cfg = VOICES[v]
    key = hashlib.md5((name + json.dumps(cfg, sort_keys=True) + text).encode()).hexdigest()[:16]
    path = os.path.join(CACHE, f"{key}.wav")
    if not os.path.exists(path):
        raw = path + ".raw.wav"
        with wave.open(raw, "wb") as wf:
            voice(v).synthesize_wav(text, wf, syn_config=SynthesisConfig(**cfg))
        a, sr = sf.read(raw, dtype="float32")
        os.remove(raw)
        # sessizlik kirp
        env = np.convolve(np.abs(a), np.ones(256) / 256, mode="same")
        idx = np.where(env > 0.006)[0]
        if len(idx):
            a = a[max(0, idx[0] - 800): min(len(a), idx[-1] + 4400)]
        # seviye
        rms = np.sqrt(np.mean(a ** 2) + 1e-9)
        a = a * (0.1 / rms)
        pk = np.abs(a).max()
        if pk > 0.95:
            a = a * 0.95 / pk
        sf.write(path, a, sr)
    info = sf.info(path)
    return path, info.frames / info.samplerate


def sub_text(s):
    for k, v in SUB_FIX.items():
        s = s.replace(k, v)
    return s


def build():
    t = 0.0
    out = []
    for sid, fn, lines, extra in SHOTS:
        lead = extra.get("lead", 0.45)
        tail = extra.get("tail", 0.6)
        shot = dict(id=sid, fn=fn, start=round(t, 3), params=extra, lines=[])
        if not lines:
            dur = extra.get("dur", 3.0)
        else:
            cur = lead
            prev_v = None
            for i, ln in enumerate(lines):
                v = "q" if ln.startswith("q:") else "n"
                txt = ln[2:] if v == "q" else ln
                if i > 0:
                    cur += 0.5 if (v != prev_v) else 0.32
                wav, d = synth(txt, v)
                shot["lines"].append(dict(start=round(cur, 3), end=round(cur + d, 3), say=txt, sub=sub_text(txt),
                                          voice=v, wav=wav))
                cur += d
                prev_v = v
            dur = max(cur + tail, extra.get("min_dur", 0))
        shot["dur"] = round(dur, 3)
        t += dur
        out.append(shot)
        print(f"{sid:4s} {fn:20s} {dur:6.2f}s  toplam {t/60:5.2f} dk", flush=True)
    tl = dict(total=round(t, 3), shots=out)
    with open(os.path.join(WORK, "timeline.json"), "w") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    return tl


if __name__ == "__main__":
    build()

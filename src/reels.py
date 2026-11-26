"""Ana videodan en fazla 60 sn'lik dikey (1080x1920) Reels/Shorts kurgusu."""
import json
import os
import subprocess

import numpy as np
import skia
import soundfile as sf
from scipy.signal import resample_poly

import music
import synth as Y
import tts
from gfx import FONT_DIR, big_number, font, label_tag, ribbon, text
from synth import SR, place

WORK = tts.WORK
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "reels_gladyator_okulu.mp4")
RD = os.path.join(WORK, "reels")
os.makedirs(RD, exist_ok=True)
SRC = os.path.join(WORK, "render", "video_noaudio.mp4")

PICK = [("s01", 1), ("s02", 0), ("s03", 0), ("s16", 1), ("s30", 0), ("s47", 0), ("s47", 1), ("s48", 0),
        ("s49", 1), ("s32", 0), ("s28", 1)]
CTA = "Hikayenin tamamı Zaman Kırığı kanalında!"
CTA_SUB = "Hikâyenin tamamı Zaman Kırığı kanalında!"
PRE, POST = 0.15, 0.2


def run(cmd):
    subprocess.run(cmd, check=True)


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def overlay_png(path):
    s = skia.Surface(1080, 1920)
    cv = s.getCanvas()
    cv.clear(skia.ColorTRANSPARENT)
    cv.save()
    cv.translate(540, 300)
    big_number(cv, "MS 160", 0, 0, 190, rot=-2)
    cv.restore()
    ribbon(cv, "GLADYATÖR OLSAYDIN?", 540, 420, 66, rot=-2, maxw=1020)
    label_tag(cv, "@zamankırığıyt", 540, 1800, 40, rot=0)
    s.makeImageSnapshot().save(path, skia.kPNG)


def build():
    tl = json.load(open(os.path.join(WORK, "timeline.json")))
    by = {s["id"]: s for s in tl["shots"]}
    segs, lines = [], []
    t = 0.0
    cwav, cd = tts.synth(CTA, "n")
    for sid, li in PICK:
        sh = by[sid]
        l = sh["lines"][li]
        if t + (l["end"] - l["start"]) + PRE + POST + cd + 1.2 > 59.0:
            continue
        a = sh["start"] + l["start"] - PRE
        d = (l["end"] - l["start"]) + PRE + POST
        segs.append((a, d))
        lines.append(dict(t=t + PRE, wav=l["wav"], sub=l["sub"], d=l["end"] - l["start"]))
        t += d
    # kapanis (abone ol bolumu)
    s66 = by["s56"]
    a = s66["start"] + s66["lines"][1]["start"] + 0.6
    segs.append((a, cd + 1.2))
    lines.append(dict(t=t + 0.3, wav=cwav, sub=CTA_SUB, d=cd))
    total = t + cd + 1.2
    print("reels suresi:", round(total, 2), "sn")
    assert total <= 60.0
    # video parcalari
    parts = []
    for i, (a, d) in enumerate(segs):
        p = os.path.join(RD, f"p{i:02d}.mp4")
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-i", SRC, "-t", f"{d:.3f}", "-an", "-c:v", "libx264",
             "-preset", "fast", "-crf", "16", "-r", "30", p])
        parts.append(p)
    lst = os.path.join(RD, "parts.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    cat = os.path.join(RD, "cat.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", cat])
    # ses
    n = int((total + 0.2) * SR)
    nar = np.zeros((n, 2))
    mask = np.zeros(n)
    for l in lines:
        x, sr = sf.read(l["wav"], dtype="float32")
        x = resample_poly(x, 320, 147).astype(np.float64)
        x = Y.hp(x, 75)
        x = x / (np.abs(x).max() + 1e-9) * 0.85
        place(nar, x, l["t"])
        mask[int(l["t"] * SR):int((l["t"] + l["d"]) * SR)] = 1
    k = int(0.25 * SR)
    c = np.concatenate([[0.0], np.cumsum(mask)])
    idx = np.arange(n)
    mask = (c[np.clip(idx + k // 2, 0, n)] - c[np.clip(idx - k // 2, 0, n)]) / k
    mus = music.gen("arena", total + 0.2, seed=777)[:n]
    mus[:int(10 * SR)] = music.gen("intro", 10.0, seed=778)[:int(10 * SR)] * np.linspace(1, 0.6, int(10 * SR))[:, None] + \
        mus[:int(10 * SR)] * np.linspace(0, 1, int(10 * SR))[:, None]
    mus *= (1 - 0.7 * mask)[:, None]
    fx = np.zeros((n, 2))
    tt = 0.0
    for (a, d) in segs[:-1]:
        tt += d
        place(fx, Y.pan(Y.whoosh(0.45, 1.0, 300, 3000, int(tt * 10)), 0), tt - 0.2, 0.5)
    place(fx, Y.pan(Y.impact(0.8), 0), 0.05, 0.6)
    fo = int(1.0 * SR)
    mus[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix = nar + mus * 0.5 + fx * 0.5
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    wav = os.path.join(RD, "reels.wav")
    sf.write(wav, mix.astype(np.float32), SR, subtype="FLOAT")
    # buyuk altyazilar (3-4 kelimelik parcalar)
    ev = []
    for l in lines:
        words = l["sub"].split()
        chunks, cur = [], []
        for w in words:
            cur.append(w)
            if len(" ".join(cur)) > 18 or w[-1] in ".,?!:":
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        tot = sum(len(x) for x in chunks)
        t0 = l["t"]
        for ch in chunks:
            dd = l["d"] * len(ch) / tot
            ev.append(f"Dialogue: 0,{ass_time(t0)},{ass_time(t0 + dd)},Cap,,0,0,0,,{ch.replace("i", "İ").replace("ı", "I").upper()}")
            t0 += dd
    ass = os.path.join(RD, "caps.ass")
    open(ass, "w", encoding="utf-8").write(
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, "
        "MarginR, MarginV, Encoding\n"
        "Style: Cap,Inter Black,78,&H00FFFFFF,&H00FFFFFF,&H00120A06,&H96000000,1,0,0,0,100,100,0,0,1,7,4,8,60,60,"
        "1330,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
        + "\n".join(ev) + "\n")
    ov = os.path.join(RD, "overlay.png")
    overlay_png(ov)
    fc = ("[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.12[bg];"
          "[b]scale=1080:-2[fg];[bg][fg]overlay=0:620[v1];[v1][2:v]overlay=0:0[v2];"
          f"[v2]ass={ass}:fontsdir={FONT_DIR}[v]")
    run(["ffmpeg", "-y", "-v", "error", "-i", cat, "-i", wav, "-i", ov, "-filter_complex", fc, "-map", "[v]",
         "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest",
         "-movflags", "+faststart", OUT])
    print("reels:", OUT)


if __name__ == "__main__":
    build()

"""Sahneler: Bolum 4 (Egitim) + Bolum 5 (Arpa adamlari) + Bolum 6 (Sohret ve utanc)"""
import math
import random

import skia

import backgrounds as B
import characters as C
import effects as FX
import engine as E
import kit as K
import scenery as S
from gfx import (OUT, W, H, big_number, circle, clamp, ease_in_out, ease_out, ellipse, fill, font, label_tag, lerp,
                 lin_grad, pop, poly, rad_grad, rgb, ribbon, rrect, shade, shape, smooth, speech_bubble, stroke,
                 text, tint, vignette, blur_paint, mix)
from shotkit import bgk, le, lf, lt, nlines, person, talk_on, walk_x, xfade_layers


# =================================================================== BOLUM 4
def swing(t, period=0.7, ph=0.0):
    """0..1 vurus egrisi (hizli vurus, yavas geri cekilme)"""
    f = ((t + ph) % period) / period
    return ease_out(f / 0.25) if f < 0.25 else 1 - ease_in_out((f - 0.25) / 0.75)


def palus(cv, t, d, p):
    t1 = lt(p, 1)
    sun_f = clamp(t / d)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.12, (960, 560), (1000, 600))
    bgk(cv, "ludus_dawn", B.ludus_court, "dawn")
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#ffd8a0", int(40 * (1 - sun_f))))
    hit = 0.0
    if t > t1:
        sw = swing(t - t1, 0.75)
        hit = max(0.0, (sw - 0.85) / 0.15)
        person(cv, "demetrios_tiro", 760, 1080, 1.5, 1, t, seed=1, expr="angry" if sw > 0.6 else "tired",
               arm_b=lerp(170, 70, sw), wpn=lerp(160, 95, sw), arm_a=30, look=(0.7, -0.1), sweat=t > t1 + 3)
        if sw > 0.95:
            FX.impact_star(cv, 1070, 760, t, t - 0.02, 0.6)
    else:
        person(cv, "demetrios_tiro", 760, 1080, 1.5, 1, t, seed=1, expr="worried", arm_b=40, wpn=30,
               look=(0.4, -0.2))
    B.palus_post(cv, 1100, 1060, 1.35, hit * 0.5)
    cv.restore()
    a, b = E.line_t(p, 0)
    K.tag(cv, "RUDIS: TAHTA KILIÇ", 520, 380, t, a + (b - a) * 0.72, 46, rot=-4, t1=t1 + 0.2)
    if t > t1:
        K.tag(cv, "PALUS: KAZIK", 1320, 330, t, lf(p, 1, 0.08), 48, rot=4)
        cnt = int(clamp((t - t1) / (d - t1)) * 600)
        s = pop(t - lf(p, 1, 0.35), 0.4)
        if s > 0:
            cv.save()
            cv.translate(1560, 560)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 330, 150, col="#2a1a10")
            text(cv, f"{cnt}", 0, 10, font("slab", 70), "#e9c46a")
            text(cv, "VURUŞ", 0, 56, font("black", 32), "#f3e3bf")
            cv.restore()
    vignette(cv, 120)


def trainer(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.05, 1.0)
    bgk(cv, "ludus", B.ludus_court)
    gladiators_bg(cv, t)
    crack = (t % 1.6) < 0.25 and t < t1
    person(cv, "trainer", 620, 1090, 1.55, 1, t, seed=2, expr="shout" if t < t1 else "determined",
           talk=talk_on(t, p, [0, 1]), arm_b=150 if crack else 60, wpn=150 if crack else 40, look=(0.7, 0))
    sw = swing(t, 1.2) if t > t1 else 0.0
    person(cv, "demetrios_tiro", 1300, 1080, 1.4, -1, t, seed=1, expr="tired" if t < t1 else "determined",
           sweat=t < t1, arm_b=lerp(60, 130, sw), wpn=lerp(40, 120, sw), look=(0.6, 0))
    cv.restore()
    K.tag(cv, "DOCTOR: HOCA", 620, 360, t, 0.6, 50, rot=-4)
    K.tag(cv, "ESKİ GLADYATÖR", 620, 450, t, 1.2, 38, rot=3)
    if t < t1:
        a = clamp((t - lf(p, 0, 0.4)) / 0.3)
        if a > 0:
            speech_bubble(cv, "Bir daha! Kalkanını kaldır!", 1150, 300, 900, 520, size=44, a=int(255 * a))
    else:
        K.tag(cv, "HER HAREKET = HAYAT", 1300, 300, t, lf(p, 1, 0.5), 48, bg="#ffd23a")
    if crack:
        FX.impact_star(cv, 960, 620, t, t - (t % 1.6), 0.5)
    vignette(cv, 110)


def gladiators_bg(cv, t):
    r = random.Random(3)
    for k in range(4):
        x = 250 + k * 470
        ph = math.sin(t * r.uniform(3, 5) + k)
        nm = ["murmillo", "thraex", "retiarius", "hoplomachus"][k]
        person(cv, nm, x, 860, 0.5, 1 if k % 2 else -1, t, seed=k + 7, expr="angry", arm_a=-24,
               arm_b=80 + ph * 30, wpn=90 + ph * 40)


def types(cv, t, d, p):
    bgk(cv, "studio", B.studio)
    slots = [("murmillo", "MURMILLO", lf(p, 1, 0.02), "#d8e4f0", "ağır piyade"),
             ("thraex", "THRAEX", lf(p, 1, 0.55), "#ead8f0", "çevik, kıvrık kılıç"),
             ("hoplomachus", "HOPLOMACHUS", lf(p, 2, 0.02), "#d8f0d8", "mızrak + yuvarlak kalkan"),
             ("retiarius", "RETIARIUS", lf(p, 3, 0.08), "#f0e0c8", "ağ + zıpkın")]
    K.rib(cv, "GLADYATÖR TÜRLERİ", W / 2, 110, t, 0.3, 58)
    for k, (nm, lab, t0, bc, sub) in enumerate(slots):
        x = 260 + k * 466
        s = pop(t - t0, 0.45)
        if s <= 0:
            continue
        cv.save()
        cv.translate(x, 600)
        cv.scale(s, s)
        K.panel(cv, 0, 0, 420, 700, col=bc)
        ph = math.sin(t * 2.4 + k)
        kw = dict(arm_a=-22, arm_b=70 + ph * 10, wpn=75 + ph * 10)
        if nm == "retiarius":
            kw = dict(arm_a=30, arm_b=40 + ph * 8, wpn=20)
        C.draw_person(cv, C.preset(nm), C.pose(expr="determined", blink=E.blink(t, k), **kw), 0, 250, 1.25, 1)
        label_tag(cv, lab, 0, -300, 46, rot=-2)
        text(cv, sub, 0, 320, font("xb", 34), "#2a1a10")
        cv.restore()
    vignette(cv, 90)


def pairing(cv, t, d, p):
    a, b = E.line_t(p, 0)
    bgk(cv, "arena_day", B.arena)
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", 70))
    pairs = [("murmillo", "thraex", "AĞIR", "ÇEVİK", 0.45, 480), ("secutor", "retiarius", "KALKANLI", "AĞLI", 0.72,
                                                                     1440)]
    for k, (n1, n2, l1, l2, fr, x) in enumerate(pairs):
        t0 = a + (b - a) * (fr - 0.25)
        s = pop(t - t0, 0.45)
        if s <= 0:
            continue
        cv.save()
        cv.translate(x, 560)
        cv.scale(s, s)
        K.panel(cv, 0, 0, 860, 760, col="#fbf3df")
        ph = math.sin((t - t0) * 3.2)
        C.draw_person(cv, C.preset(n1), C.pose(expr="angry", arm_a=-22, arm_b=80 + ph * 25, wpn=90 + ph * 25,
                                               blink=E.blink(t, k)), -190 + ph * 10, 290, 1.15, 1)
        kw2 = dict(arm_a=-22, arm_b=80 - ph * 25, wpn=100 - ph * 25) if n2 != "retiarius" else \
            dict(arm_a=30, arm_b=40 - ph * 10, wpn=20)
        C.draw_person(cv, C.preset(n2), C.pose(expr="angry", blink=E.blink(t, k + 3), **kw2), 190 - ph * 10, 290,
                      1.15, -1)
        label_tag(cv, l1, -190, -320, 40, rot=-3)
        label_tag(cv, l2, 190, -320, 40, rot=3)
        cv.restore()
        K.vs_badge(cv, x, 520, t, t0 + 0.3, 0.8)
    K.rib(cv, "DENK RAKİPLER", W / 2, 110, t, 0.3, 56)
    vignette(cv, 100)


def secutor(cv, t, d, p):
    t1 = lt(p, 1)
    bgk(cv, "studio", B.studio)
    # migfer kafaya iner
    tm = lf(p, 0, 0.25)
    if t < t1:
        f = ease_out(clamp((t - tm) / 0.5))
        person(cv, "secutor" if f >= 1 else "demetrios_tiro", 700, 1060, 1.8, 1, t, seed=1,
               expr="determined", arm_a=-22 if f >= 1 else 14, arm_b=60, wpn=70, look=(0.6, 0),
               weapon="gladius" if f >= 1 else "rudis")
        if 0 < f < 1:
            cv.save()
            cv.translate(700, lerp(-200, 1060 - 1.8 * 212, f))
            cv.scale(1.8, 1.8)
            C.draw_head_front(cv, C.preset("secutor"), C.pose())
            cv.restore()
        K.tag(cv, "SECUTOR = TAKİPÇİ", 1380, 300, t, lf(p, 0, 0.5), 64, rot=-3)
        if t > lf(p, 0, 0.7):
            person(cv, "retiarius", 1640 - (t - lf(p, 0, 0.7)) * 120, 1000, 0.9, 1, t, seed=3, expr="happy",
                   walk=t * 12, arm_a=30, arm_b=40, wpn=20)
            K.arrow_line(cv, 1050, 700, 1400, 700, t, lf(p, 0, 0.72), 0.5)
    else:
        # yakin cekim: migfer
        zf = ease_in_out(clamp((t - t1) / 0.7))
        cv.save()
        cv.translate(W / 2, H / 2)
        z = lerp(1.0, 2.6, zf)
        cv.scale(z, z)
        cv.translate(-lerp(760, 760, zf), -lerp(540, 1060 - 1.5 * 212, zf))
        person(cv, "secutor", 760, 1060, 1.5, 1, t, seed=1, expr="worried", arm_a=-22, arm_b=60, wpn=70,
               look=(0.0, 0.0), bob=math.sin(t * 7) * 1.5, breathe=False)
        cv.restore()
        # nefes buguları
        for k in range(4):
            ph = ((t - t1) * 0.8 + k * 0.25) % 1.0
            cv.drawPath(circle(W / 2 + 40 + ph * 160, 720 - ph * 60, 30 + ph * 70),
                        blur_paint("#ffffff", 20, int(90 * (1 - ph))))
        K.tag(cv, "PÜRÜZSÜZ: AĞ TAKILMAZ", 470, 260, t, lf(p, 1, 0.12), 44, rot=-4)
        K.tag(cv, "İKİ KÜÇÜK GÖZ DELİĞİ", 1450, 300, t, lf(p, 1, 0.4), 44, rot=3)
        K.tag(cv, "NEFES ALMAK ZOR", 1400, 860, t, lf(p, 1, 0.75), 44, rot=-2, bg="#ffd23a")
    vignette(cv, 100)


# =================================================================== BOLUM 5
def barley(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.06)
    bgk(cv, "mess", B.mess)
    for x in (360, 1560):
        B.flame(cv, x, 270, t, 1.0, seed=x)
    B.table(cv, 160, 1300, 930, food=False)
    for k, (nm, x) in enumerate((("thracian", 330), ("egyptian", 620), ("demetrios_tiro", 910), ("galatian", 1180))):
        eat = math.sin(t * 3 + k) > 0.3
        person(cv, nm, x, 1040, 1.05, 1, t, seed=k, seated=True, expr="happy" if k != 2 else "neutral",
               item="bowl", arm_b=110 if eat else 60, wpn=0, weapon=None, mouth=0.4 if eat else 0, look=(0.3, 0.4))
    cv.restore()
    K.rib(cv, "HORDEARII", W / 2, 110, t, lf(p, 0, 0.55), 60, color="#8a6a1a")
    K.txt(cv, "\"arpa adamları\"", W / 2, 210, t, lf(p, 0, 0.62), 46, "#fff4d6", "xb", oc=OUT, ow=4)
    tm = lf(p, 0, 0.25)
    if t < t1 + 0.3:
        s = pop(t - tm, 0.4)
        if s > 0:
            cv.save()
            cv.translate(1600, 430)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 260, 220)
            S.meat(cv, 0, 60, 1.2)
            cv.restore()
            E.cross_out(cv, 1480, 330, 1720, 530, t, tm + 0.3)
    if t > t1:
        items = [("ARPA LAPASI", "bowl"), ("BAKLA", "bean"), ("FASULYE", "bean2")]
        for k, (lab, kind) in enumerate(items):
            def drawfn(c, kind=kind):
                if kind == "bowl":
                    C.draw_item(c, "bowl", 0, 50)
                    c.scale(1.6, 1.6)
                else:
                    r = random.Random(len(kind))
                    for j in range(9):
                        cx, cy = r.uniform(-60, 60), r.uniform(-30, 40)
                        shape(c, ellipse(cx, cy, 16 if kind == "bean" else 12, 11 if kind == "bean" else 8),
                              "#8fae5a" if kind == "bean" else "#c88a6a", w=2.5)
            E.icon_card(cv, 1520, 340 + k * 190, 300, 170, lab, drawfn, t, lf(p, 1, 0.05 + k * 0.12), tsize=32)
        if t > lf(p, 1, 0.55):
            K.tag(cv, "YAĞ TABAKASI = KORUMA?", 760, 330, t, lf(p, 1, 0.6), 46, bg="#ffd23a")
    vignette(cv, 120)


def ephesus_bones(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    if t < t1:
        cv.save()
        E.camera(cv, t, d, 1.0, 1.1, (960, 600), (960, 700))
        bgk(cv, "dig", B.dig)
        r = random.Random(5)
        for k in range(7):
            x, y = 420 + k * 170 + r.uniform(-30, 30), 700 + (k % 3) * 100
            K.skull_holes(cv, x, y, 0.32)
            cv.save()
            cv.translate(x + 60, y + 30)
            cv.rotate(r.uniform(-40, 40))
            shape(cv, rrect(-70, -9, 140, 18, 9), "#efe6cc", w=3)
            shape(cv, circle(-70, 0, 14), "#efe6cc", w=3)
            shape(cv, circle(70, 0, 14), "#efe6cc", w=3)
            cv.restore()
        cv.restore()
        E.year_stamp(cv, "1993", t, 0.5, 1640, 190, 110)
        E.lower_third(cv, "EFES • GLADYATÖR MEZARLIĞI", t, 1.0, t1)
    elif t < t2:
        bgk(cv, "studio", B.studio)
        K.rib(cv, "KEMİK ANALİZİ", W / 2, 110, t, t1 + 0.1, 56, color="#2f6b9a")
        K.bar(cv, 520, 820, 200, 500, 0.85, "#6f9a3a", "BİTKİ", t, t1 + 0.4)
        K.bar(cv, 820, 820, 200, 500, 0.18, "#b0402a", "ET", t, t1 + 0.6)
        tm = lf(p, 1, 0.5)
        if t > tm:
            s = pop(t - tm, 0.45)
            cv.save()
            cv.translate(1390, 540)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 640, 420)
            K.skull_holes(cv, -150, 80, 0.7)
            shape(cv, rrect(-10, -16, 260, 32, 16), "#efe6cc", w=4)
            text(cv, "MİNERAL", 120, -100, font("black", 46), "#2a1a10")
            K.arrow_line(cv, 120, 140, 120, -40, t, tm + 0.3, 0.4, col="#2a9a3a")
            cv.restore()
            K.tag(cv, "KÜL KARIŞIK İÇECEK?", 1390, 830, t, lf(p, 1, 0.8), 44, bg="#ffd23a")
    else:
        cv.save()
        E.camera(cv, t, d, 1.0, 1.06)
        bgk(cv, "ludus", B.ludus_court)
        person(cv, "thracian", 760, 1060, 1.5, 1, t, seed=2, expr="tired", item="cup", arm_b=120, wpn=0,
               bandage=True, look=(0.6, -0.2))
        cv.restore()
        for k in range(4):
            ph = (t * 0.7 + k * 0.25) % 1.0
            cv.drawPath(circle(980 + math.sin(ph * 6 + k) * 20, 560 - ph * 160, 18 + ph * 26),
                        blur_paint("#d8d8d0", 10, int(120 * (1 - ph))))
        K.tag(cv, "PLINIUS", 1400, 280, t, t2 + 0.3, 48)
        K.tag(cv, "BİTKİ KÜLÜ İÇECEĞİ", 1400, 400, t, lf(p, 2, 0.5), 46, bg="#ffd23a", rot=3)
    vignette(cv, 110)


def galen(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.05)
    bgk(cv, "clinic", B.clinic)
    if t < t1:
        person(cv, "galen", 940, 1060, 1.55, 1, t, seed=3, expr="happy", look=(-0.2, 0), arm_b=40, wpn=10)
    else:
        K.lying(cv, "demetrios_tiro", 680, 740, 1.05, t, ang=-90, expr="hurt" if t < t2 else "happy",
                bandage=True, arm_a=20, arm_b=20, weapon=None)
        person(cv, "galen", 1260, 1060, 1.45, -1, t, seed=3, expr="determined", item=None, arm_b=100, wpn=0,
               look=(0.5, 0.4))
        B.amphora(cv, 1560, 1000, 0.9, col="#8a2a3a")
    cv.restore()
    if t < t1:
        K.tag(cv, "GALENOS", 940, 300, t, lf(p, 0, 0.75), 70, rot=-3)
        K.txt(cv, "Bergamalı hekim • gladyatörlerin doktoru", 940, 400, t, lf(p, 0, 0.82), 40, "#2a1a10")
    elif t < t2:
        K.tag(cv, "ŞARAPLI BEZ", 1400, 300, t, lf(p, 1, 0.2), 48, rot=3)
        K.tag(cv, "BESLENME", 1400, 410, t, lf(p, 1, 0.65), 48, rot=-2)
    else:
        s = pop(t - t2 - 0.2, 0.45)
        if s > 0:
            cv.save()
            cv.translate(W / 2, 360)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 860, 420)
            K.bar(cv, -200, 140, 200, 280, 1.0, "#b0402a", "ÖNCESİ", t, t2 + 0.5)
            K.bar(cv, 200, 140, 200, 280, 0.22, "#6f9a3a", "GALENOS", t, t2 + 0.9)
            text(cv, "ÖLEN GLADYATÖRLER", 0, -150, font("black", 40), "#2a1a10")
            cv.restore()
            K.tag(cv, "KENDİ İDDİASI", 1380, 600, t, t2 + 1.4, 38, rot=4)
    vignette(cv, 110)


def investment(cv, t, d, p):
    a, b = E.line_t(p, 0)
    bgk(cv, "studio", B.studio)
    person(cv, "lanista", 520, 1060, 1.5, 1, t, seed=2, expr="happy" if t < a + (b - a) * 0.7 else "worried",
           look=(0.7, 0))
    person(cv, "demetrios_tiro", 1380, 1060, 1.35, -1, t, seed=1, expr="neutral", look=(0.6, 0))
    K.coins_pile(cv, 960, 1000, 18, t, a + (b - a) * 0.3, 1.2, seed=7)
    K.tag(cv, "PAHALI YATIRIM", 1380, 470, t, a + (b - a) * 0.4, 50, rot=3, bg="#ffd23a")
    tm = a + (b - a) * 0.72
    if t > tm:
        s = pop(t - tm, 0.45)
        cv.save()
        cv.translate(W / 2, 200)
        cv.scale(s, s)
        K.panel(cv, 0, 0, 760, 150, col="#2a1a10")
        text(cv, "ÖLÜ GLADYATÖR = 0 DRAHMİ", 0, 18, font("black", 50), "#ff6a5a")
        cv.restore()
    vignette(cv, 100)


# =================================================================== BOLUM 6
def fame(cv, t, d, p):
    t1 = lt(p, 1)
    if t < t1:
        bgk(cv, "studio", B.studio)
        K.rib(cv, "ANTİK ÇAĞIN YILDIZLARI", W / 2, 110, t, 0.3, 56)
        s = pop(t - lf(p, 0, 0.55), 0.5)
        if s > 0:
            cv.save()
            cv.translate(W / 2 - 80, 640)
            cv.scale(2.4 * s, 2.4 * s)
            K.oil_lamp(cv, 0, 0, 1.0, t, relief=True)
            cv.restore()
            K.tag(cv, "GLADYATÖR RESİMLİ KANDİL", W / 2, 840, t, lf(p, 0, 0.7), 44)
        person(cv, "thraex", 300, 1060, 1.2, 1, t, seed=3, expr="happy", arm_a=-22, arm_b=150, wpn=160)
        K.hearts(cv, t, lf(p, 0, 0.2), 300, 600, 6, seed=1)
    else:
        bgk(cv, "street_day", B.street, "day")
        tt = t - t1
        txt_ = "CELADVS THRAEX"
        txt2 = "SVSPIRIVM PVELLARVM"
        n1 = int(clamp(tt / 1.2) * len(txt_))
        n2 = int(clamp((tt - 1.2) / 1.6) * len(txt2))
        text(cv, txt_[:n1], W / 2, 450, font("bevan", 110), "#8a2a1a", a=230)
        text(cv, txt2[:n2], W / 2, 600, font("bevan", 90), "#8a2a1a", a=230)
        K.tag(cv, "POMPEII DUVAR YAZISI", 380, 300, t, t1 + 0.2, 44, rot=-4)
        tm = lf(p, 1, 0.6)
        s = pop(t - tm, 0.45)
        if s > 0:
            cv.save()
            cv.translate(W / 2, 760)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 1100, 130, col="#fbf3df")
            text(cv, "\"Trakyalı Celadus, kızların iç çektiği adam\"", 0, 16, font("xb", 46), "#2a1a10")
            cv.restore()
        K.hearts(cv, t, tm + 0.3, W / 2, 700, 8, seed=2)
    vignette(cv, 100)


def infamia(cv, t, d, p):
    a, b = E.line_t(p, 0)
    bgk(cv, "studio", B.studio)
    rungs = [("SENATÖRLER", "#e9c46a"), ("VATANDAŞLAR", "#e8dcc0"), ("OYUNCULAR", "#d8c0b0"),
             ("GLADYATÖRLER", "#b0402a")]
    for k, (lab, col) in enumerate(rungs):
        t0 = a + (b - a) * (0.25 + k * 0.15)
        s = pop(t - t0, 0.4)
        if s <= 0:
            continue
        cv.save()
        cv.translate(1300, 260 + k * 190)
        cv.scale(s, s)
        w_ = 700 - k * 60
        K.panel(cv, 0, 0, w_, 130, col=col, r=14)
        text(cv, lab, 0, 18, font("black", 50), "#2a1a10" if k < 3 else "#ffffff")
        cv.restore()
    person(cv, "demetrios_tiro", 480, 1060, 1.5, 1, t, seed=1, expr="sad", look=(0.7, 0.2), weapon=None)
    K.arrow_line(cv, 760, 830, 920, 830, t, a + (b - a) * 0.85, 0.4)
    vignette(cv, 100)


def family(cv, t, d, p):
    a, b = E.line_t(p, 0)
    bgk(cv, "museum", B.museum)

    def rel(c):
        C.draw_person(c, C.preset("retiarius"), C.pose(arm_a=30, arm_b=40, wpn=20), 0, -270, 0.95, 1)
    K.stele(cv, W / 2 + 60, 1020, 1.25, relief=rel, lines=4)
    person(cv, "woman", 520, 1060, 1.45, 1, t, seed=2, expr="sad", look=(0.7, -0.2), tears=t > a + (b - a) * 0.6)
    K.tag(cv, "MEZAR TAŞI", 1500, 300, t, a + (b - a) * 0.4, 46, rot=3)
    K.tag(cv, "EŞİ YAPTIRDI", 520, 360, t, a + (b - a) * 0.75, 50, rot=-4, bg="#ffd23a")
    vignette(cv, 120)


def women(cv, t, d, p):
    t1 = lt(p, 1)
    bgk(cv, "museum", B.museum)
    s = pop(t - 0.3, 0.6)
    if s > 0:
        cv.save()
        cv.translate(W / 2, 560)
        cv.scale(s, s)
        col = "#d8ccb0"
        slab = rrect(-640, -330, 1280, 640, 10)
        cv.drawPath(rrect(-630, -318, 1280, 640, 10), fill((0, 0, 0), 120))
        cv.drawPath(slab, lin_grad((-640, 0), (640, 0), [shade(col, 0.85), shade(col, 1.06), shade(col, 0.9)]))
        cv.drawPath(slab, stroke(OUT, 6))
        shape(cv, rrect(-600, -260, 1200, 480, 6), shade(col, 0.9), w=3)

        def rel(c):
            C.draw_person(c, C.preset("amazon"), C.pose(arm_a=-24, arm_b=90, wpn=100, expr="determined"),
                          -240, 210, 1.3, 1)
            C.draw_person(c, C.preset("achillia"), C.pose(arm_a=-24, arm_b=90, wpn=100, expr="determined"),
                          240, 210, 1.3, -1)
            for sx in (-1, 1):
                c.save()
                c.translate(sx * 520, 170)
                c.scale(0.8, 0.8)
                C.draw_head_front(c, C.preset("murmillo"), C.pose())
                c.restore()
        cv.save()
        cv.clipPath(rrect(-600, -260, 1200, 480, 6), skia.ClipOp.kIntersect, True)
        K.stone_layer(cv, rel, col)
        cv.restore()
        for sx, nm in ((-1, "AMAZON"), (1, "ACHILLIA")):
            text(cv, nm, sx * 240, -280, font("bold", 34), shade(col, 0.45))
        if t > t1:
            text(cv, "ΑΠΕΛΥΘΗΣΑΝ", 0, 300, font("bold", 34), shade(col, 0.45))
        cv.restore()
    K.tag(cv, "HALİKARNASSOS (BODRUM)", 520, 100, t, lf(p, 0, 0.35), 44, rot=-3)
    if t > t1:
        K.tag(cv, "\"BAĞIŞLANDILAR\"", W / 2, 1010, t, t1 + 0.6, 50, bg="#ffd23a")
        K.txt(cv, "Bugün British Museum'da", 1640, 1040, t, t1 + 1.0, 30, "#cfc8be", "bold")
    vignette(cv, 120)

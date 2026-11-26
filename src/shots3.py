"""Sahneler: Bolum 7 (Oyun gunu) + Bolum 8 (Arena) + Bolum 9 (Ozgurluk ya da mezar) + kapanis"""
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
from shots1 import hourglass, heartbeat_vignette


def lion_head(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    pts = []
    for k in range(18):
        a = k / 18 * math.tau
        r = 70 if k % 2 == 0 else 56
        pts.append((math.cos(a) * r, math.sin(a) * r))
    shape(cv, poly(pts), "#a8622a", w=4)
    shape(cv, circle(0, 4, 44), "#e8b060", w=4)
    for sx in (-1, 1):
        cv.drawPath(circle(sx * 16, -6, 6), fill(OUT))
    shape(cv, poly([(-10, 12), (10, 12), (0, 22)]), "#5a3a22", w=2)
    cv.drawLine(0, 22, -10, 32, stroke(OUT, 3))
    cv.drawLine(0, 22, 10, 32, stroke(OUT, 3))
    cv.restore()


def crossed_swords(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    for sg in (-1, 1):
        C.draw_weapon(cv, C.preset("murmillo"), sg * 34, 40, sg * -40, "gladius")
    cv.restore()


def referees(cv, t, xs=(260, 1660), y=860, s=0.8):
    for k, x in enumerate(xs):
        person(cv, "referee", x, y, s, 1 if x < W / 2 else -1, t, seed=20 + k, expr="determined", arm_b=10, wpn=4,
               look=(0.6, 0))


def cornu(cv, x, y, s=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.drawPath(circle(0, 0, 70), stroke(OUT, 18))
    cv.drawPath(circle(0, 0, 70), stroke("#d9a548", 11))
    cv.drawLine(-20, -10, 40, 50, stroke("#6a4424", 8))
    shape(cv, poly([(60, -60), (110, -110), (122, -80)]), "#d9a548", w=3)
    cv.restore()


def hydraulis(cv, x, y, s=1.0, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    shape(cv, rrect(-120, -120, 240, 120, 10), "#8a5a2e", w=4)
    for k in range(11):
        h_ = 120 + 80 * math.sin(k / 10 * math.pi)
        shape(cv, rrect(-100 + k * 19, -120 - h_, 14, h_, 6), "#d9c070", w=2.5)
    shape(cv, ellipse(0, 6, 140, 26), "#5a5a60", w=3)
    cv.restore()


# =================================================================== BOLUM 7
def announcement(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.05)
    bgk(cv, "street_day", B.street, "day")
    lines_ = [("ASYA BAŞRAHİBİ SUNAR:", 80, 380, 0.05, 0.3), ("İMPARATOR ONURUNA OYUNLAR!", 80, 500, 0.3, 0.65),
              ("20 ÇİFT GLADYATÖR • HAYVAN AVLARI • GÜNEŞ PERDESİ", 44, 600, 0.65, 0.95)]
    pen = None
    for (s_, size, y, f0, f1) in lines_:
        a0, a1 = lf(p, 0, f0), lf(p, 0, f1)
        n = int(clamp((t - a0) / (a1 - a0)) * len(s_))
        if n > 0:
            f = font("bevan", size)
            full = f.measureText(s_)
            x0 = 960 - full / 2
            text(cv, s_[:n], x0, y, f, "#a8201a", align="left", a=235)
            if n < len(s_):
                pen = (x0 + f.measureText(s_[:n]), y)
    if pen is None and t < t1:
        pen = (1500, 600)
    if pen:
        person(cv, "citizen4", pen[0] + 60, 1060, 1.15, -1, t, seed=3, expr="happy", arm_b=150, wpn=140,
               look=(0.6, -0.4), weapon="staff")
    cv.restore()
    if t > t1:
        icons = [("HAYVAN AVLARI", lambda c: lion_head(c, 0, 0, 1.0)), ("İDAMLAR", lambda c: K.skull_holes(c, 0, 30, 0.45)),
                 ("GLADYATÖRLER", lambda c: crossed_swords(c, 0, -10, 1.2))]
        for k, (lab, fn) in enumerate(icons):
            E.icon_card(cv, 480 + k * 480, 860, 360, 300, lab, fn, t, lf(p, 1, 0.05 + k * 0.25), tsize=36)
    vignette(cv, 110)


def last_supper(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.08, (960, 580), (1000, 600))
    bgk(cv, "banquet", B.banquet)
    for x in (200, 960, 1720):
        B.torch_holder(cv, x, 620)
        B.flame(cv, x, 540, t, 1.0, seed=x)
    for k, nm in enumerate(("citizen", "woman2", "citizen3", "citizen2", "woman", "citizen4")):
        x = 120 + k * 340
        person(cv, nm, x, 820, 0.75, 1 if k % 2 else -1, t, seed=30 + k, expr="happy", look=(0.3, 0.3))
    crew = [("thracian", 420), ("demetrios_tiro", 760), ("galatian", 1100), ("egyptian", 1440)]
    for k, (nm, x) in enumerate(crew):
        eat = math.sin(t * 4 + k) > 0.2 and nm == "thracian"
        talk = talk_on(t, p, [1]) if (nm == "galatian" and t > lf(p, 1, 0.55)) else 0.0
        person(cv, nm, x, 1010, 1.1, 1 if k < 2 else -1, t, seed=k, seated=True,
               expr="happy" if nm == "thracian" else ("sad" if nm == "demetrios_tiro" else "worried"),
               arm_b=120 if eat else 30, wpn=0, weapon=None, mouth=0.5 if eat else 0.0, talk=talk,
               look=(0.4, 0.3) if nm != "galatian" else (0.7, 0))
    B.table(cv, 180, 1700, 960, food=True, seed=5)
    cv.restore()
    K.rib(cv, "SON AKŞAM YEMEĞİ", W / 2, 110, t, 0.4, 58, color="#5a1a40")
    if t > t1:
        K.tag(cv, "TIKA BASA", 420, 420, t, lf(p, 1, 0.05), 40, rot=-4)
        K.tag(cv, "TEK LOKMA YOK", 760, 470, t, lf(p, 1, 0.22), 40, rot=3)
        a = clamp((t - lf(p, 1, 0.55)) / 0.3)
        if a > 0:
            speech_bubble(cv, "Karımı sana emanet ediyorum...", 1400, 320, 1160, 560, size=40, a=int(255 * a))
        K.tag(cv, "PLUTARKHOS", 1600, 480, t, lf(p, 1, 0.4), 36, rot=4)
    vignette(cv, 140)


def morning(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    bgk(cv, "arena_day", B.arena)
    B.arena_crowd_overlay(cv, t, excite=0.4 + 0.5 * (t > t1))
    if t > t1:
        ph = math.sin(t * 3)
        person(cv, "murmillo", 760 + ph * 20, 1050, 1.0, 1, t, seed=3, expr="angry", arm_a=-24,
               arm_b=90 + ph * 30, wpn=100 + ph * 30)
        person(cv, "thraex", 1160 - ph * 20, 1050, 1.0, -1, t, seed=4, expr="angry", arm_a=-24,
               arm_b=90 - ph * 30, wpn=110 - ph * 30)
    cv.restore()
    # zaman cizelgesi
    s = pop(t - 0.3, 0.45)
    if s > 0:
        cv.save()
        cv.translate(W / 2, 180)
        cv.scale(s, s)
        K.panel(cv, 0, 0, 1640, 230, col="#fbf3df")
        cv.drawLine(-700, 30, 700, 30, stroke("#c9a040", 8))
        fr = clamp(t / d)
        S.sun(cv, -700 + 1400 * fr, -50 - math.sin(fr * math.pi) * 20, 26)
        items = [("SABAH", "HAYVAN AVI", -540, 0.1), ("ÖĞLE", "İDAMLAR", 0, 0.55),
                 ("ÖĞLEDEN SONRA", "GLADYATÖRLER", 540, None)]
        for k, (when, what, x, ff) in enumerate(items):
            t0 = lf(p, 0, ff) if ff is not None else t1 + 0.3
            if t > t0:
                a = clamp((t - t0) / 0.3)
                text(cv, when, x, 10, font("black", 36), "#8a2a1a", a=int(255 * a))
                text(cv, what, x, 76, font("black", 48), "#2a1a10", a=int(255 * a))
                if k < 2:
                    lion_head(cv, x + 230, 40, 0.4) if k == 0 else K.skull_holes(cv, x + 220, 60, 0.22)
        cv.restore()
    if t > t1:
        FX.flash(cv, t, t1 + 0.3, 0.3, "#fff2c0", 140)
    vignette(cv, 110)


def parade(cv, t, d, p):
    t1 = lt(p, 1)
    if t < t1 + 0.2:
        cv.save()
        E.camera(cv, t, d, 1.0, 1.04)
        bgk(cv, "arena_day", B.arena)
        B.arena_crowd_overlay(cv, t, excite=0.6)
        hydraulis(cv, 1690, 900, 0.9, t)
        person(cv, "citizen", 1690, 1010, 0.9, -1, t, seed=9, expr="happy", arm_a=60, arm_b=60, look=(0, 0.3))
        x0 = 700 + t * 170
        order = ["citizen2", "citizen4", "murmillo", "thraex", "retiarius", "secutor", "hoplomachus"]
        for k, nm in enumerate(order):
            x = x0 - k * 220
            if -200 < x < 2100:
                kw = dict(arm_a=-20, arm_b=24, wpn=10) if nm not in ("citizen2", "citizen4") else \
                    dict(arm_a=20, arm_b=110, wpn=0)
                person(cv, nm, x, 1060, 0.95, 1, t, seed=k, walk=t * 8 + k, expr="determined", **kw)
                if nm in ("citizen2", "citizen4"):
                    cornu(cv, x + 34, 1060 - 0.95 * 160, 0.5)
        cv.restore()
        K.tag(cv, "BORU (CORNU)", 420, 330, t, lf(p, 0, 0.3), 42, rot=-4)
        K.tag(cv, "SU ORGU (HYDRAULIS)", 1600, 300, t, lf(p, 0, 0.6), 42, rot=4)
    else:
        bgk(cv, "arena_day", B.arena)
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", 60))
        person(cv, "asiarch", 1500, 1060, 1.4, -1, t, seed=3, expr="determined", look=(0.6, 0.2),
               arm_b=80, wpn=30)
        person(cv, "referee", 500, 1060, 1.4, 1, t, seed=4, expr="determined", weapon="gladius", arm_b=100,
               wpn=60, look=(0.8, -0.2))
        K.tag(cv, "SİLAH KONTROLÜ", W / 2, 140, t, t1 + 0.4, 54)
        for k, (lab, fr) in enumerate((("KESKİN", 0.45), ("GERÇEK", 0.62))):
            t0 = lf(p, 1, fr)
            s = pop(t - t0, 0.4)
            if s > 0:
                cv.save()
                cv.translate(W / 2, 360 + k * 150)
                cv.scale(s, s)
                K.panel(cv, 0, 0, 460, 120)
                text(cv, lab, -40, 18, font("black", 54), "#2a1a10")
                cv.restore()
                E.check_mark(cv, W / 2 + 160, 360 + k * 150, 1.0, t, t0 + 0.2)
        K.tag(cv, "HİLE YOK", W / 2, 690, t, lf(p, 1, 0.85), 56, bg="#ffd23a")
    vignette(cv, 110)


# =================================================================== BOLUM 8
def gate_open(cv, t, d, p):
    t1 = lt(p, 1)
    tg = lf(p, 0, 0.45)
    if t < tg + 0.4:
        cv.save()
        z = lerp(1.0, 1.6, ease_in_out(clamp((t - lf(p, 0, 0.2)) / (tg - lf(p, 0, 0.2) + 0.4))))
        cv.translate(W / 2, H / 2)
        cv.scale(z, z)
        cv.translate(-W / 2, -560)
        bgk(cv, "tunnel", B.tunnel)
        lift = ease_in_out(clamp((t - lf(p, 0, 0.12)) / 1.6))
        B.portcullis(cv, 620, 1300, 250, 900, lift)
        cv.restore()
        FX.light_rays(cv, 960, 420, t, n=9, a=int(40 + 80 * clamp((t - lf(p, 0, 0.2)) / 1.0)), length=1100)
        if t > tg:
            cv.drawRect(skia.Rect.MakeWH(W, H), fill("#fff8e0", int(255 * clamp((t - tg) / 0.4))))
    else:
        cv.save()
        E.camera(cv, t, d, 1.12, 1.0, (960, 620), (960, 540))
        bgk(cv, "arena_day", B.arena)
        B.arena_crowd_overlay(cv, t, excite=0.8)
        referees(cv, t, (180, 1740), 900, 0.85)
        sx, mv = walk_x(t, tg + 0.4, tg + 2.0, 200, 560)
        person(cv, "secutor", sx, 1080, 1.4, 1, t, seed=1, expr="worried", walk=t * 8 if mv else None,
               arm_a=-20, arm_b=30, wpn=20, look=(0.8, 0))
        tw = math.sin(t * 2.4) * 16
        person(cv, "retiarius", 1360, 1080, 1.4, -1, t, seed=3, expr="happy", arm_a=24, arm_b=40, wpn=12 + tw,
               look=(0.6, 0))
        cv.restore()
        FX.flash(cv, t, tg + 0.4, 0.5, "#fff8e0", 255)
        if t > t1:
            K.tag(cv, "RETIARIUS", 1360, 330, t, lf(p, 1, 0.05), 54, rot=3)
            K.tag(cv, "ÇEVİK, HAFİF", 1360, 430, t, lf(p, 1, 0.2), 40, rot=-2)
            K.tag(cv, "SUMMA RUDIS", 300, 380, t, lf(p, 1, 0.5), 40, rot=-4)
            K.tag(cv, "SECUNDA RUDIS", 1650, 560, t, lf(p, 1, 0.62), 36, rot=4)
            K.tag(cv, "KURALLAR VAR!", W / 2, 170, t, lf(p, 1, 0.85), 50, bg="#ffd23a")
    vignette(cv, 120)


def fight_positions(t):
    rx = 1220 + math.sin(t * 0.9) * 300
    sx = rx - 470 + math.sin(t * 0.9 - 0.7) * 90
    return sx, rx


def fight(cv, t, d, p):
    t1 = lt(p, 1)
    sx, rx = fight_positions(t)
    thrust_t = lf(p, 1, 0.08)
    slash_t = lf(p, 1, 0.55)
    th = clamp(1 - abs(t - thrust_t - 0.2) / 0.35)
    sl = clamp(1 - abs(t - slash_t - 0.2) / 0.3)
    cam_x = (sx + rx) / 2
    cv.save()
    E.camera(cv, t, d, 1.18, 1.18, (cam_x, 640), (cam_x, 640), ease=False)
    if abs(t - thrust_t - 0.3) < 0.2 or abs(t - slash_t - 0.3) < 0.2:
        E.shake(cv, t, 7)
    bgk(cv, "arena_day", B.arena)
    B.arena_crowd_overlay(cv, t, excite=0.7 + 0.3 * (t > t1))
    referees(cv, t, (cam_x - 700, cam_x + 700), 880, 0.75)
    FX.ground_dust(cv, sx - 100, rx + 100, 1080, t, col="#e8cf98", a=70, seed=2, density=8)
    moving = th < 0.1 and sl < 0.1
    person(cv, "secutor", sx + th * -20, 1080, 1.35, 1, t, seed=1, expr="determined" if sl < 0.1 else "shout",
           walk=t * 10 if moving else None, arm_a=-20 + th * -10, arm_b=lerp(40, 150, sl), wpn=lerp(40, 160, sl),
           look=(0.8, 0), bob=math.sin(t * 9) * 3, breathe=False)
    person(cv, "retiarius", rx + th * -60 + sl * 50, 1080, 1.35, -1, t, seed=3,
           expr="angry" if th > 0.1 else ("scared" if sl > 0.1 else "happy"), walk=t * 11 if moving else None,
           arm_a=28, arm_b=lerp(40, 80, th), wpn=lerp(20, 95, th), lean=th * -8 + sl * 10, look=(0.7, 0))
    FX.sparks(cv, sx + 90, 820, t, thrust_t + 0.25, 1.2, seed=3)
    FX.impact_star(cv, sx + 90, 820, t, thrust_t + 0.25, 1.0)
    cv.restore()
    if t < t1:
        # nefes / kalp vignette (miğfer içi)
        cv.drawPath(rrect(-200, -200, W + 400, H + 400, 0), fill("#000000", 0))
        heartbeat_vignette(cv, t, lf(p, 0, 0.5), 60)
    K.tag(cv, "TAKİP!", 300, 200, t, lf(p, 0, 0.18), 52, rot=-5, t1=t1 - 0.3)
    vignette(cv, 120)


def net(cv, t, d, p):
    t1 = lt(p, 1)
    throw_t = lf(p, 0, 0.05)
    land_t = throw_t + 0.8
    fall_t = lf(p, 0, 0.72)
    sx, rx = 760, 1260
    cv.save()
    zf = ease_in_out(clamp((t - t1) / 1.0))
    E.camera(cv, t, d, lerp(1.15, 1.25, zf), lerp(1.15, 1.25, zf), (lerp(1000, 900, zf), lerp(640, 820, zf)),
             None, ease=False)
    bgk(cv, "arena_day", B.arena)
    B.arena_crowd_overlay(cv, t, excite=1.0)
    fall = ease_in(clamp((t - fall_t) / 0.45))
    if fall <= 0:
        person(cv, "secutor", sx, 1080, 1.35, 1, t, seed=1, expr="scared" if t > throw_t + 0.3 else "determined",
               arm_a=-20, arm_b=40, wpn=40, look=(0.8, -0.3), lean=-6 * clamp((t - land_t) / 0.5))
    else:
        K.lying(cv, "secutor", sx + 150 * fall, 1080, 1.35, t, ang=-88 * fall, expr="scared", arm_a=-10,
                arm_b=60, wpn=60, look=(0.0, -0.8))
    if fall >= 1:
        FX.ground_dust(cv, sx - 260, sx + 260, 1090, t, col="#e8cf98", a=90, seed=5, density=6)
    # retiarius
    if t < t1:
        thr = ease_out(clamp((t - throw_t) / 0.4))
        person(cv, "retiarius", rx, 1080, 1.35, -1, t, seed=3, expr="shout" if thr < 1 else "happy",
               arm_a=lerp(28, 150, thr), arm_b=40, wpn=20, net_thrown=t > throw_t + 0.1, look=(0.8, 0))
    else:
        wx, mv = walk_x(t, t1, t1 + 0.8, rx, 1000)
        person(cv, "retiarius", wx, 1080, 1.35, -1, t, seed=3, expr="angry", walk=t * 9 if mv else None,
               arm_a=28, arm_b=78, wpn=118, look=(0.6, 0.6), net_thrown=True)
    # ag ucusu
    if t > throw_t:
        f = clamp((t - throw_t) / 0.8)
        if f < 1:
            nx = lerp(rx - 120, sx, ease_out(f))
            ny = lerp(780, 820, f) - math.sin(f * math.pi) * 200
            K.net_shape(cv, nx, ny, lerp(50, 190, f), lerp(40, 150, f), rot=f * 120)
        else:
            if fall <= 0:
                K.net_shape(cv, sx, 840, 190, 230, rot=0)
            else:
                cx_ = sx + 150 * fall - 250 * fall
                K.net_shape(cv, cx_, 1060 - 230 * (1 - fall), lerp(190, 300, fall), lerp(230, 110, fall))
    cv.restore()
    K.tag(cv, "AĞ!", 1300, 260, t, throw_t + 0.2, 70, rot=-6, t1=t1)
    if t > t1:
        heartbeat_vignette(cv, t, t1, 120)
    vignette(cv, 140)


def ease_in(x):
    x = clamp(x)
    return x * x


def finger(cv, t, d, p):
    t1 = lt(p, 1)
    if t < t1:
        bgk(cv, "arena_day", B.arena)
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", 70))
        cv.drawRect(skia.Rect.MakeWH(W, H), blur_paint("#e6c98e", 60, 120))
        fu = ease_out(clamp((t - lf(p, 0, 0.62)) / 0.6))
        K.hand(cv, W / 2, 620 + (1 - fu) * 60, 1.5, finger=fu, glove=True)
        K.tag(cv, "AD DIGITUM: TESLİM!", W / 2, 150, t, lf(p, 0, 0.3), 54)
        heartbeat_vignette(cv, t, 0.0, 120)
    else:
        bgk(cv, "arena_day", B.arena)
        B.arena_crowd_overlay(cv, t, excite=1.0)
        cv.save()
        cv.translate(W / 2, 0)
        look = math.sin((t - t1) * 1.6)
        person(cv, "asiarch", 0, 600, 1.0, 1, t, seed=3, expr="worried", look=(look, 0.1))
        cv.restore()
        K.tag(cv, "BAŞRAHİP", W / 2, 230, t, t1 + 0.2, 44)
        tq = lf(p, 1, 0.45)
        if t > tq:
            s = pop(t - tq, 0.45)
            cv.save()
            cv.translate(W / 2, 860)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 900, 300, col="#fbf3df")
            K.thumb_icon(cv, -200, 30, 1.2, down=False)
            K.thumb_icon(cv, 200, -10, 1.2, down=True)
            cv.restore()
            K.tag(cv, "ANLAMI BELİRSİZ", W / 2, 1020, t, lf(p, 1, 0.75), 44, bg="#ffd23a")
    vignette(cv, 130)


def missio(cv, t, d, p):
    t1 = lt(p, 1)
    bgk(cv, "arena_day", B.arena)
    B.arena_crowd_overlay(cv, t, excite=1.0, n=110)
    r = random.Random(4)
    if t < t1 + 1.0:
        for k in range(8):
            t0 = 0.3 + k * 0.35
            a = clamp((t - t0) / 0.2) * (1 - clamp((t - t0 - 1.4) / 0.3))
            if a > 0:
                x, y = r.uniform(250, 1670), r.uniform(150, 520)
                cv.save()
                cv.translate(x, y)
                s = pop(t - t0, 0.3)
                cv.scale(s, s)
                speech_bubble(cv, "BIRAK ONU!", 0, 0, r.uniform(-40, 40), 90, size=40, a=int(255 * a))
                cv.restore()
    if t > t1:
        up = ease_out(clamp((t - t1 - 0.3) / 0.5))
        person(cv, "asiarch", 1500, 760, 0.95, -1, t, seed=3, expr="happy", arm_b=lerp(30, 170, up), wpn=0,
               look=(0.5, 0.2))
        rise = ease_out(clamp((t - lf(p, 1, 0.4)) / 0.8))
        if rise > 0:
            person(cv, "secutor", 560, 1080 + (1 - rise) * 200, 1.4, 1, t, seed=1, expr="happy", arm_a=-10,
                   arm_b=20, wpn=10, look=(0.5, -0.3), bandage=True)
        K.rib(cv, "MISSIO", W / 2, 700, t, lf(p, 1, 0.55), 90, color="#2a8a3a")
        K.txt(cv, "Bugün ölmeyeceksin.", W / 2, 840, t, lf(p, 1, 0.8), 56, "#fff4d6", "black", oc=OUT, ow=5)
    vignette(cv, 120)


def death_rule(cv, t, d, p):
    t1 = lt(p, 1)
    if t < t1:
        cv.drawRect(skia.Rect.MakeWH(W, H), lin_grad((0, 0), (0, H), ["#2a0a0a", "#7a2a1a", "#d8783a"]))
        S.sun(cv, W / 2, 760, 160, col="#ffcf8a", glow="#ff7a3a", ga=180)
        cv.drawRect(skia.Rect.MakeLTRB(0, 860, W, H), fill("#1a0c08"))

        def kneel(c):
            person(c, "murmillo", 820, 900, 1.6, 1, t, seed=1, seated=True, expr="sad", arm_a=10, arm_b=10,
                   weapon=None, shield=None, breathe=False)
            person(c, "thraex", 1180, 880, 1.6, -1, t, seed=2, expr="angry", arm_a=-20, arm_b=160, wpn=170,
                   breathe=False)
        C.draw_silhouette(cv, kneel, glow="#ffb070", glow_a=160)
        K.tag(cv, "ONURLU ÖLÜM", W / 2, 180, t, lf(p, 0, 0.45), 54, bg="#2a1a10", fg="#f3e3bf")
    else:
        bgk(cv, "museum", B.museum)
        hf = clamp((t - lf(p, 1, 0.3)) / 0.6)
        K.skull_holes(cv, W / 2, 700, 2.0, holes=hf)
        if t > lf(p, 1, 0.7):
            a = clamp((t - lf(p, 1, 0.7)) / 0.4)
            cv.saveLayerAlpha(None, int(170 * a))
            C.draw_weapon(cv, C.preset("retiarius"), W / 2, 950, 0, "trident")
            cv.restore()
        K.tag(cv, "EFES", 520, 260, t, t1 + 0.2, 58, rot=-4)
        K.tag(cv, "3 DELİK", 1400, 300, t, lf(p, 1, 0.55), 52, rot=4, bg="#ffd23a")
    vignette(cv, 150)


# =================================================================== BOLUM 9
def odds(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    bgk(cv, "studio", B.studio)
    K.rib(cv, "HAYATTA KALMA ŞANSI", W / 2, 110, t, 0.3, 58)
    if t < t1:
        K.tag(cv, "HER DÖVÜŞ ÖLÜMLE BİTMEZDİ", W / 2, 540, t, lf(p, 0, 0.55), 64, bg="#ffd23a")
        person(cv, "secutor", 300, 1060, 1.2, 1, t, seed=1, expr="happy", arm_a=-20, arm_b=30, wpn=20)
        person(cv, "retiarius", 1620, 1060, 1.2, -1, t, seed=3, expr="happy", arm_a=28, arm_b=40, wpn=20)
    else:
        s = pop(t - t1 - 0.1, 0.45)
        if s > 0:
            cv.save()
            cv.translate(420, 480)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 520, 420)
            text(cv, "YILDA", 0, -120, font("black", 50), "#2a1a10")
            big_number(cv, "2–3", 0, 40, 150)
            text(cv, "DÖVÜŞ", 0, 150, font("black", 50), "#2a1a10")
            cv.restore()
        tg = lf(p, 1, 0.45)
        for k in range(10):
            s2 = pop(t - tg - k * 0.07, 0.3)
            if s2 <= 0:
                continue
            x, y = 900 + (k % 5) * 190, 340 + (k // 5) * 260
            dead = k == 9 and t > lf(p, 1, 0.8)
            ext = 1.0
            if t > t2 and k in (7, 8):
                dead = t > t2 + 0.4 + (k - 7) * 0.3
            cv.save()
            cv.translate(x, y)
            cv.scale(s2 * 0.62, s2 * 0.62)
            p_ = skia.Paint()
            if dead:
                p_.setColorFilter(skia.ColorFilters.Blend(rgb("#b0141a"), skia.BlendMode.kSrcIn))
            cv.saveLayer(None, p_)
            C.draw_head_front(cv, C.preset("secutor"), C.pose())
            cv.restore()
            cv.restore()
        K.tag(cv, "~1/10 (1. YÜZYIL, TAHMİN)", 1280, 740, t, lf(p, 1, 0.85), 40, rot=-2)
        if t > t2:
            K.arrow_line(cv, 1820, 640, 1820, 300, t, t2 + 0.2, 0.5, col="#b0141a")
            K.tag(cv, "ZAMANLA ARTTI", 1500, 220, t, t2 + 0.4, 44, rot=3, bg="#ffd23a")
            s3 = pop(t - lf(p, 2, 0.5), 0.45)
            if s3 > 0:
                cv.save()
                cv.translate(1280, 880)
                cv.scale(s3, s3)
                K.panel(cv, 0, 0, 900, 170, col="#2a1a10")
                text(cv, "EFES: ÇOĞU 20–30 YAŞINDA", 0, 18, font("black", 50), "#f3e3bf")
                cv.restore()
    vignette(cv, 100)


def diodorus(cv, t, d, p):
    t1 = lt(p, 1)
    bgk(cv, "museum", B.museum)

    def rel(c):
        C.draw_person(c, C.preset("murmillo"), C.pose(arm_a=-20, arm_b=60, wpn=40), 0, -270, 0.95, 1)
    cv.save()
    sx = W / 2
    K.stele(cv, sx, 1030, 1.2, relief=rel, lines=5)
    cv.restore()
    K.tag(cv, "DİODOROS", sx, 160, t, 0.6, 58, rot=-3)
    if t > t1 - 0.2:
        E.quote_card(cv, "Rakibim Demetrios'u yere serdim, ama hemen öldürmedim. Beni öldüren, kader ve hakemin "
                         "hilesi oldu.", "Diodoros'un mezar taşı", t, t1, y=1050, size=44)
        K.portrait_card(cv, 1560, 420, 260, 300, t, lf(p, 1, 0.7), "referee", "HAKEM", bgcol="#f0d8d0",
                        ps_scale=1.0, dy=30, pose=dict(expr="happy", look=(-0.5, 0)))
    vignette(cv, 130)


def rudis(cv, t, d, p):
    t1 = lt(p, 1)
    if t < t1:
        cv.save()
        E.camera(cv, t, d, 1.0, 1.08)
        bgk(cv, "arena_golden", B.arena, "golden")
        B.arena_crowd_overlay(cv, t, excite=0.8)
        give = ease_out(clamp((t - lf(p, 0, 0.3)) / 0.8))
        person(cv, "asiarch", 1150, 1060, 1.35, -1, t, seed=3, expr="happy", arm_b=lerp(40, 85, give), wpn=90,
               weapon="rudis" if give < 1 else None, look=(0.5, 0))
        person(cv, "demetrios_free", 700, 1060, 1.4, 1, t, seed=1, expr="happy", weapon="rudis" if give >= 1 else None,
               arm_b=150 if give >= 1 else 40, wpn=10, look=(0.6, -0.2), tears=give >= 1)
        cv.restore()
        if give >= 1:
            K.rib(cv, "RUDIS = ÖZGÜRLÜK", W / 2, 150, t, lf(p, 0, 0.3) + 0.8, 64, color="#2a8a3a")
            K.hearts(cv, t, lf(p, 0, 0.3) + 0.9, 700, 500, 6, seed=3)
    else:
        bgk(cv, "studio", B.studio)
        K.portrait_card(cv, 560, 560, 620, 760, t, t1 + 0.1, "trainer", "HOCA OLDU", bgcol="#e8dcc0", ps_scale=1.6,
                        dy=-120, pose=dict(expr="happy", arm_b=60, wpn=40))
        K.portrait_card(cv, 1360, 560, 620, 760, t, lf(p, 1, 0.45), "murmillo", "YENİDEN ARENAYA",
                        bgcol="#f0d0b0", ps_scale=1.5, dy=-120, pose=dict(expr="happy", arm_a=-20, arm_b=150, wpn=170))
        if t > lf(p, 1, 0.6):
            K.coins_pile(cv, 1620, 900, 10, t, lf(p, 1, 0.6), 0.9, seed=4)
    vignette(cv, 110)


def homecoming(cv, t, d, p):
    a, b = E.line_t(p, 0)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.08, (960, 560), (900, 600))
    bgk(cv, "harbor_sunset", B.harbor, "sunset")
    S.ship(cv, 1400, 800, 0.7, t)
    dx, mv = walk_x(t, 0.2, 3.5, -200, 760)
    person(cv, "demetrios_free", dx, 1070, 1.35, 1, t, seed=1, expr="happy", walk=t * 8 if mv else None,
           arm_b=20, wpn=150, look=(0.6, 0))
    mx, mv2 = walk_x(t, 2.0, 4.0, 2100, 1100)
    person(cv, "mother", mx, 1060, 1.15, -1, t, seed=2, expr="happy", walk=t * 9 if mv2 else None,
           tears=t > 4.0, arm_a=60 if not mv2 else 14, arm_b=60 if not mv2 else 14, look=(0.6, 0))
    kx, mv3 = walk_x(t, 2.3, 4.2, 2200, 1320)
    person(cv, "sister", kx, 1060, 1.0, -1, t, seed=3, expr="happy", walk=t * 11 if mv3 else None,
           arm_a=150 if not mv3 else 40, arm_b=150 if not mv3 else 40, look=(0.6, -0.2))
    cv.restore()
    K.tag(cv, "YARA İZLERİ", 560, 420, t, a + (b - a) * 0.55, 40, rot=-4)
    K.tag(cv, "BİR SÜRÜ HİKÂYE", 1300, 300, t, a + (b - a) * 0.8, 44, rot=3)
    if t > 4.3:
        K.hearts(cv, t, 4.3, 1000, 600, 6, seed=9)
    vignette(cv, 120)


def outro(cv, t, d, p):
    t1 = lt(p, 1)
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H * 0.4), 1300, ["#3a2414", "#1e130b", "#0a0604"]))
    FX.embers(cv, t, 30)
    a, b = E.line_t(p, 0)
    if t < t1 + 0.2:
        opts = [("A", "RETIARIUS", 0.4, "retiarius", dict(arm_a=30, arm_b=40, wpn=20)),
                ("B", "MURMILLO", 0.62, "murmillo", dict(arm_a=-22, arm_b=80, wpn=90)),
                ("C", "THRAEX", 0.86, "thraex", dict(arm_a=-22, arm_b=80, wpn=90))]
        for k, (letter, lab, fr, nm, kw) in enumerate(opts):
            x = 400 + k * 560
            s = pop(t - (a + (b - a) * fr), 0.45)
            if s <= 0:
                continue
            cv.save()
            cv.translate(x, 560)
            cv.scale(s, s)
            cv.drawPath(rrect(-230, -330, 460, 660, 30), fill("#f4e6c4"))
            cv.drawPath(rrect(-230, -330, 460, 660, 30), stroke("#d9a83a", 8))
            cv.save()
            cv.clipPath(rrect(-230, -330, 460, 660, 30), skia.ClipOp.kIntersect, True)
            C.draw_person(cv, C.preset(nm), C.pose(expr="determined", blink=E.blink(t, k), **kw), 0, 250, 1.15, 1)
            cv.restore()
            cv.drawPath(circle(-180, -280, 46), fill("#c8202a"))
            cv.drawPath(circle(-180, -280, 46), stroke(OUT, 4))
            text(cv, letter, -180, -262, font("slab", 52), "#ffffff")
            label_tag(cv, lab, 0, 300, 40)
            cv.restore()
        K.rib(cv, "SEN HANGİSİ OLURDUN?", W / 2, 110, t, 0.3, 58)
    else:
        tt = t - t1
        s = pop(tt - 0.1, 0.6)
        cv.save()
        cv.translate(W / 2, 330)
        cv.scale(s * 0.9, s * 0.9)
        hourglass(cv, 0, 0, 1.0, t)
        cv.restore()
        text(cv, "ZAMAN KIRIĞI", W / 2, 560, font("deco", 76), "#e9c46a", a=int(255 * clamp(tt / 0.5)),
             shadow=(3, 5, 6, 160))
        text(cv, "Yorumlarda buluşalım!", W / 2, 640, font("xb", 46), "#f3e3bf", a=int(255 * clamp((tt - 0.4) / 0.5)))
        bs = pop(tt - 1.0, 0.5)
        if bs > 0:
            clicked = tt > 3.2
            sc = bs * (0.94 if 3.0 < tt < 3.3 else 1.0)
            cv.save()
            cv.translate(W / 2, 800)
            cv.scale(sc, sc)
            col = "#cc0000" if not clicked else "#5a5a5a"
            cv.drawPath(rrect(-260, -60, 520, 120, 60), fill(col))
            cv.drawPath(rrect(-260, -60, 520, 120, 60), stroke("#ffffff", 4))
            text(cv, "ABONE OL" if not clicked else "ABONE OLUNDU", 35, 18, font("black", 52 if not clicked else 42),
                 "#ffffff")
            cv.drawPath(smooth([(-225, 20), (-221, -10), (-205, -26), (-189, -10), (-185, 20)]), fill("#ffffff"))
            cv.drawPath(circle(-205, 28, 6), fill("#ffffff"))
            cv.restore()
            cx = lerp(1500, W / 2 + 160, ease_in_out((tt - 1.6) / 1.2))
            cy = lerp(1000, 830, ease_in_out((tt - 1.6) / 1.2))
            if tt > 1.4:
                pth = poly([(cx, cy), (cx, cy + 56), (cx + 14, cy + 42), (cx + 26, cy + 66), (cx + 36, cy + 60),
                            (cx + 24, cy + 38), (cx + 44, cy + 38)])
                cv.drawPath(pth, fill("#ffffff"))
                cv.drawPath(pth, stroke("#000000", 3))
            if clicked:
                FX.impact_star(cv, W / 2 + 160, 830, t, t1 + 3.2, 1.0)
        fo = clamp((t - (d - 0.8)) / 0.8)
        if fo > 0:
            cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", int(255 * fo)))

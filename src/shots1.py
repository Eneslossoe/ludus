"""Sahneler: Giris + Bolum 1 (Yunan'da gladyator mu?) + Bolum 2 (Okula dusmek) + Bolum 3 (Ludus)"""
import math
import random

import skia

import backgrounds as B
import characters as C
import effects as FX
import engine as E
import kit as K
import maps as M
import scenery as S
from gfx import (OUT, W, H, big_number, circle, clamp, ease_in_out, ease_out, ellipse, fill, font, label_tag, lerp,
                 lin_grad, pop, poly, rad_grad, rgb, ribbon, rrect, shade, shape, smooth, speech_bubble, stroke,
                 text, tint, vignette, blur_paint, mix)
from shotkit import bgk, le, lf, lt, nlines, person, talk_on, walk_x, xfade_layers


# =================================================================== ortak
def hourglass(cv, x, y, s=1.0, t=0.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(s, s)
    cv.drawPath(circle(0, 0, 150), fill("#1a120c"))
    cv.drawPath(circle(0, 0, 150), stroke("#d9a83a", 8))
    cv.drawPath(circle(0, 0, 136), stroke("#d9a83a", 2))
    for sy in (-1, 1):
        cv.drawPath(rrect(-70, sy * 100 - 10, 140, 20, 6), fill("#c9963a"))
        cv.drawPath(rrect(-70, sy * 100 - 10, 140, 20, 6), stroke(OUT, 3))
    g = skia.Path()
    g.moveTo(-52, -90)
    g.lineTo(52, -90)
    g.cubicTo(52, -40, 8, -20, 8, 0)
    g.cubicTo(8, 20, 52, 40, 52, 90)
    g.lineTo(-52, 90)
    g.cubicTo(-52, 40, -8, 20, -8, 0)
    g.cubicTo(-8, -20, -52, -40, -52, -90)
    g.close()
    cv.drawPath(g, fill("#fff6e0", 60))
    cv.drawPath(g, stroke("#f0d090", 4))
    f = (t * 0.15) % 1.0
    cv.drawPath(poly([(-44 * (1 - f) - 4, -88 + f * 70), (44 * (1 - f) + 4, -88 + f * 70), (4, -14), (-4, -14)]),
                fill("#e8b040"))
    cv.drawPath(poly([(-50, 88), (50, 88), (12 + f * 30, 88 - 30 - f * 30), (-12 - f * 30, 88 - 30 - f * 30)]),
                fill("#e8b040"))
    cv.drawLine(0, -14, 0, 88, stroke("#e8b040", 3))
    for sx in (-1, 1):
        cv.drawLine(sx * 62, -92, sx * 62, 92, stroke("#c9963a", 8))
    cv.restore()


def chapter(cv, t, d, p):
    E.chapter_card(cv, t, d, p["num"], p["title"], p.get("sub"))
    fo = clamp((t - (d - 0.35)) / 0.35)
    if fo > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", int(200 * fo)))


def heartbeat_vignette(cv, t, t0, a=110):
    if t < t0:
        return
    hb = 0.5 + 0.5 * math.sin((t - t0) * 7.5)
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H / 2), 1200, [rgb("#ff0000", 0), rgb("#ff0000", 0),
                                                                    rgb("#a00000", int(a * hb))], [0, 0.6, 1]))


# =================================================================== GIRIS
def hook_tunnel(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.14, (960, 560), (900, 520))
    bgk(cv, "tunnel", B.tunnel)
    # kapinin ardinda isik titresimi + kalabalik kollari
    cv.save()
    arch = skia.Path()
    arch.addRect(skia.Rect.MakeLTRB(620, 250, 1300, 900))
    cv.clipPath(arch, skia.ClipOp.kIntersect, True)
    B.arena_crowd_overlay(cv, t, 620, 1300, 380, 600, n=40, seed=5, excite=0.4 + 0.4 * (t > t1))
    cv.restore()
    FX.light_rays(cv, 960, 420, t, n=9, a=40, length=1100, spread=50, base_ang=90)
    B.portcullis(cv, 620, 1300, 250, 900, 0.0)
    FX.embers(cv, t, 22, col="#ffe0a0")
    # sen: secutor (soldan)
    hb = math.sin(t * (6 if t > t2 else 2.2)) * (3 if t > t2 else 1.6)
    person(cv, "secutor", 560, 1090, 1.45, 1, t, seed=1, expr="worried", look=(0.8, -0.2), arm_a=-18, arm_b=24,
           wpn=10, bob=hb, breathe=False)
    cv.restore()
    E.year_stamp(cv, "MS 160", t, 0.5, 1640, 190, 104)
    E.lower_third(cv, "BERGAMA • ROMA'NIN ASYA EYALETİ", t, 1.1, t1 - 0.2)
    if t > t2:
        for k, (s_, x, y, fr) in enumerate((("TUNÇ MİĞFER", 760, 380, 0.08), ("KISA KILIÇ", 860, 860, 0.3),
                                             ("BÜYÜK KALKAN", 300, 760, 0.42))):
            K.tag(cv, s_, x, y, t, lf(p, 2, fr), 38, rot=-4 + k * 3, t1=d - 0.4)
    heartbeat_vignette(cv, t, lf(p, 2, 0.6), 90)
    vignette(cv, 150)


def hook_opponent(cv, t, d, p):
    a, b = E.line_t(p, 0)
    cv.save()
    E.camera(cv, t, d, 1.08, 1.0, (960, 600), (960, 540))
    bgk(cv, "arena_day", B.arena)
    B.arena_crowd_overlay(cv, t, excite=0.6)
    tw = math.sin(t * 2.0) * 14
    person(cv, "retiarius", 960, 1130, 1.6, 1, t, seed=3, expr="happy", look=(-0.3, 0), arm_a=24, arm_b=40,
           wpn=12 + tw)
    cv.restore()
    for k, (lab, x, y, fr) in enumerate((("MİĞFER", 360, 330, 0.16), ("KALKAN", 360, 640, 0.32))):
        s = pop(t - lf(p, 0, fr), 0.4)
        if s > 0:
            cv.save()
            cv.translate(x, y)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 340, 120)
            text(cv, lab, 0, 16, font("black", 52), "#2a1a10")
            cv.restore()
            E.cross_out(cv, x - 150, y - 50, x + 150, y + 50, t, lf(p, 0, fr) + 0.3)
    K.tag(cv, "AĞ", 720, 760, t, lf(p, 0, 0.66), 56, rot=4)
    K.tag(cv, "ÜÇ DİŞLİ ZIPKIN", 1520, 300, t, lf(p, 0, 0.82), 50, rot=-3)
    vignette(cv, 120)


def hook_question(cv, t, d, p):
    t2 = lt(p, 1)
    zf = ease_in_out((t - t2) / 0.8) if t > t2 else 0.0
    z = 1.0 + 0.5 * zf
    cv.save()
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-lerp(960, 1300, zf), -lerp(540, 600, zf))
    left = poly([(0, 0), (1060, 0), (860, H), (0, H)])
    right = poly([(1060, 0), (W, 0), (W, H), (860, H)])
    cv.save()
    cv.clipPath(left, skia.ClipOp.kIntersect, True)
    bgk(cv, "harbor_day", B.harbor, "day")
    person(cv, "demetrios", 470, 1130, 1.55, 1, t, expr="worried" if t < t2 else "scared", look=(0.7, -0.1))
    cv.restore()
    cv.save()
    cv.clipPath(right, skia.ClipOp.kIntersect, True)
    bgk(cv, "arena_day", B.arena)
    person(cv, "secutor", 1300, 1120, 1.35, 1, t, seed=2, expr="determined", look=(0.6, 0), arm_a=-22, arm_b=70,
           wpn=80)
    person(cv, "retiarius", 1680, 1120, 1.35, -1, t, seed=4, expr="angry", look=(0.6, 0), arm_a=20, arm_b=60,
           wpn=40)
    cv.restore()
    zig = [(1060, -20), (1000, 300), (1040, 330), (950, 700), (990, 720), (860, 1100)]
    cv.drawPath(poly(zig, closed=False), stroke("#ffffff", 22))
    cv.drawPath(poly(zig, closed=False), stroke("#ffe680", 9))
    label_tag(cv, "İZMİRLİ BİR GENÇ", 300, 990, 44, rot=-5)
    label_tag(cv, "GLADYATÖR", 1500, 990, 50, rot=4)
    cv.restore()
    a = 1.0 - clamp((t - t2) / 0.4)
    if a > 0:
        cv.saveLayerAlpha(None, int(255 * a))
        K.num(cv, "160", W / 2, 210, t, 0.15, 180, rot=-2)
        K.rib(cv, "GLADYATÖR OLSAYDIN?", W / 2, 310, t, 0.45, 62)
        cv.restore()
    if t > t2:
        r = random.Random(2)
        for k in range(6):
            s = pop(t - t2 - 0.5 - k * 0.18, 0.4)
            if s > 0:
                x, y = 900 + r.uniform(-500, 600), 250 + r.uniform(-120, 200)
                cv.save()
                cv.translate(x, y)
                cv.scale(s, s)
                cv.rotate(r.uniform(-20, 20))
                text(cv, "?", 0, 0, font("slab", r.uniform(90, 160)), "#ffd23a", oc=OUT, ow=7, shadow=(4, 6, 0, 120))
                cv.restore()
        heartbeat_vignette(cv, t, t2)
    hz = lf(p, 1, 0.55)
    if t > hz:
        f = clamp((t - hz) / (d - hz))
        cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H / 2), 900 * (1.2 - f), [rgb("#fff2c0", 0),
                                                                                       rgb("#fff2c0", int(220 * f))]))
    vignette(cv, 120)


def title_card(cv, t, d, p):
    cv.drawRect(skia.Rect.MakeWH(W, H), rad_grad((W / 2, H * 0.4), 1300, ["#3a2414", "#1e130b", "#0a0604"]))
    FX.light_rays(cv, W / 2, -100, t, n=12, a=40, length=1300, spread=80)
    FX.embers(cv, t, 40)
    s = pop(t - 0.1, 0.6)
    cv.save()
    cv.translate(W / 2, 290)
    cv.scale(s, s)
    hourglass(cv, 0, 0, 1.0, t)
    cv.restore()
    a = int(255 * clamp((t - 0.5) / 0.5))
    text(cv, "ZAMAN KIRIĞI", W / 2, 540, font("deco", 70), "#e9c46a", a=a, shadow=(3, 5, 6, 160))
    K.rib(cv, "ANTİK YUNAN'DA GLADYATÖR OLSAYDIN?", W / 2, 690, t, 0.9, 62, maxw=1750)
    a3 = int(255 * clamp((t - 1.5) / 0.5))
    text(cv, "Roma Anadolusu  •  Bergama, MS 160", W / 2, 840, font("xb", 48), "#f3e3bf", a=a3)
    FX.flash(cv, t, 0.05, 0.35, "#fff2c0", 180)
    fo = clamp((t - (d - 0.5)) / 0.5)
    if fo > 0:
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#000000", int(255 * fo)))


# =================================================================== BOLUM 1
def wrestle(cv, t, x, y, s=1.0):
    ph = math.sin(t * 3.0)
    person(cv, "athlete", x - 90 * s + ph * 10, y, 1.05 * s, 1, t, seed=1, expr="determined", lean=8 + ph * 4,
           arm_a=-40, arm_b=110, look=(0.6, 0))
    person(cv, "athlete2", x + 90 * s + ph * 10, y, 1.05 * s, -1, t, seed=2, expr="angry", lean=8 - ph * 4,
           arm_a=-30, arm_b=100, look=(0.6, 0))


def greek_vs_roman(cv, t, d, p):
    t1 = lt(p, 1)

    def greek(c):
        c.save()
        E.camera(c, t, d, 1.0, 1.06)
        bgk(c, "olympia", B.olympia)
        wrestle(c, t, 760, 1000, 1.25)
        rx = (t * 260) % 2600 - 300
        person(c, "athlete", rx, 860, 0.7, 1, t, seed=5, walk=t * 14, arm_a=50, arm_b=50, expr="happy")
        c.restore()
        K.rib(c, "OLİMPİYAT OYUNLARI", W / 2, 130, t, 0.3, 58, color="#2f6b9a")
        for k, (s_, fr) in enumerate((("KOŞU", 0.55), ("GÜREŞ", 0.7), ("PANKRATION", 0.84))):
            K.tag(c, s_, 1500, 500 + k * 110, t, lf(p, 0, fr), 46, rot=-3 + k * 2)
        tg = lf(p, 0, 0.25)
        if t > tg:
            s = pop(t - tg, 0.4)
            c.save()
            c.translate(1500, 330)
            c.scale(s, s)
            K.panel(c, 0, 0, 430, 96, col="#fbeaea")
            text(c, "GLADYATÖR?", 0, 16, font("black", 46), "#a01818")
            c.restore()
            E.cross_out(c, 1300, 290, 1700, 370, t, tg + 0.5, w=10)

    def roman(c):
        bgk(c, "studio_dark", B.dark_studio, "#4a2a1a", "#120a06")
        c.save()
        c.translate(W / 2, 980)
        # cenaze ates/mezar
        shape(c, rrect(-120, -240, 240, 240, 10), "#b8a888", w=4)
        shape(c, poly([(-140, -240), (0, -320), (140, -240)]), "#c8b898", w=4)
        c.restore()
        S.campfire(c, W / 2, 1000, t, 0.6)
        ph = math.sin((t - t1) * 3.2)
        person(c, "murmillo", 560 + ph * 20, 1040, 1.3, 1, t, seed=3, expr="angry", arm_a=-24, arm_b=90 + ph * 30,
               wpn=100 + ph * 30)
        person(c, "thraex", 1360 - ph * 20, 1040, 1.3, -1, t, seed=4, expr="angry", arm_a=-24, arm_b=90 - ph * 30,
               wpn=110 - ph * 30)
        K.rib(c, "ROMA GELENEĞİ", W / 2, 130, t, t1 + 0.2, 60)
        K.tag(c, "CENAZE OYUNLARI", W / 2, 260, t, lf(p, 1, 0.45), 48)

    xfade_layers(cv, t, t1 - 0.25, 0.45, greek, roman)
    vignette(cv, 120)


def spread_map(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    v = M.MapView(24.5, 38.5, 16)
    cv.save()
    zf = ease_in_out(clamp((t - t1 + 0.4) / 1.2))
    z = lerp(1.0, 1.25, zf)
    cx, cy = lerp(960, 1150, zf), lerp(540, 560, zf)
    cv.translate(W / 2, H / 2)
    cv.scale(z, z)
    cv.translate(-cx, -cy)
    M.draw_map_base(cv, v, "med_east", rivers=False)
    M.region_label(cv, v, "İTALYA", 42.6, 13.8, 40)
    M.region_label(cv, v, "YUNANİSTAN", 39.6, 22.0, 36)
    M.region_label(cv, v, "ANADOLU", 39.2, 33.0, 50)
    M.place(cv, v, "Roma", t, 0.3, star=True)
    M.route(cv, v, [(41.9, 12.5), (40.2, 17.5), (38.3, 21.8), (37.9, 22.9)], t, 0.9, 1.4, col="#b01818")
    M.place(cv, v, "Korint", t, 2.0)
    M.place(cv, v, "Atina", t, 2.2, dy=36)
    M.route(cv, v, [(37.9, 23.5), (38.6, 25.5), (38.9, 26.9)], t, 2.3, 1.0, col="#b01818")
    M.place(cv, v, "Bergama", t, 3.2)
    M.place(cv, v, "Efes", t, 3.4, dy=36)
    M.route(cv, v, [(37.5, 24.5), (35.2, 30.5), (36.0, 35.4)], t, t1, 1.2, col="#7a2a8a")
    M.place(cv, v, "Antakya", t, t1 + 1.1)
    cv.restore()
    K.portrait_card(cv, 1560, 330, 300, 360, t, t1 + 1.3, "antiochus", "KRAL ANTİOKHOS", bgcol="#e0c8f0",
                    ps_scale=1.05, dy=-8, pose=dict(expr="happy", look=(-0.4, 0)))
    K.tag(cv, "MÖ 2. YÜZYIL", 1560, 590, t, t1 + 1.8, 38, rot=3)
    if t > t2:
        for k, (ex, lab, fr) in enumerate((("scared", "DEHŞET", 0.3), ("neutral", "ALIŞTI", 0.55),
                                          ("happy", "BAYILDI!", 0.8))):
            x = 450 + k * 520
            K.portrait_card(cv, x, 760, 330, 380, t, lf(p, 2, fr), "citizen2" if k != 1 else "citizen", lab,
                            bgcol=["#f0c0b0", "#e8dcc0", "#c8e8b0"][k], ps_scale=1.2, dy=40,
                            pose=dict(expr=ex, mouth=0.6 if ex == "happy" else 0.0, look=(0, 0)))
        K.tag(cv, "LIVIUS", 1700, 1000, t, t2 + 0.3, 36, rot=-4)
    vignette(cv, 110)


def greek_cities(cv, t, d, p):
    t1 = lt(p, 1)

    def mp(c):
        v = M.MapView(28.4, 38.6, 6.0)
        c.save()
        z = lerp(1.0, 1.08, clamp(t / t1))
        c.translate(W / 2, H / 2)
        c.scale(z, z)
        c.translate(-W / 2, -H / 2)
        M.draw_map_base(c, v, "asia", rivers=False)
        M.region_label(c, v, "ASYA EYALETİ", 39.6, 30.6, 54, rot=-3)
        for k, (nm, lab, fr) in enumerate((("Efes", "Efes", 0.42), ("Bergama", "Bergama", 0.55),
                                           ("Smyrna", "İzmir (Smyrna)", 0.68), ("Afrodisias", "Afrodisias", 0.82))):
            M.place(c, v, nm, t, lf(p, 0, fr), size=40, label=lab, star=(nm == "Bergama"))
        c.restore()

    def th(c):
        c.save()
        E.camera(c, t, d, 1.15, 1.0, (960, 640), (960, 540))
        bgk(c, "theater", B.theater)
        ph = math.sin(t * 3.4)
        person(c, "murmillo", 820 + ph * 16, 1020, 0.85, 1, t, seed=3, expr="angry", arm_a=-24, arm_b=90 + ph * 30,
               wpn=100 + ph * 30)
        person(c, "thraex", 1100 - ph * 16, 1020, 0.85, -1, t, seed=4, expr="angry", arm_a=-24, arm_b=90 - ph * 30,
               wpn=110 - ph * 30)
        c.restore()
        K.tag(c, "TİYATRO → ARENA", 400, 170, t, t1 + 0.3, 46)
        tg = lf(p, 1, 0.45)
        s = pop(t - tg, 0.5)
        if s > 0:
            c.save()
            c.translate(W / 2, 330)
            c.scale(s, s)
            K.panel(c, 0, 0, 900, 220, col="#fbf3df")
            text(c, "μονομάχος", 0, -10, font("black", 96), "#7a1a12")
            text(c, "monomakhos = teke tek dövüşen", 0, 70, font("xb", 44), "#2a1a10")
            c.restore()

    xfade_layers(cv, t, t1 - 0.3, 0.45, mp, th)
    vignette(cv, 110)


def philosophers(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.08, (960, 560), (1000, 540))
    bgk(cv, "theater", B.theater)
    B.arena_crowd_overlay(cv, t, 0, W, 200, 700, n=60, seed=7, excite=0.3 + 0.7 * (t > t1))
    s_ph = lerp(1.0, 0.8, clamp((t - t1) / 0.6))
    person(cv, "philosopher", 380, 1100, 1.5 * s_ph, 1, t, seed=2, expr="angry" if t < t1 else "sad",
           talk=talk_on(t, p, [0]), look=(0.6, 0), arm_b=70, arm_a=10, wpn=-10)
    for k, nm in enumerate(("citizen2", "citizen4", "woman2", "citizen")):
        x = 1050 + k * 230
        person(cv, nm, x, 1120 + (k % 2) * 30, 1.15, -1, t, seed=10 + k,
               expr="shout" if t > t1 else "happy", arm_a=60 if t > t1 else 14,
               arm_b=150 + math.sin(t * 8 + k) * 20 if t > t1 else 20, look=(0.5, -0.3))
    cv.restore()
    if t < t1 + 0.6:
        a = 1 - clamp((t - t1) / 0.4)
        speech_bubble(cv, "Ne utanç verici!", 560, 330, 470, 560, size=44, a=int(255 * a))
    if t > t1:
        K.bar(cv, 1240, 300, 520, 60, 1.0, "#c8202a", "KALABALIK", t, t1 + 0.3, vertical=False)
        K.bar(cv, 1240, 400, 520, 60, 0.08, "#4f6f8f", "FİLOZOFLAR", t, t1 + 0.3, vertical=False)
    vignette(cv, 120)


# =================================================================== BOLUM 2
def smyrna(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.1, 1.0, (1100, 520), (960, 540))
    bgk(cv, "harbor_day", B.harbor, "day")
    S.ship(cv, 1350, 820, 0.7, t)
    S.ship(cv, 1750, 780, 0.45, t + 2)
    x, mv = walk_x(t, t1 - 0.2, t1 + 2.0, -150, 700)
    person(cv, "mother", 260, 1000, 0.95, 1, t, seed=2, expr="happy", look=(0.6, 0))
    person(cv, "demetrios", x, 1060, 1.25, 1, t, seed=1, expr="happy", walk=t * 9 if mv else None,
           look=(0.5, 0) if mv else (-0.2, 0.1), item="cup" if False else None)
    cv.restore()
    E.lower_third(cv, "SMYRNA • BUGÜNKÜ İZMİR", t, 0.4, t1 + 0.2)
    if t > t1 + 1.2:
        K.tag(cv, "DEMETRİOS", min(x, 700), 520, t, t1 + 1.2, 60)
    K.tag(cv, "ÇÖMLEKÇİ AİLESİ", 1500, 300, t, lf(p, 1, 0.6), 44, rot=3)
    vignette(cv, 110)


def debt(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.08, (960, 560), (900, 560))
    bgk(cv, "shop", B.shop)
    # babanin anisi: kucuk mezar tasi kandil
    K.oil_lamp(cv, 260, 760, 0.8, t)
    person(cv, "mother", 560, 1060, 1.15, 1, t, seed=2, expr="sad", tears=t > lf(p, 0, 0.4), look=(0.4, 0.2))
    person(cv, "sister", 760, 1060, 1.0, 1, t, seed=3, expr="worried", look=(0.5, 0))
    person(cv, "demetrios", 960, 1080, 1.3, 1, t, seed=1, expr="worried" if t < t1 else "scared", look=(0.7, 0),
           sweat=t > t1)
    cx, mv = walk_x(t, lf(p, 0, 0.45), lf(p, 0, 0.75), 2100, 1450)
    person(cv, "creditor", cx, 1080, 1.3, -1, t, seed=4, expr="angry", walk=t * 8 if mv else None,
           talk=talk_on(t, p, [1]), arm_b=60 if t > t1 else 14, wpn=40)
    if t > t1:
        cx2, mv2 = walk_x(t, t1 + 0.2, t1 + 1.2, 2200, 1720)
        person(cv, "citizen2", cx2, 1040, 1.15, -1, t, seed=5, expr="angry", walk=t * 8 if mv2 else None,
               item="scroll")
    cv.restore()
    tb = lf(p, 0, 0.62)
    if t > tb:
        for k in range(6):
            s = pop(t - tb - k * 0.12, 0.35)
            if s <= 0:
                continue
            cv.save()
            cv.translate(1100 + (k % 3) * 160, 200 + (k // 3) * 150)
            cv.scale(s, s)
            cv.rotate((k - 3) * 5)
            S.scroll_shape(cv, 0, 0, 120, 80)
            cv.drawPath(circle(0, 10, 16), fill("#b01818"))
            cv.drawPath(circle(0, 10, 16), stroke(OUT, 3))
            cv.restore()
        K.rib(cv, "BORÇLAR", 1260, 120, t, tb + 0.4, 60)
    vignette(cv, 130)


def four_roads(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    bgk(cv, "studio", B.studio)
    K.rib(cv, "OKULA NASIL DÜŞÜLÜR?", W / 2, 120, t, 0.3, 58)
    cards = [("thracian", "SAVAŞ ESİRİ", lf(p, 1, 0.05), "#e8c8b0"),
             ("galatian", "MAHKÛM SUÇLU", lf(p, 1, 0.38), "#d8d0e8"),
             ("egyptian", "SATILMIŞ KÖLE", lf(p, 1, 0.72), "#e8dcb0"),
             ("demetrios", "GÖNÜLLÜ", lf(p, 2, 0.35), "#ffe08a")]
    for k, (nm, lab, t0, bc) in enumerate(cards):
        x = 290 + k * 447
        K.portrait_card(cv, x, 560, 380, 520, t, t0, nm, lab, bgcol=bc, ps_scale=1.45, dy=60,
                        pose=dict(expr="sad" if k < 3 else "determined", look=(0.2, 0)))
        if k < 3 and t > t0 + 0.3:
            K.chains(cv, x - 120, 740, x + 120, 740, 1.0)
    if t > lf(p, 2, 0.4):
        s = pop(t - lf(p, 2, 0.4), 0.4)
        cv.drawPath(rrect(1631 - 200, 290, 400, 540, 30), stroke("#ffd23a", 10 * s))
        K.tag(cv, "PARA KARŞILIĞI", 1631, 900, t, lf(p, 2, 0.6), 40, bg="#ffd23a")
    vignette(cv, 100)


def lucian(cv, t, d, p):
    a, b = E.line_t(p, 0)
    bgk(cv, "studio", B.studio)
    # sol: Karadeniz haritasi madalyonu
    s = pop(t - 0.2, 0.5)
    if s > 0:
        cv.save()
        cv.translate(520, 520)
        cv.scale(s, s)
        clip = circle(0, 0, 330)
        cv.drawPath(circle(8, 12, 330), fill((0, 0, 0), 80))
        cv.save()
        cv.clipPath(clip, skia.ClipOp.kIntersect, True)
        v = M.MapView(32.39, 41.45, 3.0)
        cv.translate(-W / 2, -H / 2)
        M.draw_map_base(cv, v, "amastris", rivers=False)
        M.place(cv, v, "Amastris", t, lf(p, 0, 0.18), size=50, label="Amastris")
        M.region_label(cv, v, "KARADENİZ", 42.35, 32.2, 50)
        cv.restore()
        cv.drawPath(clip, stroke("#d9a83a", 12))
        cv.drawPath(clip, stroke(OUT, 4))
        cv.restore()
    K.tag(cv, "LUKIANOS • TOXARIS", 520, 140, t, 0.5, 46)
    K.tag(cv, "BUGÜNKÜ AMASRA", 520, 900, t, lf(p, 0, 0.3), 42, rot=3)
    person(cv, "athlete2", 1350, 1060, 1.45, -1, t, seed=6, expr="determined", weapon="gladius", balteus="#a8803a",
           shield="parmula", arm_a=-20, arm_b=60, wpn=70, look=(0.4, 0))
    K.tag(cv, "SİSİNNES", 1350, 300, t, lf(p, 0, 0.45), 52)
    if t > lf(p, 0, 0.72):
        K.num(cv, "10.000", 1500, 520, t, lf(p, 0, 0.72), 120)
        K.txt(cv, "DRAHMİ", 1500, 600, t, lf(p, 0, 0.75), 48, "#2a1a10", "black")
        K.coins_pile(cv, 1720, 1000, 14, t, lf(p, 0, 0.75), 1.0, seed=3)
    vignette(cv, 110)


def recruiter(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.1, (960, 560), (960, 600))
    bgk(cv, "harbor_dusk", B.harbor, "sunset")
    lx, mv = walk_x(t, 0.2, 1.8, 2200, 1280)
    person(cv, "demetrios", 640, 1080, 1.35, 1, t, seed=1, expr="worried", look=(0.6, 0))
    person(cv, "lanista", lx, 1090, 1.4, -1, t, seed=2, expr="happy", walk=t * 7 if mv else None,
           talk=talk_on(t, p, [1]), arm_b=70 if t > t1 else 20, wpn=40, look=(0.5, 0))
    cv.restore()
    if t < t1:
        K.tag(cv, "LANİSTA", 1290, 380, t, lf(p, 0, 0.35), 56, rot=4)
        K.txt(cv, "gladyatör tüccarı", 1290, 470, t, lf(p, 0, 0.6), 40, "#fff4d6", "xb", oc=OUT, ow=4)
    if t > t1:
        # terazi: para <-> yillar
        s = pop(t - t1 - 0.2, 0.5)
        if s > 0:
            cv.save()
            cv.translate(W / 2, 260)
            cv.scale(s, s)
            tilt = math.sin(clamp((t - t1 - 0.5) / 1.0) * math.pi / 2) * 6
            cv.drawLine(0, -40, 0, 120, stroke(OUT, 12))
            cv.drawLine(0, -40, 0, 120, stroke("#c9963a", 7))
            cv.rotate(tilt)
            cv.drawLine(-260, -40, 260, -40, stroke(OUT, 12))
            cv.drawLine(-260, -40, 260, -40, stroke("#c9963a", 7))
            for sx in (-1, 1):
                cv.drawLine(sx * 250, -40, sx * 250, 40, stroke("#8a6a3a", 3))
                shape(cv, smooth([(sx * 250 - 80, 40), (sx * 250 + 80, 40), (sx * 250 + 50, 70),
                                  (sx * 250 - 50, 70)]), "#c9963a", w=3)
            for k in range(5):
                S.coin(cv, -250 - 40 + k * 20, 24 - (k % 2) * 14, 18)
            hourglass(cv, 250, -30, 0.32, t)
            cv.restore()
            K.tag(cv, "BORÇLARIN", W / 2 - 260, 400, t, lf(p, 1, 0.3), 38, rot=-3)
            K.tag(cv, "BİRKAÇ YILIN", W / 2 + 260, 400, t, lf(p, 1, 0.75), 38, rot=3)
    vignette(cv, 130)


def oath(cv, t, d, p):
    t1, t2 = lt(p, 1), lt(p, 2)
    bgk(cv, "studio_fire", B.dark_studio, "#5a2a14", "#140806")
    FX.embers(cv, t, 30)
    S.campfire(cv, W / 2, 1040, t, 0.9)
    person(cv, "demetrios", W / 2, 1000, 1.45, 1, t, seed=1, expr="determined" if t < t2 else "sad",
           arm_b=165 if t1 - 0.3 < t < t2 else 14, wpn=0, look=(0, -0.2) if t < t2 else (0.3, 0.3))
    if t1 - 0.2 < t < t2 + 0.3:
        a, b = E.line_t(p, 1)
        icons = [("YAKILMAK", "fire"), ("ZİNCİR", "chain"), ("DAYAK", "whip"), ("KILIÇ", "sword")]
        for k, (lab, kind) in enumerate(icons):
            fr = (0.02, 0.25, 0.5, 0.72)[k]

            def drawfn(c, kind=kind):
                c.scale(1.7, 1.7)
                if kind == "fire":
                    S.campfire(c, 0, 50, t, 0.5)
                elif kind == "chain":
                    K.chains(c, -80, -10, 80, -10, 1.3)
                elif kind == "whip":
                    C.draw_weapon(c, C.preset("trainer"), -30, 40, 30, "whip")
                else:
                    C.draw_weapon(c, C.preset("murmillo"), -10, 60, 20, "gladius")
            x = 300 + k * 440 if k < 2 else 300 + k * 440
            E.icon_card(cv, 250 + k * 470, 250, 280, 260, lab, drawfn, t, a + (b - a) * fr, col="#2a1a10",
                        tcol="#f3e3bf")
        E.quote_card(cv, "Yakılmaya, zincire vurulmaya, dövülmeye ve kılıçla öldürülmeye razıyım.", "Gladyatör yemini",
                     t, t1 - 0.1, y=1000, size=46)
    if t > t2:
        K.rib(cv, "UTANÇ VERİCİ MESLEK", W / 2, 180, t, t2 + 0.3, 60, color="#5a1a40")
        K.tag(cv, "INFAMIS", W / 2, 300, t, lf(p, 2, 0.5), 50, bg="#2a1a10", fg="#f3e3bf")
    vignette(cv, 160)


# =================================================================== BOLUM 3
def road_pergamon(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.08, (900, 560), (1100, 520))
    bgk(cv, "road", B.road)
    x0 = lerp(300, 820, clamp(t / d))
    person(cv, "guard", x0 - 200, 1010, 1.0, 1, t, seed=2, walk=t * 8, wpn=0, expr="neutral")
    person(cv, "demetrios", x0, 1040, 1.1, 1, t, seed=1, walk=t * 8 + 1, expr="sad", look=(0.5, 0))
    person(cv, "lanista", x0 + 220, 1030, 1.05, 1, t, seed=3, walk=t * 8 + 2, expr="happy", look=(0.6, 0))
    cv.restore()
    E.lower_third(cv, "BERGAMA (PERGAMON)", t, 0.6, t1)
    if t > t1:
        K.portrait_card(cv, 1560, 420, 360, 460, t, t1 + 0.3, "asiarch", "ASYA BAŞRAHİBİ", bgcol="#e8d0f0",
                        ps_scale=1.3, dy=40, pose=dict(expr="happy", look=(-0.4, 0)))
        K.tag(cv, "İMPARATOR ONURUNA OYUNLAR", 1440, 720, t, lf(p, 1, 0.55), 38, rot=-3)
    vignette(cv, 110)


def gladiators_training(cv, t, seed=0, x0=200, x1=1700, y=900, s=0.6, n=4):
    r = random.Random(seed)
    for k in range(n):
        x = x0 + k * (x1 - x0) / max(n - 1, 1)
        ph = math.sin(t * r.uniform(3, 5) + k)
        nm = r.choice(["murmillo", "thraex", "retiarius", "hoplomachus", "demetrios_tiro"])
        person(cv, nm, x, y, s, 1 if k % 2 else -1, t, seed=k + 7, expr="angry", arm_a=-24,
               arm_b=80 + ph * 30, wpn=90 + ph * 40)


def courtyard(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.15, 1.0, (700, 600), (960, 540))
    bgk(cv, "ludus", B.ludus_court)
    B.palus_post(cv, 300, 860, 0.7)
    B.palus_post(cv, 1640, 860, 0.7)
    gladiators_training(cv, t, 1, 520, 1420, 880, 0.62, 4)
    person(cv, "guard", 90, 1090, 1.25, 1, t, seed=4, expr="angry" if t > t1 else "neutral", look=(0.6, 0))
    person(cv, "guard", 1830, 1090, 1.25, -1, t, seed=5, expr="angry" if t > t1 else "neutral", look=(0.6, 0))
    gx = lerp(780, 980, clamp(t / (t1 + 0.5)))
    person(cv, "demetrios", gx, 1120, 1.35, 1, t, seed=1, expr="scared" if t > t1 else "worried",
           look=(-0.8, 0) if t > t1 else (0.3, -0.2))
    cv.restore()
    K.tag(cv, "LUDUS", 960, 150, t, 0.6, 64)
    K.tag(cv, "REVAK", 300, 330, t, lf(p, 0, 0.55), 40, rot=-4)
    K.tag(cv, "HÜCRELER", 1600, 420, t, lf(p, 0, 0.8), 40, rot=4)
    if t > t1:
        s = pop(t - lf(p, 1, 0.35), 0.4)
        if s > 0:
            cv.save()
            cv.translate(W / 2, 330)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 520, 120, col="#fbeaea")
            text(cv, "KAÇMAK?", 0, 20, font("black", 64), "#a01818")
            cv.restore()
            E.cross_out(cv, W / 2 - 230, 280, W / 2 + 230, 380, t, lf(p, 1, 0.6), w=12)
    vignette(cv, 110)


def cell(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.0, 1.1, (960, 560), (800, 600))
    bgk(cv, "cell", B.cell)
    K.oil_lamp(cv, 1080, 900, 0.7, t)
    person(cv, "demetrios_tiro", 520, 900, 1.3, 1, t, seed=1, seated=True, expr="sad",
           look=(0.4, 0.3) if t < t1 else (0.9, -0.1), weapon=None, arm_a=30, arm_b=30)
    cv.restore()
    for k, (s_, fr) in enumerate((("BİRKAÇ ADIM", 0.2), ("SAMAN YATAK", 0.45), ("KANDİL", 0.62),
                                  ("AĞIR KAPI", 0.82))):
        K.tag(cv, s_, (520, 520, 1080, 1640)[k], (700, 760, 700, 300)[k], t, lf(p, 0, fr), 40, rot=-3 + k * 2,
              t1=t1 + 0.4)
    if t > t1:
        dk = clamp((t - t1) / 1.0)
        cv.drawRect(skia.Rect.MakeWH(W, H), fill("#05051a", int(110 * dk)))
        r = random.Random(4)
        for k, s_ in enumerate(("Ahh...", "Zeus, koru beni...", "Anne...", "Ahh...")):
            t0 = lf(p, 1, 0.1 + k * 0.2)
            a = clamp((t - t0) / 0.4) * (1 - clamp((t - t0 - 1.6) / 0.5))
            if a > 0:
                x, y = 1500 + r.uniform(-200, 200), 200 + k * 150
                text(cv, s_, x, y - (t - t0) * 20, font("xb", 46), "#d8d0ff", a=int(220 * a), shadow=(0, 0, 8, 200))
    vignette(cv, 170)


def familia(cv, t, d, p):
    t1 = lt(p, 1)
    cv.save()
    E.camera(cv, t, d, 1.05, 1.0)
    bgk(cv, "ludus", B.ludus_court)
    crew = [("thracian", 330), ("egyptian", 720), ("demetrios_tiro", 1110), ("galatian", 1500)]
    for k, (nm, x) in enumerate(crew):
        person(cv, nm, x, 1080, 1.3, 1 if x < 960 else -1, t, seed=k + 2, expr="neutral" if t < t1 else "worried",
               look=(0.4 if x < 960 else 0.4, 0), weapon="rudis" if nm != "demetrios_tiro" else "rudis")
    cv.restore()
    K.rib(cv, "FAMILIA", W / 2, 130, t, 0.4, 66)
    for k, (s_, x, fr) in enumerate((("TRAKYALI ESİR", 330, 0.05), ("MISIRLI KAÇAK KÖLE", 720, 0.22),
                                     ("GALATYALI HIRSIZ", 1500, 0.4))):
        K.tag(cv, s_, x, 680 + (k % 2) * 60, t, lf(p, 1, fr), 36, rot=-3 + k * 3)
    if t > lf(p, 1, 0.66):
        K.vs_badge(cv, 920, 520, t, lf(p, 1, 0.7), 0.9)
        FX.flash(cv, t, lf(p, 1, 0.7), 0.2, "#ff4040", 90)
    vignette(cv, 110)


def tiro(cv, t, d, p):
    t1 = lt(p, 1)
    bgk(cv, "studio", B.studio)
    # basamaklar
    steps = [("TIRO (ACEMİ)", 900), ("VETERANUS", 720), ("PRIMUS PALUS", 540)]
    for k, (lab, y) in enumerate(steps):
        s = pop(t - 0.3 - k * 0.25, 0.4)
        if s <= 0:
            continue
        x = 1260 + k * 120
        cv.save()
        cv.translate(x, y)
        cv.scale(s, s)
        K.panel(cv, 0, 0, 480, 110, col=["#f6e2c0", "#ecd6a8", "#ffe08a"][k], r=12)
        text(cv, lab, 0, 16, font("black", 44), "#2a1a10")
        cv.restore()
    person(cv, "demetrios_tiro", 560, 1060, 1.55, 1, t, seed=1, expr="worried" if t < t1 else "happy",
           look=(0.7, 0.1))
    if t < t1 + 0.3:
        K.arrow_line(cv, 860, 800, 1000, 890, t, lf(p, 0, 0.5), 0.5)
    if t > t1:
        s = pop(t - lf(p, 1, 0.45), 0.55)
        if s > 0:
            cv.save()
            cv.translate(1300, 260)
            cv.scale(s, s)
            K.panel(cv, 0, 0, 760, 200, col="#2a1a10")
            text(cv, "NİKEPHOROS", 0, 10, font("deco", 84), "#e9c46a")
            text(cv, "Zafer getiren", 0, 70, font("xb", 40), "#f3e3bf")
            cv.restore()
    vignette(cv, 100)

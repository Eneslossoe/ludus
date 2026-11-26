"""Cizgi film karakterleri: insanlar, gladyatorler (teçhizatlariyla), atlar, siluetler.

Kanal stiline uygun: buyuk kafa, kocaman yuvarlak gozler, kalin kahverengi kontur.
Yerel koordinat: ayaklar (0,0), yukari negatif y.
"""
import math

import skia

from gfx import (OUT, OUTW, P, capsule, circle, ellipse, fill, lin_grad, mix, poly, rad_grad,
                 rgb, rrect, shade, shape, smooth, stroke, blur_paint)

SKIN_ARAB = "#d9a06e"
SKIN_DARK = "#b97f50"
SKIN_ROMAN = "#efc29a"
SKIN_LIGHT = "#f3cfae"
SKIN_GREEK = "#e9b991"
SKIN_GREEK2 = "#dba479"


def rounded(pts, r=10):
    p = poly(pts)
    return p


def round_paint(base, r):
    base.setPathEffect(skia.CornerPathEffect.Make(r))
    return base


def rshape(cv, pts, fc, oc=OUT, w=OUTW, r=12, a=255):
    p = poly(pts)
    if fc is not None:
        cv.drawPath(p, round_paint(fill(fc, a), r))
    if oc is not None:
        cv.drawPath(p, round_paint(stroke(oc, w, a), r))
    return p


# ======================================================================== PRESETLER
def preset(name, **kw):
    base = dict(
        skin=SKIN_ARAB, beard=None, beard_color="#2a1a12", mustache=False,
        head="turban", head_color="#efe6d2", head_color2="#c9b58f", turban_tail=True,
        tunic="#a87a4a", tunic_long=True, belt="#5a3a22", sash=None,
        armor=None, cloak=None, legs="#d9a06e", boots=False, shoe="#5b3a22",
        shield=None, shield_color="#9a6a3a", weapon=None, item=None,
        age="adult", female=False, body=1.0, head_scale=1.0, expr="neutral",
        quiver=False, eyepatch=False, cross=False, hair="#2a1a12", plume="#c0262b",
        banner_color="#1d1b1a",
        # gladyator / antik Yunan ekleri
        torso=None, loin="#f1e9d6", balteus=None, manica=None, greave=None, galerus=False, item_a=None,
        himation=None, wide=1.0, stripes=None, scars=False, chest_band=None,
    )
    def mk(*ds, **kw):
        out = {}
        for d_ in ds:
            out.update(d_)
        out.update(kw)
        return out

    G = dict(skin=SKIN_GREEK, head="curly", tunic_long=False, legs=SKIN_GREEK, belt="#6a4a2a")
    GL = dict(torso="bare", tunic_long=False, balteus="#c9963a", loin="#f3ecdc", shoe="#6a4a2a")
    P_ = {
        # ana karakter
        "demetrios": mk(G, beard="stubble", tunic="#c8a66e", hair="#2a1a12", age="young"),
        "demetrios_kid": mk(G, tunic="#d8bb88", body=0.7, head_scale=0.92, age="kid"),
        "demetrios_tiro": mk(G, GL, beard="stubble", hair="#2a1a12", weapon="rudis", age="young",
                               balteus="#7a5a3a"),
        "secutor": mk(G, GL, head="secutor", beard="stubble", shield="scutum", shield_color="#b3262a",
                        weapon="gladius", manica="B", greave="A", plume="#c9963a"),
        "demetrios_free": mk(G, beard="short", tunic="#b9935a", hair="#2a1a12", weapon="rudis", scars=True),
        # gladyator turleri
        "retiarius": mk(G, GL, head="hair", hair="#1e140e", beard="short", beard_color="#1e140e",
                          skin=SKIN_GREEK2, legs=SKIN_GREEK2, weapon="trident", item_a="net", manica="A",
                          galerus=True, balteus="#a8803a"),
        "murmillo": mk(G, GL, head="murmillo", shield="scutum", shield_color="#2f5e8f", weapon="gladius",
                         manica="B", greave="A", plume="#c0262b"),
        "thraex": mk(G, GL, head="thraex", shield="parmula", shield_color="#7a3a8a", weapon="sica",
                       manica="B", greave="both", plume="#e8e0c8", skin=SKIN_GREEK2, legs=SKIN_GREEK2),
        "hoplomachus": mk(G, GL, head="hoplo", shield="hoplo", weapon="spear", manica="B", greave="both",
                            plume="#2f6b3a"),
        # okul halki
        "trainer": mk(G, head="bald", beard="short", beard_color="#5a4a3a", tunic="#5a4636", weapon="whip",
                        scars=True, wide=1.12, skin=SKIN_GREEK2, legs=SKIN_GREEK2),
        "lanista": mk(G, head="fringe", hair="#4a3a2a", beard=None, tunic="#7a2a4a", tunic_long=True,
                        himation="#d9a83a", wide=1.35, legs="#7a2a4a", item="coin"),
        "thracian": mk(G, GL, head="long_hair", hair="#d9b060", beard="full", beard_color="#c9a050",
                         skin="#f1c8a0", legs="#f1c8a0", balteus="#7a5a3a"),
        "egyptian": mk(G, GL, head="bald", skin="#a8703f", legs="#a8703f", beard=None, balteus="#7a5a3a"),
        "galatian": mk(G, GL, head="hair", hair="#b0461e", beard="stubble", beard_color="#b0461e",
                         skin="#f3cfae", legs="#f3cfae", balteus="#7a5a3a"),
        "guard": dict(skin=SKIN_GREEK, head="roman_helmet", beard="stubble", tunic="#b02a2a", tunic_long=False,
                      armor="mail", legs=SKIN_GREEK, boots=False, shoe="#5a3a22", weapon="spear", shield="oval",
                      shield_color="#b3262a"),
        "galen": mk(G, beard="full", beard_color="#3a2414", hair="#3a2414", tunic="#4f6f8f", tunic_long=True,
                      himation="#efe8d6", legs="#4f6f8f", item="scroll"),
        "asiarch": mk(G, head="priest_crown", hair="#cfc8be", beard="full", beard_color="#d8d2c8", age="old",
                        tunic="#f4f0e4", tunic_long=True, cloak="#6a1f7a", legs="#f4f0e4", belt="#d9a83a"),
        "referee": mk(G, beard="short", beard_color="#4a3a2a", hair="#4a3a2a", tunic="#f2ede0", stripes="#b02020",
                        weapon="pole"),
        # sehir halki
        "mother": dict(skin=SKIN_GREEK, female=True, head="veil", head_color="#6a5a7a", tunic="#8a7a9a", beard=None),
        "sister": dict(skin=SKIN_GREEK, female=True, head="bun", hair="#2a1a12", tunic="#d88a6a", body=0.66,
                       head_scale=0.9, age="kid"),
        "creditor": mk(G, head="fringe", hair="#3a2a1a", beard="full", beard_color="#3a2a1a", tunic="#5a6a3a",
                         tunic_long=True, legs="#5a6a3a", wide=1.25, item="scroll"),
        "citizen": mk(G, beard="short", tunic="#5a7a8a", himation="#e8dcc0"),
        "citizen2": mk(G, head="hair", hair="#4a2a1a", beard="full", beard_color="#4a2a1a", tunic="#8a5a3a"),
        "citizen3": mk(G, head="bald", beard="long", beard_color="#e0dad0", age="old", tunic="#6a7a4a",
                         tunic_long=True, legs="#6a7a4a", himation="#d8ccb0"),
        "citizen4": mk(G, beard=None, tunic="#a8423a", hair="#3a2010"),
        "woman": dict(skin=SKIN_GREEK, female=True, head="veil", head_color="#3a6a7a", tunic="#7aa0a8", beard=None),
        "woman2": dict(skin=SKIN_GREEK, female=True, head="bun", hair="#3a2010", tunic="#c0703a", beard=None,
                       himation="#efe2c8"),
        "kid": mk(G, tunic="#c9a070", body=0.66, head_scale=0.9, age="kid"),
        "philosopher": mk(G, head="bald", beard="long", beard_color="#e8e4dc", age="old", tunic="#e8e0cc",
                            tunic_long=True, legs="#e8e0cc", himation="#b8a888", weapon="staff"),
        "athlete": mk(G, GL, beard=None, balteus=None, loin="#f3ecdc"),
        "athlete2": mk(G, GL, head="hair", hair="#6a3a1a", beard="stubble", balteus=None, skin=SKIN_GREEK2,
                         legs=SKIN_GREEK2),
        "roman": dict(skin=SKIN_GREEK, head="hair", hair="#2a1a12", beard=None, tunic="#f2eee4", tunic_long=True,
                      legs="#f2eee4", himation="#f8f4ea", stripes="#7a1a3a"),
        "antiochus": dict(skin=SKIN_GREEK, head="diadem", hair="#3a2414", beard=None, tunic="#5b1d6e",
                          tunic_long=True, cloak="#7b2a8e", legs="#5b1d6e", belt="#d9a83a"),
        "amazon": mk(G, GL, head="bun", hair="#2a1a12", female=True, beard=None, shield="scutum",
                       shield_color="#b3262a", weapon="gladius", greave="A", manica="B", chest_band="#efe6d2"),
        "achillia": mk(G, GL, head="bun", hair="#5a2a1a", female=True, beard=None, shield="scutum",
                         shield_color="#2f5e8f", weapon="gladius", greave="A", manica="B", chest_band="#efe6d2",
                         skin=SKIN_GREEK2, legs=SKIN_GREEK2),
        "noxius": mk(G, head="hair", hair="#2a1a12", beard="short", tunic="#9a8a70"),
    }
    d = dict(base)
    d.update(P_.get(name, {}))
    d.update(kw)
    d["name"] = name
    return d


DEFAULT_POSE = dict(arm_a=14, arm_b=14, wpn=8, walk=None, bob=0.0, look=(0.35, 0.0), blink=0.0,
                    mouth=0.0, expr=None, lean=0.0, seated=False, hurt=False, tears=False,
                    sweat=False, sick=False, bandage=False, arrow=False, blood=0.0, eyes_closed=False)


def pose(**kw):
    d = dict(DEFAULT_POSE)
    d.update(kw)
    return d


# ======================================================================== YUZ
def draw_face(cv, c, ps, expr):
    skin = c["skin"]
    look = ps["look"]
    blink = ps["blink"]
    old = c["age"] == "old"
    big = expr in ("scared", "surprised")
    er = 19 if not big else 22
    if c["age"] == "kid":
        er += 2
    pr = 8 if not big else 5.5
    eye_y = -6
    for sx in (-1, 1):
        ex = sx * 24
        cv.drawPath(circle(ex, eye_y, er), fill("#ffffff"))
        # gozbebegi
        px = ex + look[0] * (er - pr - 3)
        py = eye_y + look[1] * (er - pr - 3)
        lid = blink
        if expr == "tired":
            lid = max(lid, 0.45)
        if expr in ("angry", "shout", "determined"):
            lid = max(lid, 0.18)
        if ps.get("sick"):
            lid = max(lid, 0.5)
        if expr == "hurt" and sx == -1:
            lid = max(lid, 0.85)
        closed = ps.get("eyes_closed") or lid > 0.92 or (expr == "happy" and ps.get("mouth", 0) > 0.85)
        if not closed:
            cv.drawPath(circle(px, py, pr), fill("#1a120c"))
            cv.drawPath(circle(px - pr * 0.35, py - pr * 0.4, pr * 0.32), fill("#ffffff"))
            if lid > 0.02:
                cv.save()
                cv.clipPath(circle(ex, eye_y, er + 0.5), skia.ClipOp.kIntersect, True)
                cv.drawRect(skia.Rect.MakeLTRB(ex - er - 2, eye_y - er - 2, ex + er + 2,
                                               eye_y - er + 2 * er * lid), fill(shade(skin, 0.92)))
                cv.drawLine(ex - er, eye_y - er + 2 * er * lid, ex + er, eye_y - er + 2 * er * lid,
                            stroke(OUT, 3))
                cv.restore()
            cv.drawPath(circle(ex, eye_y, er), stroke(OUT, 3.6))
        else:
            cv.drawPath(circle(ex, eye_y, er), fill(shade(skin, 0.92)))
            cv.drawPath(circle(ex, eye_y, er), stroke(OUT, 3.0))
            arc = P()
            arc.moveTo(ex - er * 0.8, eye_y + 2)
            arc.quadTo(ex, eye_y + (8 if expr != "happy" else -9), ex + er * 0.8, eye_y + 2)
            cv.drawPath(arc, stroke(OUT, 3.6))
        if ps.get("eyepatch") and sx == -1:
            cv.drawPath(circle(ex, eye_y, er + 2), fill("#1b1410"))
            cv.drawLine(-60, -30, 55, -10, stroke("#1b1410", 5))
    # kaslar
    bc = c["beard_color"] if c.get("beard") else c.get("hair", "#2a1a12")
    if c["female"]:
        bc = "#2a1a12"
    for sx in (-1, 1):
        x0, x1 = sx * 10, sx * 40
        y0 = y1 = -32
        if expr in ("angry", "shout", "determined", "hurt"):
            y0 += 8; y1 -= 4
        elif expr in ("sad", "scared", "worried"):
            y0 -= 8; y1 += 3
        elif expr in ("surprised", "happy"):
            y0 -= 7; y1 -= 7
        if big:
            y0 -= 4; y1 -= 4
        cv.drawLine(x0, y0, x1, y1, stroke(bc if not old else "#cfc8be", 7 if not c["female"] else 5))
    # burun
    cv.drawPath(ellipse(0, 16, 9, 7), fill(shade(skin, 0.85)))
    nose = P()
    nose.moveTo(-8, 18)
    nose.quadTo(0, 25, 8, 18)
    cv.drawPath(nose, stroke(OUT, 3))
    # yanak
    if c["female"] or c["age"] == "kid":
        for sx in (-1, 1):
            cv.drawPath(circle(sx * 38, 18, 9), fill("#e77d6a", 90))
    if old:
        for sx in (-1, 1):
            w = P()
            w.moveTo(sx * 44, -4)
            w.quadTo(sx * 50, 0, sx * 47, 8)
            cv.drawPath(w, stroke(shade(skin, 0.7), 2.4))


def draw_mouth(cv, c, ps, expr):
    m = ps["mouth"]
    my = 38
    if expr in ("shout",) or m > 0.05 or expr in ("surprised",):
        op = max(m, 0.9 if expr == "shout" else 0.0, 0.55 if expr == "surprised" else 0.0)
        wdt = 15 + 6 * op if expr != "shout" else 22
        hgt = 3 + 15 * op
        if expr == "surprised":
            wdt = 10
        path = ellipse(0, my + 2, wdt, hgt)
        cv.drawPath(path, fill("#5a1a14"))
        cv.save()
        cv.clipPath(path, skia.ClipOp.kIntersect, True)
        cv.drawPath(ellipse(0, my + 2 + hgt * 0.8, wdt * 0.7, hgt * 0.6), fill("#d0605a"))
        if expr in ("shout", "angry", "hurt"):
            cv.drawRect(skia.Rect.MakeLTRB(-wdt, my + 2 - hgt, wdt, my + 2 - hgt * 0.55), fill("#ffffff"))
        cv.restore()
        cv.drawPath(path, stroke(OUT, 3.4))
        return
    p = P()
    if expr == "happy":
        p.moveTo(-18, my - 4)
        p.quadTo(0, my + 16, 18, my - 4)
        p.close()
        cv.drawPath(p, fill("#5a1a14"))
        cv.drawPath(p, stroke(OUT, 3.4))
    elif expr in ("sad", "worried", "tired"):
        p.moveTo(-13, my + 6)
        p.quadTo(0, my - 5, 13, my + 6)
        cv.drawPath(p, stroke(OUT, 3.6))
    elif expr == "scared":
        p.moveTo(-14, my + 2)
        for i in range(1, 8):
            p.lineTo(-14 + i * 4, my + (3 if i % 2 else -2))
        cv.drawPath(p, stroke(OUT, 3.4))
    elif expr in ("angry", "determined", "hurt"):
        cv.drawPath(rrect(-15, my - 4, 30, 9, 3), fill("#ffffff"))
        cv.drawPath(rrect(-15, my - 4, 30, 9, 3), stroke(OUT, 3))
        cv.drawLine(-15, my + 0.5, 15, my + 0.5, stroke(OUT, 1.6))
    else:
        p.moveTo(-12, my)
        p.quadTo(0, my + 7, 12, my)
        cv.drawPath(p, stroke(OUT, 3.6))


def draw_beard_back(cv, c):
    pass


def draw_beard(cv, c, ps):
    b = c.get("beard")
    if not b:
        return
    bc = c["beard_color"]
    skin = c["skin"]
    if b == "stubble":
        p = smooth([(-56, 12), (-40, 44), (0, 62), (40, 44), (56, 12), (30, 30), (0, 34), (-30, 30)])
        cv.drawPath(p, fill(mix(skin, bc, 0.35), 170))
        return
    ext = {"short": 70, "full": 86, "long": 128}[b]
    pts = [(-61, -6), (-60, 26), (-44, 56), (-18, ext - 6), (0, ext), (18, ext - 6), (44, 56), (60, 26),
           (61, -6), (50, 18), (30, 30), (0, 28), (-30, 30), (-50, 18)]
    if b == "long":
        pts = [(-61, -6), (-60, 30), (-46, 70), (-22, 110), (0, ext), (22, 110), (46, 70), (60, 30),
               (61, -6), (50, 18), (30, 30), (0, 28), (-30, 30), (-50, 18)]
    p = smooth(pts, tension=0.45)
    cv.drawPath(p, fill(bc))
    cv.drawPath(p, stroke(OUT, 3.6))
    # dokular
    for i in range(-2, 3):
        l = P()
        l.moveTo(i * 15, 46)
        l.quadTo(i * 17, ext - 22, i * 12, ext - 12)
        cv.drawPath(l, stroke(shade(bc, 0.75 if sum(shade(bc, 1)) > 150 else 1.4), 2.2))
    # biyik
    m = smooth([(-26, 30), (-12, 22), (0, 25), (12, 22), (26, 30), (12, 30), (0, 31), (-12, 30)])
    cv.drawPath(m, fill(shade(bc, 0.9)))
    cv.drawPath(m, stroke(OUT, 2.6))


# ======================================================================== BAS
def draw_head_back(cv, c, ps):
    h = c["head"]
    hc = c["head_color"]
    if h == "turban" and c.get("turban_tail", True):
        tail = smooth([(-46, -20), (-66, 14), (-70, 70), (-60, 100), (-50, 66), (-50, 20)], closed=True)
        shape(cv, tail, shade(hc, 0.88))
    elif h == "keffiyeh":
        back = smooth([(-70, -50), (-30, -88), (30, -88), (70, -50), (84, 40), (100, 118), (-100, 118),
                       (-84, 40)], tension=0.5)
        shape(cv, back, hc)
        # desen
        cv.save()
        cv.clipPath(back, skia.ClipOp.kIntersect, True)
        c2 = c["head_color2"]
        for yy in range(-90, 130, 18):
            cv.drawLine(-110, yy, 110, yy + 30, stroke(c2, 2.2, 150))
            cv.drawLine(-110, yy + 30, 110, yy, stroke(c2, 2.2, 150))
        cv.restore()
        shape(cv, back, None)
    elif h == "veil":
        back = smooth([(-74, -40), (-40, -86), (40, -86), (74, -40), (84, 40), (96, 122), (-96, 122),
                       (-84, 40)], tension=0.5)
        shape(cv, back, hc)
    elif h == "byz_helmet":
        av = smooth([(-66, -10), (-74, 60), (-50, 92), (50, 92), (74, 60), (66, -10)], closed=True)
        shape(cv, av, "#8d949c")
        cv.save()
        cv.clipPath(av, skia.ClipOp.kIntersect, True)
        for yy in range(-10, 100, 9):
            for xx in range(-80, 80, 9):
                cv.drawPath(circle(xx + (yy // 9 % 2) * 4.5, yy, 3.6), stroke("#5f666e", 1.6))
        cv.restore()
        shape(cv, av, None)
    elif h == "long_hair":
        hair = smooth([(-62, -30), (-74, 30), (-70, 96), (-40, 110), (40, 110), (70, 96), (74, 30), (62, -30)],
                      closed=True)
        shape(cv, hair, c.get("hair", "#2a1a12"))
    elif h == "bun":
        shape(cv, circle(0, -66, 30), c.get("hair", "#2a1a12"))
    elif h in ("murmillo", "thraex", "hoplo"):
        # genis siperlik (arkada)
        brim = smooth([(-98, -6), (-84, -30), (0, -40), (84, -30), (98, -6), (60, -16), (0, -22), (-60, -16)],
                      tension=0.5)
        shape(cv, brim, "#b8863a")
    elif h == "roman_helmet":
        ng = smooth([(-70, -10), (-84, 40), (-60, 52), (60, 52), (84, 40), (70, -10)], closed=True)
        shape(cv, ng, "#9aa2aa")
    elif h == "crown":
        # sac arkada
        hair = smooth([(-62, -20), (-70, 30), (-60, 70), (60, 70), (70, 30), (62, -20)], closed=True)
        shape(cv, hair, c["beard_color"])


def draw_head_front(cv, c, ps):
    h = c["head"]
    hc = c["head_color"]
    if h == "turban":
        main = smooth([(-64, -12), (-72, -42), (-56, -76), (-20, -92), (20, -92), (56, -76), (72, -42),
                       (64, -12), (32, -24), (0, -26), (-32, -24)], tension=0.5)
        shape(cv, main, hc)
        cv.save()
        cv.clipPath(main, skia.ClipOp.kIntersect, True)
        for k, (y0, y1) in enumerate([(-34, -62), (-50, -80), (-22, -46)]):
            f = P()
            f.moveTo(-74, y0 + 12)
            f.quadTo(0, y1, 74, y0 + 4 * (k + 1))
            cv.drawPath(f, stroke(shade(hc, 0.78), 3.2))
        cv.drawPath(ellipse(20, -60, 40, 14), fill(shade(hc, 1.12), 120))
        cv.restore()
        shape(cv, main, None)
    elif h == "kufi":
        cap = smooth([(-58, -20), (-56, -60), (0, -78), (56, -60), (58, -20), (0, -30)], tension=0.5)
        shape(cv, cap, hc)
        for x in range(-40, 50, 16):
            cv.drawPath(circle(x, -46, 3), fill(shade(hc, 0.75)))
    elif h == "keffiyeh":
        front = smooth([(-66, -16), (-70, -50), (-40, -84), (40, -84), (70, -50), (66, -16), (30, -30),
                        (0, -32), (-30, -30)], tension=0.5)
        shape(cv, front, hc)
        cv.save()
        cv.clipPath(front, skia.ClipOp.kIntersect, True)
        c2 = c["head_color2"]
        for yy in range(-100, 0, 16):
            cv.drawLine(-80, yy, 80, yy + 24, stroke(c2, 2.0, 150))
            cv.drawLine(-80, yy + 24, 80, yy, stroke(c2, 2.0, 150))
        cv.restore()
        shape(cv, front, None)
        # agal
        cv.drawPath(ellipse(0, -60, 62, 14), stroke("#141210", 9))
        cv.drawPath(ellipse(0, -48, 66, 13), stroke("#141210", 8))
    elif h == "veil":
        outer = ellipse(0, -8, 76, 84)
        inner = ellipse(0, 8, 52, 58)
        frame = skia.Op(outer, inner, skia.PathOp.kDifference_PathOp)
        clipb = P()
        clipb.addRect(skia.Rect.MakeLTRB(-120, -120, 120, 60))
        frame = skia.Op(frame, clipb, skia.PathOp.kIntersect_PathOp)
        shape(cv, frame, hc)
        cv.drawLine(-46, -36, 46, -36, stroke(shade(hc, 1.3), 4, 150))
    elif h == "byz_helmet":
        # tepe sorgucu
        pl = smooth([(-8, -92), (-30, -120), (-70, -126), (-96, -104), (-80, -112), (-50, -108),
                     (-20, -96)], tension=0.5)
        shape(cv, pl, c.get("plume", "#c0262b"))
        dome = P()
        dome.moveTo(-66, -14)
        dome.cubicTo(-70, -70, -40, -100, 0, -102)
        dome.cubicTo(40, -100, 70, -70, 66, -14)
        dome.quadTo(0, -30, -66, -14)
        dome.close()
        cv.drawPath(dome, lin_grad((-60, -100), (60, -10), ["#e6eaee", "#a9b1b9", "#6f7780"]))
        cv.drawPath(dome, stroke(OUT, OUTW))
        for x in (-30, 0, 30):
            cv.drawLine(x, -97 + abs(x) * 0.3, x * 1.1, -24, stroke("#c9a040", 6))
        band = P()
        band.moveTo(-66, -14)
        band.quadTo(0, -32, 66, -14)
        cv.drawPath(band, stroke("#c9a040", 10))
        cv.drawPath(band, stroke(OUT, 2.4))
        for sx in (-1, 1):
            cheek = rrect(sx * 64 - 11, -18, 22, 56, 10)
            shape(cv, cheek, "#a9b1b9", w=3)
        cv.drawPath(circle(0, -102, 7), fill("#c9a040"))
        cv.drawPath(circle(0, -102, 7), stroke(OUT, 2.5))
    elif h == "crown":
        cap = smooth([(-54, -40), (-48, -80), (0, -96), (48, -80), (54, -40)], closed=True)
        shape(cv, cap, "#6a1f7a")
        band = rrect(-62, -54, 124, 30, 8)
        cv.drawPath(band, lin_grad((0, -54), (0, -24), ["#fff0a0", "#e0a92e", "#a8701a"]))
        cv.drawPath(band, stroke(OUT, 3.5))
        for i, x in enumerate(range(-44, 50, 22)):
            cv.drawPath(circle(x, -39, 6), fill("#c0262b" if i % 2 else "#2a6ad0"))
            cv.drawPath(circle(x, -39, 6), stroke(OUT, 2))
        cv.drawLine(0, -96, 0, -132, stroke("#e0a92e", 7))
        cv.drawLine(-14, -118, 14, -118, stroke("#e0a92e", 7))
        cv.drawLine(0, -96, 0, -132, stroke(OUT, 1.5))
        for sx in (-1, 1):
            for k in range(5):
                cv.drawPath(circle(sx * 62, -20 + k * 12, 5), fill("#fbf6ea"))
                cv.drawPath(circle(sx * 62, -20 + k * 12, 5), stroke(OUT, 1.6))
    elif h in ("curly", "fringe", "bald", "priest_crown", "diadem"):
        hc_ = c.get("hair", "#2a1a12") if c["age"] != "old" else "#cfc8be"
        if h in ("curly", "priest_crown", "diadem"):
            path = None
            for (x, y, r) in ((-52, -28, 17), (-46, -52, 19), (-28, -70, 20), (-4, -78, 21), (22, -74, 20),
                              (44, -58, 19), (54, -34, 16), (-60, -8, 12), (60, -10, 12)):
                cc = circle(x, y, r)
                path = cc if path is None else skia.Op(path, cc, skia.PathOp.kUnion_PathOp)
            band = smooth([(-58, -10), (-56, -50), (0, -66), (56, -50), (58, -10), (30, -40), (0, -44),
                           (-30, -40)], tension=0.5)
            path = skia.Op(path, band, skia.PathOp.kUnion_PathOp)
            shape(cv, path, hc_)
            for (x, y) in ((-30, -62), (0, -68), (28, -60), (-46, -40), (46, -42)):
                a_ = P()
                a_.moveTo(x - 7, y + 2)
                a_.quadTo(x, y - 7, x + 7, y + 2)
                cv.drawPath(a_, stroke(shade(hc_, 0.6 if sum(shade(hc_, 1)) > 200 else 1.6), 2.4))
        elif h == "fringe":
            for sx in (-1, 1):
                fr = smooth([(sx * 44, -44), (sx * 64, -30), (sx * 66, 4), (sx * 56, 10), (sx * 50, -20)])
                shape(cv, fr, hc_, w=3)
            cv.drawPath(ellipse(-16, -46, 16, 8), fill("#ffffff", 70))
        else:
            cv.drawPath(ellipse(-18, -44, 18, 9), fill("#ffffff", 80))
        if h == "priest_crown":
            band = rrect(-60, -62, 120, 24, 8)
            cv.drawPath(band, lin_grad((0, -62), (0, -38), ["#fff0a0", "#e0a92e", "#a8701a"]))
            cv.drawPath(band, stroke(OUT, 3.2))
            for k, x in enumerate(range(-40, 50, 20)):
                cv.drawPath(circle(x, -62, 10), lin_grad((0, -72), (0, -52), ["#fff6c0", "#d9a030"]))
                cv.drawPath(circle(x, -62, 10), stroke(OUT, 2.2))
                cv.drawPath(circle(x, -64, 3.5), fill("#a8701a"))
        elif h == "diadem":
            cv.drawLine(-60, -40, 60, -40, stroke("#f6f0e0", 8))
            cv.drawLine(-60, -40, 60, -40, stroke(OUT, 1.5))
            tail = smooth([(56, -40), (70, -20), (76, 10), (68, 12), (62, -18)])
            shape(cv, tail, "#f6f0e0", w=2)
    elif h == "laurel":
        hc_ = c.get("hair", "#2a1a12")
        shape(cv, smooth([(-60, -8), (-62, -50), (-28, -76), (20, -78), (60, -52), (62, -8), (40, -40), (0, -46),
                          (-36, -40)], tension=0.5), hc_)
        for sx in (-1, 1):
            for k in range(6):
                a = math.radians(200 + k * 22) if sx < 0 else math.radians(-20 - k * 22)
                x, y = math.cos(a) * 58, -30 + math.sin(a) * 40
                cv.save()
                cv.translate(x, y)
                cv.rotate(math.degrees(a) + 90)
                shape(cv, ellipse(0, 0, 7, 15), "#5f8f3a", w=2)
                cv.restore()
    elif h == "secutor":
        # puruzsuz yumurta migfer: sadece iki goz deligi
        dome = smooth([(-70, 40), (-74, -20), (-62, -72), (-28, -98), (28, -98), (62, -72), (74, -20), (70, 40),
                       (52, 64), (-52, 64)], tension=0.5)
        holes = skia.Op(circle(-24, -6, 14), circle(24, -6, 14), skia.PathOp.kUnion_PathOp)
        hel = skia.Op(dome, holes, skia.PathOp.kDifference_PathOp)
        cv.drawPath(hel, lin_grad((-70, -90), (70, 60), ["#fff0b8", "#e0b050", "#b07a26", "#7a4a14"],
                                  [0, 0.35, 0.75, 1]))
        cv.drawPath(hel, stroke(OUT, OUTW))
        for sx in (-1, 1):
            cv.drawPath(circle(sx * 24, -6, 14), stroke(OUT, 3))
            cv.drawPath(circle(sx * 24, -6, 18), stroke(shade("#b07a26", 0.8), 3))
        fin = rrect(-9, -122, 18, 56, 8)
        shape(cv, fin, c.get("plume", "#c9963a"), w=3)
        cv.drawPath(ellipse(-24, -60, 22, 12), fill("#ffffff", 90))
        neck = smooth([(-60, 50), (-80, 70), (80, 70), (60, 50)], closed=True)
        shape(cv, neck, "#b07a26", w=3)
    elif h in ("murmillo", "thraex", "hoplo"):
        dome = smooth([(-64, -10), (-66, -60), (-36, -96), (0, -104), (36, -96), (66, -60), (64, -10)],
                      tension=0.5)
        cv.drawPath(dome, lin_grad((-60, -100), (60, -10), ["#fff0b8", "#d9a548", "#9a6a22"]))
        cv.drawPath(dome, stroke(OUT, OUTW))
        brim = smooth([(-96, -8), (-80, -26), (0, -34), (80, -26), (96, -8), (60, -14), (0, -18), (-60, -14)],
                      tension=0.5)
        shape(cv, brim, "#c9963a", w=3.4)
        plate = smooth([(-58, -22), (-60, 30), (-40, 62), (40, 62), (60, 30), (58, -22)], closed=True)
        holes = skia.Op(circle(-24, -4, 16), circle(24, -4, 16), skia.PathOp.kUnion_PathOp)
        vis = skia.Op(plate, holes, skia.PathOp.kDifference_PathOp)
        cv.drawPath(vis, lin_grad((-60, -20), (60, 60), ["#e8eef2", "#a9b1b9", "#6f7780"]))
        cv.drawPath(vis, stroke(OUT, 3.6))
        for sx in (-1, 1):
            cx_ = sx * 24
            cv.save()
            cv.clipPath(circle(cx_, -4, 16), skia.ClipOp.kIntersect, True)
            for k in range(-3, 4):
                cv.drawLine(cx_ + k * 6, -24, cx_ + k * 6, 16, stroke("#3a3a3a", 1.3, 120))
                cv.drawLine(cx_ - 20, -4 + k * 6, cx_ + 20, -4 + k * 6, stroke("#3a3a3a", 1.3, 120))
            cv.restore()
            cv.drawPath(circle(cx_, -4, 16), stroke("#c9963a", 4))
            cv.drawPath(circle(cx_, -4, 18), stroke(OUT, 2))
        for k in range(3):
            cv.drawPath(circle(-30 + k * 30, 46, 3), fill("#5a6068"))
        pc = c.get("plume", "#c0262b")
        if h == "murmillo":
            cr = smooth([(-14, -96), (-22, -150), (0, -172), (22, -150), (14, -96)], tension=0.5)
            shape(cv, cr, pc)
            for k in range(-1, 2):
                cv.drawLine(k * 8, -100, k * 9, -158, stroke(shade(pc, 0.75), 2.4))
        elif h == "thraex":
            gr = smooth([(-8, -98), (-16, -132), (0, -158), (30, -164), (56, -150), (40, -142), (16, -140),
                         (10, -100)], tension=0.45)
            shape(cv, gr, "#d9a548")
            cv.drawPath(circle(30, -152, 4), fill(OUT))
            for sx in (-1, 1):
                fe = smooth([(sx * 52, -60), (sx * 62, -110), (sx * 70, -130), (sx * 66, -100), (sx * 60, -62)])
                shape(cv, fe, pc, w=2.6)
        else:
            pl = smooth([(-10, -100), (-40, -150), (-10, -190), (30, -180), (14, -140), (10, -100)], tension=0.5)
            shape(cv, pl, pc)
            for sx in (-1, 1):
                fe = smooth([(sx * 52, -60), (sx * 64, -120), (sx * 72, -140), (sx * 68, -104), (sx * 60, -62)])
                shape(cv, fe, "#efe6d0", w=2.6)
        cv.drawPath(ellipse(-22, -70, 20, 10), fill("#ffffff", 90))
    elif h == "roman_helmet":
        dome = P()
        dome.moveTo(-64, -14)
        dome.cubicTo(-68, -70, -40, -98, 0, -100)
        dome.cubicTo(40, -98, 68, -70, 64, -14)
        dome.quadTo(0, -30, -64, -14)
        dome.close()
        cv.drawPath(dome, lin_grad((-60, -100), (60, -10), ["#eef2f4", "#aab2ba", "#70787f"]))
        cv.drawPath(dome, stroke(OUT, OUTW))
        brow = P()
        brow.moveTo(-64, -18)
        brow.quadTo(0, -36, 64, -18)
        cv.drawPath(brow, stroke("#c9a040", 9))
        cv.drawPath(brow, stroke(OUT, 2.2))
        for sx in (-1, 1):
            shape(cv, smooth([(sx * 56, -22), (sx * 70, -20), (sx * 66, 40), (sx * 52, 34)]), "#aab2ba", w=3)
        shape(cv, rrect(-8, -114, 16, 18, 5), "#c9a040", w=2.5)
    elif h == "mitre":
        m = smooth([(-48, -26), (-46, -80), (0, -98), (46, -80), (48, -26)], closed=True)
        shape(cv, m, "#1c1c1c")
        cv.drawLine(0, -92, 0, -40, stroke("#d9a83a", 4))
        cv.drawLine(-14, -70, 14, -70, stroke("#d9a83a", 4))
    elif h == "hair":
        hr = smooth([(-62, -6), (-64, -50), (-30, -78), (20, -80), (60, -52), (62, -8), (40, -40),
                     (0, -46), (-36, -40)], tension=0.5)
        shape(cv, hr, c.get("hair", "#2a1a12") if c["age"] != "old" else "#cfc8be")
    elif h == "cap":
        cap = smooth([(-60, -24), (-58, -64), (0, -84), (58, -64), (60, -24), (0, -34)], tension=0.5)
        shape(cv, cap, hc)


def draw_head(cv, c, ps, expr):
    s = c.get("head_scale", 1.0)
    cv.save()
    cv.scale(s, s)
    draw_head_back(cv, c, ps)
    skin = c["skin"]
    if ps.get("sick"):
        skin = mix(skin, "#a8b48a", 0.45)
    # kulaklar
    if c["head"] not in ("veil", "keffiyeh", "byz_helmet", "secutor", "murmillo", "thraex", "hoplo",
                         "roman_helmet", "long_hair"):
        for sx in (-1, 1):
            shape(cv, circle(sx * 60, 4, 12), shade(skin, 0.95), w=3.2)
    head = ellipse(0, 0, 60, 64)
    cv.drawPath(head, fill(skin))
    cv.save()
    cv.clipPath(head, skia.ClipOp.kIntersect, True)
    cv.drawPath(ellipse(28, 18, 50, 60), fill(shade(skin, 0.9), 120))
    cv.restore()
    cv.drawPath(head, stroke(OUT, OUTW))
    cc = dict(c)
    cc["skin"] = skin
    draw_beard(cv, cc, ps)
    draw_face(cv, cc, ps, expr)
    draw_mouth(cv, cc, ps, expr)
    if ps.get("sweat") or ps.get("sick"):
        for (x, y) in ((52, -40), (-56, -20)):
            d = smooth([(x, y - 12), (x + 6, y + 2), (x, y + 8), (x - 6, y + 2)])
            shape(cv, d, "#9fd4ff", w=2)
    if ps.get("tears"):
        for sx in (-1, 1):
            d = smooth([(sx * 26, 14), (sx * 31, 30), (sx * 26, 36), (sx * 21, 30)])
            shape(cv, d, "#8fd0ff", w=2)
    draw_head_front(cv, c, ps)
    if ps.get("bandage"):
        b = rrect(-64, -40, 128, 20, 8)
        shape(cv, b, "#f3eee2", w=3)
        cv.drawPath(circle(-30, -30, 7), fill("#b0201a", 200))
    cv.restore()


# ======================================================================== SILAHLAR
def draw_weapon(cv, c, hx, hy, ang, kind):
    r = math.radians(ang)
    dx, dy = math.sin(r), -math.cos(r)
    nx, ny = -dy, dx
    if kind in ("spear", "staff", "pole", "banner", "hoe", "torch"):
        top = 200 if kind != "staff" else 120
        if kind == "pole":
            top = 170
        bot = -90 if kind != "staff" else -150
        x0, y0 = hx + dx * bot, hy + dy * bot
        x1, y1 = hx + dx * top, hy + dy * top
        capsule(cv, x0, y0, x1, y1, 7, "#8a5a2e", ow=3)
        if kind == "spear":
            tip = poly([(x1 - nx * 9, y1 - ny * 9), (x1 + dx * 48, y1 + dy * 48), (x1 + nx * 9, y1 + ny * 9),
                        (x1 - dx * 6, y1 - dy * 6)])
            cv.drawPath(tip, lin_grad((x1 - nx * 9, y1), (x1 + nx * 9, y1), ["#f2f4f6", "#9aa3ab"]))
            cv.drawPath(tip, stroke(OUT, 3))
        elif kind == "banner":
            bc = c.get("banner_color", "#1d1b1a")
            fl = [(x1, y1), (x1 + nx * 110 + dx * -10, y1 + ny * 110 + dy * -10),
                  (x1 + nx * 96 - dx * 40, y1 + ny * 96 - dy * 40),
                  (x1 + nx * 112 - dx * 76, y1 + ny * 112 - dy * 76), (x1 - dx * 74, y1 - dy * 74)]
            shape(cv, smooth(fl, tension=0.3), bc)
            if c.get("cross"):
                cx_, cy_ = x1 + nx * 50 - dx * 36, y1 + ny * 50 - dy * 36
                cv.drawLine(cx_ - 14, cy_, cx_ + 14, cy_, stroke("#f0c040", 6))
                cv.drawLine(cx_, cy_ - 18, cx_, cy_ + 18, stroke("#f0c040", 6))
        elif kind == "hoe":
            cv.drawLine(x1, y1, x1 + nx * 34 - dx * 10, y1 + ny * 34 - dy * 10, stroke("#8f969c", 10))
        elif kind == "torch":
            cv.drawPath(circle(x1, y1 - 6, 16), blur_paint("#ffb020", 6))
            cv.drawPath(circle(x1, y1 - 4, 9), fill("#fff0a0"))
        elif kind == "staff" and c.get("cross"):
            cv.drawLine(x1 - 14, y1 + 14, x1 + 14, y1 + 14, stroke("#d9a83a", 6))
            cv.drawLine(x1, y1, x1, y1 + 30, stroke("#d9a83a", 6))
    elif kind in ("gladius", "rudis", "dagger"):
        L = {"gladius": 92, "rudis": 98, "dagger": 50}[kind]
        wd = 9 if kind != "dagger" else 6
        x0, y0 = hx + dx * 14, hy + dy * 14
        x1, y1 = hx + dx * L, hy + dy * L
        blade = poly([(x0 - nx * wd, y0 - ny * wd), (x1 - nx * wd * 0.8, y1 - ny * wd * 0.8),
                      (x1 + dx * 16, y1 + dy * 16), (x1 + nx * wd * 0.8, y1 + ny * wd * 0.8), (x0 + nx * wd, y0 + ny * wd)])
        if kind == "rudis":
            cv.drawPath(blade, lin_grad((x0 - nx * wd, y0 - ny * wd), (x0 + nx * wd, y0 + ny * wd),
                                        ["#d8a86a", "#a8783e", "#7a5228"]))
        else:
            cv.drawPath(blade, lin_grad((x0 - nx * wd, y0 - ny * wd), (x0 + nx * wd, y0 + ny * wd),
                                        ["#ffffff", "#b9c2ca", "#7d868e"]))
        cv.drawPath(blade, stroke(OUT, 3))
        gc = "#c9a040" if kind != "rudis" else "#6a4424"
        cv.drawLine(hx + dx * 10 - nx * 16, hy + dy * 10 - ny * 16, hx + dx * 10 + nx * 16,
                    hy + dy * 10 + ny * 16, stroke(OUT, 11))
        cv.drawLine(hx + dx * 10 - nx * 16, hy + dy * 10 - ny * 16, hx + dx * 10 + nx * 16,
                    hy + dy * 10 + ny * 16, stroke(gc, 7))
        cv.drawPath(circle(hx - dx * 15, hy - dy * 15, 8), fill(gc))
        cv.drawPath(circle(hx - dx * 15, hy - dy * 15, 8), stroke(OUT, 2.5))
    elif kind == "sica":
        x0, y0 = hx + dx * 14, hy + dy * 14
        pts = []
        for k in range(9):
            f = k / 8
            bend = math.sin(f * math.pi * 0.9) * 26 * f
            pts.append((x0 + dx * 80 * f + nx * bend, y0 + dy * 80 * f + ny * bend))
        p = P()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        cv.drawPath(p, stroke(OUT, 16))
        cv.drawPath(p, stroke("#c3cbd2", 10))
        cv.drawPath(p, stroke("#ffffff", 3))
        cv.drawLine(hx + dx * 10 - nx * 14, hy + dy * 10 - ny * 14, hx + dx * 10 + nx * 14,
                    hy + dy * 10 + ny * 14, stroke("#c9a040", 7))
    elif kind == "trident":
        bot, top = -90, 210
        x0, y0 = hx + dx * bot, hy + dy * bot
        x1, y1 = hx + dx * top, hy + dy * top
        capsule(cv, x0, y0, x1, y1, 7, "#8a5a2e", ow=3)
        cv.drawLine(x1 - nx * 22, y1 - ny * 22, x1 + nx * 22, y1 + ny * 22, stroke(OUT, 10))
        cv.drawLine(x1 - nx * 22, y1 - ny * 22, x1 + nx * 22, y1 + ny * 22, stroke("#aab2ba", 6))
        for k in (-1, 0, 1):
            bx_, by_ = x1 + nx * 20 * k, y1 + ny * 20 * k
            ex_, ey_ = bx_ + dx * (44 if k == 0 else 36), by_ + dy * (44 if k == 0 else 36)
            cv.drawLine(bx_, by_, ex_, ey_, stroke(OUT, 9))
            cv.drawLine(bx_, by_, ex_, ey_, stroke("#dfe5ea", 5))
            tip = poly([(ex_ - nx * 6, ey_ - ny * 6), (ex_ + dx * 12, ey_ + dy * 12), (ex_ + nx * 6, ey_ + ny * 6)])
            shape(cv, tip, "#dfe5ea", w=2.4)
    elif kind == "whip":
        x0, y0 = hx - dx * 14, hy - dy * 14
        x1, y1 = hx + dx * 46, hy + dy * 46
        capsule(cv, x0, y0, x1, y1, 8, "#5a3a22", ow=3)
        p = P()
        p.moveTo(x1, y1)
        p.cubicTo(x1 + dx * 60 + nx * 40, y1 + dy * 60 + ny * 40, x1 + dx * 30 + nx * 120, y1 + dy * 30 + ny * 120,
                  x1 - dx * 40 + nx * 150, y1 - dy * 40 + ny * 150)
        cv.drawPath(p, stroke(OUT, 6))
        cv.drawPath(p, stroke("#7a5030", 3))
    elif kind == "sword":
        x0, y0 = hx + dx * 14, hy + dy * 14
        x1, y1 = hx + dx * 128, hy + dy * 128
        blade = poly([(x0 - nx * 7, y0 - ny * 7), (x1 - nx * 5, y1 - ny * 5), (x1 + dx * 14, y1 + dy * 14),
                      (x1 + nx * 5, y1 + ny * 5), (x0 + nx * 7, y0 + ny * 7)])
        cv.drawPath(blade, lin_grad((x0 - nx * 7, y0 - ny * 7), (x0 + nx * 7, y0 + ny * 7),
                                    ["#ffffff", "#b9c2ca", "#7d868e"]))
        cv.drawPath(blade, stroke(OUT, 3))
        cv.drawLine(hx + dx * 10 - nx * 20, hy + dy * 10 - ny * 20, hx + dx * 10 + nx * 20,
                    hy + dy * 10 + ny * 20, stroke("#c9a040", 8))
        cv.drawPath(circle(hx - dx * 16, hy - dy * 16, 7), fill("#c9a040"))
        cv.drawPath(circle(hx - dx * 16, hy - dy * 16, 7), stroke(OUT, 2.5))
    elif kind == "bow":
        p = P()
        p.moveTo(hx + dx * 90 - nx * 6, hy + dy * 90 - ny * 6)
        p.quadTo(hx + nx * 40, hy + ny * 40, hx - dx * 90 - nx * 6, hy - dy * 90 - ny * 6)
        cv.drawPath(p, stroke(OUT, 10))
        cv.drawPath(p, stroke("#7a4a22", 6))
        cv.drawLine(hx + dx * 90 - nx * 6, hy + dy * 90 - ny * 6, hx - dx * 90 - nx * 6,
                    hy - dy * 90 - ny * 6, stroke("#efe6d0", 2))


def draw_shield(cv, c, x, y, kind, scale=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale, scale)
    sc = c.get("shield_color", "#9a6a3a")
    if kind == "round":
        cv.drawPath(circle(3, 5, 48), fill((0, 0, 0), 60))
        cv.drawPath(circle(0, 0, 48), rad_grad((-14, -16), 60, [shade(sc, 1.25), sc, shade(sc, 0.75)]))
        cv.drawPath(circle(0, 0, 48), stroke(OUT, OUTW))
        p = stroke(shade(sc, 0.55), 2.4)
        p.setPathEffect(skia.DashPathEffect.Make([7, 6], 0))
        cv.drawPath(circle(0, 0, 40), p)
        cv.drawPath(circle(0, 0, 12), fill("#b8bfc5"))
        cv.drawPath(circle(0, 0, 12), stroke(OUT, 3))
        if c.get("cross"):
            cv.drawLine(0, -30, 0, 30, stroke("#e8d8a8", 6))
            cv.drawLine(-22, -8, 22, -8, stroke("#e8d8a8", 6))
    elif kind == "scutum":
        body_ = rrect(-52, -82, 104, 164, 16)
        cv.drawPath(rrect(-48, -76, 104, 164, 16), fill((0, 0, 0), 60))
        cv.drawPath(body_, lin_grad((-52, 0), (52, 0), [shade(sc, 0.7), shade(sc, 1.2), sc, shade(sc, 0.7)],
                                    [0, 0.35, 0.65, 1]))
        cv.drawPath(rrect(-44, -74, 88, 148, 12), stroke("#e2b842", 4))
        cv.drawPath(body_, stroke(OUT, OUTW))
        for sy in (-1, 1):
            z = P()
            z.moveTo(-6, sy * 30)
            z.lineTo(10, sy * 44)
            z.lineTo(-4, sy * 52)
            z.lineTo(8, sy * 68)
            cv.drawPath(z, stroke("#e2b842", 4))
        cv.drawPath(circle(0, 0, 20), lin_grad((0, -20), (0, 20), ["#fff0b8", "#d9a548", "#8a5a1a"]))
        cv.drawPath(circle(0, 0, 20), stroke(OUT, 3))
    elif kind == "parmula":
        b_ = rrect(-36, -42, 72, 84, 8)
        cv.drawPath(rrect(-32, -36, 72, 84, 8), fill((0, 0, 0), 60))
        cv.drawPath(b_, rad_grad((-10, -14), 70, [shade(sc, 1.25), sc, shade(sc, 0.75)]))
        cv.drawPath(rrect(-29, -35, 58, 70, 5), stroke("#e2b842", 3))
        cv.drawPath(b_, stroke(OUT, OUTW))
        cv.drawPath(circle(0, 0, 10), fill("#e2b842"))
        cv.drawPath(circle(0, 0, 10), stroke(OUT, 2.4))
    elif kind == "hoplo":
        cv.drawPath(circle(3, 5, 40), fill((0, 0, 0), 60))
        cv.drawPath(circle(0, 0, 40), rad_grad((-12, -14), 52, ["#fff0b8", "#d9a548", "#8a5a1a"]))
        cv.drawPath(circle(0, 0, 40), stroke(OUT, OUTW))
        cv.drawPath(circle(0, 0, 32), stroke("#8a5a1a", 2.4))
        cv.drawPath(circle(0, 0, 9), fill("#fff0b8"))
        cv.drawPath(circle(0, 0, 9), stroke(OUT, 2.2))
    elif kind == "oval":
        e = ellipse(0, 0, 44, 66)
        cv.drawPath(ellipse(4, 6, 44, 66), fill((0, 0, 0), 60))
        cv.drawPath(e, rad_grad((-12, -20), 80, [shade(sc, 1.25), sc, shade(sc, 0.7)]))
        cv.drawPath(ellipse(0, 0, 38, 60), stroke("#e2b842", 4))
        cv.drawPath(e, stroke(OUT, OUTW))
        for sy in (-1, 1):
            w_ = P()
            w_.moveTo(-26, sy * 30)
            w_.quadTo(0, sy * 14, 26, sy * 30)
            cv.drawPath(w_, stroke("#e2b842", 4))
        cv.drawPath(circle(0, 0, 11), fill("#e2b842"))
        cv.drawPath(circle(0, 0, 11), stroke(OUT, 2.6))
    elif kind == "byz":
        e = ellipse(0, 0, 44, 66)
        cv.drawPath(ellipse(4, 6, 44, 66), fill((0, 0, 0), 60))
        cv.drawPath(e, rad_grad((-12, -20), 80, [shade(sc, 1.25), sc, shade(sc, 0.7)]))
        cv.drawPath(ellipse(0, 0, 38, 60), stroke("#e2b842", 5))
        cv.drawPath(e, stroke(OUT, OUTW))
        # chi-rho benzeri yildiz
        for a in (0, 60, 120):
            r = math.radians(a)
            cv.drawLine(-math.sin(r) * 34, -math.cos(r) * 50, math.sin(r) * 34, math.cos(r) * 50,
                        stroke("#e2b842", 5))
        cv.drawPath(circle(0, 0, 10), fill("#e2b842"))
        cv.drawPath(circle(0, 0, 10), stroke(OUT, 2.6))
    cv.restore()


# ======================================================================== GOVDE
def draw_person(cv, c, ps=None, x=0, y=0, scale=1.0, facing=1):
    if ps is None:
        ps = DEFAULT_POSE
    expr = ps.get("expr") or c.get("expr", "neutral")
    b = c.get("body", 1.0)
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    seated = ps.get("seated")
    walk = ps.get("walk")
    bob = ps.get("bob", 0.0)
    if walk is not None:
        bob += -abs(math.sin(walk)) * 6
    cv.translate(0, bob)
    if ps.get("lean"):
        cv.rotate(ps["lean"])
    sy = -150 * b
    hip = -58 * b
    hem = -24 if c["tunic_long"] else hip + 18
    if seated:
        hem = hip + 6
    bare = c.get("torso") == "bare"
    tunic = c["tunic"] if not bare else c["skin"]
    skin = c["skin"]
    if bare:
        hem = hip + 4

    # pelerin
    if c.get("cloak"):
        cl = [(-38, sy + 2), (-66, hem + 8 if not seated else hip + 10), (66, hem + 8 if not seated else hip + 10),
              (38, sy + 2)]
        rshape(cv, cl, c["cloak"], r=16)
    # sadak
    if c.get("quiver"):
        cv.save()
        cv.translate(-22, sy + 30)
        cv.rotate(-28)
        shape(cv, rrect(-14, -70, 28, 100, 8), "#6b4424", w=3.4)
        for k in range(3):
            cv.drawLine(-8 + k * 8, -70, -8 + k * 8, -92, stroke("#d8d0c0", 4))
            cv.drawPath(poly([(-8 + k * 8, -92), (-13 + k * 8, -104), (-3 + k * 8, -104)]), fill("#b03030"))
        cv.restore()

    # bacaklar
    if not seated:
        for sx, ph in ((-1, 0.0), (1, math.pi)):
            ang = 0.0
            if walk is not None:
                ang = math.sin(walk + ph) * 26
            r = math.radians(ang)
            hx, hy = sx * 17, hip
            L = -hip - 8
            fx, fy = hx + math.sin(r) * L, hy + math.cos(r) * L
            leg_c = c["legs"] if not c["boots"] else c["legs"]
            capsule(cv, hx, hy, fx, fy, 24 * min(1, b + 0.15), leg_c, ow=3.6)
            if c["boots"]:
                capsule(cv, hx + (fx - hx) * 0.55, hy + (fy - hy) * 0.55, fx, fy, 26, "#4a3020", ow=3.6)
            foot = ellipse(fx + 9, fy + 2, 19, 9)
            shape(cv, foot, c["shoe"] if not c["boots"] else "#3a2416", w=3.4)
            if not c["boots"] and c["tunic_long"]:
                cv.drawLine(fx - 8, fy - 8, fx + 10, fy - 4, stroke(c["shoe"], 3))
            gv = c.get("greave")
            if gv == "both" or (gv == "A" and sx < 0) or (gv == "B" and sx > 0):
                f0 = 0.12 if gv == "both" else 0.5
                gx0, gy0 = hx + (fx - hx) * f0, hy + (fy - hy) * f0
                capsule(cv, gx0, gy0, fx - (fx - hx) * 0.05, fy - 10, 28, "#d9a548", ow=3.4)
                cv.drawLine(gx0 - 6, gy0 + 6, fx - 6, fy - 16, stroke("#fff0b8", 3, 160))
                if gv == "both":
                    for k in range(3):
                        yy = gy0 + (fy - gy0) * (0.15 + k * 0.08)
                        cv.drawLine(gx0 - 13, yy, gx0 + 13, yy, stroke(shade("#d9a548", 0.7), 2))
    # govde
    wide = c.get("wide", 1.0)
    shw = (40 if not c["female"] else 36) * (1 + (wide - 1) * 0.6)
    hw = (54 if c["tunic_long"] else 50) * wide
    body_pts = [(-shw + 4, sy), (-shw - 6, sy + 22), (-hw + 6, hip), (-hw, hem), (hw, hem), (hw - 6, hip),
                (shw + 6, sy + 22), (shw - 4, sy)]
    bp = poly(body_pts)
    cv.drawPath(bp, round_paint(fill(tunic), 14))
    cv.save()
    cv.clipPath(bp, skia.ClipOp.kIntersect, True)
    cv.drawRect(skia.Rect.MakeLTRB(18, sy - 10, 70, 10), fill(shade(tunic, 0.82)))
    arm = c.get("armor")
    if arm == "mail":
        cv.drawRect(skia.Rect.MakeLTRB(-70, sy - 10, 70, hip + 14), fill("#8d949c"))
        for yy in range(int(sy - 4), int(hip + 14), 9):
            for xx in range(-64, 66, 10):
                cv.drawPath(circle(xx + ((yy // 9) % 2) * 5, yy, 4.2), stroke("#5f666e", 1.7))
        cv.drawRect(skia.Rect.MakeLTRB(18, sy - 10, 70, hip + 14), fill((0, 0, 0), 40))
    elif arm == "lamellar":
        cv.drawRect(skia.Rect.MakeLTRB(-70, sy - 10, 70, hip + 12), fill("#a6aeb6"))
        row = 0
        for yy in range(int(sy + 4), int(hip + 12), 12):
            for xx in range(-66, 70, 9):
                cv.drawPath(rrect(xx + (row % 2) * 4.5, yy, 8, 11, 2), stroke("#5f666e", 1.5))
            row += 1
        cv.drawRect(skia.Rect.MakeLTRB(18, sy - 10, 70, hip + 12), fill((0, 0, 0), 40))
        cv.drawLine(-60, hip + 12, 60, hip + 12, stroke("#c9a040", 5))
        # pteruges
        for xx in range(-44, 50, 12):
            cv.drawPath(rrect(xx - 5, hip + 14, 10, 24, 3), fill("#7a4a2a"))
            cv.drawPath(rrect(xx - 5, hip + 14, 10, 24, 3), stroke(OUT, 1.6))
    if c["name"] == "heraclius":
        cv.drawRect(skia.Rect.MakeLTRB(-12, sy, 12, hem), fill("#e0a92e"))
        cv.drawPath(rrect(-50, sy + 20, 36, 36, 4), fill("#e0a92e"))
    if bare and not c["female"]:
        for sx in (-1, 1):
            pc = P()
            pc.moveTo(sx * 4, sy + 40)
            pc.quadTo(sx * 22, sy + 50, sx * 34, sy + 36)
            cv.drawPath(pc, stroke(shade(skin, 0.72), 3))
        for k in range(2):
            cv.drawLine(-10, sy + 62 + k * 16, -2, sy + 64 + k * 16, stroke(shade(skin, 0.75), 2.4))
            cv.drawLine(10, sy + 62 + k * 16, 2, sy + 64 + k * 16, stroke(shade(skin, 0.75), 2.4))
        cv.drawPath(circle(0, sy + 84, 2.5), fill(shade(skin, 0.7)))
    if c.get("chest_band"):
        cv.drawRect(skia.Rect.MakeLTRB(-60, sy + 26, 60, sy + 52), fill(c["chest_band"]))
        cv.drawLine(-60, sy + 26, 60, sy + 26, stroke(OUT, 2.5))
        cv.drawLine(-60, sy + 52, 60, sy + 52, stroke(OUT, 2.5))
    if c.get("stripes"):
        for sx in (-1, 1):
            cv.drawRect(skia.Rect.MakeLTRB(sx * 20 - 5, sy - 10, sx * 20 + 5, hem + 10), fill(c["stripes"]))
    if c.get("scars"):
        for (x0, y0, x1, y1) in ((-26, sy + 30, -6, sy + 54), (14, sy + 70, 34, sy + 60)):
            cv.drawLine(x0, y0, x1, y1, stroke("#c86a5a", 3.4))
            for k in range(3):
                mx, my = x0 + (x1 - x0) * (k + 1) / 4, y0 + (y1 - y0) * (k + 1) / 4
                cv.drawLine(mx - 4, my + 4, mx + 4, my - 4, stroke("#c86a5a", 2))
    if c.get("himation"):
        hm = poly([(-shw - 2, sy - 2), (-shw + 22, sy - 6), (hw - 4, hip + 10), (hw - 2, hem if c["tunic_long"]
                   else hip + 26), (hw - 26, hem if c["tunic_long"] else hip + 26), (-shw - 8, sy + 40)])
        cv.drawPath(hm, round_paint(fill(c["himation"]), 10))
        for k in range(3):
            cv.drawLine(-shw + 4 + k * 14, sy + 12 + k * 4, hw - 30 + k * 6, hip + 6 + k * 8,
                        stroke(shade(c["himation"], 0.8), 2.4))
        cv.drawPath(hm, round_paint(stroke(OUT, 3), 10))
    cv.restore()
    cv.drawPath(bp, round_paint(stroke(OUT, OUTW), 14))
    # gladyator: subligaculum + balteus
    if bare:
        lc = c.get("loin", "#f1e9d6")
        loin = smooth([(-hw + 2, hip - 6), (hw - 2, hip - 6), (hw - 6, hip + 20), (18, hip + 26), (0, hip + 44),
                       (-18, hip + 26), (-hw + 6, hip + 20)], tension=0.3)
        shape(cv, loin, lc, w=3.4)
        cv.drawLine(-12, hip + 8, -4, hip + 34, stroke(shade(lc, 0.8), 2.4))
        cv.drawLine(12, hip + 8, 4, hip + 34, stroke(shade(lc, 0.8), 2.4))
    if bare and c.get("balteus"):
        bc_ = c["balteus"]
        bt = rrect(-hw + 2, hip - 20, (hw - 2) * 2, 22, 7)
        cv.drawPath(bt, lin_grad((0, hip - 20), (0, hip + 2), [shade(bc_, 1.3), bc_, shade(bc_, 0.75)]))
        cv.drawPath(bt, stroke(OUT, 3))
        for xx in range(int(-hw + 12), int(hw - 6), 14):
            cv.drawPath(circle(xx, hip - 9, 2.6), fill(shade(bc_, 0.6)))
    # kemer
    if (not arm or arm == "mail") and not bare:
        cv.drawPath(rrect(-hw + 4, hip - 10, (hw - 4) * 2, 14, 5), fill(c["belt"]))
        cv.drawPath(rrect(-hw + 4, hip - 10, (hw - 4) * 2, 14, 5), stroke(OUT, 3))
        if c.get("sash"):
            sp = smooth([(-hw + 6, hip - 12), (hw - 6, hip - 12), (hw - 4, hip + 4), (-hw + 4, hip + 4)])
            shape(cv, sp, c["sash"], w=3)
            tail = smooth([(10, hip), (24, hip + 30), (14, hip + 34), (4, hip + 4)])
            shape(cv, tail, shade(c["sash"], 0.85), w=3)
    # oturuyorsa: bacak
    if seated:
        capsule(cv, 10, hip + 4, 38, hip + 46, 26, c["legs"] if c["boots"] else tunic, ow=3.6)
        capsule(cv, 38, hip + 46, 32, hip + 92, 22, c["legs"] if c["boots"] else skin, ow=3.6)
        shape(cv, ellipse(44, hip + 96, 18, 9), "#3a2416", w=3.2)

    # kollar
    sl = tunic if not c.get("armor") else (tunic if c["armor"] != "lamellar" else c["tunic"])
    shoulder_y = sy + 14
    L = 74 * max(0.75, b)

    def arm_end(sx, ang):
        r = math.radians(ang)
        return sx * (shw + 2) + sx * math.sin(r) * L, shoulder_y + math.cos(r) * L

    ax, ay = arm_end(-1, ps["arm_a"])
    bx, by = arm_end(1, ps["arm_b"])
    def manica(x0, y0, x1, y1):
        capsule(cv, x0, y0, x1, y1, 25, "#e6dcc4", ow=3.4)
        for k in range(1, 6):
            f = k / 6
            mx, my = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
            ddx, ddy = (y1 - y0), -(x1 - x0)
            ln = math.hypot(ddx, ddy) + 1e-6
            ddx, ddy = ddx / ln * 12, ddy / ln * 12
            cv.drawLine(mx - ddx, my - ddy, mx + ddx, my + ddy, stroke("#9a8a6a", 2.4))

    # galerus (retiarius omuz kalkani) - kafanin arkasinda kalir
    if c.get("galerus"):
        gx = -(shw + 2)
        gal = smooth([(gx - 22, shoulder_y + 18), (gx - 30, shoulder_y - 30), (gx - 18, shoulder_y - 96),
                      (gx + 2, shoulder_y - 100), (gx + 14, shoulder_y - 40), (gx + 20, shoulder_y + 12)],
                     tension=0.4)
        cv.drawPath(gal, lin_grad((gx - 30, 0), (gx + 20, 0), ["#8a5a1a", "#e0b050", "#fff0b8"]))
        cv.drawPath(gal, stroke(OUT, 3.6))
    # kol A (sol)
    capsule(cv, -(shw + 2), shoulder_y, ax, ay, 22, sl, ow=3.6)
    if c.get("manica") == "A":
        manica(-(shw + 2), shoulder_y, ax, ay)
    cv.drawPath(circle(ax, ay, 12), fill(skin))
    cv.drawPath(circle(ax, ay, 12), stroke(OUT, 3.4))
    if c.get("item_a") == "net" and not ps.get("net_thrown"):
        nt = smooth([(ax - 10, ay - 6), (ax - 44, ay + 30), (ax - 40, ay + 86), (ax + 8, ay + 96), (ax + 34, ay + 60),
                     (ax + 14, ay + 4)], tension=0.5)
        cv.drawPath(nt, fill("#d8c8a0", 200))
        cv.save()
        cv.clipPath(nt, skia.ClipOp.kIntersect, True)
        for k in range(-6, 8):
            cv.drawLine(ax - 60 + k * 12, ay - 10, ax - 20 + k * 12, ay + 110, stroke("#8a7450", 2))
            cv.drawLine(ax + 60 + k * 12 - 120, ay - 10, ax + 20 + k * 12 - 120 + 80, ay + 110, stroke("#8a7450", 2))
        cv.restore()
        cv.drawPath(nt, stroke(OUT, 3))
    if c.get("shield"):
        draw_shield(cv, c, ax + 8, ay - 8, c["shield"], 1.0)

    # kafa
    head_cy = sy - 62 * c.get("head_scale", 1.0)
    cv.save()
    cv.translate(0, head_cy)
    if ps.get("head_tilt"):
        cv.rotate(ps["head_tilt"])
    draw_head(cv, c, ps, expr)
    cv.restore()

    # yaralar
    if ps.get("arrow"):
        cv.drawPath(circle(-24, sy + 18, 10), fill("#a01818", 220))
        cv.drawLine(-24, sy + 18, -70, sy - 40, stroke(OUT, 7))
        cv.drawLine(-24, sy + 18, -70, sy - 40, stroke("#7a5030", 4))
        for k in (-1, 1):
            cv.drawLine(-64, sy - 32, -64 + k * 10, sy - 50, stroke("#e8e0d0", 5))
    if ps.get("blood", 0) > 0:
        bl = ps["blood"]
        for (bx_, by_, r_) in ((14, sy + 40, 12), (-10, sy + 70, 9), (30, hip - 20, 7)):
            cv.drawPath(circle(bx_, by_, r_ * bl), fill("#9a1010", 210))

    # kol B (sag) + silah
    if c.get("weapon"):
        draw_weapon(cv, c, bx, by, ps.get("wpn", 8), c["weapon"])
    capsule(cv, shw + 2, shoulder_y, bx, by, 22, sl, ow=3.6)
    if c.get("manica") == "B":
        manica(shw + 2, shoulder_y, bx, by)
    if c.get("item"):
        draw_item(cv, c["item"], bx, by)
    cv.drawPath(circle(bx, by, 12), fill(skin))
    cv.drawPath(circle(bx, by, 12), stroke(OUT, 3.4))
    cv.restore()


def draw_item(cv, item, x, y):
    if item == "pen":
        cv.drawLine(x, y, x + 30, y - 40, stroke(OUT, 5))
        cv.drawLine(x, y, x + 30, y - 40, stroke("#e8dcc0", 3))
    elif item == "dates":
        for k in range(3):
            shape(cv, ellipse(x - 10 + k * 10, y - 14, 7, 11), "#6a2e12", w=2)
    elif item == "coin":
        shape(cv, circle(x, y - 14, 13), "#e8c050", w=3)
    elif item == "waterskin":
        shape(cv, smooth([(x - 6, y - 4), (x - 30, y + 20), (x - 22, y + 56), (x + 18, y + 56), (x + 26, y + 22),
                          (x + 6, y - 4)]), "#8a5a30")
    elif item == "scroll":
        shape(cv, rrect(x - 10, y - 48, 20, 52, 8), "#f2e2b8", w=3)
        shape(cv, rrect(x - 14, y - 52, 28, 10, 5), "#c9a870", w=2.4)
    elif item == "cup":
        shape(cv, poly([(x - 18, y - 40), (x + 18, y - 40), (x + 12, y - 8), (x - 12, y - 8)]), "#c9a870", w=3)
        cv.drawPath(ellipse(x, y - 40, 18, 5), fill("#8a8a80"))
    elif item == "bowl":
        shape(cv, smooth([(x - 30, y - 30), (x + 30, y - 30), (x + 20, y - 4), (x - 20, y - 4)]), "#a8623a", w=3)
        cv.drawPath(ellipse(x, y - 30, 30, 7), fill("#e8d8a8"))
        cv.drawPath(ellipse(x, y - 30, 30, 7), stroke(OUT, 2.4))
    elif item == "palm":
        cv.drawLine(x, y + 10, x + 10, y - 130, stroke(OUT, 7))
        cv.drawLine(x, y + 10, x + 10, y - 130, stroke("#5f8f3a", 4))
        for k in range(8):
            yy = y - 30 - k * 13
            for sg in (-1, 1):
                cv.drawLine(x + 3 + k * 1.2, yy, x + 3 + sg * (34 - k * 3), yy - 16, stroke("#5f8f3a", 4))
    elif item == "rope":
        cv.drawLine(x, y, x + 140, y - 30, stroke("#a07840", 4))


# ======================================================================== AT
def draw_horse(cv, x, y, scale=1.0, facing=1, phase=0.0, gallop=0.0, color="#7a4a2a", armored=False,
               mane="#2a1a10", rider=None, rider_pose=None, run_speed=1.0):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    bobv = -abs(math.sin(phase)) * 10 * gallop
    cv.translate(0, bobv)
    # bacaklar (arkadakiler)
    legs = [(-70, 0.0, True), (68, math.pi * 0.6, True), (-56, math.pi, False), (82, math.pi * 1.6, False)]

    def leg(lx, ph, back):
        a1 = math.sin(phase + ph) * 34 * gallop
        a2 = (math.cos(phase + ph) * 0.5 + 0.5) * 50 * gallop
        r1 = math.radians(a1)
        kx, ky = lx + math.sin(r1) * 62, -130 + math.cos(r1) * 62
        r2 = math.radians(a1 - a2 if lx > 0 else a1 + a2 * 0.4)
        fx, fy = kx + math.sin(r2) * 62, ky + math.cos(r2) * 62
        cc = shade(color, 0.78) if back else color
        capsule(cv, lx, -140, kx, ky, 20, cc, ow=3.6)
        capsule(cv, kx, ky, fx, fy, 15, cc, ow=3.6)
        shape(cv, rrect(fx - 11, fy - 6, 22, 12, 3), "#2a1a10", w=3)

    for lx, ph, back in legs[:2]:
        leg(lx, ph + math.pi * 0.5, True)
    # kuyruk
    sw = math.sin(phase * 0.5) * 10
    tail = smooth([(-104, -175), (-140, -160 + sw), (-160, -100 + sw), (-146, -96 + sw), (-122, -140),
                   (-100, -160)], tension=0.5)
    shape(cv, tail, mane)
    # govde
    body = smooth([(-110, -170), (-80, -196), (0, -200), (70, -196), (108, -170), (110, -132), (60, -112),
                   (-60, -112), (-112, -134)], tension=0.5)
    shape(cv, body, color)
    cv.save()
    cv.clipPath(body, skia.ClipOp.kIntersect, True)
    cv.drawPath(ellipse(0, -110, 130, 30), fill(shade(color, 0.8), 150))
    cv.drawPath(ellipse(-20, -190, 70, 14), fill(shade(color, 1.18), 110))
    cv.restore()
    shape(cv, body, None)
    # boyun + bas
    neck = smooth([(70, -190), (110, -246), (132, -290), (162, -296), (176, -270), (130, -200), (104, -160)],
                  tension=0.5)
    shape(cv, neck, color)
    headp = smooth([(124, -298), (154, -320), (230, -262), (236, -236), (216, -224), (150, -244)], tension=0.4)
    shape(cv, headp, color)
    shape(cv, ellipse(226, -238, 13, 11), shade(color, 0.8), w=3)
    cv.drawPath(circle(230, -240, 3), fill(OUT))
    shape(cv, poly([(136, -306), (140, -336), (156, -310)]), color, w=3)
    cv.drawPath(circle(160, -280, 7), fill("#ffffff"))
    cv.drawPath(circle(162, -280, 4), fill("#1a120c"))
    cv.drawPath(circle(160, -280, 7), stroke(OUT, 2.4))
    mn = smooth([(132, -300), (100, -260), (76, -206), (64, -196), (84, -246), (112, -290)], tension=0.5)
    shape(cv, mn, mane)
    if armored:
        for pth in (body, neck):
            cv.save()
            cv.clipPath(pth, skia.ClipOp.kIntersect, True)
            cv.drawRect(skia.Rect.MakeLTRB(-130, -320, 200, -100), fill("#9aa2aa"))
            for yy in range(-320, -100, 11):
                for xx in range(-130, 200, 12):
                    o = ((yy // 11) % 2) * 6
                    arc = P()
                    arc.moveTo(xx + o - 6, yy)
                    arc.quadTo(xx + o, yy + 12, xx + o + 6, yy)
                    cv.drawPath(arc, stroke("#5f666e", 1.8))
            cv.restore()
            shape(cv, pth, None)
        shape(cv, poly([(150, -300), (204, -258), (196, -246), (146, -276)]), "#c2c9d0", w=3)
    # eyer
    shape(cv, smooth([(-40, -198), (30, -200), (34, -176), (-44, -174)]), "#8a2222" if not armored else "#6a1a1a",
          w=3)
    # rider
    if rider is not None:
        rp = dict(rider_pose or DEFAULT_POSE)
        rp["seated"] = True
        draw_person(cv, rider, rp, x=-4, y=-160, scale=0.8, facing=1)
    for lx, ph, back in legs[2:]:
        leg(lx, ph + math.pi * 0.5, False)
    cv.restore()


# ======================================================================== DEVE
def draw_camel(cv, x, y, scale=1.0, facing=1, phase=0.0, walk=0.0, color="#c99a5e", load=False, rider=None,
               rider_pose=None, kneel=False):
    cv.save()
    cv.translate(x, y)
    cv.scale(scale * facing, scale)
    cv.translate(0, -abs(math.sin(phase)) * 6 * walk)
    if kneel:
        cv.translate(0, 100)

    def leg(lx, ph, back):
        a = math.sin(phase + ph) * 24 * walk
        r = math.radians(a)
        L1, L2 = 82, 84
        kx, ky = lx + math.sin(r) * L1, -170 + math.cos(r) * L1
        r2 = math.radians(a - abs(math.sin(phase + ph)) * 18 * walk)
        fx, fy = kx + math.sin(r2) * L2, ky + math.cos(r2) * L2
        if kneel:
            kx, ky, fx, fy = lx + 20, -110, lx - 30, -100
        cc = shade(color, 0.8) if back else color
        capsule(cv, lx, -180, kx, ky, 18, cc, ow=3.6)
        cv.drawPath(circle(kx, ky, 11), fill(cc))
        cv.drawPath(circle(kx, ky, 11), stroke(OUT, 3))
        capsule(cv, kx, ky, fx, fy, 14, cc, ow=3.6)
        shape(cv, ellipse(fx + 4, fy - 2, 15, 7), shade(color, 0.6), w=3)

    leg(-78, math.pi, True)
    leg(88, 0, True)
    tail = smooth([(-118, -230), (-134, -200), (-128, -168), (-120, -200)])
    shape(cv, tail, shade(color, 0.85), w=3)
    body = smooth([(-124, -220), (-100, -262), (-46, -320), (-10, -326), (30, -296), (90, -262), (126, -236),
                   (124, -196), (90, -176), (-90, -176), (-124, -192)], tension=0.5)
    shape(cv, body, color)
    cv.save()
    cv.clipPath(body, skia.ClipOp.kIntersect, True)
    cv.drawPath(ellipse(0, -176, 140, 30), fill(shade(color, 0.82), 150))
    cv.drawPath(ellipse(-20, -310, 40, 14), fill(shade(color, 1.15), 120))
    cv.restore()
    shape(cv, body, None)
    neck = smooth([(100, -250), (150, -240), (176, -276), (190, -330), (214, -340), (206, -300), (186, -240),
                   (150, -206), (112, -206)], tension=0.5)
    shape(cv, neck, color)
    headp = smooth([(190, -344), (220, -356), (262, -340), (270, -320), (250, -308), (204, -316)], tension=0.45)
    shape(cv, headp, color)
    lip = smooth([(252, -318), (272, -318), (270, -306), (250, -304)])
    shape(cv, lip, shade(color, 0.85), w=3)
    shape(cv, ellipse(204, -352, 7, 12), color, w=3)
    cv.drawPath(circle(226, -338, 8), fill("#ffffff"))
    cv.drawPath(circle(229, -337, 4), fill("#1a120c"))
    cv.drawPath(circle(226, -338, 8), stroke(OUT, 2.4))
    cv.drawLine(216, -347, 236, -345, stroke(OUT, 3.4))
    if load:
        shape(cv, rrect(-70, -300, 64, 70, 10), "#8a3a2a", w=3.4)
        shape(cv, rrect(10, -292, 60, 60, 10), "#5a6a3a", w=3.4)
        cv.drawLine(-80, -268, 80, -262, stroke("#d8c090", 5))
    else:
        shape(cv, smooth([(-60, -316), (40, -300), (44, -276), (-64, -290)]), "#a8282b", w=3)
        for k in range(5):
            cv.drawLine(-50 + k * 22, -286, -52 + k * 22, -270, stroke("#e8c050", 4))
    if rider is not None:
        rp = dict(rider_pose or DEFAULT_POSE)
        rp["seated"] = True
        draw_person(cv, rider, rp, x=-10, y=-284, scale=0.8, facing=1)
    leg(-62, 0, False)
    leg(104, math.pi, False)
    cv.restore()


# ======================================================================== SILUET
def silhouette_begin(cv, glow="#ffd27a", glow_a=200, dark="#17110c"):
    """Sahabe/halife gibi tarihi sahsiyetler yuzsuz siluetle gosterilir."""
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(rgb(dark), skia.BlendMode.kSrcIn))
    cv.saveLayer(None, p)


def silhouette_end(cv):
    cv.restore()


def draw_silhouette(cv, drawfn, glow="#ffd88a", glow_sigma=14, glow_a=220, dark="#1a130e"):
    # parlama
    gp = skia.Paint()
    gp.setColorFilter(skia.ColorFilters.Blend(rgb(glow, glow_a), skia.BlendMode.kSrcIn))
    gp.setImageFilter(skia.ImageFilters.Blur(glow_sigma, glow_sigma))
    cv.saveLayer(None, gp)
    drawfn(cv)
    cv.restore()
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Blend(rgb(dark), skia.BlendMode.kSrcIn))
    cv.saveLayer(None, p)
    drawfn(cv)
    cv.restore()

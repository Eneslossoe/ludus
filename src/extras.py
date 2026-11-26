"""Kucuk resim (thumbnail), altyazi (SRT) ve YouTube aciklamasi uretir."""
import json
import math
import os

import skia

import backgrounds as B
import characters as C
import effects as FX
import engine as E
import kit as K
from gfx import (OUT, W, H, big_number, fill, label_tag, lin_grad, poly, rgb, ribbon, stroke, vignette)
from script import CHAPTERS, TITLE

WORK = os.environ.get("ZK_WORK", "/home/user/work")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(ROOT, "output")


def thumbnail(path):
    s = skia.Surface(W, H)
    cv = s.getCanvas()
    left = poly([(0, 0), (1010, 0), (900, H), (0, H)])
    right = poly([(1010, 0), (W, 0), (W, H), (900, H)])
    cv.save()
    cv.clipPath(left, skia.ClipOp.kIntersect, True)
    E.draw_bg(cv, "tunnel", B.tunnel)
    B.portcullis(cv, 620, 1300, 250, 900, 0.0)
    cv.drawRect(skia.Rect.MakeWH(W, H), fill("#10182a", 90))
    C.draw_person(cv, C.preset("secutor"), C.pose(expr="scared", look=(0.7, -0.2), arm_a=-24, arm_b=70, wpn=80),
                  470, 1290, 2.15, 1)
    cv.restore()
    cv.save()
    cv.clipPath(right, skia.ClipOp.kIntersect, True)
    cv.drawRect(skia.Rect.MakeWH(W, H), lin_grad((0, 0), (0, H), ["#ffcf6a", "#f3a640", "#c66a20"]))
    for k in range(16):
        a = math.radians(-90 + (k - 8) * 11)
        cv.drawPath(poly([(1460, 760), (1460 + math.cos(a) * 1400 + 50, 760 + math.sin(a) * 1400),
                          (1460 + math.cos(a) * 1400 - 50, 760 + math.sin(a) * 1400)]), fill("#fff2b0", 50))
    B.crowd_band(cv, 900, W + 20, 760, 1.0, 7, dark=0.7)
    B.crowd_band(cv, 900, W + 20, 820, 1.1, 8, dark=0.75)
    cv.drawRect(skia.Rect.MakeLTRB(900, 840, W, H), fill("#e6c98e"))
    C.draw_person(cv, C.preset("retiarius"), C.pose(expr="happy", look=(-0.6, 0), arm_a=40, arm_b=50, wpn=10,
                                                    mouth=0.6), 1480, 1280, 2.05, -1)
    cv.restore()
    zig = [(1010, -20), (950, 300), (995, 330), (900, 700), (945, 720), (860, 1100)]
    cv.drawPath(poly(zig, closed=False), stroke("#ffffff", 26))
    cv.drawPath(poly(zig, closed=False), stroke("#ffe680", 11))
    cv.save()
    cv.translate(W / 2, 250)
    big_number(cv, "MS 160", 0, 0, 210, rot=-2)
    cv.restore()
    ribbon(cv, "GLADYATÖR OKULUNA DÜŞSEYDİN?", W / 2, 360, 70, rot=-2.5, maxw=1800)
    label_tag(cv, "SEN", 220, 1000, 72, rot=-6)
    label_tag(cv, "RETIARIUS", 1690, 1000, 64, rot=5)
    vignette(cv, 90)
    img = s.makeImageSnapshot()
    small = skia.Surface(1280, 720)
    small.getCanvas().drawImageRect(img, skia.Rect.MakeWH(1280, 720),
                                    skia.SamplingOptions(skia.CubicResampler.Mitchell()))
    small.makeImageSnapshot().save(path, skia.kJPEG, 92)
    img.save(path.replace(".jpg", "_1080p.png"), skia.kPNG)


def fmt(t):
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"


def srt(path):
    tl = json.load(open(os.path.join(WORK, "timeline.json")))
    idx = 1
    out = []
    for sh in tl["shots"]:
        for l in sh["lines"]:
            txt = l["sub"]
            a, b = sh["start"] + l["start"], sh["start"] + l["end"]
            words = txt.split()
            chunks, cur = [], ""
            for w in words:
                if len(cur) + len(w) + 1 > 80 and cur:
                    chunks.append(cur)
                    cur = w
                else:
                    cur = (cur + " " + w).strip()
            if cur:
                chunks.append(cur)
            total = sum(len(c) for c in chunks)
            t = a
            for c in chunks:
                d = (b - a) * len(c) / total
                if len(c) > 42:
                    ws = c.split()
                    best = min(range(1, len(ws)), key=lambda k: abs(len(" ".join(ws[:k])) - len(c) / 2))
                    c = " ".join(ws[:best]) + "\n" + " ".join(ws[best:])
                if l["voice"] == "q":
                    c = "“" + c + "”"
                out.append(f"{idx}\n{fmt(t)} --> {fmt(t + d)}\n{c}\n")
                idx += 1
                t += d
    open(path, "w", encoding="utf-8").write("\n".join(out))


def description(path):
    tl = json.load(open(os.path.join(WORK, "timeline.json")))
    lines = [TITLE, "",
             "Yıl MS 160. Bergama'da, karanlık bir tünelde, demir parmaklıkların ardında bekliyorsun. Karşında ağ ve "
             "üç dişli zıpkınla bir retiarius... Antik Yunan dünyasında, yani Roma'nın Anadolu'daki Yunan "
             "şehirlerinde bir gladyatör okuluna (ludus) düşseydin hayatın nasıl olurdu? İzmir'de borç batağından "
             "gladyatör yeminine, tahta kılıçla geçen eğitimden 'arpa adamları'nın sofrasına, okulun doktoru "
             "Galenos'tan arena gününe ve özgürlüğün sembolü tahta kılıca (rudis) kadar bir gladyatörün hikâyesi.",
             "", "Sen olsan hangi gladyatör olurdun: retiarius mu, murmillo mu, thraex mi? Yorumlara yaz!", "",
             "⏱ BÖLÜMLER"]
    for sh in tl["shots"]:
        if sh["id"] in CHAPTERS:
            t = sh["start"]
            lines.append(f"{int(t // 60):d}:{int(t % 60):02d} {CHAPTERS[sh['id']]}")
    lines += ["",
              "📚 Not: Gladyatör dövüşleri klasik Yunan değil, Roma geleneğidir; MS 2. yüzyılda Roma yönetimindeki "
              "Yunan şehirlerinde (Efes, Bergama, İzmir, Afrodisias) yaygınlaşmıştır. Demetrios kurgusal bir "
              "karakterdir; çevresindeki bilgiler tarihsel kaynaklara dayanır. Ölüm oranları ve beslenmenin koruyucu "
              "etkisi gibi konular tarihçilerin tahminleridir.",
              "",
              "📖 Kaynaklar",
              "- Livius, Roma Tarihi 41.20 (Kral Antiokhos'un gladyatör gösterileri)",
              "- Lukianos, Toxaris (Amastris'te Sisinnes'in hikâyesi)",
              "- Petronius, Satyricon 117; Seneca, Mektuplar 37 (gladyatör yemini)",
              "- Yaşlı Plinius, Doğa Tarihi 18.72 (hordearii) ve 36.203 (kül içeceği)",
              "- Plutarkhos, Moralia 1099B (dövüş öncesi son yemek)",
              "- Galenos'un eserleri (Bergama'da gladyatör hekimliği, MS 157–161)",
              "- Kanz & Grossschmidt (2006); Lösch ve ark. (2014, PLOS ONE): Efes gladyatör mezarlığı",
              "- Halikarnassos kabartması: Amazon ve Achillia (British Museum)",
              "- Diodoros'un mezar taşı (Yunanca gladyatör yazıtı)",
              "- L. Robert, Les gladiateurs dans l'Orient grec (1940); G. Ville, La gladiature en Occident (1981)",
              "",
              "🎙 Bu videonun tüm görselleri, animasyonları, müziği, efektleri ve seslendirmesi kodla üretilmiştir.",
              "", "#ZamanKırığı #Gladyatör #AntikYunan #Roma #Bergama #Efes #Tarih #Olsaydın", "",
              "ETİKETLER: gladyatör, gladyatör okulu, ludus, antik yunan, roma imparatorluğu, bergama, pergamon, efes, "
              "izmir, smyrna, galenos, retiarius, murmillo, thraex, secutor, arena, gladyatör yemini, "
              "efes gladyatör mezarlığı, kadın gladyatör, halikarnassos, olsaydın, zaman kırığı, tarih animasyon"]
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    os.makedirs(OUTD, exist_ok=True)
    thumbnail(os.path.join(OUTD, "kucuk_resim.jpg"))
    srt(os.path.join(OUTD, "altyazi_tr.srt"))
    description(os.path.join(OUTD, "youtube_aciklama.txt"))
    print("ok")

# Zaman Kırığı — Antik Yunan'da Bir Gladyatör Okuluna Düşseydin?

Bu depo, "Zaman Kırığı" kanalı için hazırlanan videonun **tamamen kodla üretilmiş** kaynaklarını içerir:
görseller, animasyonlar, haritalar, müzik, ses efektleri ve seslendirme. Hiçbir hazır görsel/ses dosyası,
stok içerik veya ElevenLabs kullanılmamıştır.

## Çıktılar (`output/`)

| Dosya | Açıklama |
|---|---|
| `gladyator_okulu_olsaydin_github.mp4` | 1920×1080, 30 fps final video (GitHub 100 MB sınırı için sıkıştırılmış kopya) |
| `reels_gladyator_okulu.mp4` | 1080×1920 dikey Reels/Shorts (60 sn altı), büyük altyazılı |
| `kucuk_resim.jpg` | 1280×720 YouTube küçük resmi (kanal stilinde) |
| `kucuk_resim_1080p.png` | Küçük resmin yüksek çözünürlüklü hâli |
| `altyazi_tr.srt` | Türkçe altyazı (YouTube'a yüklenebilir) |
| `youtube_aciklama.txt` | Başlık, açıklama, bölüm zaman damgaları, kaynaklar, etiketler |

## Hikâye

MS 160, Roma'nın Asya eyaleti. İzmirli (Smyrna) genç Demetrios babasından kalan borçlar yüzünden kendini bir
lanistaya satar, gladyatör yeminini eder ve Bergama'daki gladyatör okuluna (ludus) düşer. Video; gladyatörlüğün
Yunan dünyasına nasıl geldiğini, okula düşmenin yollarını, tahta kılıç (rudis) ve kazıkla (palus) eğitimi,
gladyatör türlerini (murmillo, thraex, hoplomachus, retiarius, secutor), "arpa adamları"nın beslenmesini,
okulun doktoru Galenos'u, şöhret ve utancı, oyun gününü, arenadaki dövüşü, missio'yu ve özgürlüğü anlatır.

Tarihsel dayanaklar: Livius 41.20, Lukianos (Toxaris), Petronius 117 / Seneca Ep. 37 (yemin), Yaşlı Plinius 18.72
ve 36.203, Plutarkhos Moralia 1099B, Galenos, Efes gladyatör mezarlığı çalışmaları (Kanz & Grossschmidt 2006;
Lösch ve ark. 2014), Halikarnassos'taki Amazon–Achillia kabartması, Diodoros'un mezar taşı, L. Robert (1940),
G. Ville (1981). Demetrios kurgusal bir karakterdir.

## Nasıl üretildi?

- **Seslendirme:** Açık kaynak, yerel çalışan [Piper](https://github.com/rhasspy/piper) Türkçe sesleri
  (`tr_TR-dfki-medium` anlatıcı, `tr_TR-fahrettin-medium` alıntılar: gladyatör yemini, Diodoros'un mezar taşı).
  `src/tts.py`
- **Çizimler:** `skia-python` ile vektörel çizim. Karakterler ve gladyatör teçhizatı (`src/characters.py`),
  mekânlar: arena, tünel, ludus avlusu, hücre, Bergama akropolü, İzmir limanı, Efes kazısı… (`src/backgrounds.py`),
  kart/ikon parçaları (`src/kit.py`), efektler (`src/effects.py`).
- **Haritalar:** `global-land-mask` kara/deniz verisiyle parşömen stili haritalar. `src/maps.py`
- **Müzik:** Dor ve Frig modlarında lir (kithara), aulos, tympanon, krotala, su orgu (hydraulis), kornu ve koro;
  numpy ile sentezlendi. `src/synth.py`, `src/music.py`
- **Efektler:** Kalabalık, tezahürat ("Bırak onu!"), tahta kılıç, kalkan çınlaması, kırbaç, zincir, demir kapı,
  ağ, düşüş, miğfer içi nefes, ateş, deniz, cırcır böcekleri… hepsi matematiksel olarak sentezlendi. `src/audio.py`
- **Sahneler:** 56 sahne; senaryo `src/script.py`, çizimler `src/shots1.py`, `src/shots2.py`, `src/shots3.py`.

## Yeniden üretmek

```bash
pip install skia-python piper-tts soundfile scipy numpy global-land-mask
# Linux'ta skia için: apt-get install -y libegl1 libgl1
# Piper Türkçe ses modelleri: $ZK_WORK/models/vits-piper-tr_TR-{dfki,fahrettin}-medium/
#   (https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models)
export ZK_WORK=/home/user/work
cd src
python3 tts.py                  # seslendirme + timeline.json
python3 audio.py                # müzik + efekt + miksaj -> soundtrack.wav
python3 render.py video         # sahne sahne render -> video_noaudio.mp4
python3 final.py                # ses + görüntü, -14 LUFS -> output/
python3 extras.py               # küçük resim, altyazı, açıklama
python3 reels.py                # dikey Reels/Shorts
```

Tek bir sahneyi yeniden çizmek: `python3 render.py video --only s46` ; test karesi: `python3 render.py stills s46:3.0`

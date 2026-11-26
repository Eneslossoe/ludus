"""Video senaryosu: anlatim satirlari + sahne listesi.

Her sahne: (id, fonksiyon, [satirlar], ekstra)
Satir basinda "q:" olan satirlar alinti sesiyle okunur.
Satirlar TTS icin yazilmistir (sayilar yaziyla, Latince terimler okunusa yakin);
altyazidaki dogru imla SUB_FIX ile geri getirilir.
"""

TITLE = "Antik Yunan'da Bir Gladyatör Okuluna Düşseydin?"
SHORT = "GLADYATÖR OLSAYDIN?"

SHOTS = [
    # ------------------------------------------------------------ GIRIS
    ("s01", "hook_tunnel", [
        "Yıl yüz altmış. Anadolu'nun Ege kıyısında, Bergama'dasın.",
        "Karanlık bir tünelin içinde bekliyorsun. Demir parmaklıkların ardında, binlerce kişinin uğultusu yükseliyor.",
        "Başında ağır bir tunç miğfer, elinde kısa bir kılıç ve büyük bir kalkan. Kalbin, göğsünden çıkacak gibi atıyor.",
    ], dict(music="intro", lead=0.9)),
    ("s02", "hook_opponent", [
        "Kapı açıldığında karşına çıkacak adamın ise ne miğferi var, ne de kalkanı. Sadece bir ağ, ve üç dişli bir zıpkın.",
    ], {}),
    ("s03", "hook_question", [
        "Peki Antik Yunan dünyasında bir gladyatör okuluna düşseydin, hayatın nasıl olurdu?",
        "Ve en önemlisi, o arenadan sağ çıkabilir miydin? Hazırsan, zaman kırığından geçiyoruz.",
    ], {}),
    ("s04", "title_card", [], dict(dur=4.4)),

    # ------------------------------------------------------------ BOLUM 1
    ("s05", "chapter", [], dict(dur=3.2, num=1, title="YUNAN'DA GLADYATÖR MÜ?", sub="Roma'nın oyunu, Yunan'ın sahnesi",
                                music="greek")),
    ("s06", "greek_vs_roman", [
        "Önce şunu bilelim: Klasik çağın Yunanlıları gladyatör nedir bilmezdi. Onların sporu, Olimpiyat oyunlarıydı. Koşu, güreş, pankration.",
        "Gladyatör dövüşleri ise bir Roma geleneğiydi. Başlangıçta, önemli kişilerin cenazelerinde yapılan kanlı bir törendi.",
    ], {}),
    ("s07", "spread_map", [
        "Ama Roma, Yunanistan'ı ve Anadolu'yu fethettikçe, bu gelenek de doğuya yayıldı.",
        "Milattan önce ikinci yüzyılda, Suriye kralı Antiohos, Roma'dan getirttiği gladyatörlerle bir gösteri düzenledi.",
        "Roma tarihçisi Livius'a göre halk önce dehşete düştü. Sonra alıştı. Sonra da bayıldı.",
    ], {}),
    ("s08", "greek_cities", [
        "Senin zamanında, Anadolu'nun Yunan şehirleri bu dövüşlerle çalkalanıyordu. Efes, Bergama, İzmir, Afrodisias...",
        "Tiyatrolar ve stadyumlar arenaya dönüştü. Yunanlılar bu savaşçılara monomahos derdi. Yani, teke tek dövüşen.",
    ], {}),
    ("s09", "philosophers", [
        "Bazı Yunan filozofları, insanların birbirini öldürmesini seyretmeyi utanç verici buluyordu.",
        "Ama kalabalığın sesi, filozoflarınkinden çok daha yüksekti.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 2
    ("s10", "chapter", [], dict(dur=3.2, num=2, title="OKULA DÜŞMEK", sub="Smyrna (İzmir), MS 160", music="sad")),
    ("s11", "smyrna", [
        "Hikayemiz İzmir'de başlıyor. O zamanki adıyla Smirna.",
        "Adın Demetrios olsun. Limanın yakınında, küçük bir çömlekçi dükkanı olan bir ailenin oğlusun.",
    ], {}),
    ("s12", "debt", [
        "Ama baban ölünce, geriye bir dükkandan çok daha fazlası kalıyor: borçlar.",
        "Alacaklılar her gün kapınızda. Annen ve küçük kardeşin için, bir çıkış yolu bulmak zorundasın.",
    ], {}),
    ("s13", "four_roads", [
        "Peki insanlar gladyatör okuluna nasıl düşerdi? Çoğu, kendi isteğiyle değil.",
        "Kimi bir savaş esiriydi, kimi okula mahkum edilmiş bir suçlu, kimi de satılmış bir köle.",
        "Ama bir yol daha vardı: Özgür bir insanın, kendini para karşılığında okula bağlaması.",
    ], {}),
    ("s14", "lucian", [
        "Yunan yazar Lukianos, Amastris'te, yani bugünkü Amasra'da, arkadaşına yardım etmek için on bin drahmiye arenaya çıkan Sisinnes adlı bir gencin hikayesini anlatır.",
    ], {}),
    ("s15", "recruiter", [
        "Senin karşına da bir gün bir lanista çıkıyor, yani bir gladyatör tüccarı.",
        "Teklifi basit: Borçlarını kapatacak kadar para. Karşılığında, birkaç yıllık hayatın.",
    ], {}),
    ("s16", "oath", [
        "Kabul ediyorsun. Ve insanın kanını donduran o yemini ediyorsun:",
        "q:Yakılmaya, zincire vurulmaya, dövülmeye ve kılıçla öldürülmeye razıyım.",
        "Artık toplumun gözünde, utanç verici bir mesleğin sahibisin.",
    ], dict(music="dark")),

    # ------------------------------------------------------------ BOLUM 3
    ("s17", "chapter", [], dict(dur=3.2, num=3, title="LUDUS", sub="Bergama'daki gladyatör okulu", music="ludus")),
    ("s18", "road_pergamon", [
        "Birkaç gün sonra kuzeye, Bergama'ya varıyorsun.",
        "Bu okulun gladyatörleri, Asya eyaletinin başrahibine ait. İmparator onuruna büyük oyunlar düzenleyen zengin bir adam.",
    ], {}),
    ("s19", "courtyard", [
        "Kapıdan girince kum serili bir avlu görüyorsun. Etrafında sütunlu bir revak ve sıra sıra küçük hücreler.",
        "Kapıda nöbetçiler var. Kaçmak mı? Aklından bile geçirme.",
    ], {}),
    ("s20", "cell", [
        "Senin hücren birkaç adım genişliğinde. Bir saman yatak, küçük bir kandil ve ağır bir kapı.",
        "Gece, diğer hücrelerden inlemeler ve dualar duyuyorsun.",
    ], {}),
    ("s21", "familia", [
        "Bu okuldaki herkes artık senin ailen. Onlara familia denir.",
        "Trakyalı bir savaş esiri, Mısırlı bir kaçak köle, Galatyalı bir hırsız... Bir gün arenada, birbirinizle dövüşebilirsiniz.",
    ], {}),
    ("s22", "tiro", [
        "Okulun en alt basamağındasın. Hiç dövüşmemiş bir acemiye tiro denir.",
        "Bir de yeni bir adın olacak. Gösterişli bir sahne adı: Nikeforos. Yani, zafer getiren.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 4
    ("s23", "chapter", [], dict(dur=3.2, num=4, title="EĞİTİM", sub="Tahta kılıç ve kazık")),
    ("s24", "palus", [
        "Eğitim şafakta başlar. İlk aylarda gerçek kılıca dokunmazsın bile. Elinde ağır, tahta bir kılıç var: rudis.",
        "Karşında yere çakılmış bir kazık. Saatlerce ona vurursun. Kolların kopacak gibi olana kadar.",
    ], {}),
    ("s25", "trainer", [
        "Hocaların, eski gladyatörler. Bağırırlar, iterler, gerekirse kırbaçlarlar.",
        "Ama bildikleri her hareket, bir gün seni hayatta tutabilir.",
    ], {}),
    ("s26", "types", [
        "Çünkü her gladyatör türünün, kendine özgü silahı ve zırhı vardı.",
        "Murmillo; büyük kalkanı ve sorguçlu miğferiyle ağır bir piyade. Traks; küçük kalkanı ve kıvrık kılıcıyla çevik bir dövüşçü.",
        "Hoplomakus; mızrağı ve yuvarlak kalkanıyla eski Yunan hoplitlerini andırırdı.",
        "Ve en tuhafı: retiarius. Miğfersiz, kalkansız. Elinde sadece bir ağ ve üç dişli bir zıpkın.",
    ], {}),
    ("s27", "pairing", [
        "Dövüşler rastgele değildi. Her tür, kendisine denk bir rakiple eşleştirilirdi. Ağır olan çevik olanla, kalkanlı olan ağlı olanla.",
    ], {}),
    ("s28", "secutor", [
        "Aylar sonra hocalar karar verir: Sen bir sekutorsun, yani takipçi. Görevin, ağlı retiariusu kovalamak.",
        "Miğferin pürüzsüz ve yuvarlak, ki ağ takılmasın. Gözler için sadece iki küçük delik var. İçinde nefes almak bile zor.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 5
    ("s29", "chapter", [], dict(dur=3.2, num=5, title="ARPA ADAMLARI", sub="Yemek, ilaç ve Galenos", music="greek2")),
    ("s30", "barley", [
        "Peki bir gladyatör ne yerdi? Et değil. Romalı yazar Plinius'a göre, gladyatörlere arpa adamları denirdi.",
        "Menüde arpa lapası, bakla ve fasulye var. Bazı araştırmacılara göre bu yemekler, koruyucu bir yağ tabakası da kazandırıyordu.",
    ], {}),
    ("s31", "ephesus_bones", [
        "Bunu nereden mi biliyoruz? Bin dokuz yüz doksan üç yılında, Efes'te bir gladyatör mezarlığı bulundu.",
        "Kemikler, bu adamların ağırlıklı olarak bitkisel beslendiğini gösterdi. Yüksek mineral oranı ise kül karıştırılmış bir içeceğe işaret ediyordu.",
        "Plinius da, gladyatörlerin dövüşten sonra bitki külünden bir içecek içtiğini yazar.",
    ], {}),
    ("s32", "galen", [
        "Ve şansına bak: Okulun doktoru, tıp tarihinin en ünlü isimlerinden biri olacak genç bir adam: Galenos.",
        "Galenos yaraları şaraplı bezlerle sarar, gladyatörlerin beslenmesini düzenlerdi.",
        "Kendi iddiasına göre, onun döneminde ölen gladyatör sayısı çok azaldı.",
    ], {}),
    ("s33", "investment", [
        "Neden bu kadar özen mi? Çünkü sen, sahibin için pahalı bir yatırımsın. Ölü bir gladyatör, kimseye para kazandırmaz.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 6
    ("s34", "chapter", [], dict(dur=3.2, num=6, title="ŞÖHRET VE UTANÇ", sub="Hem alkışlanan, hem aşağılanan")),
    ("s35", "fame", [
        "Kazanan gladyatörler, bugünün futbol yıldızları gibiydi. Resimleri kandillere işlenirdi.",
        "İtalya'da, Pompei'deki bir duvar yazısı, Keladus adlı bir gladyatörü, kızların iç çektiği adam diye anar.",
    ], {}),
    ("s36", "infamia", [
        "Ama aynı kalabalık, arenanın dışında seni küçümser. Toplumun gözünde bir gladyatör, oyunculardan bile aşağıdaydı.",
    ], {}),
    ("s37", "family", [
        "Yine de pek çok gladyatörün bir ailesi vardı. Anadolu'da bulunan gladyatör mezar taşlarının birçoğunu, onların eşleri diktirmişti.",
    ], {}),
    ("s38", "women", [
        "Ve evet, kadın gladyatörler de vardı. Bodrum'da, antik Halikarnassos'ta bulunan bir kabartma, Amazon ve Ahillia adlı iki kadın gladyatörü gösterir.",
        "Yazıya göre, ikisi de bağışlanmıştı.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 7
    ("s39", "chapter", [], dict(dur=3.2, num=7, title="OYUN GÜNÜ", sub="Munus", music="feast")),
    ("s40", "announcement", [
        "Sonunda o gün yaklaşıyor. Duvarlara boyalı ilanlar yazılır: Başrahip, imparator onuruna oyunlar düzenliyor!",
        "Programda hayvan avları, idamlar ve elbette, gladyatörler var.",
    ], {}),
    ("s41", "last_supper", [
        "Dövüşten önceki gece, gladyatörlere halka açık bir ziyafet verilir. Masalar et ve şarapla dolu, meraklı halk etrafınızda dolaşır.",
        "Bazıları tıka basa yer, bazıları tek lokma yutamaz. Plutarhos, bu son yemekte bazı gladyatörlerin karılarını arkadaşlarına emanet ettiğini anlatır.",
    ], {}),
    ("s42", "morning", [
        "Sabah kalabalık stadyumu doldurur. Önce hayvan avları, öğlen idamlar.",
        "Ve öğleden sonra, herkesin beklediği an: gladyatörler.",
    ], dict(music="festival")),
    ("s43", "parade", [
        "Önce bir geçit töreni. Borular çalar, su orgu inler.",
        "Silahlarınız başrahibin önünde tek tek kontrol edilir. Keskin mi? Gerçek mi? Hile yok.",
    ], {}),

    # ------------------------------------------------------------ BOLUM 8
    ("s44", "chapter", [], dict(dur=3.2, num=8, title="ARENA", sub="Secutor, retiariusa karşı", music="arena_pre")),
    ("s45", "gate_open", [
        "Ve senin sıran geliyor. Kapı açılıyor. Güneş gözlerini kör ediyor.",
        "Karşında bir retiarius. Çevik, hafif ve sırıtıyor. İki hakem, uzun sopalarıyla dövüşü yönetiyor.",
    ], {}),
    ("s46", "fight", [
        "İşaret verilir. O kaçar, sen kovalarsın. Miğferinin içinde, kendi nefesini duyuyorsun.",
        "Bir zıpkın darbesi! Kalkanın son anda yetişiyor. Kılıcını savuruyorsun, kalabalık çılgına dönüyor.",
    ], dict(music="arena")),
    ("s47", "net", [
        "Ve sonra ağ havalanıyor. Kalkanına dolanıyor, ayağın kayıyor.",
        "Kumun üstüne sırt üstü düşüyorsun. Retiarius tepende, zıpkın boğazında.",
    ], {}),
    ("s48", "finger", [
        "Kural belli: Teslim olan gladyatör, bir parmağını kaldırır. Kaldırıyorsun.",
        "Şimdi karar, oyunları düzenleyen adamın. Ama o da kalabalığa bakar. Bu arada, filmlerdeki o başparmak işaretinin anlamını, aslında kimse kesin olarak bilmiyor.",
    ], dict(music="heartbeat")),
    ("s49", "missio", [
        "Binlerce ağızdan aynı söz yükselir: Bırak onu! İyi dövüştün, kalabalık seni sevdi.",
        "Başrahip elini kaldırır ve hayatını bağışlar. Buna missio denir. Bugün ölmeyeceksin.",
    ], dict(music="relief")),
    ("s50", "death_rule", [
        "Ama herkes bu kadar şanslı değildi. Bağışlanmayan gladyatörün, son darbeyi kıpırdamadan, onurla karşılaması beklenirdi.",
        "Efes'te bulunan bir kafatasında, yan yana üç delik var. Tıpkı bir zıpkının üç dişi gibi.",
    ], dict(music="sad")),

    # ------------------------------------------------------------ BOLUM 9
    ("s51", "chapter", [], dict(dur=3.2, num=9, title="ÖZGÜRLÜK YA DA MEZAR", sub="Tahta kılıç")),
    ("s52", "odds", [
        "Peki hayatta kalma şansın ne kadardı? Sanıldığının aksine, her dövüş ölümle bitmezdi.",
        "Bir gladyatör yılda iki üç kez dövüşürdü. Bazı tahminlere göre birinci yüzyılda, kabaca her on dövüşten birinde bir gladyatör ölüyordu.",
        "Ama zamanla bu oran arttı. Efes'teki adamların çoğu, yirmi ile otuz yaş arasında ölmüştü.",
    ], {}),
    ("s53", "diodorus", [
        "Bir mezar taşında, Diodoros adlı bir gladyatörün sitemi okunur:",
        "q:Rakibim Demetrios'u yere serdim, ama hemen öldürmedim. Beni öldüren, kader ve hakemin hilesi oldu.",
    ], {}),
    ("s54", "rudis", [
        "Ama yıllarca hayatta kalırsan, bir gün sana tahta bir kılıç verilir: rudis. Yani, artık özgürsün.",
        "Bazıları okullara hoca olarak döndü. Bazıları ise para ve alkış için, yeniden arenaya çıktı.",
    ], dict(music="epic_end")),
    ("s55", "homecoming", [
        "Belki sen de borçlarını kapatıp İzmir'e dönersin. Elinde tahta bir kılıç, vücudunda yara izleri ve anlatacak bir sürü hikayeyle.",
    ], {}),
    ("s56", "outro", [
        "Peki sen olsaydın, hangi gladyatör olurdun? Ağlı bir retiarius mu, ağır kalkanlı bir murmillo mu, yoksa kıvrık kılıçlı bir traks mı?",
        "Cevabını yorumlara yaz. Zaman Kırığı'na abone olmayı ve bildirimleri açmayı unutma. Bir sonraki videoda görüşmek üzere!",
    ], dict(music="outro", tail=3.0)),
]

# Altyazida farkli yazilmasi gerekenler (TTS icin sadelestirilmis -> dogru imla)
SUB_FIX = {
    "Yıl yüz altmış.": "Yıl MS 160.",
    "Hikayemiz": "Hikâyemiz", "hikaye": "hikâye", "dükkanı": "dükkânı", "dükkandan": "dükkândan",
    "mahkum": "mahkûm",
    "Smirna": "Smyrna", "Antiohos": "Antiokhos", "Plutarhos": "Plutarkhos", "monomahos": "monomakhos",
    "Nikeforos": "Nikephoros", "Traks": "Thraex", "traks": "thraex", "Hoplomakus": "Hoplomachus",
    "sekutorsun": "secutorsun", "sekutor": "secutor", "Keladus": "Celadus", "Pompei'deki": "Pompeii'deki", "Ahillia": "Achillia",
    "on bin drahmiye": "10 bin drahmiye", "Bin dokuz yüz doksan üç": "1993",
    "yirmi ile otuz": "20 ile 30", "her on dövüşten": "her 10 dövüşten", "kabaca her on": "kabaca her 10", "birinci yüzyılda": "1. yüzyılda",
    "ikinci yüzyılda": "2. yüzyılda", "iki üç kez": "2-3 kez",
}

# Bolum basliklari (YouTube bolumleri icin)
CHAPTERS = {
    "s01": "Giriş", "s05": "Yunan'da gladyatör mü?", "s10": "Okula düşmek", "s17": "Ludus: Gladyatör okulu",
    "s23": "Eğitim ve gladyatör türleri", "s29": "Arpa adamları ve Galenos", "s34": "Şöhret ve utanç",
    "s39": "Oyun günü", "s44": "Arena", "s51": "Özgürlük ya da mezar",
}

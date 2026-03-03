# ============================================================
# hizli_okuma_engine.py — v1.0
# Hızlı Okuma + Okuduğunu Anlama Testi
# 4 Kademe: 5-6 / 7-8 / 9-10 / 11-12
# Her kademe: 1 metin + 10 anlama sorusu
# Ölçüm: Kelime/Dakika (WPM) + Anlama Yüzdesi
# ============================================================

KADEME_MAP = {
    5: "kademe_1", 6: "kademe_1",
    7: "kademe_2", 8: "kademe_2",
    9: "kademe_3", 10: "kademe_3",
    11: "kademe_4", 12: "kademe_4",
}

KADEME_LABELS = {
    "kademe_1": "5-6. Sınıf (Temel)",
    "kademe_2": "7-8. Sınıf (Orta)",
    "kademe_3": "9-10. Sınıf (İleri)",
    "kademe_4": "11-12. Sınıf (Üst)",
}

# ============================================================
# YAŞA GÖRE OKUMA HIZI NORMLARI (Kelime/Dakika)
# Türkçe okuma hızı referans değerleri
# ============================================================
WPM_NORMS = {
    "kademe_1": {
        "cok_yavas":  60,   # %0-10
        "yavas":      80,   # %10-25
        "ortalama":   110,  # %25-75
        "hizli":      140,  # %75-90
        "cok_hizli":  170,  # %90+
    },
    "kademe_2": {
        "cok_yavas":  90,
        "yavas":      120,
        "ortalama":   155,
        "hizli":      190,
        "cok_hizli":  230,
    },
    "kademe_3": {
        "cok_yavas":  120,
        "yavas":      155,
        "ortalama":   195,
        "hizli":      240,
        "cok_hizli":  280,
    },
    "kademe_4": {
        "cok_yavas":  150,
        "yavas":      185,
        "ortalama":   230,
        "hizli":      275,
        "cok_hizli":  320,
    },
}

def grade_to_kademe(grade):
    return KADEME_MAP.get(grade, "kademe_2")


# ============================================================
# KADEME 1 — 5-6. SINIF METİNLERİ
# ============================================================
K1_PASSAGES = [
    {
        "id": "k1_p1",
        "title": "Deniz Kaplumbağalarının Yolculuğu",
        "text": (
            "Deniz kaplumbağaları, dünyanın en ilginç gezginlerinden biridir. Her yıl binlerce kilometre yüzerek "
            "doğdukları sahillere geri dönerler. Dişi kaplumbağalar yumurtalarını kumda açtıkları çukurlara bırakır "
            "ve üzerlerini kumla örter. Yaklaşık iki ay sonra yumurtadan çıkan minik yavrular, ay ışığının "
            "yansımasını takip ederek denize ulaşmaya çalışır. Ancak bu yolculuk oldukça tehlikelidir. Kuşlar, "
            "yengeçler ve diğer avcılar yavruları yakalamaya çalışır. Denize ulaşmayı başaran yavrulardan sadece "
            "binde biri yetişkin olabilir.\n\n"
            "Bilim insanları, deniz kaplumbağalarının dünyanın manyetik alanını kullanarak yollarını bulduğunu "
            "keşfetmiştir. Bu yetenek sayesinde okyanusun ortasında bile kaybolmadan binlerce kilometre yüzebilirler. "
            "Kaplumbağalar ayrıca denizanası, yosun ve küçük deniz canlılarıyla beslenir. Plastik poşetler "
            "denizanasına benzediği için kaplumbağalar bazen bunları yutarak hastalanır veya ölür.\n\n"
            "Bugün yedi deniz kaplumbağası türünden altısı nesli tehlike altında olan canlılar listesindedir. "
            "Sahillerdeki yapay ışıklar, yavruların deniz yerine karaya doğru yönelmesine neden olur. Plastik "
            "kirliliği, iklim değişikliği ve avlanma da kaplumbağaların hayatını tehdit etmektedir. Birçok ülke "
            "kaplumbağa yumurtlama sahillerini koruma altına almış ve gönüllü koruma programları başlatmıştır. "
            "Türkiye'de de Dalyan, Patara ve Anamur gibi sahiller önemli yumurtlama alanlarıdır."
        ),
        "questions": [
            {"id": "k1_p1_q1", "text": "Dişi kaplumbağalar yumurtalarını nereye bırakır?",
             "options": {"a": "Denizin dibine", "b": "Kayaların arasına", "c": "Kumda açtıkları çukurlara", "d": "Ağaçların altına"},
             "answer": "c"},
            {"id": "k1_p1_q2", "text": "Yumurtadan çıkan yavrular denizi nasıl bulur?",
             "options": {"a": "Annelerini takip ederek", "b": "Ay ışığının yansımasını takip ederek", "c": "Koku alarak", "d": "Rüzgârı takip ederek"},
             "answer": "b"},
            {"id": "k1_p1_q3", "text": "Denize ulaşan yavrulardan ne kadarı yetişkin olabilir?",
             "options": {"a": "Yarısı", "b": "Onda biri", "c": "Binde biri", "d": "Hepsi"},
             "answer": "c"},
            {"id": "k1_p1_q4", "text": "Kaplumbağalar yollarını nasıl bulur?",
             "options": {"a": "Yıldızlara bakarak", "b": "Dünyanın manyetik alanını kullanarak", "c": "Akıntıları takip ederek", "d": "Diğer kaplumbağaları izleyerek"},
             "answer": "b"},
            {"id": "k1_p1_q5", "text": "Plastik poşetler neden kaplumbağalar için tehlikelidir?",
             "options": {"a": "Gürültü çıkardığı için", "b": "Suyun sıcaklığını değiştirdiği için", "c": "Denizanasına benzediği için yutarlar", "d": "Yüzmelerini engellediği için"},
             "answer": "c"},
            {"id": "k1_p1_q6", "text": "Kaç deniz kaplumbağası türü nesli tehlike altındadır?",
             "options": {"a": "Üç", "b": "Dört", "c": "Beş", "d": "Altı"},
             "answer": "d"},
            {"id": "k1_p1_q7", "text": "Sahillerdeki yapay ışıklar yavruları nasıl etkiler?",
             "options": {"a": "Daha hızlı büyümelerini sağlar", "b": "Deniz yerine karaya yönelmelerine neden olur", "c": "Yumurtadan daha erken çıkmalarına neden olur", "d": "Hiç etkilemez"},
             "answer": "b"},
            {"id": "k1_p1_q8", "text": "Aşağıdakilerden hangisi Türkiye'deki kaplumbağa yumurtlama sahillerinden biridir?",
             "options": {"a": "Kızkumu", "b": "Dalyan", "c": "Ölüdeniz", "d": "Çeşme"},
             "answer": "b"},
            {"id": "k1_p1_q9", "text": "Metnin ana düşüncesi aşağıdakilerden hangisidir?",
             "options": {"a": "Kaplumbağalar çok hızlı yüzer", "b": "Deniz kaplumbağaları ilginç canlılardır ve korunmaya ihtiyaçları vardır", "c": "Türkiye'nin sahilleri çok güzeldir", "d": "Plastik poşetler yasaklanmalıdır"},
             "answer": "b"},
            {"id": "k1_p1_q10", "text": "Yumurtalar yaklaşık ne kadar sürede yavruya dönüşür?",
             "options": {"a": "Bir hafta", "b": "İki hafta", "c": "Bir ay", "d": "İki ay"},
             "answer": "d"},
        ],
    },
]

# ============================================================
# KADEME 2 — 7-8. SINIF METİNLERİ
# ============================================================
K2_PASSAGES = [
    {
        "id": "k2_p1",
        "title": "Yapay Zekâ ve Geleceğimiz",
        "text": (
            "Yapay zekâ, son yılların en çok konuşulan teknolojik gelişmesidir. Bilgisayarların insan gibi "
            "düşünmesi, öğrenmesi ve karar vermesi anlamına gelen bu kavram, hayatımızın birçok alanına girmiştir. "
            "Telefonlarımızdaki sesli asistanlar, sosyal medyadaki öneri algoritmaları ve otomobillerdeki sürücü "
            "destek sistemleri yapay zekânın günlük hayattaki örneklerindendir.\n\n"
            "Yapay zekânın temelinde makine öğrenmesi adı verilen bir yöntem bulunur. Bu yöntemde bilgisayarlara "
            "büyük miktarda veri verilir ve bilgisayar bu verilerden kalıplar çıkararak kendi kendine öğrenir. "
            "Örneğin bir yapay zekâya milyonlarca kedi fotoğrafı gösterildiğinde, bir süre sonra daha önce hiç "
            "görmediği bir kedi fotoğrafını tanıyabilir hâle gelir. Bu süreç insan beynindeki öğrenmeye benzer "
            "ama çok daha hızlı gerçekleşir.\n\n"
            "Tıp alanında yapay zekâ büyük bir devrim yaratmaktadır. Röntgen ve MR görüntülerini analiz ederek "
            "hastalıkları doktorlardan daha erken tespit edebilen sistemler geliştirilmiştir. İlaç geliştirme "
            "sürecinde de yapay zekâ, yıllar süren deneyleri aylar içinde tamamlayabilmektedir. Eğitim alanında "
            "ise her öğrencinin seviyesine göre özelleştirilmiş ders içerikleri sunan akıllı sistemler "
            "kullanılmaya başlanmıştır.\n\n"
            "Ancak yapay zekânın bazı riskleri de bulunmaktadır. İş gücü piyasasında birçok mesleğin ortadan "
            "kalkacağı öngörülmektedir. Fabrika işçiliği, veri girişi, çeviri gibi tekrara dayalı işler yapay "
            "zekâ tarafından devralınabilir. Bunun yanı sıra gizlilik ve güvenlik sorunları da endişe "
            "yaratmaktadır. Yüz tanıma teknolojisinin kötüye kullanılması veya yapay zekânın önyargılı kararlar "
            "vermesi tartışılan konular arasındadır.\n\n"
            "Uzmanlar, yapay zekânın insanların yerini almayacağını, aksine onlarla birlikte çalışacağını "
            "düşünmektedir. Gelecekte en başarılı olanlar, yapay zekâyı etkili bir şekilde kullanabilen insanlar "
            "olacaktır. Bu nedenle eleştirel düşünme, yaratıcılık ve duygusal zekâ gibi insana özgü becerilerin "
            "önemi daha da artacaktır. Yapay zekâ bir araçtır ve bu aracı nasıl kullandığımız, geleceğimizi "
            "şekillendirecektir."
        ),
        "questions": [
            {"id": "k2_p1_q1", "text": "Makine öğrenmesi nasıl çalışır?",
             "options": {"a": "Bilgisayara tek tek kurallar yazılır", "b": "Bilgisayar büyük verilerden kalıplar çıkararak kendi kendine öğrenir", "c": "İnsan beyni bilgisayara bağlanır", "d": "Bilgisayarlar birbirleriyle konuşarak öğrenir"},
             "answer": "b"},
            {"id": "k2_p1_q2", "text": "Tıp alanında yapay zekânın en önemli katkısı nedir?",
             "options": {"a": "Ameliyat yapmak", "b": "Hastalıkları erken tespit etmek", "c": "Doktorların yerini almak", "d": "Hastane yönetimi"},
             "answer": "b"},
            {"id": "k2_p1_q3", "text": "Aşağıdakilerden hangisi yapay zekâ tarafından devralınabilecek işlerden değildir?",
             "options": {"a": "Veri girişi", "b": "Fabrika işçiliği", "c": "Yaratıcı sanat", "d": "Çeviri"},
             "answer": "c"},
            {"id": "k2_p1_q4", "text": "Yüz tanıma teknolojisiyle ilgili endişe nedir?",
             "options": {"a": "Çok pahalı olması", "b": "Yavaş çalışması", "c": "Kötüye kullanılma riski", "d": "Sadece beyaz yüzleri tanıması"},
             "answer": "c"},
            {"id": "k2_p1_q5", "text": "Uzmanlar gelecekte en başarılı olacak kişilerin hangi özelliğe sahip olacağını düşünüyor?",
             "options": {"a": "En hızlı yazabilenler", "b": "Yapay zekâyı etkili kullanabilenler", "c": "En çok programlama dili bilenler", "d": "Robotlardan kaçınanlar"},
             "answer": "b"},
            {"id": "k2_p1_q6", "text": "Yapay zekânın eğitim alanındaki kullanımı nedir?",
             "options": {"a": "Öğretmenlerin maaşını hesaplamak", "b": "Her öğrencinin seviyesine göre özelleştirilmiş ders içerikleri sunmak", "c": "Sınav sorularını sızdırmak", "d": "Öğrencilerin notlarını yükseltmek"},
             "answer": "b"},
            {"id": "k2_p1_q7", "text": "Metne göre yapay zekânın öğrenmesi insan beyninden nasıl farklıdır?",
             "options": {"a": "Daha yavaştır", "b": "Hiç farklı değildir", "c": "Daha az doğrudur", "d": "Çok daha hızlı gerçekleşir"},
             "answer": "d"},
            {"id": "k2_p1_q8", "text": "İlaç geliştirmede yapay zekânın avantajı nedir?",
             "options": {"a": "İlaçları ücretsiz yapar", "b": "Yıllar süren deneyleri aylar içinde tamamlayabilir", "c": "Hiç yan etkisi olmayan ilaçlar üretir", "d": "İlaç kullanımını ortadan kaldırır"},
             "answer": "b"},
            {"id": "k2_p1_q9", "text": "Metnin son paragrafındaki ana mesaj nedir?",
             "options": {"a": "Yapay zekâ tehlikelidir", "b": "Herkes programlama öğrenmeli", "c": "İnsana özgü becerilerin önemi artacak ve yapay zekâ bir araç olarak doğru kullanılmalı", "d": "Yapay zekâ yasaklanmalı"},
             "answer": "c"},
            {"id": "k2_p1_q10", "text": "Aşağıdakilerden hangisi metinde insana özgü beceri olarak belirtilmemiştir?",
             "options": {"a": "Eleştirel düşünme", "b": "Yaratıcılık", "c": "Hızlı hesaplama", "d": "Duygusal zekâ"},
             "answer": "c"},
        ],
    },
]

# ============================================================
# KADEME 3 — 9-10. SINIF METİNLERİ
# ============================================================
K3_PASSAGES = [
    {
        "id": "k3_p1",
        "title": "Bilişsel Önyargılar ve Karar Alma",
        "text": (
            "İnsan beyni, saniyede milyonlarca bilgiyi işleyen olağanüstü bir organdır. Ancak bu muazzam işlem "
            "gücüne rağmen, beynimiz sistematik düşünme hataları yapabilir. Psikologlar bu hatalara bilişsel "
            "önyargı adını verir. Bilişsel önyargılar, evrimsel süreçte hayatta kalmamızı kolaylaştırmak için "
            "gelişmiş zihinsel kestirme yollardır; ancak modern dünyada çoğu zaman bizi yanlış kararlara "
            "götürebilir.\n\n"
            "En yaygın bilişsel önyargılardan biri doğrulama önyargısıdır. İnsanlar, zaten inandıkları şeyleri "
            "destekleyen bilgileri arayıp bulma, buna karşın inançlarıyla çelişen bilgileri görmezden gelme "
            "eğilimindedir. Örneğin bir kişi alternatif tıbba inanıyorsa, bu yöntemlerin işe yaradığını gösteren "
            "haberlere dikkat ederken bilimsel çalışmaların aksini kanıtladığı bilgileri göz ardı edecektir. "
            "Sosyal medya algoritmaları, kullanıcılara sevdikleri içerikleri göstererek doğrulama önyargısını "
            "daha da güçlendirmektedir.\n\n"
            "Bir diğer önemli önyargı çıpalama etkisidir. Karar verirken karşılaştığımız ilk bilgi, sonraki "
            "değerlendirmelerimizi orantısız biçimde etkiler. Bir mağazada 500 TL'lik bir ceketin üzerinde "
            "\"eski fiyatı 1200 TL\" yazıyorsa, gerçekte o ceket 500 TL değerinde olsa bile bize ucuz gelir. "
            "Pazarlıkta ilk teklifi veren tarafın avantajlı olmasının nedeni de budur. Emlak piyasasında "
            "satıcının belirlediği ilk fiyat, alıcının değer algısını şekillendirir.\n\n"
            "Hayatta kalma önyargısı da sıklıkla gözden kaçar. Başarılı girişimcilerin hikayeleri medyada sürekli "
            "yer alırken, aynı yolu izleyip başarısız olan binlerce kişi görünmez kalır. Bu durum, başarı "
            "olasılığının gerçekte olduğundan çok daha yüksek algılanmasına neden olur. Üniversite terkleri "
            "başarılı olduğunda haber olur, ancak büyük çoğunluğunun zor durumda kaldığı gösterilmez.\n\n"
            "Grup düşüncesi önyargısı ise topluluk içinde ortaya çıkar. Bir grubun üyeleri, uyum bozmamak "
            "adına farklı fikirlerini söylemekten kaçınır ve grubun genel görüşüne uyum sağlar. Tarihte birçok "
            "felaket, karar vericilerin birbirlerini eleştirmekten kaçındığı ortamlarda meydana gelmiştir.\n\n"
            "Bilişsel önyargıların farkında olmak, onları tamamen ortadan kaldırmaz ancak etkilerini azaltabilir. "
            "Eleştirel düşünme eğitimi, farklı bakış açılarını değerlendirme alışkanlığı ve önemli kararlarda "
            "acele etmemek, daha sağlıklı düşünme ve karar alma süreçlerinin temelini oluşturur. Veriye dayalı "
            "düşünme ve kendi düşüncelerimizi sorgulama cesareti, modern dünyanın belki de en değerli "
            "becerilerindendir."
        ),
        "questions": [
            {"id": "k3_p1_q1", "text": "Bilişsel önyargılar evrimsel süreçte hangi amaçla gelişmiştir?",
             "options": {"a": "Sanat üretmek için", "b": "Hayatta kalmayı kolaylaştırmak için", "c": "Sosyal ilişkileri güçlendirmek için", "d": "Dil öğrenmeyi hızlandırmak için"},
             "answer": "b"},
            {"id": "k3_p1_q2", "text": "Doğrulama önyargısı nedir?",
             "options": {"a": "Her bilgiyi doğru kabul etme", "b": "İnandığımız şeyleri destekleyen bilgileri arayıp çelişenleri görmezden gelme", "c": "Başkalarının fikirlerini onaylama", "d": "Her zaman doğru karar verme"},
             "answer": "b"},
            {"id": "k3_p1_q3", "text": "Sosyal medya algoritmaları doğrulama önyargısını nasıl etkiler?",
             "options": {"a": "Azaltır", "b": "Farklı görüşler sunarak dengeler", "c": "Kullanıcılara sevdikleri içerikleri göstererek güçlendirir", "d": "Hiç etkilemez"},
             "answer": "c"},
            {"id": "k3_p1_q4", "text": "Çıpalama etkisine göre pazarlıkta kim avantajlıdır?",
             "options": {"a": "Son teklifi veren", "b": "En çok pazarlık yapan", "c": "İlk teklifi veren taraf", "d": "Sessiz kalan taraf"},
             "answer": "c"},
            {"id": "k3_p1_q5", "text": "Hayatta kalma önyargısının sonucu nedir?",
             "options": {"a": "Herkes hayatta kalır", "b": "Başarı olasılığı olduğundan yüksek algılanır", "c": "Başarısızlar hep hatırlanır", "d": "Medya dengelidir"},
             "answer": "b"},
            {"id": "k3_p1_q6", "text": "Grup düşüncesi önyargısında ne olur?",
             "options": {"a": "Herkes özgürce fikrini söyler", "b": "Grup bölünür", "c": "Üyeler uyum bozmamak için farklı fikirlerini söylemekten kaçınır", "d": "Lider her zaman haklı çıkar"},
             "answer": "c"},
            {"id": "k3_p1_q7", "text": "Metne göre bilişsel önyargılar tamamen ortadan kaldırılabilir mi?",
             "options": {"a": "Evet, eğitimle tamamen ortadan kalkar", "b": "Hayır, ama farkındalıkla etkileri azaltılabilir", "c": "Sadece çocuklukta önlenebilir", "d": "İlaçla tedavi edilebilir"},
             "answer": "b"},
            {"id": "k3_p1_q8", "text": "Çıpalama etkisi emlak piyasasında nasıl işler?",
             "options": {"a": "Alıcı ilk fiyatı belirler", "b": "Satıcının belirlediği ilk fiyat alıcının değer algısını şekillendirir", "c": "Banka faiz oranını belirler", "d": "Devlet fiyat belirler"},
             "answer": "b"},
            {"id": "k3_p1_q9", "text": "Metinde modern dünyanın en değerli becerisi olarak ne gösterilmiştir?",
             "options": {"a": "Hızlı karar verme", "b": "Çok çalışma", "c": "Veriye dayalı düşünme ve kendi düşüncelerimizi sorgulama cesareti", "d": "Gruba uyum sağlama"},
             "answer": "c"},
            {"id": "k3_p1_q10", "text": "Aşağıdakilerden hangisi metinde bahsedilen bir önyargı türü değildir?",
             "options": {"a": "Doğrulama önyargısı", "b": "Çıpalama etkisi", "c": "Otorite önyargısı", "d": "Hayatta kalma önyargısı"},
             "answer": "c"},
        ],
    },
]

# ============================================================
# KADEME 4 — 11-12. SINIF METİNLERİ
# ============================================================
K4_PASSAGES = [
    {
        "id": "k4_p1",
        "title": "Entropi, Düzen ve Evrenin Kaderi",
        "text": (
            "Termodinamiğin ikinci yasası, fizik biliminin en temel ve en felsefi yasalarından biridir. Bu yasa, "
            "kapalı bir sistemdeki düzensizliğin — yani entropinin — zamanla her zaman artacağını söyler. Bir "
            "bardak sıcak çayın soğuması, buzun erimesi, demir bir çitin paslanması; bunların hepsi entropinin "
            "artışının günlük hayattaki tezahürleridir. Doğada kendiliğinden gerçekleşen süreçler her zaman "
            "düzenden düzensizliğe doğru ilerler.\n\n"
            "Entropi kavramı ilk kez 1865'te Alman fizikçi Rudolf Clausius tarafından formüle edilmiştir. "
            "Clausius, buhar makinelerinin verimliliğini incelerken, enerjinin her dönüşümde bir miktar "
            "kullanılamaz hâle geldiğini fark etmiştir. Bu kullanılamaz enerji entropiyle doğru orantılıdır. "
            "Ludwig Boltzmann ise entropiyi istatistiksel bir çerçeveye oturtarak, bir sistemin mikro durumlarının "
            "sayısıyla ilişkilendirmiştir. Boltzmann'ın ünlü denklemi S = k log W, entropi ile olasılık arasındaki "
            "derin bağlantıyı ortaya koyar: bir sistemin en olası durumu, aynı zamanda en düzensiz olanıdır.\n\n"
            "Entropinin artışı, zamanın yönünü belirleyen temel mekanizmadır. Fiziğin diğer yasaları — Newton "
            "mekaniği, elektromanyetizma, hatta kuantum mekaniği — zamanın yönüne karşı simetriktir; yani bu "
            "yasalara göre olaylar geriye doğru da aynı şekilde işleyebilir. Ancak termodinamiğin ikinci yasası "
            "bu simetriyi kırar. Kırılan bir yumurtanın kendiliğinden birleşmemesinin, geçmişi hatırlayıp geleceği "
            "hatırlayamamamızın nedeni entropinin sürekli artmasıdır. Fizikçi Arthur Eddington bu durumu \"zamanın "
            "oku\" olarak adlandırmıştır.\n\n"
            "Canlı sistemler, ilk bakışta entropiye meydan okuyor gibi görünür. Bir tohum, karmaşık bir ağaca "
            "dönüşürken düzeni artırıyor gibidir. Ancak bu bir yanılsamadır. Canlılar, kendi iç düzenlerini "
            "artırırken çevrelerine daha fazla düzensizlik yayar. Fotosentez yapan bir bitki güneş enerjisini "
            "düzenli yapılara dönüştürürken, ısı olarak çevresine entropi ihraç eder. Erwin Schrödinger'in "
            "ifadesiyle yaşam, negatif entropi ile beslenir.\n\n"
            "Evrensel ölçekte entropi artışı, kozmolojinin en büyük sorularından birini gündeme getirir: "
            "evrenin kaderi ne olacaktır? Eğer entropi artmaya devam ederse, evren sonunda \"ısı ölümü\" denilen "
            "bir duruma ulaşacaktır. Bu senaryoda tüm enerji eşit olarak dağılmış, hiçbir iş yapılamaz, hiçbir "
            "yapı var olamaz bir denge durumu oluşur. Yıldızlar sönmüş, kara delikler buharlaşmış, evren tekdüze "
            "ve soğuk bir boşluğa dönüşmüş olacaktır. Bu son, büyük patlama ile başlayan kozmik hikâyenin en "
            "sessiz finali olacaktır."
        ),
        "questions": [
            {"id": "k4_p1_q1", "text": "Termodinamiğin ikinci yasası temelde ne söyler?",
             "options": {"a": "Enerji yoktan var edilebilir", "b": "Kapalı sistemlerdeki entropi zamanla her zaman artar", "c": "Sıcaklık her zaman yükselir", "d": "Düzen her zaman artar"},
             "answer": "b"},
            {"id": "k4_p1_q2", "text": "Entropi kavramını ilk formüle eden bilim insanı kimdir?",
             "options": {"a": "Isaac Newton", "b": "Albert Einstein", "c": "Rudolf Clausius", "d": "Ludwig Boltzmann"},
             "answer": "c"},
            {"id": "k4_p1_q3", "text": "Boltzmann'ın S = k log W denklemi neyi ifade eder?",
             "options": {"a": "Enerji korunumunu", "b": "Entropi ile olasılık arasındaki bağlantıyı", "c": "Işık hızını", "d": "Kütle çekim kuvvetini"},
             "answer": "b"},
            {"id": "k4_p1_q4", "text": "\"Zamanın oku\" kavramını ortaya atan fizikçi kimdir?",
             "options": {"a": "Boltzmann", "b": "Schrödinger", "c": "Clausius", "d": "Arthur Eddington"},
             "answer": "d"},
            {"id": "k4_p1_q5", "text": "Canlı sistemler entropiyle nasıl bir ilişki içindedir?",
             "options": {"a": "Entropiyi tamamen yok ederler", "b": "Kendi düzenlerini artırırken çevrelerine daha fazla düzensizlik yayarlar", "c": "Entropi yasasını ihlal ederler", "d": "Entropiden etkilenmezler"},
             "answer": "b"},
            {"id": "k4_p1_q6", "text": "Schrödinger'e göre yaşam neyle beslenir?",
             "options": {"a": "Pozitif enerji", "b": "Negatif entropi", "c": "Sıcaklık farkı", "d": "Kimyasal bağ"},
             "answer": "b"},
            {"id": "k4_p1_q7", "text": "Fiziğin diğer yasaları (Newton, kuantum vb.) zamanla ilgili nasıl bir özellik taşır?",
             "options": {"a": "Zamanı ileriye doğru zorunlu kılar", "b": "Zamanın yönüne karşı simetriktir", "c": "Zamanı durdurabilir", "d": "Sadece gelecek için geçerlidir"},
             "answer": "b"},
            {"id": "k4_p1_q8", "text": "Evrenin 'ısı ölümü' senaryosunda ne olur?",
             "options": {"a": "Evren çok sıcak olur", "b": "Yeni yıldızlar doğar", "c": "Tüm enerji eşit dağılmış, hiçbir iş yapılamaz bir denge oluşur", "d": "Evren tekrar büyük patlamaya döner"},
             "answer": "c"},
            {"id": "k4_p1_q9", "text": "Clausius entropiyi hangi bağlamda keşfetmiştir?",
             "options": {"a": "Canlı hücreleri incelerken", "b": "Yıldızları gözlemlerken", "c": "Buhar makinelerinin verimliliğini incelerken", "d": "Atom çekirdeğini araştırırken"},
             "answer": "c"},
            {"id": "k4_p1_q10", "text": "Metne göre kırılan bir yumurtanın kendiliğinden birleşmemesinin nedeni nedir?",
             "options": {"a": "Yer çekimi kuvveti", "b": "Kimyasal bağların kopması", "c": "Entropinin sürekli artması", "d": "Yumurtanın iç yapısı"},
             "answer": "c"},
        ],
    },
]


# ============================================================
# TÜM KADEMELER BİRLEŞİK SÖZLÜK
# ============================================================
ALL_PASSAGES = {
    "kademe_1": K1_PASSAGES,
    "kademe_2": K2_PASSAGES,
    "kademe_3": K3_PASSAGES,
    "kademe_4": K4_PASSAGES,
}


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def count_words(text):
    """Türkçe metin kelime sayısı hesaplar."""
    return len(text.split())


def get_passage_for_grade(grade):
    """Sınıfa uygun metni döndürür."""
    kademe = grade_to_kademe(grade)
    passages = ALL_PASSAGES.get(kademe, K2_PASSAGES)
    # Şimdilik her kademede 1 metin var, ileride random seçilebilir
    return passages[0], kademe


def get_wpm_norms(kademe):
    """Kademe bazlı WPM norm değerlerini döndürür."""
    return WPM_NORMS.get(kademe, WPM_NORMS["kademe_2"])


def classify_wpm(wpm, kademe):
    """
    Okuma hızını sınıflandırır.
    Returns: (seviye_key, seviye_label, seviye_emoji, yorum)
    """
    norms = get_wpm_norms(kademe)

    if wpm < norms["cok_yavas"]:
        return "cok_yavas", "Çok Yavaş", "🔴", "Okuma hızı yaş grubunun oldukça altında. Düzenli okuma alıştırması önerilir."
    elif wpm < norms["yavas"]:
        return "yavas", "Yavaş", "🟠", "Okuma hızı ortalamanın altında. Günlük okuma süresi artırılmalı."
    elif wpm < norms["hizli"]:
        return "ortalama", "Ortalama", "🟡", "Okuma hızı yaş grubuna uygun düzeyde."
    elif wpm < norms["cok_hizli"]:
        return "hizli", "Hızlı", "🔵", "Okuma hızı ortalamanın üzerinde. Güçlü bir okuyucu."
    else:
        return "cok_hizli", "Çok Hızlı", "🟢", "Okuma hızı mükemmel düzeyde!"


# ============================================================
# PUANLAMA
# ============================================================

def calculate_speed_reading(answers, passage_data, reading_time_seconds, kademe):
    """
    Hızlı okuma testini puanlar.
    
    Args:
        answers: dict — {soru_id: seçilen_şık}
        passage_data: dict — metin ve soruları içeren dict
        reading_time_seconds: float — okuma süresi (saniye)
        kademe: str — "kademe_1" vb.
    
    Returns:
        dict — tüm skorlar ve analiz
    """
    # --- Kelime Sayısı & WPM ---
    word_count = count_words(passage_data["text"])
    reading_time_minutes = reading_time_seconds / 60.0
    wpm = round(word_count / max(reading_time_minutes, 0.01))
    
    speed_key, speed_label, speed_emoji, speed_comment = classify_wpm(wpm, kademe)
    norms = get_wpm_norms(kademe)
    
    # --- Anlama Puanı ---
    questions = passage_data["questions"]
    correct = 0
    total = len(questions)
    detail = []
    
    for q in questions:
        user_ans = answers.get(q["id"], "")
        is_correct = (user_ans == q["answer"])
        if is_correct:
            correct += 1
        detail.append({
            "id": q["id"],
            "text": q["text"],
            "user": user_ans,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
        })
    
    comprehension_pct = round(correct / max(total, 1) * 100, 1)
    
    if comprehension_pct >= 80:
        comp_level, comp_emoji = "Çok İyi", "🟢"
    elif comprehension_pct >= 60:
        comp_level, comp_emoji = "İyi", "🔵"
    elif comprehension_pct >= 40:
        comp_level, comp_emoji = "Orta", "🟡"
    elif comprehension_pct >= 20:
        comp_level, comp_emoji = "Düşük", "🟠"
    else:
        comp_level, comp_emoji = "Çok Düşük", "🔴"
    
    # --- Etkili Okuma Skoru (Hız × Anlama) ---
    # WPM'i 0-100 arasına normalize et
    max_expected = norms["cok_hizli"] * 1.3
    speed_normalized = min(wpm / max_expected * 100, 100)
    
    effective_score = round(speed_normalized * 0.4 + comprehension_pct * 0.6, 1)
    
    if effective_score >= 80:
        eff_level, eff_emoji = "Mükemmel", "🟢"
    elif effective_score >= 65:
        eff_level, eff_emoji = "İyi", "🔵"
    elif effective_score >= 50:
        eff_level, eff_emoji = "Orta", "🟡"
    elif effective_score >= 35:
        eff_level, eff_emoji = "Gelişime Açık", "🟠"
    else:
        eff_level, eff_emoji = "Destek Gerekli", "🔴"
    
    # --- Okuyucu Profili ---
    if wpm >= norms["hizli"] and comprehension_pct >= 70:
        profile = "⚡ Hızlı & Anlayan Okuyucu"
        profile_desc = "Hem hızlı okuyor hem de okuduğunu iyi anlıyorsun. Harika!"
    elif wpm >= norms["hizli"] and comprehension_pct < 50:
        profile = "💨 Hızlı Ama Yüzeysel Okuyucu"
        profile_desc = "Hızlı okuyorsun ama anlama oranın düşük. Yavaşlayıp odaklanman gerekebilir."
    elif wpm < norms["yavas"] and comprehension_pct >= 70:
        profile = "🔍 Yavaş Ama Derinlemesine Okuyucu"
        profile_desc = "Yavaş okuyorsun ama okuduğunu çok iyi anlıyorsun. Hız artırma çalışmaları faydalı olabilir."
    elif wpm < norms["yavas"] and comprehension_pct < 50:
        profile = "📖 Destek İhtiyacı Olan Okuyucu"
        profile_desc = "Hem hız hem anlama konusunda desteğe ihtiyacın var. Düzenli okuma alışkanlığı edinmek öncelikli."
    else:
        profile = "📚 Dengeli Okuyucu"
        profile_desc = "Okuma hızın ve anlamanı dengeli bir şekilde geliştirmeye devam edebilirsin."
    
    return {
        "passage_title": passage_data["title"],
        "word_count": word_count,
        "reading_time_seconds": round(reading_time_seconds, 1),
        "reading_time_minutes": round(reading_time_minutes, 2),
        "wpm": wpm,
        "speed_key": speed_key,
        "speed_label": speed_label,
        "speed_emoji": speed_emoji,
        "speed_comment": speed_comment,
        "norms": norms,
        "kademe": kademe,
        "kademe_label": KADEME_LABELS.get(kademe, ""),
        "correct": correct,
        "total": total,
        "comprehension_pct": comprehension_pct,
        "comp_level": comp_level,
        "comp_emoji": comp_emoji,
        "detail": detail,
        "effective_score": effective_score,
        "eff_level": eff_level,
        "eff_emoji": eff_emoji,
        "profile": profile,
        "profile_desc": profile_desc,
    }


# ============================================================
# RAPOR ÜRETİCİ
# ============================================================

def generate_speed_reading_report(scores):
    """Hızlı okuma + anlama raporunu markdown olarak üretir."""
    
    norms = scores["norms"]
    
    def bar(pct):
        filled = int(pct / 5)
        return "█" * filled + "░" * (20 - filled)
    
    report = f"""# 📖 Hızlı Okuma & Anlama Raporu

---

## 📋 Test Bilgileri

| Bilgi | Değer |
|-------|-------|
| Metin | {scores['passage_title']} |
| Kademe | {scores['kademe_label']} |
| Kelime Sayısı | {scores['word_count']} kelime |
| Okuma Süresi | {scores['reading_time_seconds']} saniye ({scores['reading_time_minutes']} dk) |

---

## ⏱️ Okuma Hızı

### {scores['speed_emoji']} {scores['wpm']} Kelime/Dakika — {scores['speed_label']}

{scores['speed_comment']}

**Yaş Grubu Normları ({scores['kademe_label']}):**

| Seviye | Kelime/Dk |
|--------|-----------|
| 🔴 Çok Yavaş | < {norms['cok_yavas']} |
| 🟠 Yavaş | {norms['cok_yavas']} - {norms['yavas']} |
| 🟡 Ortalama | {norms['yavas']} - {norms['hizli']} |
| 🔵 Hızlı | {norms['hizli']} - {norms['cok_hizli']} |
| 🟢 Çok Hızlı | > {norms['cok_hizli']} |

**Senin hızın:** {scores['wpm']} kel/dk → **{scores['speed_label']}**

---

## 🧠 Okuduğunu Anlama

### {scores['comp_emoji']} %{scores['comprehension_pct']} — {scores['comp_level']}

{scores['correct']}/{scores['total']} soruyu doğru cevapladın.

{bar(scores['comprehension_pct'])} %{scores['comprehension_pct']}

### Soru Detayları

| # | Sonuç | Soru |
|---|-------|------|
"""
    
    for i, d in enumerate(scores["detail"], 1):
        icon = "✅" if d["is_correct"] else "❌"
        report += f"| {i} | {icon} | {d['text'][:60]}... |\n"
    
    report += f"""
---

## 🎯 Etkili Okuma Skoru

### {scores['eff_emoji']} %{scores['effective_score']} — {scores['eff_level']}

> Etkili okuma = Hız (%40) + Anlama (%60)

{bar(scores['effective_score'])} %{scores['effective_score']}

---

## 🧑‍🎓 Okuyucu Profilin

### {scores['profile']}

{scores['profile_desc']}

---

## 💡 Öneriler

"""
    
    # Hıza göre öneriler
    if scores["speed_key"] in ("cok_yavas", "yavas"):
        report += """### Okuma Hızını Artırmak İçin
- Günde en az 20 dakika sessiz okuma yap
- Parmağınla veya kalemle satırı takip ederek oku (göz rehberi)
- Kelime kelime değil, kelime grupları halinde okumaya çalış
- Dudaklarını kıpırdatmadan (içinden seslendirmeden) okumaya alış
- Kolay ve eğlenceli kitaplarla başla, zorluğu yavaş yavaş artır

"""
    elif scores["speed_key"] == "ortalama":
        report += """### Okuma Hızını Geliştirmek İçin
- Hız artırma egzersizleri yap (zamanlı okuma)
- Göz genişliği çalışmaları yap — bir bakışta daha fazla kelime gör
- Farklı türde metinler oku (hikâye, bilim, haber)
- Geri dönüp tekrar okuma alışkanlığını azalt

"""
    else:
        report += """### Okuma Hızı Mükemmel!
- Bu hızı korumak için düzenli okumaya devam et
- Farklı zorlukta ve türde metinlerle kendini sına
- Anlama oranını da yüksek tutmaya dikkat et

"""
    
    # Anlamaya göre öneriler
    if scores["comprehension_pct"] < 50:
        report += """### Okuduğunu Anlamayı Geliştirmek İçin
- Okurken anahtar kelimelerin altını çiz
- Her paragraftan sonra "Ne anladım?" diye kendine sor
- Okuduğunu kendi cümlelerinle özetle
- Bilinmeyen kelimelerin anlamını araştır
- Metni ikinci kez okuyarak detayları yakala

"""
    elif scores["comprehension_pct"] < 70:
        report += """### Okuduğunu Anlamayı Güçlendirmek İçin
- Okumadan önce başlığa bakarak tahmin yap
- Okurken zihinsel sorular sor (neden, nasıl, ne olacak?)
- Okuduklarını başkasına anlatma pratiği yap
- Not alma tekniklerini kullan

"""
    else:
        report += """### Anlama Gücü Güçlü!
- Bu becerini eleştirel okuma ile derinleştir
- Yazarın bakış açısını sorgula
- Farklı kaynakları karşılaştırarak oku

"""
    
    report += f"""---

## 📌 Özet Tablo

| Gösterge | Sonuç |
|----------|-------|
| Kademe | {scores['kademe_label']} |
| Okuma Hızı | **{scores['wpm']} kel/dk** ({scores['speed_label']}) |
| Anlama Oranı | **%{scores['comprehension_pct']}** ({scores['comp_level']}) |
| Etkili Okuma | **%{scores['effective_score']}** ({scores['eff_level']}) |
| Profil | {scores['profile']} |
"""
    return report.strip()

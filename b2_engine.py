"""
B2 Dikkat Testi — Dijital Motor
================================
b2dikkat.com formatında, "p" harfi hedefli dikkat testi.

Semboller : "d" ve "p" harfleri, üst/altlarında 0-2 arası nokta (•)
Hedef     : Toplam 2 noktası olan "p" harfleri
           → üstte 2, altta 0  (p̈)
           → üstte 0, altta 2  (p)
           → üstte 1, altta 1  (ṗ)
Yapı      : 15 satır × 30 sembol = 450 stimulus
Süre      : Yaşa göre değişken (satır bazlı otomatik geçiş)

Skorlama (d2 formüllerine uygun):
  TN   – Toplam İşaretleme (her satırda tıklanan sembol sayısı toplamı)
  E1   – Atlama Hatası  (hedef olan p atlandı)
  E2   – Yanlış İşaretleme (hedef olmayan sembol işaretlendi)
  E    – Toplam Hata (E1 + E2)
  TN-E – Toplam Performans
  CP   – Konsantrasyon Performansı (doğru hedef − E2)
  FR   – Dalgalanma Oranı (max satır CP − min satır CP)

Ek: Satır bazlı hata/kaçırma analizi raporu
"""

import random

# ============================================================
# KONFİGÜRASYON
# ============================================================
B2_CONFIG = {
    "rows": 15,
    "symbols_per_row": 30,
    "time_per_row": 20,           # varsayılan saniye
    "target_ratio": 0.38,         # her satırda ~%38 hedef (~11-12 hedef)
    "practice_symbols": 30,       # alıştırma satırı (b2dikkat gibi tam satır)
}

# ============================================================
# YAŞA GÖRE SÜRE TABLOSU
# ============================================================
AGE_TIME_TABLE = [
    (9,  25),   # 7-9 yaş   → 25 saniye
    (12, 20),   # 10-12 yaş → 20 saniye
    (15, 15),   # 13-15 yaş → 15 saniye
    (999, 12),  # 16+ yaş   → 12 saniye
]

AGE_TIME_LABELS = [
    {"label": "7 – 9 yaş",  "min": 7,  "max": 9,   "seconds": 25},
    {"label": "10 – 12 yaş", "min": 10, "max": 12,  "seconds": 20},
    {"label": "13 – 15 yaş", "min": 13, "max": 15,  "seconds": 15},
    {"label": "16+ yaş",     "min": 16, "max": 999, "seconds": 12},
]


def get_time_per_row(age=None):
    """Öğrenci yaşına göre satır başına süreyi (saniye) döndürür."""
    if age is None:
        return B2_CONFIG["time_per_row"]
    for max_age, seconds in AGE_TIME_TABLE:
        if age <= max_age:
            return seconds
    return B2_CONFIG["time_per_row"]


def get_age_group_index(age):
    """Yaş grubu index'ini döndürür (tabloda vurgulama için)."""
    if age is None:
        return -1
    for i, grp in enumerate(AGE_TIME_LABELS):
        if grp["min"] <= age <= grp["max"]:
            return i
    return len(AGE_TIME_LABELS) - 1


# ============================================================
# SEMBOL TİPLERİ — Nokta bazlı (• simgesi)
# ============================================================
# (harf, üst_nokta, alt_nokta) → toplam 1-4 arası nokta
ALL_SYMBOL_TYPES = []
for letter in ("d", "p"):
    for above in range(3):       # 0, 1, 2
        for below in range(3):
            total = above + below
            if 1 <= total <= 4:
                ALL_SYMBOL_TYPES.append({
                    "letter": letter,
                    "above": above,
                    "below": below,
                    "total": total,
                    "is_target": (letter == "p" and total == 2),
                })

TARGET_TYPES     = [s for s in ALL_SYMBOL_TYPES if s["is_target"]]
DISTRACTOR_TYPES = [s for s in ALL_SYMBOL_TYPES if not s["is_target"]]


# ============================================================
# SATIR / TEST ÜRETİCİ
# ============================================================
def generate_b2_row(n=30, target_ratio=0.38, rng=None):
    """Bir satır B2 sembolü üretir."""
    if rng is None:
        rng = random.Random()

    num_targets = round(n * target_ratio)
    num_dist    = n - num_targets

    row = []
    for _ in range(num_targets):
        row.append({**rng.choice(TARGET_TYPES)})
    for _ in range(num_dist):
        row.append({**rng.choice(DISTRACTOR_TYPES)})

    rng.shuffle(row)
    for i, sym in enumerate(row):
        sym["index"] = i
    return row


def generate_b2_test(seed=None):
    """15 satırlık tam B2 testi üretir."""
    rng = random.Random(seed)
    return [
        generate_b2_row(B2_CONFIG["symbols_per_row"],
                        B2_CONFIG["target_ratio"], rng)
        for _ in range(B2_CONFIG["rows"])
    ]


def generate_practice_row(seed=42):
    """Alıştırma satırı (30 sembol, b2dikkat gibi tam satır)."""
    rng = random.Random(seed)
    return generate_b2_row(B2_CONFIG["practice_symbols"], 0.40, rng)


# ============================================================
# HTML RENDER — Nokta stili (b2dikkat formatı)
# ============================================================
def _dots_html(count, position="above"):
    """Noktaları render eder (üst veya alt)."""
    if count == 0:
        return f'<div style="height:10px;">&nbsp;</div>'
    dots = "".join(
        '<span style="display:inline-block;width:5px;height:5px;'
        'background:#333;border-radius:50%;margin:0 1px;"></span>'
        for _ in range(count)
    )
    return (
        f'<div style="height:10px;display:flex;'
        f'justify-content:center;align-items:center;">{dots}</div>'
    )


def render_symbol_inline(symbol, selected=False, show_result=False,
                         is_missed=False, is_wrong=False):
    """
    B2 sembolünü tek satır inline formatında render eder.
    b2dikkat tarzı: sadece harf + noktalar, minimalist.

    show_result=True ise test sonrası renklendirme:
      - is_missed (E1): kırmızı çerçeve (kaçırılan hedef)
      - is_wrong  (E2): turuncu çerçeve (yanlış işaretleme)
      - doğru seçim: yeşil çerçeve
    """
    above = symbol["above"]
    below = symbol["below"]
    letter = symbol["letter"]

    # Renk & çerçeve belirleme
    border = "2px solid transparent"
    bg = "transparent"
    letter_color = "#333"

    if selected and not show_result:
        # Test sırasında seçim: kırmızı (b2dikkat tarzı)
        border = "2px solid #E74C3C"
        bg = "rgba(231,76,60,0.08)"
        letter_color = "#E74C3C"
    elif show_result:
        if is_missed:
            # Kaçırılan hedef: kırmızı arka plan
            border = "2px solid #E74C3C"
            bg = "rgba(231,76,60,0.12)"
            letter_color = "#E74C3C"
        elif is_wrong:
            # Yanlış işaretleme: turuncu
            border = "2px solid #F39C12"
            bg = "rgba(243,156,18,0.12)"
            letter_color = "#F39C12"
        elif selected and symbol["is_target"]:
            # Doğru seçim: yeşil
            border = "2px solid #27AE60"
            bg = "rgba(39,174,96,0.10)"
            letter_color = "#27AE60"

    dots_above = _dots_html(above, "above")
    dots_below = _dots_html(below, "below")

    return f"""<div style="display:inline-flex;flex-direction:column;align-items:center;
        min-width:28px;padding:3px 2px;margin:0 1px;cursor:pointer;
        border:{border};border-radius:6px;background:{bg};
        transition:all 0.1s ease;user-select:none;">
    {dots_above}
    <div style="font-size:22px;font-weight:700;color:{letter_color};
        line-height:24px;font-family:'Segoe UI',Arial,sans-serif;">{letter}</div>
    {dots_below}
</div>"""


# ============================================================
# HEDEF SEMBOL GÖSTERİMİ (Yönerge & Alıştırma)
# ============================================================
def render_target_examples():
    """Hedef 3 sembolü büyük boyutta gösterir (b2dikkat tarzı)."""
    targets = [
        {"letter": "p", "above": 2, "below": 0, "index": 0, "is_target": True, "total": 2},
        {"letter": "p", "above": 0, "below": 2, "index": 1, "is_target": True, "total": 2},
        {"letter": "p", "above": 1, "below": 1, "index": 2, "is_target": True, "total": 2},
    ]
    html_parts = []
    for t in targets:
        above_dots = _dots_html(t["above"])
        below_dots = _dots_html(t["below"])
        html_parts.append(f"""<div style="display:inline-flex;flex-direction:column;
            align-items:center;min-width:44px;padding:6px 8px;margin:0 8px;
            border:2px solid #3498DB;border-radius:8px;background:#EBF5FB;">
            {above_dots}
            <div style="font-size:28px;font-weight:800;color:#1B2A4A;line-height:30px;">p</div>
            {below_dots}
        </div>""")
    return "".join(html_parts)


# ============================================================
# YÖNERGE SAYFASI HTML (b2dikkat formatı)
# ============================================================
def render_instructions_html(time_per_row, age=None):
    """b2dikkat tarzı yönerge sayfası."""

    age_idx = get_age_group_index(age)
    time_table_rows = ""
    for i, grp in enumerate(AGE_TIME_LABELS):
        if i == age_idx:
            time_table_rows += (
                f'<tr style="background:#d5f5e3;font-weight:700;">'
                f'<td>➤ {grp["label"]}</td><td>{grp["seconds"]} saniye</td></tr>'
            )
        else:
            time_table_rows += (
                f'<tr><td>{grp["label"]}</td><td>{grp["seconds"]} saniye</td></tr>'
            )

    age_info = ""
    if age is not None:
        age_info = f"""
        <div style="background:#FEF9E7;border:1px solid #F9E79F;border-radius:8px;
                    padding:10px 14px;margin-bottom:16px;">
            <div style="font-weight:700;color:#7D6608;">
                ⏱️ Senin Süren: Her satır için <b>{time_per_row} saniye</b> (Yaşın: {age})
            </div>
            <table style="width:100%;margin-top:8px;border-collapse:collapse;font-size:0.9rem;">
                <tr style="background:#F8F9FA;font-weight:600;">
                    <td style="padding:4px 8px;border:1px solid #ddd;">Yaş Grubu</td>
                    <td style="padding:4px 8px;border:1px solid #ddd;">Satır Süresi</td>
                </tr>
                {time_table_rows}
            </table>
        </div>"""

    return f"""
    <div style="background:#EBF5FB;border:1px solid #AED6F1;border-radius:8px;
                padding:10px 14px;margin-bottom:16px;text-align:center;
                font-weight:600;color:#1B4F72;">
        Uygulama Yapacağınız Bilgisayarın Mouse'unu Rahat Bir Şekilde
        Kullanabilmeniz Gerekmektedir.
    </div>

    {age_info}

    <h3 style="font-family:'Georgia',serif;color:#1B2A4A;">Uygulama;</h3>
    <ol style="line-height:1.9;color:#333;font-size:0.95rem;">
        <li>Üzerinde işaretleme yapacağın <b>15 satır</b> vardır.</li>
        <li>Testte sadece <b>"d"</b> ve <b>"p"</b> harfleri vardır.</li>
        <li>Her bir satır için belli bir süre verilmiştir.</li>
        <li>Bu süre tamamlanınca ekrana işaretleme yapacağın diğer satır
            <b>otomatik olarak</b> gelecektir.</li>
        <li>Her satıra <b>sol baştan</b> başlamalısın. Sağ baştan veya ortadan
            işaretlemeye başlarsan sağlıklı ve güvenilir sonuçlara ulaşılamaz.</li>
        <li>İşaretlemen gereken karakterler yalnızca, <b>üstünde iki nokta olan (p)</b>,
            <b>altında iki nokta olan (p)</b> ve <b>altta ve üstte bir nokta olan (p)</b>'lerdir.</li>
        <li>Satır başından sonuna kadar, <b>SİZDEN İSTENEN KARAKTERLERİ</b>
            işaretleyerek devam ediniz.</li>
        <li>İstenmeyen bir karakteri işaretlediğinizi fark ederseniz,
            o karakterin üzerine tekrar tıklayarak işaretlemenizi
            <b>iptal edebilirsiniz</b>.</li>
    </ol>

    <div style="background:#FDEDEC;border:1px solid #F5B7B1;border-radius:8px;
                padding:10px 14px;margin-top:12px;text-align:center;
                font-size:0.92rem;color:#922B21;">
        Satırlarda yapacağın işaretlemelerde önemli olan, satırın sonuna kadar
        gelmek değil; <b>acele etmeden</b> kendi hızınızda sizden istenen
        karakterleri işaretleyerek ilerlemenizdir.
    </div>
    """


# ============================================================
# ALIŞTIRMA SAYFASI HTML (b2dikkat formatı)
# ============================================================
def render_practice_instructions_html():
    """Alıştırma yönerge HTML'i."""
    target_html = render_target_examples()

    return f"""
    <div style="background:#EBF5FB;border:1px solid #AED6F1;border-radius:8px;
                padding:10px 14px;margin-bottom:16px;text-align:center;
                font-weight:600;color:#1B4F72;">
        Önemli olan senden istenen karakterleri işaretleyerek devam etmendir.
    </div>

    <h3 style="font-family:'Georgia',serif;color:#1B2A4A;">Örnek Uygulama;</h3>
    <ol style="line-height:1.9;color:#333;font-size:0.95rem;">
        <li><b>"Alıştırmayı"</b> yapmadan asıl teste geçmeyiniz.</li>
        <li>"Alıştırma"da sizden istenen karakterlerin (üstünde iki nokta olan <b>(p)</b>'lerin,
            altında iki nokta olan <b>(p)</b>'lerin, altında ve üstünde birer nokta
            olan <b>(p)</b>'lerin) üzerine tıklayarak işaretle meyapınız.</li>
        <li>İstenen karakterler: {target_html}</li>
        <li>Satır başından sonuna kadar, sizden istenen karakterleri işaretleyerek devam edin.</li>
    </ol>
    """


# ============================================================
# TEST EKRANI CSS — b2dikkat minimalist stili
# ============================================================
B2_CSS = """
<style>
/* ── B2 Test — minimalist beyaz ekran ── */
.b2-test-container {
    max-width: 100%;
    margin: 0 auto;
    padding: 40px 20px;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.b2-row-symbols {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 2px;
    justify-content: center;
}

/* ── Satır numarası ── */
.b2-row-num {
    font-size: 16px;
    font-weight: 700;
    color: #999;
    margin-right: 12px;
    min-width: 24px;
    text-align: right;
}

/* ── Checkbox kartları ── */
div[data-testid="stForm"] div[data-testid="stCheckbox"] {
    background: transparent;
    border: 2px solid transparent;
    border-radius: 6px;
    padding: 2px;
    text-align: center;
    transition: all 0.1s ease;
    cursor: pointer;
    min-width: 32px;
}
div[data-testid="stForm"] div[data-testid="stCheckbox"]:hover {
    border-color: #ccc;
    background: #fafafa;
}

/* ── Seçili: kırmızı (b2dikkat tarzı) ── */
div[data-testid="stForm"] div[data-testid="stCheckbox"]:has(input:checked) {
    border-color: #E74C3C !important;
    background: rgba(231,76,60,0.06) !important;
}
div[data-testid="stForm"] div[data-testid="stCheckbox"]:has(input:checked) div[style*="font-size"] {
    color: #E74C3C !important;
}

/* ── Checkbox native gizle ── */
div[data-testid="stForm"] div[data-testid="stCheckbox"] > label > div:first-child {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
    overflow: hidden;
}

/* ── Progress bar gizle — temiz ekran ── */
.b2-clean .stProgress { display: none; }
</style>
"""


def render_symbol_label(symbol):
    """
    Bir B2 sembolünü checkbox label'ı olarak render eder.
    Minimalist: sadece nokta + harf + nokta
    """
    above = symbol["above"]
    below = symbol["below"]
    letter = symbol["letter"]

    def dots(count):
        if count == 0:
            return '<div style="height:10px;">&nbsp;</div>'
        d = "".join(
            '<span style="display:inline-block;width:5px;height:5px;'
            'background:#333;border-radius:50%;margin:0 1px;"></span>'
            for _ in range(count)
        )
        return (
            f'<div style="height:10px;display:flex;'
            f'justify-content:center;align-items:center;">{d}</div>'
        )

    return (
        f'<div style="text-align:center;min-width:28px;padding:1px 0;">'
        f'{dots(above)}'
        f'<div style="font-size:22px;font-weight:700;color:#333;'
        f'line-height:24px;font-family:\'Segoe UI\',Arial,sans-serif;">{letter}</div>'
        f'{dots(below)}'
        f'</div>'
    )


# ============================================================
# SKORLAMA
# ============================================================
def calculate_b2(row_results, time_per_row=None):
    """
    B2 test skorlarını hesaplar.

    Parametre
    ---------
    row_results : list[dict]
        Her eleman: {symbols, selected (list[bool]), elapsed_time}
    time_per_row : int | None

    Döndürür
    --------
    dict : TN, E1, E2, E, TN_E, CP, FR, satır detayları, yorumlar
    """
    total_tn = total_e1 = total_e2 = total_correct = total_targets = 0
    row_cps    = []
    row_tns    = []
    row_times  = []
    row_details = []   # ← YENİ: satır bazlı hata/kaçırma detayları

    for row_idx, row in enumerate(row_results):
        symbols  = row["symbols"]
        selected = row["selected"]
        elapsed  = row.get("elapsed_time", B2_CONFIG["time_per_row"])

        tn = sum(1 for s in selected if s)
        e1 = e2 = correct = targets = 0
        missed_indices = []    # kaçırılan hedef indeksleri
        wrong_indices  = []    # yanlış işaretleme indeksleri
        correct_indices = []   # doğru seçim indeksleri
        blank_count = 0        # hiç dokunulmamış (sol taraftan kesilen)

        # Son işaretlenen sembolün indeksini bul
        last_selected = -1
        for i in range(len(selected) - 1, -1, -1):
            if selected[i]:
                last_selected = i
                break

        for i, (sym, sel) in enumerate(zip(symbols, selected)):
            if sym["is_target"]:
                targets += 1
                if sel:
                    correct += 1
                    correct_indices.append(i)
                else:
                    e1 += 1
                    # Sadece "ulaşılan alan"daki kaçırmaları say
                    if last_selected == -1 or i <= last_selected:
                        missed_indices.append(i)
            else:
                if sel:
                    e2 += 1
                    wrong_indices.append(i)

        # Ulaşılamayan (boş bırakılan) alan
        if last_selected >= 0:
            blank_count = len(symbols) - last_selected - 1
        else:
            blank_count = len(symbols)

        cp = correct - e2
        row_cps.append(cp)
        row_tns.append(tn)
        row_times.append(elapsed)

        total_tn += tn
        total_e1 += e1
        total_e2 += e2
        total_correct += correct
        total_targets += targets

        row_details.append({
            "row_num": row_idx + 1,
            "total_symbols": len(symbols),
            "targets_in_row": targets,
            "correct": correct,
            "missed": e1,
            "wrong": e2,
            "blank": blank_count,
            "cp": cp,
            "tn": tn,
            "elapsed": round(elapsed, 1),
            "missed_indices": missed_indices,
            "wrong_indices": wrong_indices,
            "correct_indices": correct_indices,
            "symbols": symbols,
            "selected": selected,
        })

    total_e  = total_e1 + total_e2
    tn_e     = total_tn - total_e

    max_possible_cp = total_targets
    cp_pct = round(total_correct / max(1, max_possible_cp) * 100, 1)

    hit_rate   = round(total_correct / max(1, total_targets) * 100, 1)
    error_pct  = round(total_e / max(1, total_tn) * 100, 1)

    total_cp = total_correct - total_e2

    fr = (max(row_cps) - min(row_cps)) if row_cps else 0

    # ── Dikkat Seviyesi
    if cp_pct >= 90:
        level, level_desc = "Çok Yüksek", "Dikkat ve konsantrasyon kapasitesi çok güçlü."
    elif cp_pct >= 75:
        level, level_desc = "Yüksek", "Ortalamanın üzerinde dikkat performansı."
    elif cp_pct >= 55:
        level, level_desc = "Orta", "Ortalama düzeyde dikkat. Gelişim potansiyeli var."
    elif cp_pct >= 35:
        level, level_desc = "Düşük", "Dikkat alanında destek ihtiyacı var."
    else:
        level, level_desc = "Çok Düşük", "Dikkat ve konsantrasyon alanında ciddi gelişim ihtiyacı tespit edildi."

    # ── Hız-Doğruluk Dengesi
    if hit_rate >= 80 and error_pct <= 10:
        balance, balance_desc = "Dengeli", "Hem hızlı hem doğru çalışıyor."
    elif hit_rate < 60 and error_pct <= 10:
        balance, balance_desc = "Temkinli (Yavaş ama Doğru)", "Doğruluk yüksek ama hız düşük."
    elif error_pct > 20:
        balance, balance_desc = "Dürtüsel (Hızlı ama Hatalı)", "Hızlı ama hata oranı yüksek."
    else:
        balance, balance_desc = "Gelişen", "Hız ve doğruluk arasında denge kuruluyor."

    # ── Tutarlılık
    if fr <= 3:
        cons, cons_desc = "Çok Tutarlı", "Satırlar arası performans oldukça dengeli."
    elif fr <= 6:
        cons, cons_desc = "Tutarlı", "Performans satırlar arasında makul düzeyde sabit."
    elif fr <= 10:
        cons, cons_desc = "Dalgalı", "Performansta belirgin iniş çıkışlar var."
    else:
        cons, cons_desc = "Tutarsız", "Satırlar arası performans çok değişken."

    return {
        "TN": total_tn, "E1": total_e1, "E2": total_e2, "E": total_e,
        "TN_E": tn_e, "CP": total_cp, "FR": fr,
        "cp_pct": cp_pct, "hit_rate": hit_rate, "error_pct": error_pct,
        "level": level, "level_desc": level_desc,
        "balance": balance, "balance_desc": balance_desc,
        "consistency": cons, "consistency_desc": cons_desc,
        "row_performances": row_cps, "row_speeds": row_tns,
        "row_times": row_times,
        "row_details": row_details,
        "total_targets": total_targets, "total_correct": total_correct,
        "time_per_row": time_per_row,
    }


# ============================================================
# SATIR BAZLI HATA ANALİZİ HTML RAPORU
# ============================================================
def render_row_analysis_html(row_detail):
    """
    Tek bir satırın hata analizini HTML olarak render eder.
    Semboller renklendirilmiş şekilde gösterilir:
      - Yeşil: doğru seçim
      - Kırmızı: kaçırılan hedef (E1)
      - Turuncu: yanlış işaretleme (E2)
      - Gri: normal (dokunulmamış, doğru bırakılmış)
    """
    symbols = row_detail["symbols"]
    selected = row_detail["selected"]
    missed_set = set(row_detail["missed_indices"])
    wrong_set  = set(row_detail["wrong_indices"])
    correct_set = set(row_detail["correct_indices"])

    sym_html_parts = []
    for i, sym in enumerate(symbols):
        sel = selected[i] if i < len(selected) else False
        is_missed = i in missed_set
        is_wrong  = i in wrong_set
        is_correct = i in correct_set

        sym_html_parts.append(
            render_symbol_inline(
                sym,
                selected=sel,
                show_result=True,
                is_missed=is_missed,
                is_wrong=is_wrong,
            )
        )

    symbols_line = "".join(sym_html_parts)

    # Özet istatistikler
    row_num = row_detail["row_num"]
    stats_html = (
        f'<span style="color:#27AE60;font-weight:600;">✓ Doğru: {row_detail["correct"]}</span>'
        f' &nbsp;|&nbsp; '
        f'<span style="color:#E74C3C;font-weight:600;">✗ Kaçırılan: {row_detail["missed"]}</span>'
        f' &nbsp;|&nbsp; '
        f'<span style="color:#F39C12;font-weight:600;">⚠ Yanlış: {row_detail["wrong"]}</span>'
        f' &nbsp;|&nbsp; '
        f'<span style="color:#95A5A6;">Boş: {row_detail["blank"]}</span>'
    )

    return f"""
    <div style="margin-bottom:16px;padding:10px 12px;background:#fafafa;
                border:1px solid #eee;border-radius:8px;">
        <div style="font-weight:700;color:#1B2A4A;margin-bottom:6px;font-size:0.95rem;">
            Satır {row_num}
            <span style="font-weight:400;font-size:0.82rem;color:#888;margin-left:10px;">
                CP: {row_detail['cp']} &nbsp; | &nbsp; Süre: {row_detail['elapsed']}sn
            </span>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:1px;margin-bottom:6px;">
            {symbols_line}
        </div>
        <div style="font-size:0.82rem;">{stats_html}</div>
    </div>
    """


def render_full_analysis_html(scores):
    """Tüm satırların hata analizini HTML olarak render eder."""
    legend = """
    <div style="display:flex;gap:16px;margin-bottom:16px;padding:10px;
                background:#f0f7ff;border:1px solid #b0d4f1;border-radius:8px;
                font-size:0.85rem;flex-wrap:wrap;">
        <span><span style="display:inline-block;width:12px;height:12px;
            background:rgba(39,174,96,0.15);border:2px solid #27AE60;
            border-radius:3px;margin-right:4px;"></span> Doğru Seçim</span>
        <span><span style="display:inline-block;width:12px;height:12px;
            background:rgba(231,76,60,0.15);border:2px solid #E74C3C;
            border-radius:3px;margin-right:4px;"></span> Kaçırılan Hedef (E1)</span>
        <span><span style="display:inline-block;width:12px;height:12px;
            background:rgba(243,156,18,0.15);border:2px solid #F39C12;
            border-radius:3px;margin-right:4px;"></span> Yanlış İşaretleme (E2)</span>
        <span><span style="display:inline-block;width:12px;height:12px;
            background:#f8f8f8;border:2px solid transparent;
            border-radius:3px;margin-right:4px;"></span> Normal</span>
    </div>
    """

    rows_html = ""
    for detail in scores["row_details"]:
        rows_html += render_row_analysis_html(detail)

    return legend + rows_html


# ============================================================
# RAPOR ÜRETİCİ (metin bazlı — AI analiz ve PDF için)
# ============================================================
def generate_b2_report(scores):
    """Şablon tabanlı metin rapor üretir."""

    def bar(pct):
        n = max(0, min(10, round(pct / 10)))
        return "█" * n + "░" * (10 - n)

    row_table = ""
    for d in scores["row_details"]:
        row_table += (
            f"| Satır {d['row_num']:2d} | {d['cp']:4d} | "
            f"{d['correct']:3d} | {d['missed']:3d} | "
            f"{d['wrong']:3d} | {d['blank']:3d} |\n"
        )

    report = f"""# 🎯 B2 DİKKAT TESTİ RAPORU

---

## 📊 Genel Performans Özeti

| Metrik | Değer | Açıklama |
|--------|-------|----------|
| 🎯 Konsantrasyon (CP) | **{scores['CP']}** | Doğru hedefler − Yanlış işaretlemeler |
| ⚡ Toplam Performans (TN-E) | **{scores['TN_E']}** | Toplam işaretleme − Toplam hata |
| 📊 Toplam İşaretleme (TN) | {scores['TN']} | Tüm satırlarda işaretlenen sembol sayısı |
| ❌ Toplam Hata (E) | {scores['E']} | Atlama ({scores['E1']}) + Yanlış ({scores['E2']}) |
| 📈 Dalgalanma (FR) | {scores['FR']} | En yüksek − en düşük satır performansı |"""

    if scores.get("time_per_row"):
        report += f"""
| ⏱️ Satır Süresi | {scores['time_per_row']} sn | Yaşa göre belirlenen süre |"""

    report += f"""

---

## 🧠 Dikkat Seviyesi: **{scores['level']}**

{bar(scores['cp_pct'])} %{scores['cp_pct']}

{scores['level_desc']}

---

## ⚖️ Hız-Doğruluk Dengesi: **{scores['balance']}**

| Gösterge | Değer |
|----------|-------|
| Hedef Yakalama Oranı | %{scores['hit_rate']} |
| Hata Oranı | %{scores['error_pct']} |

{scores['balance_desc']}

---

## 📈 Tutarlılık: **{scores['consistency']}**

{scores['consistency_desc']}

---

## 📉 Satır Bazlı Performans & Hata Analizi

| Satır | CP | Doğru | Kaçırılan | Yanlış | Boş |
|-------|-----|-------|-----------|--------|-----|
{row_table}

---

## 🔍 Hata Analizi Özet

| Hata Türü | Sayı | Anlam |
|-----------|------|-------|
| Atlama Hatası (E1) | {scores['E1']} | Hedef "p" sembollerinin kaçırılması — dikkat dağılması |
| Yanlış İşaretleme (E2) | {scores['E2']} | Hedef olmayan sembollerin işaretlenmesi — dürtüsellik |

---

## 💡 Yorum ve Öneriler

"""

    # Seviyeye göre öneriler
    if scores["level"] in ("Çok Yüksek", "Yüksek"):
        report += (
            "Dikkat ve konsantrasyon kapasitesi güçlü bir profil sergileniyor.\n\n"
            "**Öneriler:**\n"
            "- 🎯 Karmaşık görevlerle dikkat kapasitesini daha da geliştir\n"
            "- 📚 Uzun süreli odaklanma gerektiren çalışmalarda bu güçlü yanını kullan\n"
            "- 🧘 Düzenli zihinsel egzersizlerle bu seviyeyi koru\n"
        )
    elif scores["level"] == "Orta":
        report += (
            "Dikkat seviyesi ortalama düzeyde. Gelişim potansiyeli var.\n\n"
            "**Öneriler:**\n"
            "- ⏱️ Pomodoro tekniği ile odaklanma sürelerini kademeli artır\n"
            "- 🎮 Dikkat geliştirici oyunlar ve bulmacalar ile pratik yap\n"
            "- 📵 Çalışma ortamından dikkat dağıtıcıları uzaklaştır\n"
            "- 💤 Düzenli uyku ve beslenme dikkat performansını doğrudan etkiler\n"
        )
    else:
        report += (
            "Dikkat ve konsantrasyon alanında gelişim ihtiyacı tespit edildi. "
            "Bu tamamen geliştirilebilir bir beceridir.\n\n"
            "**Öneriler:**\n"
            "- 🏃 Düzenli fiziksel aktivite dikkat kapasitesini artırır\n"
            "- ⏱️ Kısa odaklanma süreleriyle başla (5 dk) ve kademeli artır\n"
            "- 🎯 Tek seferde tek iş yap — çoklu görevden kaçın\n"
            "- 📝 Görevleri küçük parçalara böl\n"
            "- 🧘 Nefes egzersizleri ve mindfulness pratikleri faydalı olabilir\n"
        )

    if scores["balance"] == "Dürtüsel (Hızlı ama Hatalı)":
        report += (
            "\n**⚡ Dürtüsellik Notu:**\n"
            "Hızlı çalışma eğilimi hata oranını artırıyor. "
            "'Önce doğru, sonra hızlı' prensibini benimse.\n"
        )
    elif scores["balance"] == "Temkinli (Yavaş ama Doğru)":
        report += (
            "\n**🐢 Temkinlilik Notu:**\n"
            "Doğruluk oranı yüksek ama hız düşük. "
            "Zamanlı pratiklerle hızı kademeli olarak artır.\n"
        )

    report += f"""
---

## 📌 Özet Tablo

| Gösterge | Sonuç |
|----------|-------|
| Dikkat Seviyesi | **{scores['level']}** |
| Hız-Doğruluk | **{scores['balance']}** |
| Tutarlılık | **{scores['consistency']}** |
| Konsantrasyon Puanı | **{scores['CP']}/{scores['total_targets']}** |
| Genel Hata | **{scores['E']}** (Atlama: {scores['E1']}, Yanlış: {scores['E2']}) |
"""
    return report.strip()

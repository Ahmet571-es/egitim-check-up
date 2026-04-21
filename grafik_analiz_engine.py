"""
=============================================================
🎨 GRAFİK BAZLI ANALİZ MOTORU (Eğitim Check-Up)
=============================================================
Her öğrencinin tüm testlerinden renkli profesyonel grafikler
üretir, Claude ile yalın Türkçe bütünsel analiz yazdırır ve
hepsini tek bir PDF'te birleştirir.

Palet: Lacivert (#1B2A4A) + Altın (#D4A84C) + destekleyici
tonlar. Hedef kitle: hem veli hem öğrenci. Dil: yalın Türkçe,
teknik terim yok, öz-farkındalık ve motivasyon odaklı.
=============================================================
"""

import io
import os
import base64
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    PageBreak, Table, TableStyle, KeepTogether
)


# =============================================================
# 🎨 MARKA PALETİ (Lacivert / Altın profesyonel)
# =============================================================
NAVY = "#1B2A4A"        # Ana lacivert
NAVY_LIGHT = "#2E4374"  # Açık lacivert
GOLD = "#D4A84C"        # Altın
GOLD_LIGHT = "#E8C878"  # Açık altın
CREAM = "#FAF6EC"       # Krem arka plan
CHARCOAL = "#2D3142"    # Koyu kömür metin
SOFT_GREY = "#F0F2F5"   # Yumuşak gri
ACCENT_BURGUNDY = "#8B2635"
ACCENT_TEAL = "#4A7C7E"
ACCENT_SAGE = "#87A878"

# Kategorik grafikler için çok renkli ama uyumlu palet
PALETTE_PRO = [NAVY, GOLD, ACCENT_BURGUNDY, ACCENT_TEAL, ACCENT_SAGE,
               NAVY_LIGHT, GOLD_LIGHT, "#6B4226", "#536878", "#A77B68"]


# =============================================================
# 🔤 FONT KAYDI (ReportLab + Matplotlib için ortak)
# =============================================================
_FONTS_REGISTERED = False


def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    candidates = [
        "fonts",
        os.path.join(os.path.dirname(__file__), "fonts"),
    ]
    for base in candidates:
        normal = os.path.join(base, "DejaVuSans.ttf")
        bold = os.path.join(base, "DejaVuSans-Bold.ttf")
        italic = os.path.join(base, "DejaVuSans-Oblique.ttf")
        bolditalic = os.path.join(base, "DejaVuSans-BoldOblique.ttf")
        if os.path.exists(normal) and os.path.exists(bold):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", normal))
                pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold))
                if os.path.exists(italic):
                    pdfmetrics.registerFont(TTFont("DejaVu-Italic", italic))
                if os.path.exists(bolditalic):
                    pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", bolditalic))
                # Matplotlib için de
                from matplotlib import font_manager
                for f in [normal, bold, italic, bolditalic]:
                    if os.path.exists(f):
                        font_manager.fontManager.addfont(f)
                plt.rcParams["font.family"] = "DejaVu Sans"
                _FONTS_REGISTERED = True
                return
            except Exception:
                continue
    # Fallback — sistem fontu
    plt.rcParams["font.family"] = "DejaVu Sans"
    _FONTS_REGISTERED = True


# =============================================================
# 📊 GRAFİK ÜRETİCİ (her test için)
# =============================================================

def _apply_pro_style(ax, title=None):
    """Profesyonel grafik stilini uygular."""
    ax.set_facecolor(CREAM)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(NAVY)
    ax.spines["bottom"].set_color(NAVY)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.tick_params(colors=CHARCOAL, labelsize=10)
    ax.grid(axis="y", color=SOFT_GREY, linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold",
                     color=NAVY, pad=15)


def _chart_to_bytes(fig):
    """Figürü PNG byte'a çevirir."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)
    buf.seek(0)
    return buf


def _bar_chart(scores_dict, title):
    """Yatay bar grafiği — kategori skorları için."""
    _register_fonts()
    if not scores_dict:
        return None
    # Sıralı, en yüksek üstte
    items = sorted(scores_dict.items(), key=lambda x: _to_float(x[1]),
                   reverse=False)
    labels = [str(k) for k, _ in items]
    values = [_to_float(v) for _, v in items]

    fig, ax = plt.subplots(figsize=(9, max(4, len(labels) * 0.55)))
    colors = [PALETTE_PRO[i % len(PALETTE_PRO)] for i in range(len(labels))]
    bars = ax.barh(labels, values, color=colors, edgecolor=NAVY, linewidth=0.8)

    # Değer etiketleri
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + max(values) * 0.015,
                bar.get_y() + bar.get_height() / 2,
                f"{val:g}", va="center", ha="left",
                color=CHARCOAL, fontsize=10, fontweight="bold")

    _apply_pro_style(ax, title)
    ax.set_xlim(0, max(values) * 1.15)
    fig.tight_layout()
    return _chart_to_bytes(fig)


def _radar_chart(scores_dict, title):
    """Radar (örümcek) grafiği — Holland, Çoklu Zeka için."""
    _register_fonts()
    if not scores_dict or len(scores_dict) < 3:
        return _bar_chart(scores_dict, title)

    labels = [str(k) for k in scores_dict.keys()]
    values = [_to_float(v) for v in scores_dict.values()]
    n = len(labels)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    values_c = values + values[:1]
    angles_c = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.set_facecolor(CREAM)
    ax.plot(angles_c, values_c, color=NAVY, linewidth=2.5)
    ax.fill(angles_c, values_c, color=GOLD, alpha=0.35)
    ax.scatter(angles, values, color=NAVY, s=80, zorder=5, edgecolor=GOLD,
               linewidth=2)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, color=CHARCOAL, fontsize=11, fontweight="bold")
    ax.tick_params(colors=CHARCOAL)
    ax.spines["polar"].set_color(NAVY)
    ax.grid(color=SOFT_GREY, linewidth=1)
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold",
                     color=NAVY, pad=25)

    fig.tight_layout()
    return _chart_to_bytes(fig)


def _donut_chart(scores_dict, title):
    """Donut grafiği — Enneagram, VARK gibi oransal dağılımlar için."""
    _register_fonts()
    if not scores_dict:
        return None
    items = sorted(scores_dict.items(), key=lambda x: _to_float(x[1]),
                   reverse=True)
    labels = [str(k) for k, _ in items]
    values = [_to_float(v) for _, v in items]
    total = sum(values) or 1

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [PALETTE_PRO[i % len(PALETTE_PRO)] for i in range(len(labels))]

    wedges, _ = ax.pie(
        values, colors=colors, startangle=90,
        wedgeprops=dict(width=0.35, edgecolor="white", linewidth=2)
    )
    # Merkez yüzde
    top_pct = values[0] / total * 100 if values else 0
    ax.text(0, 0.08, f"%{top_pct:.0f}", ha="center", va="center",
            fontsize=28, fontweight="bold", color=NAVY)
    ax.text(0, -0.15, labels[0] if labels else "", ha="center", va="center",
            fontsize=11, color=CHARCOAL)

    # Legend
    legend_labels = [f"{lbl}  •  {val:g}  (%{val/total*100:.0f})"
                     for lbl, val in zip(labels, values)]
    ax.legend(wedges, legend_labels, loc="center left",
              bbox_to_anchor=(1.0, 0.5), frameon=False,
              fontsize=10, labelcolor=CHARCOAL)

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold",
                     color=NAVY, pad=15)
    fig.tight_layout()
    return _chart_to_bytes(fig)


def _gauge_chart(value, max_value, title, subtitle=""):
    """Gauge/gösterge — Sınav Kaygısı, P2 Dikkat tek değerli testler için."""
    _register_fonts()
    value = _to_float(value)
    max_value = _to_float(max_value) or 100
    pct = min(100, max(0, value / max_value * 100))

    fig, ax = plt.subplots(figsize=(8, 5), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, np.pi)

    # Renk: düşük=yeşil, orta=altın, yüksek=bordo (kaygı için ters olabilir
    # ama burada nötr gösterim — yorumu AI yapacak)
    if pct < 33:
        color = ACCENT_SAGE
    elif pct < 66:
        color = GOLD
    else:
        color = ACCENT_BURGUNDY

    theta = np.linspace(0, np.pi * pct / 100, 100)
    ax.plot(theta, [0.9] * len(theta), color=color, linewidth=22,
            solid_capstyle="round")
    # Arka plan
    bg_theta = np.linspace(0, np.pi, 100)
    ax.plot(bg_theta, [0.9] * len(bg_theta), color=SOFT_GREY, linewidth=22,
            solid_capstyle="round", zorder=-1)

    ax.set_axis_off()
    ax.text(np.pi / 2, 0.2, f"{value:g}", ha="center", va="center",
            fontsize=36, fontweight="bold", color=NAVY)
    ax.text(np.pi / 2, 0.02, f"/ {max_value:g}", ha="center", va="center",
            fontsize=12, color=CHARCOAL)
    if subtitle:
        ax.text(np.pi / 2, -0.2, subtitle, ha="center", va="center",
                fontsize=11, color=CHARCOAL, style="italic")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold",
                     color=NAVY, pad=20)
    fig.tight_layout()
    return _chart_to_bytes(fig)


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# =============================================================
# Test → Grafik eşlemesi (akıllı seçici)
# =============================================================

def build_chart_for_test(test_name, scores):
    """
    Test adına ve skor yapısına bakarak en uygun grafiği seçer.
    Dönüş: (chart_bytes, chart_type_string) — grafik oluşamazsa (None, None)
    """
    if not scores or not isinstance(scores, dict):
        return None, None

    # Numeric değerleri olan anahtarları al
    # Filtreleme: metin alanları ("dominant": "V" gibi) ve 0 değerler düşür
    numeric_scores = {}
    for k, v in scores.items():
        # Metin değerleri (örn. "dominant": "V") float'a çevrilemez, atla
        if isinstance(v, str) and not v.replace(".", "", 1).replace("-", "", 1).isdigit():
            continue
        val = _to_float(v)
        if val <= 0:
            continue
        # Anahtar adı metadata gibiyse atla
        k_lower = str(k).lower().strip()
        if k_lower in ("dominant", "baskın", "baskin", "total", "toplam", "max", "maksimum"):
            continue
        numeric_scores[k] = val

    if not numeric_scores:
        return None, None

    # Kısaltmaları tam isme çevir (VARK vs için okunaklılık)
    label_map_vark = {
        "V": "Görsel", "A": "İşitsel", "R": "Okuma/Yazma", "K": "Kinestetik",
    }
    label_map_holland = {
        "R": "Gerçekçi", "I": "Araştırıcı", "A": "Sanatsal",
        "S": "Sosyal", "E": "Girişimci", "C": "Geleneksel",
    }
    tn_low = (test_name or "").lower()
    label_map = None
    if "vark" in tn_low or "öğrenme stil" in tn_low:
        label_map = label_map_vark
    elif "holland" in tn_low:
        label_map = label_map_holland

    if label_map:
        remapped = {}
        for k, v in numeric_scores.items():
            new_key = label_map.get(str(k).strip().upper(), k)
            remapped[new_key] = v
        numeric_scores = remapped

    tn = (test_name or "").lower()

    # Holland / Çoklu Zeka / Sağ-Sol Beyin → radar
    if any(k in tn for k in ["holland", "çoklu zeka", "zekâ",
                              "beyin dominans", "sağ-sol"]):
        chart = _radar_chart(numeric_scores, test_name)
        return chart, "radar"

    # Enneagram / VARK → donut (oransal)
    if any(k in tn for k in ["enneagram", "vark", "öğrenme stil"]):
        chart = _donut_chart(numeric_scores, test_name)
        return chart, "donut"

    # P2 Dikkat / Sınav Kaygısı / Hızlı Okuma → gauge (tek değerli)
    if any(k in tn for k in ["p2 dikkat", "sınav kayg", "hızlı okuma"]):
        # Ana skoru bul
        main_key = next(iter(numeric_scores.keys()))
        main_val = numeric_scores[main_key]
        # Max değer tahmin et (belli anahtarlarda toplam varsa)
        total_candidates = [v for k, v in numeric_scores.items()
                            if "max" in k.lower() or "toplam" in k.lower()
                            or "total" in k.lower()]
        if total_candidates:
            max_val = max(total_candidates)
        else:
            max_val = max(max(numeric_scores.values()) * 1.2, 100)
        chart = _gauge_chart(main_val, max_val, test_name, f"{main_key}")
        return chart, "gauge"

    # Akademik / Çalışma Davranışı / diğer → yatay bar
    chart = _bar_chart(numeric_scores, test_name)
    return chart, "bar"


# =============================================================
# 🧠 AI PROMPT (yalın Türkçe, hem veli hem öğrenci için)
# =============================================================

def build_charts_for_test(test_name, scores):
    """
    Bir test için BİRDEN FAZLA grafik üretir — farklı açılardan aynı veriyi
    gösterir. Dönüş: [(chart_type, bytesio), ...]
    """
    charts = []
    primary, ptype = build_chart_for_test(test_name, scores)
    if primary is None:
        return []
    charts.append((ptype, primary))

    # İkincil grafik: ilkinden farklı bir tip seç
    if not scores or not isinstance(scores, dict):
        return charts

    # Aynı filtreyi uygula (build_chart_for_test'teki gibi — ancak burada
    # sadece numeric_scores lazım, tekrar oluştur)
    numeric_scores = {}
    for k, v in scores.items():
        if isinstance(v, str) and not v.replace(".", "", 1).replace("-", "", 1).isdigit():
            continue
        val = _to_float(v)
        if val <= 0:
            continue
        k_lower = str(k).lower().strip()
        if k_lower in ("dominant", "baskın", "baskin", "total", "toplam", "max", "maksimum"):
            continue
        numeric_scores[k] = val

    if not numeric_scores:
        return charts

    # Etiket mapping
    tn_low = (test_name or "").lower()
    label_map_vark = {"V": "Görsel", "A": "İşitsel", "R": "Okuma/Yazma", "K": "Kinestetik"}
    label_map_holland = {"R": "Gerçekçi", "I": "Araştırıcı", "A": "Sanatsal",
                         "S": "Sosyal", "E": "Girişimci", "C": "Geleneksel"}
    label_map = None
    if "vark" in tn_low or "öğrenme stil" in tn_low:
        label_map = label_map_vark
    elif "holland" in tn_low:
        label_map = label_map_holland
    if label_map:
        remapped = {}
        for k, v in numeric_scores.items():
            new_key = label_map.get(str(k).strip().upper(), k)
            remapped[new_key] = v
        numeric_scores = remapped

    # İkincil görünüm seçimi
    if ptype == "donut":
        # Donut'tan sonra yatay bar — kıyaslama için
        secondary = _bar_chart(numeric_scores, f"{test_name} — Kıyaslamalı Görünüm")
        if secondary:
            charts.append(("bar", secondary))
    elif ptype == "radar":
        # Radar'dan sonra bar — kesin değerleri görmek için
        secondary = _bar_chart(numeric_scores, f"{test_name} — Skor Dağılımı")
        if secondary:
            charts.append(("bar", secondary))
    elif ptype == "bar":
        # Bar'dan sonra donut — oransal bakış
        if len(numeric_scores) >= 3:
            secondary = _donut_chart(numeric_scores, f"{test_name} — Oransal Dağılım")
            if secondary:
                charts.append(("donut", secondary))

    return charts


def build_graphic_analysis_prompt(student_name, student_age, student_gender,
                                   student_grade, tests_list):
    """
    Claude'a gönderilecek prompt. Grafikleri baz alan, yalın Türkçe,
    hem veli hem öğrenci için uygun bütünsel analiz ister.
    """
    # Testlerin özetlerini metin olarak hazırla (grafikler yerine değil,
    # grafikleri tamamlayıcı olarak — Claude tüm sayısal bilgiyi görsün)
    summary_lines = []
    for t in tests_list:
        test_name = t.get("test_name", "")
        scores = t.get("scores", {}) or {}
        if not scores:
            continue
        # En yüksek 3 skoru vurgula
        sorted_scores = sorted(scores.items(), key=lambda x: _to_float(x[1]),
                                reverse=True)
        top_items = [f"{k}: {v}" for k, v in sorted_scores[:5]]
        summary_lines.append(f"• {test_name} → " + " | ".join(top_items))

    scores_summary = "\n".join(summary_lines) if summary_lines else \
                     "(Test sonucu bulunamadı)"

    prompt = f"""Sen bir rehber öğretmen ve psikolojik danışmansın. Aşağıda bir öğrencinin psikometrik test sonuçları var. Bu sonuçlara dayanarak **hem veliye, hem öğretmene/koça, hem de öğrenciye** hitap eden, **son derece yalın bir Türkçe** ile yazılmış bütünsel bir rapor hazırla.

ÖĞRENCİ BİLGİLERİ:
- Ad: {student_name}
- Yaş: {student_age}
- Cinsiyet: {student_gender}
- Sınıf: {student_grade if student_grade else "—"}

TEST SONUÇLARI ÖZETİ:
{scores_summary}

⚠️ EN ÖNEMLİ KURAL — TAVSİYE DİLİ:
Bu bir klinik teşhis değil, bir yönlendirme ve öneri raporudur. ASLA kesin ifadeler kullanma. Şu listedeki ifadeleri tercih et:
- "olabilir", "olma ihtimali var", "eğilimli görünüyor"
- "faydalı olabilir", "denenebilir", "düşünülebilir"
- "destekleyici olabilir", "katkı sağlayabilir"
- "gibi görünüyor", "izlenim veriyor", "işaret ediyor"

ŞUNLARI ASLA KULLANMA:
- "kesinlikle", "mutlaka", "hep", "her zaman"
- "X meslekte başarılı olacak", "Y yaşında şöyle olur" (kesin öngörü)
- "yapmalı", "etmeli", "şart"
- "dır/dir" kalıbı yerine "-ebilir/-abilir" kullan. Örn: "çok hareketli bir çocuktur" ❌ → "çok hareketli bir çocuk izlenimi veriyor" ✅

HER ÖNERİ İÇİN NEDEN: Her öneriye mini bir "neden" ekle — hangi skordan/testten çıkarım yapıldığını kısaca belirt. Örn: "Kinestetik puanı diğerlerine göre yüksek olduğu için, elle yapılan etkinlikler denenebilir."

DİL VE TON:
- Günlük konuşma Türkçesi kullan. "Kinestetik", "içe dönük", "analitik düşünme" gibi teknik terim KULLANMA. Kullandığında parantez içinde sade açıklama ekle.
- Eleştirel değil, yol gösterici ve pozitif ol.
- 3 okuyucuya hitap et: Veli, Öğretmen/Koç, Öğrenci.

RAPOR FORMATI (her bölüm markdown ## başlık ile):

## Özet Bakış
2-3 cümlede {student_name}'ın genel profili. Kim olduğu, nelere eğilimli göründüğü. Mutlaka "olabilir/görünüyor" dili.

## Öne Çıkan Yönler
Test sonuçlarındaki en yüksek alanlara odaklan. 3-4 madde. Her madde: "[Alan] → [ne anlama gelebileceği]". Mesela: "Görsel öğrenmeye yatkın izlenimi → Okuduğundan çok görsellerle karşılaştığında anlaması kolaylaşabilir."

## Öğrenme Stili Üzerine
Hangi yolla daha rahat öğrenebileceği konusunda fikirler. "Dersi dinlemek yerine şema, video ve resimlerle çalışmak ona daha uygun olabilir" gibi somut örnekler. Bu bölümde özellikle VARK ve Çoklu Zeka skorlarına referans ver.

## Olası İlgi ve Kariyer Yönelimleri
Holland ve diğer verilere bakarak, ilerleyen yıllarda hangi tür alanlara yönelebileceğine dair fikirler. ASLA meslek dayatma. "İnsanlarla çalışmaktan enerji alan işler ona iyi gelebilir" gibi ipuçları. "Kesinleşmiş değildir, sadece bir eğilim göstergesidir" şeklinde uyarı ekle.

## Dikkat ve Duygusal Durum
Eğer dikkat testi (P2) veya Sınav Kaygısı testi varsa buraya yaz. Yoksa bu bölümü atla. Kaygı puanı yüksekse bile "kaygılı bir çocuk" deme, "şu an için dikkat çekilebilecek bir kaygı belirtisi göze çarpıyor" de.

## Veliye Öneriler
5-7 maddelik somut öneriler. Her biri için neden (hangi skordan çıkarıldığını) ekle. "Denenebilir", "faydalı olabilir" dili kullan.

## Öğretmen ve Koçlara Notlar
3-5 maddelik sınıf ortamı veya koçluk sürecinde dikkat edilebilecek ipuçları. "Grup çalışmaları onun için daha motive edici olabilir — sosyal skoru yüksek" tarzı.

## {student_name}'a Doğrudan Mesaj
Doğrudan öğrenciye hitap eden 4-6 cümle. "Sen" diye başla. Testlerden anlaşılan güzel yönleri söyle, ona güven ver. "Sen yapabilirsin" dili. Üzerinde çalışabileceği şeyleri nazik bir dille söyle. Asla yargılayıcı değil, motive edici ol.

## Son Söz
2-3 cümlelik kapanış. Bu raporun bir teşhis değil, bir yol arkadaşı olduğunu vurgula. "Bu rapor, {student_name}'ı tanımanıza yardımcı olmak için hazırlanmış bir yol haritası taslağı niteliğindedir. Zaman içinde değişebilir ve gelişebilir." tarzı.

TOPLAM UZUNLUK: 1000-1500 kelime.
MARKDOWN: Başlıklar ##, maddeler -, kalın **...**
KAPANIŞ DİLİ: "olabilir, faydalı olabilir, izlenim veriyor" kalıpları ana dilin olsun.
"""
    return prompt


def build_single_test_graphic_prompt(student_name, student_age, student_gender,
                                      student_grade, test_name, scores):
    """
    TEK bir test için grafik bazlı kısa analiz prompt'u.
    Tekil raporlar için kullanılır.
    """
    scores_text = " | ".join(
        f"{k}: {v}" for k, v in sorted(
            (scores or {}).items(), key=lambda x: _to_float(x[1]), reverse=True
        )[:8]
    ) or "(skor verisi yok)"

    prompt = f"""Sen bir rehber öğretmen ve psikolojik danışmansın. Aşağıda bir öğrencinin TEK bir psikometrik testinin sonuçları var. Bu tek testin sonucuna dayanarak, veli + öğretmen + öğrenci için yalın Türkçe bir odaklı rapor hazırla.

ÖĞRENCİ:
- Ad: {student_name}, Yaş: {student_age}, Cinsiyet: {student_gender}, Sınıf: {student_grade or "—"}

TEST: {test_name}
SKORLAR: {scores_text}

⚠️ TAVSİYE DİLİ (çok önemli):
"kesinlikle", "mutlaka", "her zaman", "dır/dir" KULLANMA. Yerine:
- "olabilir", "görünüyor", "eğilim", "izlenim"
- "faydalı olabilir", "denenebilir"
- "-ebilir/-abilir" kipi

Tek test yorumu olduğu için şunu açıkça yaz: "Bu rapor yalnızca {test_name} sonuçlarına dayanır; kesin bir değerlendirme için diğer testlerle birlikte ele alınması önerilir."

RAPOR FORMATI (toplam 500-700 kelime):

## Testin Kısa Tanıtımı
2-3 cümle: Bu test neyi ölçüyor?

## {student_name}'ın Sonuç Özeti
Skorlardaki en belirgin eğilimi yalın Türkçe ile özetle. 3-4 cümle. Kesin ifade yok.

## Ne Anlama Gelebilir?
4-5 madde. Her madde bir skor/alan için yorum. Mutlaka "neden" (skor kaç olduğu) belirt.

## Veliye Öneriler
3-4 somut öneri. "Denenebilir" dili.

## Öğretmen/Koçlara Notlar
2-3 maddelik ipucu.

## {student_name}'a Mesaj
3-4 cümle samimi, "sen" hitabıyla, motive edici.

## Önemli Hatırlatma
Bu tek test bir "resim" değil, bir "fotoğraf karesi". Diğer testlerle birlikte değerlendirildiğinde daha anlamlı olur.

DİL: Günlük Türkçe, teknik terim yok, yumuşak ton.
"""
    return prompt


# =============================================================
# 📄 PDF ÜRETİCİ
# =============================================================

def _safe_filename(name):
    import re
    name = re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_")
    return name or "ogrenci"


def generate_graphic_report_filename(student_name):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    return f"Grafik_Analiz_{_safe_filename(student_name)}_{ts}.pdf"


def _styles():
    """Özel ParagraphStyle'lar."""
    _register_fonts()
    base = "DejaVu"
    bold = "DejaVu-Bold"
    italic = "DejaVu-Italic"

    return {
        "title": ParagraphStyle(
            "title", fontName=bold, fontSize=26, leading=30,
            textColor=HexColor(NAVY), alignment=TA_CENTER, spaceAfter=8
        ),
        "subtitle": ParagraphStyle(
            "subtitle", fontName=base, fontSize=13, leading=16,
            textColor=HexColor(GOLD), alignment=TA_CENTER, spaceAfter=20
        ),
        "cover_info": ParagraphStyle(
            "cover_info", fontName=base, fontSize=12, leading=18,
            textColor=HexColor(CHARCOAL), alignment=TA_CENTER, spaceAfter=6
        ),
        "h1": ParagraphStyle(
            "h1", fontName=bold, fontSize=18, leading=22,
            textColor=HexColor(NAVY), spaceBefore=18, spaceAfter=10,
            borderPadding=4
        ),
        "h2": ParagraphStyle(
            "h2", fontName=bold, fontSize=14, leading=18,
            textColor=HexColor(NAVY_LIGHT), spaceBefore=12, spaceAfter=8
        ),
        "body": ParagraphStyle(
            "body", fontName=base, fontSize=11, leading=17,
            textColor=HexColor(CHARCOAL), alignment=TA_JUSTIFY,
            spaceAfter=7
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName=base, fontSize=11, leading=16,
            textColor=HexColor(CHARCOAL), leftIndent=18, bulletIndent=6,
            spaceAfter=5
        ),
        "caption": ParagraphStyle(
            "caption", fontName=italic, fontSize=9, leading=11,
            textColor=HexColor(CHARCOAL), alignment=TA_CENTER,
            spaceAfter=10
        ),
        "footer": ParagraphStyle(
            "footer", fontName=base, fontSize=8, leading=10,
            textColor=HexColor(NAVY_LIGHT), alignment=TA_CENTER
        ),
    }


def _header_footer(canvas, doc):
    """Her sayfaya üst/alt çizgi + sayfa no."""
    canvas.saveState()
    w, h = A4

    # Üst şerit
    canvas.setFillColor(HexColor(NAVY))
    canvas.rect(0, h - 0.6 * cm, w, 0.6 * cm, stroke=0, fill=1)
    canvas.setFillColor(HexColor(GOLD))
    canvas.rect(0, h - 0.75 * cm, w, 0.15 * cm, stroke=0, fill=1)

    # Alt bilgi
    canvas.setFont("DejaVu", 8)
    canvas.setFillColor(HexColor(NAVY_LIGHT))
    canvas.drawCentredString(w / 2, 0.8 * cm,
                              f"EĞİTİM CHECK UP  •  Kişisel Analiz Raporu  •  Sayfa {doc.page}")
    canvas.setFillColor(HexColor(GOLD))
    canvas.rect(0, 0.5 * cm, w, 0.06 * cm, stroke=0, fill=1)
    canvas.restoreState()


def _strip_emojis_for_pdf(text):
    """DejaVu Sans'ın desteklemediği emojileri PDF için temizler."""
    import re
    # Tüm emoji unicode aralıklarını temizle
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F700-\U0001F77F"  # alchemical
        "\U0001F780-\U0001F7FF"  # geometric shapes extended
        "\U0001F800-\U0001F8FF"  # supplemental arrows-c
        "\U0001F900-\U0001F9FF"  # supplemental symbols & pictographs
        "\U0001FA00-\U0001FA6F"  # chess, etc.
        "\U0001FA70-\U0001FAFF"  # symbols & pictographs extended-a
        "\U00002600-\U000027BF"  # miscellaneous symbols
        "\U00002700-\U000027BF"  # dingbats
        "\u2300-\u23FF"          # miscellaneous technical
        "\u2B00-\u2BFF"          # arrows
        "\u3000-\u303F"          # CJK symbols
        "]+", flags=re.UNICODE)
    cleaned = emoji_pattern.sub("", text)
    # Fazla boşlukları temizle
    import re as _re
    cleaned = _re.sub(r"  +", " ", cleaned)
    cleaned = _re.sub(r"^[ \t]+", "", cleaned, flags=re.MULTILINE)
    return cleaned


def _parse_markdown_to_flowables(md_text, styles):
    """
    Basit markdown → ReportLab flowable dönüştürücü.
    ## H1, ### H2, - madde, **bold**, *italic* destekler.
    """
    # Emojileri temizle (DejaVu Sans desteklemiyor)
    md_text = _strip_emojis_for_pdf(md_text)

    flow = []
    lines = md_text.split("\n")
    paragraph_buf = []

    def flush_paragraph():
        if paragraph_buf:
            txt = " ".join(paragraph_buf).strip()
            if txt:
                # inline formatters
                txt = _md_inline(txt)
                flow.append(Paragraph(txt, styles["body"]))
            paragraph_buf.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph()
            flow.append(Spacer(1, 4))
            continue
        if line.startswith("## "):
            flush_paragraph()
            flow.append(Spacer(1, 6))
            flow.append(Paragraph(_md_inline(line[3:].strip()), styles["h1"]))
            # Altın alt çizgi efekti
            continue
        if line.startswith("### "):
            flush_paragraph()
            flow.append(Paragraph(_md_inline(line[4:].strip()), styles["h2"]))
            continue
        if line.startswith("# "):
            flush_paragraph()
            flow.append(Paragraph(_md_inline(line[2:].strip()), styles["h1"]))
            continue
        if line.lstrip().startswith(("- ", "* ", "• ")):
            flush_paragraph()
            txt = line.lstrip()[2:].strip()
            flow.append(Paragraph("• " + _md_inline(txt), styles["bullet"]))
            continue
        paragraph_buf.append(line.strip())

    flush_paragraph()
    return flow


def _md_inline(text):
    """Basit markdown inline — **bold**, *italic*. HTML'e kaçırır."""
    import re
    # HTML escape
    text = (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic (sadece tek *)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def generate_graphic_analysis_pdf(student_data, analysis_history=None,
                                    get_ai_analysis_fn=None,
                                    format_grade_fn=None):
    """
    Ana fonksiyon: öğrenci verisini alır, grafikleri üretir, Claude'dan
    analiz alır, PDF olarak döndürür.

    student_data: {"info": StudentInfo, "tests": [...]}
    get_ai_analysis_fn: teacher_view.get_ai_analysis fonksiyonu
    format_grade_fn: teacher_view.format_grade fonksiyonu

    Dönüş: BytesIO (PDF içeren)
    """
    _register_fonts()
    info = student_data["info"]
    tests = student_data.get("tests", []) or []

    # 1) Grafikleri üret — her test için birden fazla görünüm
    charts_per_test = []  # [(test_name, [(type, bytesio), ...]), ...]
    for t in tests:
        test_name = t.get("test_name", "")
        scores = t.get("scores", {}) or {}
        if not scores:
            continue
        test_charts = build_charts_for_test(test_name, scores)
        if test_charts:
            charts_per_test.append((test_name, test_charts))

    # 2) AI analiz al
    grade_val = getattr(info, "grade", None)
    grade_text = format_grade_fn(grade_val) if format_grade_fn else (
        str(grade_val) if grade_val else "—"
    )

    ai_report_md = ""
    if get_ai_analysis_fn is not None and tests:
        prompt = build_graphic_analysis_prompt(
            student_name=info.name,
            student_age=info.age,
            student_gender=info.gender,
            student_grade=grade_text,
            tests_list=tests,
        )
        ai_report_md = get_ai_analysis_fn(prompt) or ""

    # 3) PDF birleştir
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
        title=f"Grafik Analiz Raporu — {info.name}",
        author="Eğitim Check-Up",
    )

    styles = _styles()
    story = []

    # ======= KAPAK =======
    story.append(Spacer(1, 3.5 * cm))
    # Logo yerine büyük altın daire + ilk harf
    story.append(Paragraph("EĞİTİM CHECK UP", styles["subtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Kişisel Analiz Raporu", styles["title"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Grafikler ile Bütünsel Bakış", styles["subtitle"]))
    story.append(Spacer(1, 2 * cm))

    # Öğrenci kimlik kutusu
    cover_data = [
        [Paragraph("<b>Ad Soyad</b>", styles["cover_info"]),
         Paragraph(info.name or "—", styles["cover_info"])],
        [Paragraph("<b>Yaş</b>", styles["cover_info"]),
         Paragraph(str(info.age) if info.age else "—", styles["cover_info"])],
        [Paragraph("<b>Cinsiyet</b>", styles["cover_info"]),
         Paragraph(info.gender or "—", styles["cover_info"])],
        [Paragraph("<b>Sınıf</b>", styles["cover_info"]),
         Paragraph(grade_text, styles["cover_info"])],
        [Paragraph("<b>Rapor Tarihi</b>", styles["cover_info"]),
         Paragraph(datetime.now().strftime("%d.%m.%Y"), styles["cover_info"])],
        [Paragraph("<b>Çözülen Test</b>", styles["cover_info"]),
         Paragraph(f"{len(tests)} test", styles["cover_info"])],
    ]
    cover_tbl = Table(cover_data, colWidths=[6 * cm, 8 * cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor(CREAM)),
        ("BOX", (0, 0), (-1, -1), 1.5, HexColor(GOLD)),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, HexColor(GOLD_LIGHT)),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_tbl)

    story.append(PageBreak())

    # ======= AI ANALİZ =======
    if ai_report_md and not ai_report_md.startswith("⚠️"):
        story.append(Paragraph("Analiz Raporu", styles["h1"]))
        story.append(Spacer(1, 6))
        story.extend(_parse_markdown_to_flowables(ai_report_md, styles))
    elif ai_report_md:
        # Hata mesajı
        story.append(Paragraph("Analiz Raporu", styles["h1"]))
        story.append(Paragraph(ai_report_md, styles["body"]))
    else:
        story.append(Paragraph("Analiz Raporu", styles["h1"]))
        story.append(Paragraph(
            "AI analizi üretilemedi. Lütfen API anahtarı ve test verilerini "
            "kontrol edin.", styles["body"]))

    # ======= GRAFİKLER BÖLÜMÜ =======
    if charts_per_test:
        story.append(PageBreak())
        story.append(Paragraph("Test Grafikleri", styles["h1"]))
        story.append(Paragraph(
            "Aşağıdaki grafikler, raporda bahsedilen değerlendirmelerin "
            "görsel özetidir. Her test birden fazla açıdan gösterilir.",
            styles["body"]))
        story.append(Spacer(1, 10))

        for test_name, test_charts in charts_per_test:
            # Test başlığı
            story.append(Paragraph(test_name, styles["h2"]))
            # Her grafiği göster
            for idx, (chart_type, chart_bytes) in enumerate(test_charts):
                block = []
                img = RLImage(chart_bytes, width=15 * cm, height=10.5 * cm,
                              kind="proportional")
                block.append(img)
                if idx < len(test_charts) - 1:
                    block.append(Spacer(1, 8))
                else:
                    block.append(Spacer(1, 16))
                story.append(KeepTogether(block))

    doc.build(story, onFirstPage=_header_footer,
              onLaterPages=_header_footer)
    buf.seek(0)
    return buf


# =============================================================
# 🎯 TEKİL TEST PDF ÜRETİCİSİ
# =============================================================

def generate_single_test_report_filename(student_name, test_name):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    safe_test = _safe_filename(test_name)[:30]
    return f"Tekil_{_safe_filename(student_name)}_{safe_test}_{ts}.pdf"


def generate_single_test_graphic_pdf(student_data, test_index,
                                       get_ai_analysis_fn=None,
                                       format_grade_fn=None):
    """
    Öğrencinin belirli BİR testi için odaklı grafik analiz PDF'i üretir.

    student_data: {"info": StudentInfo, "tests": [...]}
    test_index: tests listesinde hangi testin raporlanacağı (int)
    """
    _register_fonts()
    info = student_data["info"]
    tests = student_data.get("tests", []) or []
    if test_index >= len(tests):
        raise ValueError("Geçersiz test indeksi")

    test = tests[test_index]
    test_name = test.get("test_name", "Test")
    scores = test.get("scores", {}) or {}

    # Grafikleri üret (çoklu görünüm)
    test_charts = build_charts_for_test(test_name, scores)

    # AI analiz
    grade_val = getattr(info, "grade", None)
    grade_text = format_grade_fn(grade_val) if format_grade_fn else (
        str(grade_val) if grade_val else "—"
    )

    ai_report_md = ""
    if get_ai_analysis_fn is not None and scores:
        prompt = build_single_test_graphic_prompt(
            student_name=info.name,
            student_age=info.age,
            student_gender=info.gender,
            student_grade=grade_text,
            test_name=test_name,
            scores=scores,
        )
        ai_report_md = get_ai_analysis_fn(prompt) or ""

    # PDF
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.6 * cm,
        title=f"Tekil Rapor — {info.name} — {test_name}",
        author="Eğitim Check-Up",
    )
    styles = _styles()
    story = []

    # Kapak
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("EĞİTİM CHECK UP", styles["subtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Tekil Test Analizi", styles["title"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(test_name, styles["subtitle"]))
    story.append(Spacer(1, 1.5 * cm))

    cover_data = [
        [Paragraph("<b>Ad Soyad</b>", styles["cover_info"]),
         Paragraph(info.name or "—", styles["cover_info"])],
        [Paragraph("<b>Sınıf</b>", styles["cover_info"]),
         Paragraph(grade_text, styles["cover_info"])],
        [Paragraph("<b>Test</b>", styles["cover_info"]),
         Paragraph(test_name, styles["cover_info"])],
        [Paragraph("<b>Rapor Tarihi</b>", styles["cover_info"]),
         Paragraph(datetime.now().strftime("%d.%m.%Y"), styles["cover_info"])],
    ]
    cover_tbl = Table(cover_data, colWidths=[6 * cm, 8 * cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor(CREAM)),
        ("BOX", (0, 0), (-1, -1), 1.5, HexColor(GOLD)),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, HexColor(GOLD_LIGHT)),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cover_tbl)

    # Analiz + grafikleri tek sayfa akışında
    story.append(PageBreak())

    # Grafikleri önce koy
    if test_charts:
        story.append(Paragraph("Görsel Özet", styles["h1"]))
        for chart_type, chart_bytes in test_charts:
            img = RLImage(chart_bytes, width=14 * cm, height=9 * cm,
                          kind="proportional")
            story.append(KeepTogether([img, Spacer(1, 8)]))
        story.append(Spacer(1, 12))

    # Analiz metni
    if ai_report_md and not ai_report_md.startswith("⚠️"):
        story.append(Paragraph("Analiz", styles["h1"]))
        story.extend(_parse_markdown_to_flowables(ai_report_md, styles))
    elif ai_report_md:
        story.append(Paragraph("Analiz", styles["h1"]))
        story.append(Paragraph(ai_report_md, styles["body"]))

    doc.build(story, onFirstPage=_header_footer,
              onLaterPages=_header_footer)
    buf.seek(0)
    return buf

"""
PDF Rapor Motoru — Eğitim Check-Up
Öğrenci kişisel bilgileri + test sonuçları + grafikler + AI analiz raporlarını
profesyonel PDF formatında dışa aktarır.

v2.1 — Türkçe karakter düzeltmesi + matplotlib grafik desteği
"""

import io
import os
import re
import textwrap
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ============================================================
# FONT KAYDI (Türkçe karakter desteği — çoklu dizin fallback)
# ============================================================

def _find_and_register_fonts():
    """
    Fontları bul ve kaydet. Sırasıyla dener:
    1) Proje dizinindeki fonts/ klasörü
    2) /usr/share/fonts/truetype/dejavu/
    3) /usr/share/fonts/truetype/liberation/ (LiberationSans)
    4) Helvetica fallback (Türkçe desteklemez!)
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    font_candidates = [
        (
            os.path.join(base_dir, "fonts"),
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
            "DejaVuSans-Oblique.ttf",
            "DejaVuSans-BoldOblique.ttf",
        ),
        (
            "/usr/share/fonts/truetype/dejavu",
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
            "DejaVuSans-Oblique.ttf",
            "DejaVuSans-BoldOblique.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation",
            "LiberationSans-Regular.ttf",
            "LiberationSans-Bold.ttf",
            "LiberationSans-Italic.ttf",
            "LiberationSans-BoldItalic.ttf",
        ),
    ]

    for font_dir, normal, bold, italic, bolditalic in font_candidates:
        normal_path = os.path.join(font_dir, normal)
        bold_path = os.path.join(font_dir, bold)
        italic_path = os.path.join(font_dir, italic)
        bolditalic_path = os.path.join(font_dir, bolditalic)

        if os.path.isfile(normal_path) and os.path.isfile(bold_path):
            try:
                pdfmetrics.registerFont(TTFont("DejaVu", normal_path))
                pdfmetrics.registerFont(TTFont("DejaVu-Bold", bold_path))
                if os.path.isfile(italic_path):
                    pdfmetrics.registerFont(TTFont("DejaVu-Italic", italic_path))
                else:
                    pdfmetrics.registerFont(TTFont("DejaVu-Italic", normal_path))
                if os.path.isfile(bolditalic_path):
                    pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", bolditalic_path))
                else:
                    pdfmetrics.registerFont(TTFont("DejaVu-BoldItalic", bold_path))
                return "DejaVu", "DejaVu-Bold", "DejaVu-Italic"
            except Exception:
                continue

    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


FONT_NAME, FONT_BOLD, FONT_ITALIC = _find_and_register_fonts()

# ============================================================
# RENK PALETİ
# ============================================================
PRIMARY   = HexColor("#1B2A4A")
SECONDARY = HexColor("#2E86AB")
ACCENT    = HexColor("#A23B72")
SUCCESS   = HexColor("#155724")
BG_LIGHT  = HexColor("#F8F9FA")
BG_HEADER = HexColor("#1B2A4A")
BORDER    = HexColor("#DEE2E6")

# ============================================================
# STİL TANIMLARI
# ============================================================

def _get_styles():
    """PDF için özel Türkçe uyumlu stiller döndürür."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='TR_Title', fontName=FONT_BOLD, fontSize=20,
        textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6, leading=26,
    ))
    styles.add(ParagraphStyle(
        name='TR_Subtitle', fontName=FONT_NAME, fontSize=10,
        textColor=SECONDARY, alignment=TA_CENTER, spaceAfter=20,
    ))
    styles.add(ParagraphStyle(
        name='TR_H1', fontName=FONT_BOLD, fontSize=14, textColor=PRIMARY,
        spaceBefore=16, spaceAfter=8, leading=18, borderPadding=(0, 0, 4, 0),
    ))
    styles.add(ParagraphStyle(
        name='TR_H2', fontName=FONT_BOLD, fontSize=12, textColor=SECONDARY,
        spaceBefore=12, spaceAfter=6, leading=16,
    ))
    styles.add(ParagraphStyle(
        name='TR_H3', fontName=FONT_BOLD, fontSize=10, textColor=ACCENT,
        spaceBefore=8, spaceAfter=4, leading=14,
    ))
    styles.add(ParagraphStyle(
        name='TR_Body', fontName=FONT_NAME, fontSize=9, textColor=black,
        alignment=TA_JUSTIFY, spaceAfter=4, leading=13,
    ))
    styles.add(ParagraphStyle(
        name='TR_Small', fontName=FONT_NAME, fontSize=7.5,
        textColor=HexColor("#6C757D"), alignment=TA_CENTER, spaceBefore=4,
    ))
    styles.add(ParagraphStyle(
        name='TR_TableHeader', fontName=FONT_BOLD, fontSize=9,
        textColor=white, alignment=TA_CENTER, leading=12,
    ))
    styles.add(ParagraphStyle(
        name='TR_TableCell', fontName=FONT_NAME, fontSize=8.5,
        textColor=black, alignment=TA_LEFT, leading=11,
    ))
    styles.add(ParagraphStyle(
        name='TR_TableCellCenter', fontName=FONT_NAME, fontSize=8.5,
        textColor=black, alignment=TA_CENTER, leading=11,
    ))
    styles.add(ParagraphStyle(
        name='TR_ReportText', fontName=FONT_NAME, fontSize=8.5,
        textColor=HexColor("#212529"), alignment=TA_JUSTIFY, spaceAfter=3, leading=12,
    ))
    styles.add(ParagraphStyle(
        name='TR_Bullet', fontName=FONT_NAME, fontSize=8.5,
        textColor=HexColor("#212529"), alignment=TA_LEFT,
        spaceAfter=2, leading=12, leftIndent=12, bulletIndent=0,
    ))

    return styles


# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================

def _safe(text):
    """XML-unsafe karakterleri temizler, Türkçe karakterleri KORUR."""
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def _section_divider():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8, spaceBefore=8)


def _header_bar(text, styles):
    data = [[Paragraph(f"<b>{_safe(text)}</b>", styles['TR_TableHeader'])]]
    t = Table(data, colWidths=[17.5 * cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, -1), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    return t


def _markdown_to_flowables(md_text, styles):
    if not md_text:
        return [Paragraph("<i>Rapor içeriği bulunamadı.</i>", styles['TR_Body'])]

    flowables = []
    lines = md_text.split('\n')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flowables.append(Spacer(1, 3))
            continue

        if stripped.startswith('#### '):
            text = stripped[5:]
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', _safe(text).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>'))
            text = re.sub(r'&lt;b&gt;(.*?)&lt;/b&gt;', r'<b>\1</b>', text)
            clean = re.sub(r'<[^>]+>', '', text).replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            flowables.append(Paragraph(f"<b>{_safe(clean)}</b>", styles['TR_H3']))
            continue
        if stripped.startswith('### '):
            text = stripped[4:]
            clean = re.sub(r'[*#]', '', text).strip()
            flowables.append(Paragraph(f"<b>{_safe(clean)}</b>", styles['TR_H2']))
            continue
        if stripped.startswith('## '):
            text = stripped[3:]
            clean = re.sub(r'[*#]', '', text).strip()
            flowables.append(Paragraph(f"<b>{_safe(clean)}</b>", styles['TR_H1']))
            continue
        if stripped.startswith('# '):
            text = stripped[2:]
            clean = re.sub(r'[*#]', '', text).strip()
            flowables.append(Paragraph(f"<b>{_safe(clean)}</b>", styles['TR_H1']))
            continue

        if stripped in ('---', '***', '___'):
            flowables.append(_section_divider())
            continue

        bullet_match = re.match(r'^[-*\u2022]\s+(.+)', stripped)
        if bullet_match:
            text = bullet_match.group(1)
            text = _format_inline(text)
            flowables.append(Paragraph(f"\u2022 {text}", styles['TR_Bullet']))
            continue

        num_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if num_match:
            num = num_match.group(1)
            text = num_match.group(2)
            text = _format_inline(text)
            flowables.append(Paragraph(f"{num}. {text}", styles['TR_Bullet']))
            continue

        text = _format_inline(stripped)
        flowables.append(Paragraph(text, styles['TR_ReportText']))

    return flowables


def _format_inline(text):
    safe = _safe(text)
    safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', safe)
    safe = re.sub(r'\*(.+?)\*', r'<i>\1</i>', safe)
    safe = re.sub(r'`(.+?)`', r'<font color="#E83E8C">\1</font>', safe)
    return safe


def _add_page_number(canvas_obj, doc):
    canvas_obj.saveState()
    page_num = canvas_obj.getPageNumber()
    canvas_obj.setStrokeColor(BORDER)
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(1.5 * cm, 1.2 * cm, A4[0] - 1.5 * cm, 1.2 * cm)
    canvas_obj.setFont(FONT_NAME, 7)
    canvas_obj.setFillColor(HexColor("#6C757D"))
    canvas_obj.drawString(1.5 * cm, 0.8 * cm,
        "E\u011fitim Check-Up | Psikometrik De\u011ferlendirme Raporu")
    canvas_obj.drawRightString(A4[0] - 1.5 * cm, 0.8 * cm, f"Sayfa {page_num}")
    canvas_obj.restoreState()


# ============================================================
# GRAFİK OLUŞTURMA — Matplotlib → ReportLab Image
# ============================================================

def _setup_matplotlib_turkish():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "fonts", "DejaVuSans.ttf")
    if os.path.isfile(font_path):
        from matplotlib import font_manager
        font_manager.fontManager.addfont(font_path)
        bold_path = os.path.join(base_dir, "fonts", "DejaVuSans-Bold.ttf")
        if os.path.isfile(bold_path):
            font_manager.fontManager.addfont(bold_path)
        plt.rcParams['font.family'] = 'DejaVu Sans'
    else:
        plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    return plt


def _create_chart_image(plot_data, title, chart_width_cm=15):
    if not plot_data:
        return None

    plt = _setup_matplotlib_turkish()
    import seaborn as sns

    valid_pairs = []
    for k, v in plot_data.items():
        try:
            val = float(v)
            valid_pairs.append((str(k), val))
        except (ValueError, TypeError):
            continue

    if not valid_pairs:
        return None

    labels = [p[0] for p in valid_pairs]
    values = [p[1] for p in valid_pairs]

    bar_count = len(labels)
    fig_height = max(2.5, bar_count * 0.55 + 1.0)
    fig_width = chart_width_cm / 2.54

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    colors = sns.color_palette("coolwarm", bar_count)
    bars = ax.barh(range(bar_count), values, color=colors, edgecolor='white', height=0.6)

    ax.set_yticks(range(bar_count))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title(title, fontsize=11, fontweight='bold', color='#1B2A4A', pad=10)
    ax.set_xlabel("Puan / Y\u00fczde", fontsize=8, color='#6C757D')
    ax.tick_params(axis='x', labelsize=7)
    ax.invert_yaxis()

    for bar_item, val in zip(bars, values):
        display_val = f"{val:.0f}" if val == int(val) else f"{val:.1f}"
        ax.text(
            bar_item.get_width() + max(values) * 0.02,
            bar_item.get_y() + bar_item.get_height() / 2,
            display_val, va='center', ha='left', fontsize=7,
            color='#1B2A4A', fontweight='bold'
        )

    if values:
        ax.set_xlim(0, max(values) * 1.15)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    img_buffer = io.BytesIO()
    fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    img_buffer.seek(0)
    return img_buffer


def _extract_chart_data(test_name, scores):
    if not scores or not isinstance(scores, dict):
        return None, None

    test_lower = test_name.lower() if test_name else ""
    plot_data = {}

    # Sag-Sol Beyin
    if "beyin" in test_lower or "brain" in test_lower:
        for k, v in scores.items():
            if not isinstance(v, (int, float)):
                continue
            kl = k.lower()
            if "yuzde" in kl or "y\u00fczde" in kl:
                label = "Sa\u011f Beyin %" if ("sag" in kl or "sa\u011f" in kl) else "Sol Beyin %"
                plot_data[label] = v
            elif kl in ("sag_beyin", "sol_beyin", "sa\u011f_beyin", "beyin", "dominant", "level", "version", "id", "user_id"):
                continue
            else:
                plot_data[k] = v
        return plot_data, "Sa\u011f-Sol Beyin Analizi"

    # Calisma Davranisi
    if "al\u0131\u015fma" in test_lower or "calisma" in test_lower or "davran\u0131\u015f" in test_lower:
        if "categories" in scores and isinstance(scores["categories"], dict):
            plot_data = {k: v for k, v in scores["categories"].items() if isinstance(v, (int, float))}
        return plot_data, "\u00c7al\u0131\u015fma Davran\u0131\u015f\u0131 Alt Boyutlar\u0131"

    # Sinav Kaygisi
    if "kayg\u0131" in test_lower or "kaygi" in test_lower or "anxiety" in test_lower:
        if "categories" in scores and isinstance(scores["categories"], dict):
            plot_data = {k: v for k, v in scores["categories"].items() if isinstance(v, (int, float))}
        return plot_data, "S\u0131nav Kayg\u0131s\u0131 Alt Boyutlar\u0131"

    # Coklu Zeka
    if "zeka" in test_lower or "intelligence" in test_lower or "\u00e7oklu" in test_lower or "coklu" in test_lower:
        if "scores" in scores and isinstance(scores["scores"], dict):
            for k, v in scores["scores"].items():
                if isinstance(v, dict) and "pct" in v:
                    plot_data[k] = v["pct"]
                elif isinstance(v, (int, float)):
                    plot_data[k] = v
        return plot_data, "\u00c7oklu Zek\u00e2 Alanlar\u0131"

    # VARK
    if "vark" in test_lower or "\u00f6\u011frenme stili" in test_lower or "ogrenme" in test_lower:
        skip = {"id", "user_id", "total", "max_total", "total_responses", "total_pct", "dominant", "level", "version"}
        for k, v in scores.items():
            if k.lower() in skip:
                continue
            if isinstance(v, (int, float)):
                plot_data[k] = v
        return plot_data, "VARK \u00d6\u011frenme Stilleri"

    # Holland RIASEC
    if "holland" in test_lower or "riasec" in test_lower or "kariyer" in test_lower or "meslek" in test_lower:
        skip = {"id", "user_id", "total", "max_total", "total_responses", "total_pct", "dominant", "level", "version"}
        for k, v in scores.items():
            if k.lower() in skip:
                continue
            if isinstance(v, (int, float)):
                plot_data[k] = v
        return plot_data, "Holland RIASEC Kariyer Profili"

    # Enneagram
    if "enneagram" in test_lower:
        skip = {"id", "user_id", "total", "max_total", "total_responses", "total_pct", "dominant", "dominant_type", "level", "version"}
        for k, v in scores.items():
            if k.lower() in skip:
                continue
            if isinstance(v, (int, float)):
                plot_data[k] = v
        return plot_data, "Enneagram Ki\u015filik Profili"

    # P2 Dikkat Testi
    if "p2" in test_lower or "dikkat" in test_lower or "d2" in test_lower:
        d2_labels = {
            "CP": "Konsantrasyon (CP)",
            "TN_E": "Toplam Performans (TN-E)",
            "TN": "Toplam \u0130\u015faretleme (TN)",
            "E1": "Atlama Hatas\u0131 (E1)",
            "E2": "Yanl\u0131\u015f \u0130\u015faretleme (E2)",
            "FR": "Dalgalanma (FR)",
        }
        for key, label in d2_labels.items():
            if key in scores and isinstance(scores[key], (int, float)):
                plot_data[label] = scores[key]
        return plot_data, "P2 Dikkat Testi Metrikleri"

    # Akademik Analiz
    if "akademik" in test_lower:
        akd_keys = {
            "overall": "Genel Skor",
            "Anlama": "Okuma Anlama",
            "Muhakeme": "Matematiksel Muhakeme",
            "D\u00fc\u015f\u00fcnme": "Mant\u0131ksal D\u00fc\u015f\u00fcnme",
            "\u00d6z-De\u011ferlendirme": "\u00d6z-De\u011ferlendirme",
        }
        for key, label in akd_keys.items():
            if key in scores and isinstance(scores[key], (int, float)):
                plot_data[label] = scores[key]
        return plot_data, "Akademik Analiz Boyutlar\u0131"

    # Hizli Okuma
    if "h\u0131zl\u0131" in test_lower or "hizli" in test_lower or "okuma" in test_lower or "speed" in test_lower:
        reading_keys = {
            "wpm": "Okuma H\u0131z\u0131 (KPD)",
            "reading_speed": "Okuma H\u0131z\u0131",
            "comprehension": "Anlama Oran\u0131 (%)",
            "comprehension_pct": "Anlama (%)",
            "effective_speed": "Etkili Okuma H\u0131z\u0131",
            "effective_wpm": "Etkili KPD",
            "correct_answers": "Do\u011fru Cevap",
            "total_questions": "Toplam Soru",
            "score": "Skor",
        }
        for key, label in reading_keys.items():
            if key in scores and isinstance(scores[key], (int, float)):
                plot_data[label] = scores[key]
        if not plot_data:
            skip = {"id", "user_id", "version", "level", "tier", "passage_id", "time_seconds"}
            for k, v in scores.items():
                if k.lower() in skip:
                    continue
                if isinstance(v, (int, float)):
                    plot_data[k] = v
        return plot_data, "H\u0131zl\u0131 Okuma Performans\u0131"

    # Genel fallback
    skip = {"id", "user_id", "total", "max_total", "total_responses", "total_pct",
            "dominant", "dominant_type", "level", "version", "beyin"}
    if "categories" in scores and isinstance(scores["categories"], dict):
        plot_data = {k: v for k, v in scores["categories"].items() if isinstance(v, (int, float))}
    elif "scores" in scores and isinstance(scores["scores"], dict):
        for k, v in scores["scores"].items():
            if isinstance(v, dict) and "pct" in v:
                plot_data[k] = v["pct"]
            elif isinstance(v, (int, float)):
                plot_data[k] = v
    else:
        for k, v in scores.items():
            if k.lower() in skip:
                continue
            if isinstance(v, (int, float)):
                plot_data[k] = v

    chart_title = test_name if test_name else "Test Sonu\u00e7lar\u0131"
    return plot_data, chart_title


def _create_chart_for_test(test_name, scores, chart_width_cm=15):
    """Belirli bir test için grafik oluştur ve ReportLab Image flowable döndür."""
    plot_data, chart_title = _extract_chart_data(test_name, scores)
    if not plot_data:
        return None

    img_buffer = _create_chart_image(plot_data, chart_title, chart_width_cm)
    if not img_buffer:
        return None

    try:
        from PIL import Image as PILImage
        img_buffer.seek(0)
        pil_img = PILImage.open(img_buffer)
        w_px, h_px = pil_img.size
        aspect = h_px / w_px
        img_width = chart_width_cm * cm
        img_height = img_width * aspect
        img_buffer.seek(0)
        rl_image = Image(img_buffer, width=img_width, height=img_height)
        return rl_image
    except ImportError:
        img_buffer.seek(0)
        bar_count = len(plot_data)
        est_height = max(4, bar_count * 0.55 + 1.5) * cm
        rl_image = Image(img_buffer, width=chart_width_cm * cm, height=est_height)
        return rl_image
    except Exception:
        return None


# ============================================================
# ANA PDF ÜRETİCİ
# ============================================================

def generate_student_pdf(student_data, analysis_history, include_charts=True):
    info = student_data["info"]
    tests = student_data["tests"]
    styles = _get_styles()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        title=f"{info.name} - E\u011fitim Check-Up Raporu",
        author="E\u011fitim Check-Up Sistemi",
    )

    story = []
    now = datetime.now()

    # ── KAPAK ──
    story.append(Spacer(1, 1.5 * cm))

    cover_data = [[
        Paragraph(
            '<b>E\u011e\u0130T\u0130M CHECK-UP</b>',
            ParagraphStyle('cover', fontName=FONT_BOLD, fontSize=24, textColor=PRIMARY, alignment=TA_CENTER)
        )
    ]]
    cover_table = Table(cover_data, colWidths=[17.5 * cm])
    cover_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('LINEBELOW', (0, 0), (-1, -1), 2, PRIMARY),
        ('LINEABOVE', (0, 0), (-1, -1), 2, PRIMARY),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Ki\u015fisel E\u011fitim &amp; Kariyer Analiz Merkezi", styles['TR_Subtitle']))
    story.append(Spacer(1, 1 * cm))

    story.append(Paragraph(
        f"<b>{_safe(info.name)}</b>",
        ParagraphStyle('name', fontName=FONT_BOLD, fontSize=18, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6)
    ))
    story.append(Paragraph("Psikometrik De\u011ferlendirme Raporu", styles['TR_Subtitle']))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph(
        f"Rapor Tarihi: {now.strftime('%d.%m.%Y %H:%M')}",
        ParagraphStyle('date', fontName=FONT_NAME, fontSize=10, textColor=HexColor("#6C757D"), alignment=TA_CENTER)
    ))
    story.append(PageBreak())

    # ── BÖLÜM 1: ÖĞRENCİ PROFİLİ ──
    story.append(_header_bar("B\u00d6L\u00dcM 1: \u00d6\u011eRENC\u0130 PROF\u0130L\u0130", styles))
    story.append(Spacer(1, 8))

    grade_val = getattr(info, 'grade', None)
    grade_text = f"{grade_val}. S\u0131n\u0131f" if grade_val else "Belirtilmemi\u015f"

    profile_rows = [
        ["Ad Soyad", str(info.name)],
        ["Ya\u015f", str(info.age)],
        ["Cinsiyet", str(info.gender)],
        ["S\u0131n\u0131f", grade_text],
        ["E-posta / Kullan\u0131c\u0131", str(info.username)],
        ["Toplam Giri\u015f", str(info.login_count)],
        ["\u00c7\u00f6z\u00fclen Test Say\u0131s\u0131", str(len(tests))],
    ]

    profile_table_data = []
    for label, value in profile_rows:
        profile_table_data.append([
            Paragraph(f"<b>{_safe(label)}</b>", styles['TR_TableCell']),
            Paragraph(_safe(value), styles['TR_TableCell']),
        ])

    profile_table = Table(profile_table_data, colWidths=[5 * cm, 12.5 * cm])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), BG_LIGHT),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(profile_table)

    if tests:
        story.append(Spacer(1, 12))
        story.append(Paragraph("<b>Tamamlanan Testler:</b>", styles['TR_H2']))

        test_summary_data = [[
            Paragraph("<b>No</b>", styles['TR_TableHeader']),
            Paragraph("<b>Test Ad\u0131</b>", styles['TR_TableHeader']),
            Paragraph("<b>Tarih</b>", styles['TR_TableHeader']),
        ]]
        for i, t in enumerate(tests, 1):
            test_summary_data.append([
                Paragraph(str(i), styles['TR_TableCellCenter']),
                Paragraph(_safe(t["test_name"]), styles['TR_TableCell']),
                Paragraph(str(t.get("date", "-")), styles['TR_TableCellCenter']),
            ])

        test_table = Table(test_summary_data, colWidths=[1.5 * cm, 11 * cm, 5 * cm])
        test_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, BG_LIGHT]),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(test_table)

    story.append(PageBreak())

    # ── BÖLÜM 2: TEST SONUÇLARI ──
    story.append(_header_bar("B\u00d6L\u00dcM 2: TEST SONU\u00c7LARI VE PUAN DETAYLARI", styles))
    story.append(Spacer(1, 8))

    if not tests:
        story.append(Paragraph("Hen\u00fcz test sonucu bulunmamaktad\u0131r.", styles['TR_Body']))
    else:
        for idx, t in enumerate(tests):
            test_title_data = [[
                Paragraph(
                    f"<b>{idx+1}. {_safe(t['test_name'])}</b> &nbsp; | &nbsp; Tarih: {t.get('date', '-')}",
                    ParagraphStyle('th', fontName=FONT_BOLD, fontSize=9.5, textColor=white, alignment=TA_LEFT)
                )
            ]]
            test_title_table = Table(test_title_data, colWidths=[17.5 * cm])
            test_title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), SECONDARY),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(Spacer(1, 8))
            story.append(test_title_table)
            story.append(Spacer(1, 6))

            if t.get("scores") and isinstance(t["scores"], dict):
                scores = t["scores"]
                score_data = [[
                    Paragraph("<b>\u00d6l\u00e7ek / Boyut</b>", styles['TR_TableHeader']),
                    Paragraph("<b>Puan / De\u011fer</b>", styles['TR_TableHeader']),
                ]]
                for k, v in scores.items():
                    score_data.append([
                        Paragraph(_safe(str(k)), styles['TR_TableCell']),
                        Paragraph(_safe(str(v)), styles['TR_TableCellCenter']),
                    ])

                score_table = Table(score_data, colWidths=[10 * cm, 7.5 * cm])
                score_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
                    ('TEXTCOLOR', (0, 0), (-1, 0), white),
                    ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, BG_LIGHT]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(score_table)
                story.append(Spacer(1, 6))

                # GRAFİK EKLE
                if include_charts:
                    try:
                        chart_image = _create_chart_for_test(t['test_name'], scores)
                        if chart_image:
                            story.append(Spacer(1, 4))
                            story.append(chart_image)
                            story.append(Spacer(1, 6))
                    except Exception:
                        pass

            report_text = t.get("report", "")
            if report_text:
                story.append(Paragraph("<b>Sistem Raporu:</b>", styles['TR_H3']))
                report_flowables = _markdown_to_flowables(report_text, styles)
                story.extend(report_flowables)

            story.append(_section_divider())

    story.append(PageBreak())

    # ── BÖLÜM 3: AI ANALİZ RAPORLARI ──
    story.append(_header_bar("B\u00d6L\u00dcM 3: AI DESTEKL\u0130 ANAL\u0130Z RAPORLARI (Claude)", styles))
    story.append(Spacer(1, 8))

    if not analysis_history:
        story.append(Paragraph(
            "Bu \u00f6\u011frenci i\u00e7in hen\u00fcz AI destekli analiz raporu olu\u015fturulmam\u0131\u015ft\u0131r.",
            styles['TR_Body']
        ))
    else:
        story.append(Paragraph(
            f"Toplam <b>{len(analysis_history)}</b> adet AI analiz raporu bulunmaktad\u0131r.",
            styles['TR_Body']
        ))
        story.append(Spacer(1, 8))

        for idx, record in enumerate(analysis_history):
            combo = record.get('combination', 'Bilinmiyor')
            date = record.get('date', '-')

            report_header_data = [[
                Paragraph(
                    f"<b>AI Rapor {idx+1}: {_safe(combo)}</b> &nbsp; | &nbsp; {date}",
                    ParagraphStyle('rh', fontName=FONT_BOLD, fontSize=9.5, textColor=white, alignment=TA_LEFT)
                )
            ]]
            report_header = Table(report_header_data, colWidths=[17.5 * cm])
            report_header.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), ACCENT),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(report_header)
            story.append(Spacer(1, 6))

            report_content = record.get('report', '')
            if report_content:
                flowables = _markdown_to_flowables(report_content, styles)
                story.extend(flowables)
            else:
                story.append(Paragraph("<i>Rapor i\u00e7eri\u011fi bo\u015f.</i>", styles['TR_Body']))

            story.append(Spacer(1, 8))
            story.append(_section_divider())

            if idx < len(analysis_history) - 1:
                story.append(PageBreak())

    # ── FOOTER NOTU ──
    story.append(Spacer(1, 1 * cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=8))

    disclaimer = (
        "Bu rapor, E\u011e\u0130T\u0130M CHECK-UP psikometrik de\u011ferlendirme sistemi taraf\u0131ndan, "
        "yapay zek\u00e2 destekli analiz altyap\u0131s\u0131yla \u00fcretilmi\u015ftir. Raporda yer alan "
        "t\u00fcm yorumlar, \u00f6\u011frencinin psikometrik test verilerine dayanmaktad\u0131r. "
        "Bu rapor klinik tan\u0131 i\u00e7ermez ve klinik de\u011ferlendirme yerine ge\u00e7mez."
    )
    story.append(Paragraph(disclaimer, styles['TR_Small']))
    story.append(Paragraph(
        f"Rapor \u00fcretim tarihi: {now.strftime('%d.%m.%Y %H:%M')} | E\u011fitim Check-Up v2.1",
        styles['TR_Small']
    ))

    doc.build(story, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    buffer.seek(0)
    return buffer


def generate_student_pdf_filename(student_name):
    safe_name = student_name.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"{safe_name}_Rapor_{timestamp}.pdf"

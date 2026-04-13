"""
Eğitim Check-Up — Sınıf & Okul Analitik Dashboard
Faz 3: Karşılaştırma, ısı haritası, risk dağılımı, KPI, rehberlik raporu
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
from datetime import datetime, timedelta
from collections import defaultdict

# ── Test listesi (kısa adlar) ──
TEST_SHORT = {
    "Enneagram Kişilik Testi": "Enneagram",
    "Çalışma Davranışı Ölçeği": "Çalışma Dav.",
    "Sağ-Sol Beyin Dominansı Testi": "Beyin Dom.",
    "Sınav Kaygısı Ölçeği": "Sınav Kaygısı",
    "VARK Öğrenme Stilleri Testi": "VARK",
    "Çoklu Zeka Testi": "Çoklu Zeka",
    "Holland Mesleki İlgi Envanteri": "Holland",
    "P2 Dikkat Testi": "P2 Dikkat",
    "Akademik Analiz Testi": "Akademik",
    "Hızlı Okuma Testi": "Hızlı Okuma",
}

ALL_TESTS = list(TEST_SHORT.keys())

# ── Norm tablosu (referans değerler — sınıf bazlı) ──
NORM_TABLE = {
    "Sınav Kaygısı Ölçeği": {"low": 15, "mid": 25, "high": 35},
    "Çalışma Davranışı Ölçeği": {"low": 30, "mid": 50, "high": 70},
    "Akademik Analiz Testi": {"low": 25, "mid": 50, "high": 75},
    "P2 Dikkat Testi": {"low": 50, "mid": 100, "high": 150},
    "Hızlı Okuma Testi": {"low": 80, "mid": 150, "high": 220},
}


# ════════════════════════════════════════════════════════════
# VERİ HAZIRLAMA
# ════════════════════════════════════════════════════════════

def _extract_main_score(scores_dict, test_name):
    """Test sonuçlarından ana puanı çıkar (0-100 arası normalize)."""
    if not scores_dict:
        return None
    # Farklı testlerin farklı skor yapıları var
    if "toplam_puan" in scores_dict:
        return scores_dict["toplam_puan"]
    if "total_score" in scores_dict:
        return scores_dict["total_score"]
    if "puan" in scores_dict:
        return scores_dict["puan"]
    if "TN_E" in scores_dict:  # P2 Dikkat — normalize et
        tn_e = scores_dict.get("TN_E", 0)
        return min(100, max(0, round(tn_e / 2)))
    if "wpm" in scores_dict:  # Hızlı Okuma
        return min(100, max(0, round(scores_dict["wpm"] / 2.5)))
    if "dominant_tip" in scores_dict:  # Enneagram — dominant tip puanı
        return scores_dict.get("max_puan", 50)
    if "R" in scores_dict and "I" in scores_dict:  # Holland RIASEC
        return max(scores_dict.get("R", 0), scores_dict.get("I", 0),
                   scores_dict.get("A", 0), scores_dict.get("S", 0),
                   scores_dict.get("E", 0), scores_dict.get("C", 0))
    if "V" in scores_dict and "A" in scores_dict and "K" in scores_dict:  # VARK
        return max(scores_dict.values()) if scores_dict.values() else 50
    if "sol_beyin" in scores_dict:  # Sağ-Sol Beyin
        return max(scores_dict.get("sol_beyin", 0), scores_dict.get("sag_beyin", 0))
    # Fallback: ortalama al
    numeric_vals = [v for v in scores_dict.values() if isinstance(v, (int, float))]
    return round(sum(numeric_vals) / len(numeric_vals)) if numeric_vals else None


def prepare_dataframe(all_data):
    """get_all_students_with_results verisini DataFrame'e çevir."""
    rows = []
    for student_data in all_data:
        info = student_data["info"]
        for test in student_data["tests"]:
            try:
                scores = test["scores"] if isinstance(test["scores"], dict) else json.loads(test["scores"]) if test["scores"] else {}
            except (json.JSONDecodeError, TypeError):
                scores = {}
            main_score = _extract_main_score(scores, test["test_name"])
            rows.append({
                "student_id": info.id,
                "student_name": info.name,
                "age": info.age,
                "gender": info.gender,
                "grade": str(info.grade) if info.grade else "Belirtilmemiş",
                "test_name": test["test_name"],
                "test_short": TEST_SHORT.get(test["test_name"], test["test_name"][:12]),
                "score": main_score,
                "date": test["date"],
                "scores_raw": scores,
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ════════════════════════════════════════════════════════════
# SINIF KARŞILAŞTIRMA
# ════════════════════════════════════════════════════════════

def render_class_comparison(df):
    """Sınıf bazlı karşılaştırma — radar chart + bar chart."""
    st.markdown("### 📊 Sınıf Karşılaştırma")

    if df.empty or "grade" not in df.columns:
        st.info("Karşılaştırma için yeterli veri yok.")
        return

    grades = sorted(df["grade"].unique())
    if len(grades) < 2:
        st.info("Karşılaştırma için en az 2 farklı sınıf gerekli.")
        return

    selected_grades = st.multiselect("Karşılaştırılacak sınıfları seçin:", grades, default=grades[:3], key="cmp_grades")
    if len(selected_grades) < 2:
        st.warning("En az 2 sınıf seçin.")
        return

    filtered = df[df["grade"].isin(selected_grades) & df["score"].notna()]
    pivot = filtered.groupby(["grade", "test_short"])["score"].mean().reset_index()

    # ── Radar Chart ──
    fig_radar = go.Figure()
    colors = px.colors.qualitative.Set2
    for i, grade in enumerate(selected_grades):
        grade_data = pivot[pivot["grade"] == grade]
        tests = grade_data["test_short"].tolist()
        scores = grade_data["score"].tolist()
        if tests:
            tests_closed = tests + [tests[0]]
            scores_closed = scores + [scores[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=scores_closed, theta=tests_closed,
                fill='toself', name=f"Sınıf {grade}",
                line=dict(color=colors[i % len(colors)]),
                opacity=0.7,
            ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Sınıf Bazlı Test Ortalamaları (Radar)",
        height=450, showlegend=True,
        font=dict(family="DM Sans, sans-serif"),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # ── Bar Chart ──
    fig_bar = px.bar(
        pivot, x="test_short", y="score", color="grade",
        barmode="group", title="Sınıf Bazlı Test Ortalamaları (Bar)",
        labels={"test_short": "Test", "score": "Ortalama Puan", "grade": "Sınıf"},
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=400,
    )
    fig_bar.update_layout(font=dict(family="DM Sans, sans-serif"))
    st.plotly_chart(fig_bar, use_container_width=True)


# ════════════════════════════════════════════════════════════
# ISI HARİTASI
# ════════════════════════════════════════════════════════════

def render_heatmap(df):
    """Okul geneli ısı haritası — sınıf × test matrisi."""
    st.markdown("### 🌡️ Okul Geneli Isı Haritası")

    if df.empty:
        st.info("Isı haritası için yeterli veri yok.")
        return

    filtered = df[df["score"].notna()]
    pivot = filtered.pivot_table(values="score", index="grade", columns="test_short", aggfunc="mean")

    if pivot.empty:
        st.info("Yeterli veri yok.")
        return

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[f"Sınıf {g}" for g in pivot.index.tolist()],
        colorscale=[
            [0, "#DC2626"],      # Kırmızı (düşük)
            [0.3, "#F59E0B"],    # Sarı
            [0.5, "#FBBF24"],    # Açık sarı
            [0.7, "#10B981"],    # Yeşil
            [1, "#059669"],      # Koyu yeşil (yüksek)
        ],
        text=pivot.values.round(1),
        texttemplate="%{text}",
        textfont=dict(size=12, color="white"),
        hovertemplate="Sınıf: %{y}<br>Test: %{x}<br>Ortalama: %{z:.1f}<extra></extra>",
        colorbar=dict(title="Puan"),
    ))
    fig.update_layout(
        title="Sınıf × Test Ortalama Puan Matrisi",
        xaxis_title="Test", yaxis_title="Sınıf",
        height=max(300, len(pivot) * 60 + 120),
        font=dict(family="DM Sans, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# RİSK DAĞILIMI
# ════════════════════════════════════════════════════════════

def _classify_risk(score):
    if score is None:
        return "Veri Yok"
    if score >= 70:
        return "Sağlıklı"
    if score >= 40:
        return "İzlenmeli"
    return "Kritik"

def render_risk_distribution(df):
    """Risk dağılım grafiği — kritik/izlenmeli/sağlıklı."""
    st.markdown("### ⚠️ Risk Dağılımı")

    if df.empty:
        st.info("Risk analizi için yeterli veri yok.")
        return

    # Öğrenci bazlı ortalama skor
    student_avg = df[df["score"].notna()].groupby(["student_id", "student_name", "grade"])["score"].mean().reset_index()
    student_avg["risk"] = student_avg["score"].apply(_classify_risk)

    # ── Pasta Grafik ──
    risk_counts = student_avg["risk"].value_counts().reset_index()
    risk_counts.columns = ["Durum", "Öğrenci Sayısı"]

    color_map = {"Sağlıklı": "#10B981", "İzlenmeli": "#F59E0B", "Kritik": "#DC2626", "Veri Yok": "#94A3B8"}

    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(
            risk_counts, names="Durum", values="Öğrenci Sayısı",
            color="Durum", color_discrete_map=color_map,
            title="Genel Risk Dağılımı", hole=0.4,
        )
        fig_pie.update_layout(font=dict(family="DM Sans, sans-serif"), height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Sınıf bazlı risk kırılımı
        grade_risk = student_avg.groupby(["grade", "risk"]).size().reset_index(name="count")
        fig_stack = px.bar(
            grade_risk, x="grade", y="count", color="risk",
            color_discrete_map=color_map,
            title="Sınıf Bazlı Risk Dağılımı",
            labels={"grade": "Sınıf", "count": "Öğrenci", "risk": "Durum"},
            barmode="stack",
        )
        fig_stack.update_layout(font=dict(family="DM Sans, sans-serif"), height=350)
        st.plotly_chart(fig_stack, use_container_width=True)

    # Kritik öğrenci listesi
    critical = student_avg[student_avg["risk"] == "Kritik"].sort_values("score")
    if not critical.empty:
        st.markdown("#### 🚨 Kritik Seviyedeki Öğrenciler")
        for _, row in critical.iterrows():
            st.markdown(f"- **{row['student_name']}** (Sınıf {row['grade']}) — Ort. Puan: **{row['score']:.0f}**")


# ════════════════════════════════════════════════════════════
# CİNSİYET & YAŞ KIRILIMI
# ════════════════════════════════════════════════════════════

def render_demographic_breakdown(df):
    """Cinsiyet ve yaş kırılımı filtreleme."""
    st.markdown("### 👥 Cinsiyet & Yaş Kırılımı")

    if df.empty:
        st.info("Demografik analiz için yeterli veri yok.")
        return

    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        gender_filter = st.multiselect("Cinsiyet:", df["gender"].dropna().unique().tolist(),
                                        default=df["gender"].dropna().unique().tolist(), key="demo_gender")
    with col_filter2:
        age_range = st.slider("Yaş Aralığı:", int(df["age"].min()), int(df["age"].max()),
                              (int(df["age"].min()), int(df["age"].max())), key="demo_age")

    filtered = df[(df["gender"].isin(gender_filter)) & (df["age"].between(*age_range)) & (df["score"].notna())]

    if filtered.empty:
        st.warning("Seçili filtrelere uygun veri bulunamadı.")
        return

    # Cinsiyet karşılaştırma
    gender_avg = filtered.groupby(["gender", "test_short"])["score"].mean().reset_index()
    fig_gender = px.bar(
        gender_avg, x="test_short", y="score", color="gender",
        barmode="group", title="Cinsiyet Bazlı Test Ortalamaları",
        labels={"test_short": "Test", "score": "Ortalama Puan", "gender": "Cinsiyet"},
        color_discrete_map={"Erkek": "#2563EB", "Kız": "#EC4899", "Kadın": "#EC4899"},
        height=400,
    )
    fig_gender.update_layout(font=dict(family="DM Sans, sans-serif"))
    st.plotly_chart(fig_gender, use_container_width=True)

    # Yaş dağılımı — scatter
    age_avg = filtered.groupby(["age", "test_short"])["score"].mean().reset_index()
    fig_age = px.scatter(
        age_avg, x="age", y="score", color="test_short", size="score",
        title="Yaş Bazlı Test Performansı",
        labels={"age": "Yaş", "score": "Ortalama Puan", "test_short": "Test"},
        height=400,
    )
    fig_age.update_layout(font=dict(family="DM Sans, sans-serif"))
    st.plotly_chart(fig_age, use_container_width=True)


# ════════════════════════════════════════════════════════════
# YÖNETİCİ KPI KARTLARI
# ════════════════════════════════════════════════════════════

def render_kpi_cards(df, all_data):
    """6 KPI metrik kartı + 14 günlük trend."""
    st.markdown("### 📈 Yönetici Özet Paneli")

    total_students = len(all_data) if all_data else 0
    total_tests_completed = len(df) if not df.empty else 0
    unique_tests = df["test_name"].nunique() if not df.empty else 0

    # Ortalama puan
    avg_score = df["score"].mean() if not df.empty and df["score"].notna().any() else 0

    # Tamamlama oranı
    if total_students > 0 and not df.empty:
        students_completed_all = 0
        for sd in all_data:
            completed = set(t["test_name"] for t in sd["tests"])
            if len(completed) >= len(ALL_TESTS):
                students_completed_all += 1
        completion_rate = round(students_completed_all / total_students * 100)
    else:
        completion_rate = 0
        students_completed_all = 0

    # Risk oranı
    if not df.empty and df["score"].notna().any():
        student_avg = df[df["score"].notna()].groupby("student_id")["score"].mean()
        critical_count = (student_avg < 40).sum()
        risk_rate = round(critical_count / len(student_avg) * 100) if len(student_avg) > 0 else 0
    else:
        critical_count = 0
        risk_rate = 0

    # ── KPI Kartları ──
    kpis = [
        {"icon": "👨‍🎓", "value": total_students, "label": "Toplam Öğrenci", "color": "#2563EB", "bg": "rgba(37,99,235,0.08)"},
        {"icon": "📝", "value": total_tests_completed, "label": "Çözülen Test", "color": "#10B981", "bg": "rgba(16,185,129,0.08)"},
        {"icon": "📊", "value": f"{avg_score:.0f}", "label": "Ortalama Puan", "color": "#8B5CF6", "bg": "rgba(139,92,246,0.08)"},
        {"icon": "✅", "value": f"%{completion_rate}", "label": "Tamamlama Oranı", "color": "#06B6D4", "bg": "rgba(6,182,212,0.08)"},
        {"icon": "⚠️", "value": critical_count, "label": "Kritik Öğrenci", "color": "#DC2626", "bg": "rgba(220,38,38,0.08)"},
        {"icon": "📉", "value": f"%{risk_rate}", "label": "Risk Oranı", "color": "#F59E0B", "bg": "rgba(245,158,11,0.08)"},
    ]

    cols = st.columns(3)
    for i, kpi in enumerate(kpis):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="glass-stat-card scroll-reveal delay-{i % 4}" style="--card-accent: {kpi['color']}; --card-accent-end: {kpi['color']}; margin-bottom: 12px;">
                    <div class="stat-icon" style="background: {kpi['bg']};">{kpi['icon']}</div>
                    <div class="stat-value">{kpi['value']}</div>
                    <div class="stat-label">{kpi['label']}</div>
                </div>
            """, unsafe_allow_html=True)

    # ── 14 Günlük Trend ──
    if not df.empty and "date" in df.columns:
        st.markdown("#### 📅 Son 14 Gün — Test Aktivitesi")
        df_dated = df[df["date"].astype(str) != ""].copy()
        if not df_dated.empty:
            try:
                df_dated["date_parsed"] = pd.to_datetime(df_dated["date"], errors="coerce")
                df_dated = df_dated.dropna(subset=["date_parsed"])
                cutoff = datetime.now() - timedelta(days=14)
                recent = df_dated[df_dated["date_parsed"] >= cutoff]
                if not recent.empty:
                    daily = recent.groupby(recent["date_parsed"].dt.date).size().reset_index(name="test_count")
                    daily.columns = ["Tarih", "Test Sayısı"]
                    fig_trend = px.area(
                        daily, x="Tarih", y="Test Sayısı",
                        title="Günlük Çözülen Test Sayısı (Son 14 Gün)",
                        color_discrete_sequence=["#2563EB"],
                        height=280,
                    )
                    fig_trend.update_layout(font=dict(family="DM Sans, sans-serif"))
                    st.plotly_chart(fig_trend, use_container_width=True)
                else:
                    st.caption("Son 14 günde test aktivitesi yok.")
            except Exception:
                st.caption("Tarih verisi analiz edilemedi.")


# ════════════════════════════════════════════════════════════
# DÖNEM SONU REHBERLİK RAPORU (PDF)
# ════════════════════════════════════════════════════════════

def render_semester_report(df, all_data):
    """MEB formatında dönem sonu rehberlik raporu PDF üretimi."""
    st.markdown("### 📄 Dönem Sonu Rehberlik Raporu")
    st.caption("MEB formatında, tüm sınıfları kapsayan özet PDF raporu oluşturur.")

    if df.empty:
        st.info("Rapor için yeterli veri yok.")
        return

    selected_grade = st.selectbox("Rapor oluşturulacak sınıf:", sorted(df["grade"].unique()), key="rpt_grade")

    if st.button("📄 PDF Raporu Oluştur", type="primary", key="gen_report"):
        with st.spinner("Rapor oluşturuluyor..."):
            pdf_buffer = _generate_semester_pdf(df, all_data, selected_grade)
            if pdf_buffer:
                timestamp = datetime.now().strftime("%Y%m%d")
                st.download_button(
                    label="📥 PDF İndir",
                    data=pdf_buffer,
                    file_name=f"Rehberlik_Raporu_Sinif{selected_grade}_{timestamp}.pdf",
                    mime="application/pdf",
                    key="dl_semester_pdf"
                )
                st.success("Rapor başarıyla oluşturuldu!")


def _generate_semester_pdf(df, all_data, grade):
    """ReportLab ile MEB formatında PDF oluştur."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # Font — DejaVu Sans Türkçe desteği
        font_name = "Helvetica"
        for fpath in ["DejaVuSans.ttf", "fonts/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            if os.path.exists(fpath):
                pdfmetrics.registerFont(TTFont("DejaVuSans", fpath))
                font_name = "DejaVuSans"
                break
        for fpath in ["DejaVuSans-Bold.ttf", "fonts/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            if os.path.exists(fpath):
                pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", fpath))
                break

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("Title_TR", parent=styles["Title"], fontName=font_name, fontSize=16,
                                      spaceAfter=12, alignment=1)
        heading_style = ParagraphStyle("Heading_TR", parent=styles["Heading2"], fontName=font_name, fontSize=12,
                                        spaceAfter=8, spaceBefore=14)
        body_style = ParagraphStyle("Body_TR", parent=styles["Normal"], fontName=font_name, fontSize=10,
                                     leading=14, spaceAfter=6)

        elements = []

        # Başlık
        elements.append(Paragraph("EGITIM CHECK-UP", title_style))
        elements.append(Paragraph(f"Donem Sonu Rehberlik Raporu - Sinif {grade}", heading_style))
        elements.append(Paragraph(f"Tarih: {datetime.now().strftime('%d.%m.%Y')}", body_style))
        elements.append(Spacer(1, 0.5*cm))

        # Sınıf istatistikleri
        grade_df = df[df["grade"] == str(grade)]
        grade_students = grade_df["student_id"].nunique()
        grade_tests = len(grade_df)
        grade_avg = grade_df["score"].mean() if grade_df["score"].notna().any() else 0

        elements.append(Paragraph("1. SINIF GENEL DURUMU", heading_style))
        stats_data = [
            ["Metrik", "Deger"],
            ["Ogrenci Sayisi", str(grade_students)],
            ["Cozulen Test", str(grade_tests)],
            ["Ortalama Puan", f"{grade_avg:.1f}"],
        ]
        stats_table = Table(stats_data, colWidths=[8*cm, 6*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*cm))

        # Test bazlı ortalamalar
        elements.append(Paragraph("2. TEST BAZLI ORTALAMALAR", heading_style))
        test_avgs = grade_df[grade_df["score"].notna()].groupby("test_short")["score"].mean()
        if not test_avgs.empty:
            test_data = [["Test", "Ortalama", "Durum"]]
            for test_name, avg_score in test_avgs.items():
                status = "Iyi" if avg_score >= 70 else "Orta" if avg_score >= 40 else "Dusuk"
                test_data.append([str(test_name), f"{avg_score:.1f}", status])
            test_table = Table(test_data, colWidths=[6*cm, 4*cm, 4*cm])
            test_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1B2A4A")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(test_table)
        elements.append(Spacer(1, 0.5*cm))

        # Risk analizi
        elements.append(Paragraph("3. RISK ANALIZI", heading_style))
        student_avgs = grade_df[grade_df["score"].notna()].groupby("student_name")["score"].mean()
        critical_students = student_avgs[student_avgs < 40]
        watch_students = student_avgs[(student_avgs >= 40) & (student_avgs < 70)]

        elements.append(Paragraph(f"Kritik seviyede {len(critical_students)} ogrenci, izlenmesi gereken {len(watch_students)} ogrenci bulunmaktadir.", body_style))

        if not critical_students.empty:
            elements.append(Paragraph("Kritik ogrenciler:", body_style))
            for name, score in critical_students.items():
                elements.append(Paragraph(f"  - {name}: Ortalama {score:.0f} puan", body_style))

        elements.append(Spacer(1, 0.5*cm))
        elements.append(Paragraph("4. ONERILER", heading_style))
        elements.append(Paragraph("- Kritik seviyedeki ogrenciler icin bireysel rehberlik gorusmesi planlanmalidir.", body_style))
        elements.append(Paragraph("- Sinav kaygisi yuksek ogrencilere gevSeme teknikleri egitimi verilebilir.", body_style))
        elements.append(Paragraph("- Dusuk dikkat puanli ogrenciler icin odaklanma egzersizleri onerilmektedir.", body_style))
        elements.append(Paragraph("- Veli bilgilendirme toplantisi duzenlenmesi tavsiye edilir.", body_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"PDF oluşturma hatası: {e}")
        return None


# ════════════════════════════════════════════════════════════
# NORM TABLOSU
# ════════════════════════════════════════════════════════════

def render_norm_table(df):
    """Norm tablosu — referans değerlerle karşılaştırma."""
    st.markdown("### 📏 Norm Tablosu")
    st.caption("Test sonuçlarını referans değerlerle karşılaştırın.")

    if df.empty:
        st.info("Norm karşılaştırması için veri yok.")
        return

    norm_data = []
    for test_name, norms in NORM_TABLE.items():
        test_df = df[df["test_name"] == test_name]
        if test_df["score"].notna().any():
            avg = test_df["score"].mean()
            short = TEST_SHORT.get(test_name, test_name[:12])
            if avg >= norms["high"]:
                level = "🟢 Yüksek"
            elif avg >= norms["mid"]:
                level = "🟡 Orta"
            else:
                level = "🔴 Düşük"
            norm_data.append({
                "Test": short,
                "Okul Ort.": f"{avg:.1f}",
                "Düşük Ref.": norms["low"],
                "Orta Ref.": norms["mid"],
                "Yüksek Ref.": norms["high"],
                "Seviye": level,
            })

    if norm_data:
        st.dataframe(pd.DataFrame(norm_data), use_container_width=True, hide_index=True)
    else:
        st.info("Norm karşılaştırması yapılabilecek test sonucu bulunamadı.")


# ════════════════════════════════════════════════════════════
# ANA RENDER FONKSİYONU
# ════════════════════════════════════════════════════════════

def render_analytics_dashboard(all_data):
    """Analitik dashboard'un tamamını render eder."""
    st.markdown("## 📊 Sınıf & Okul Analitik Dashboard")
    st.caption("Sınıf karşılaştırma, ısı haritası, risk analizi ve KPI metrikleri")

    if not all_data:
        st.info("Analitik dashboard için henüz öğrenci verisi yok. Öğrenciler test çözdükçe burada analiz göreceksiniz.")
        return

    df = prepare_dataframe(all_data)
    if df.empty:
        st.info("Analitik dashboard için henüz test sonucu yok.")
        return

    # KPI Kartları — en üstte
    render_kpi_cards(df, all_data)

    st.markdown("---")

    # Sekmeler
    tab_cmp, tab_heat, tab_risk, tab_demo, tab_norm, tab_report = st.tabs([
        "📊 Sınıf Karşılaştırma",
        "🌡️ Isı Haritası",
        "⚠️ Risk Dağılımı",
        "👥 Cinsiyet & Yaş",
        "📏 Norm Tablosu",
        "📄 Dönem Raporu",
    ])

    with tab_cmp:
        render_class_comparison(df)
    with tab_heat:
        render_heatmap(df)
    with tab_risk:
        render_risk_distribution(df)
    with tab_demo:
        render_demographic_breakdown(df)
    with tab_norm:
        render_norm_table(df)
    with tab_report:
        render_semester_report(df, all_data)

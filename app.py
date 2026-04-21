import streamlit as st
import time
import os
import base64

from db_utils import init_db, login_student, register_student, reset_student_password, repair_database, get_all_teachers, authenticate_teacher, get_db_diagnostics, bootstrap_first_teacher

st.set_page_config(
    page_title="EĞİTİM CHECK UP",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()

@st.cache_data
def get_logo_base64():
    for fname in ["logo.png", "logo.jpeg", "logo.jpg", "assets/logo.png", "assets/logo.jpeg"]:
        if os.path.exists(fname):
            with open(fname, "rb") as f:
                data = base64.b64encode(f.read()).decode()
            ext = fname.rsplit(".", 1)[-1]
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{data}"
    return None


# =========================================================
# 🎨 PREMIUM TASARIM SİSTEMİ
# =========================================================
st.markdown("""
<meta name="color-scheme" content="light only">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    :root, [data-theme="dark"], [data-theme="light"] {
        --navy: #0F1B2D;
        --blue: #2563EB;
        --blue-light: #3B82F6;
        --cyan: #06B6D4;
        --red: #DC2626;
        --red-soft: #EF4444;
        --gold: #F59E0B;
        --emerald: #10B981;
        --surface: #FFFFFF;
        --surface-alt: #F8FAFC;
        --border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;
        --radius: 14px;
        --shadow-sm: 0 1px 3px rgba(15,23,42,0.06);
        --shadow-md: 0 4px 16px rgba(15,23,42,0.08);
        --shadow-lg: 0 12px 40px rgba(15,23,42,0.12);
        color-scheme: light only !important;
    }

    /* ===== STREAMLIT DARK TEMA TAM OVERRIDE ===== */
    .stApp,
    .stApp [data-theme="dark"],
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    .main .block-container {
        background: #F8FAFC !important;
        color: #0F172A !important;
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color-scheme: light only !important;
    }
    .stApp p, .stApp span, .stApp label, .stApp li, .stApp td, .stApp th,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp [data-testid="stMarkdownContainer"],
    .stApp [data-testid="stMarkdownContainer"] p,
    .stApp [data-testid="stMarkdownContainer"] span,
    .stApp [data-testid="stWidgetLabel"],
    .stApp [data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
    }
    .stApp input, .stApp textarea, .stApp select,
    .stApp [data-baseweb="select"] span,
    .stApp [data-baseweb="input"] input {
        color: #0F172A !important;
        background-color: #FFFFFF !important;
    }
    /* Hero gradient text — güvenli fallback */
    .hero-title {
        color: #0F1B2D !important;
        -webkit-text-fill-color: #0F1B2D;
    }
    @supports (-webkit-background-clip: text) {
        .hero-title {
            -webkit-text-fill-color: transparent;
        }
    }
    /* Açık renkli label'lar — görünür ama hafif */
    .test-card-desc, .test-card-meta, .test-card-meta span,
    .stat-label, .sub-header, .section-desc,
    .field-group-title, .info-box-text {
        color: #555 !important;
    }
    .hero-subtitle { color: #475569 !important; }
    /* Motivasyon kutusu — beyaz metin dark bg üzerinde */
    .motivation-box, .motivation-box h3, .motivation-box p { color: #FFFFFF !important; }
    /* Sidebar istisna — sidebar dark kalacak */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }
    /* Butonlar istisna */
    .stApp button[kind="primary"],
    .stApp button[data-testid="stFormSubmitButton"],
    .stApp .stButton > button[type="primary"] {
        color: white !important;
    }
    /* Badge'ler — kendi renklerini korusun */
    .badge-done { color: #155724 !important; }
    .badge-ready { color: #0c5460 !important; }
    .report-header { color: #155724 !important; }
    /* Alert/notification istisna */
    .stApp .stAlert p,
    .stApp [data-testid="stNotification"] p,
    .stApp .stSuccess p, .stApp .stWarning p, .stApp .stError p, .stApp .stInfo p {
        color: inherit !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* ===== ANİMASYONLAR ===== */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(24px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes pulse-ring {
        0%, 100% { transform: scale(0.95); opacity: 0.4; }
        50% { transform: scale(1.05); opacity: 0.15; }
    }
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ===== HERO ===== */
    .hero-container {
        text-align: center;
        padding: 20px 0 10px 0;
        animation: fadeUp 0.7s ease-out;
    }
    .hero-logo-wrap {
        position: relative;
        display: inline-block;
        margin-bottom: 10px;
    }
    .hero-logo-wrap::before {
        content: "";
        position: absolute;
        inset: -14px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(37,99,235,0.06) 0%, transparent 70%);
        animation: pulse-ring 4s ease-in-out infinite;
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin: 0;
        line-height: 1.15;
        color: #0F1B2D;
        background: linear-gradient(135deg, #0F1B2D 0%, #2563EB 50%, #0F1B2D 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: #0F1B2D;
        animation: gradient-shift 6s ease infinite;
    }
    @supports (-webkit-background-clip: text) {
        .hero-title { -webkit-text-fill-color: transparent; }
    }
    .hero-subtitle {
        font-family: 'Outfit', sans-serif;
        font-size: 0.92rem;
        color: #475569;
        font-weight: 400;
        margin-top: 5px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    .hero-divider {
        height: 3px;
        background: linear-gradient(90deg, transparent 5%, #2563EB 30%, #EF4444 50%, #F59E0B 70%, transparent 95%);
        margin: 18px auto 26px auto;
        max-width: 340px;
        border-radius: 2px;
        opacity: 0.6;
    }

    /* ===== AUTH CARD ===== */
    .auth-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        max-width: 560px;
        margin: 0 auto;
        box-shadow: 0 12px 40px rgba(15,23,42,0.12);
        overflow: hidden;
        animation: fadeUp 0.5s ease-out 0.1s both;
        position: relative;
    }
    .auth-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 4px;
        background: linear-gradient(90deg, #2563EB, #06B6D4, #3B82F6);
        background-size: 200% auto;
        animation: shimmer 3s linear infinite;
    }
    .auth-card-body { padding: 32px 28px 24px; }

    /* ===== TABS ===== */
    .auth-tabs {
        display: flex;
        border-bottom: 1px solid #E2E8F0;
        background: #F8FAFC;
    }
    .auth-tab {
        flex: 1;
        padding: 14px 0;
        text-align: center;
        font-family: 'Outfit', sans-serif;
        font-size: 0.88rem;
        font-weight: 600;
        color: #94A3B8;
        position: relative;
        transition: all 0.3s ease;
    }
    .auth-tab.active {
        color: #2563EB;
        background: #FFFFFF;
    }
    .auth-tab.active::after {
        content: "";
        position: absolute;
        bottom: -1px;
        left: 20%; right: 20%;
        height: 3px;
        background: #2563EB;
        border-radius: 3px 3px 0 0;
    }
    .auth-tab-icon { display: block; font-size: 1.2rem; margin-bottom: 2px; }

    /* ===== SECTION TITLE ===== */
    .section-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0 0 4px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-title .icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.05rem;
        flex-shrink: 0;
    }
    .section-title .icon.blue { background: rgba(37,99,235,0.08); }
    .section-title .icon.green { background: rgba(16,185,129,0.08); }
    .section-title .icon.red { background: rgba(220,38,38,0.08); }
    .section-desc {
        font-size: 0.86rem;
        color: #94A3B8;
        margin: 0 0 20px 0;
        line-height: 1.5;
    }

    /* ===== INFO BOX ===== */
    .info-box {
        background: linear-gradient(135deg, rgba(37,99,235,0.03) 0%, rgba(6,182,212,0.03) 100%);
        border: 1px solid rgba(37,99,235,0.1);
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 20px;
        display: flex;
        align-items: flex-start;
        gap: 10px;
        animation: fadeIn 0.5s ease-out 0.2s both;
    }
    .info-box-icon { font-size: 1.1rem; margin-top: 1px; flex-shrink: 0; }
    .info-box-text { font-size: 0.85rem; color: #475569; line-height: 1.5; }
    .info-box-text b { color: #2563EB; font-weight: 600; }

    /* ===== FORM INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 12px !important;
        border: 1.5px solid #E2E8F0 !important;
        padding: 11px 15px !important;
        font-size: 0.93rem !important;
        font-family: 'DM Sans', sans-serif !important;
        background: #FFFFFF !important;
        transition: all 0.25s ease !important;
        color: #0F172A !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.08) !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #94A3B8 !important;
    }
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border: 1.5px solid #E2E8F0 !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.08) !important;
    }
    .stNumberInput button {
        border-radius: 8px !important;
        border: 1.5px solid #E2E8F0 !important;
        background: #F8FAFC !important;
    }
    .stNumberInput button:hover {
        border-color: #2563EB !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        border-radius: 12px !important;
        padding: 11px 24px !important;
        font-weight: 600 !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.92rem !important;
        width: 100% !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
        border: none !important;
        letter-spacing: 0.4px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 16px rgba(15,23,42,0.08) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%) !important;
        color: white !important;
    }
    .stButton > button[kind="primary"]:hover {
        box-shadow: 0 8px 24px rgba(37,99,235,0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: #FFFFFF !important;
        color: #475569 !important;
        border: 1.5px solid #E2E8F0 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #2563EB !important;
        color: #2563EB !important;
    }

    /* ===== FORM SUBMIT ===== */
    .stFormSubmitButton > button {
        border-radius: 12px !important;
        padding: 13px 28px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.98rem !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4,0,0.2,1) !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(37,99,235,0.35) !important;
    }

    /* ===== SEPARATOR ===== */
    .sep-line {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 18px 0;
        color: #94A3B8;
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'Outfit', sans-serif;
    }
    .sep-line::before, .sep-line::after {
        content: "";
        flex: 1;
        height: 1px;
        background: #E2E8F0;
    }

    /* ===== FEATURE CHIPS ===== */
    .feature-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 20px;
        animation: fadeIn 0.8s ease-out 0.5s both;
    }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        font-family: 'Outfit', sans-serif;
        background: #FFFFFF;
        color: #475569;
        border: 1px solid #E2E8F0;
        transition: all 0.2s ease;
    }
    .chip:hover {
        border-color: #2563EB;
        color: #2563EB;
        transform: translateY(-1px);
        box-shadow: 0 1px 3px rgba(15,23,42,0.06);
    }

    /* ===== VERSION BADGE ===== */
    .version-badge {
        position: fixed;
        bottom: 10px; right: 14px;
        background: #FFFFFF;
        color: #94A3B8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.68rem;
        font-family: 'Outfit', sans-serif;
        letter-spacing: 0.5px;
        box-shadow: 0 1px 3px rgba(15,23,42,0.06);
        border: 1px solid #E2E8F0;
        z-index: 999;
    }

    /* ===== BG PATTERN ===== */
    .bg-pattern {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: -1;
        background-image:
            radial-gradient(circle at 15% 15%, rgba(37,99,235,0.04) 0%, transparent 50%),
            radial-gradient(circle at 85% 85%, rgba(220,38,38,0.03) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(6,182,212,0.02) 0%, transparent 40%);
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0F1B2D 0%, #1E3A5F 100%); }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        margin-bottom: 8px;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.1) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }

    /* ===== FIELD GROUP TITLE ===== */
    .field-group-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 🎨 PREMIUM UI OVERHAUL — Sinematik Animasyonlar
# =========================================================
st.markdown("""
<style>
    /* ===== ANIMATED BLOB BACKGROUNDS ===== */
    @keyframes blob-float-1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        25% { transform: translate(30px, -50px) scale(1.1); }
        50% { transform: translate(-20px, 20px) scale(0.95); }
        75% { transform: translate(40px, 30px) scale(1.05); }
    }
    @keyframes blob-float-2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(-40px, 30px) scale(1.08); }
        66% { transform: translate(20px, -40px) scale(0.92); }
    }
    @keyframes blob-float-3 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        20% { transform: translate(50px, 20px) scale(1.12); }
        40% { transform: translate(-30px, -30px) scale(0.96); }
        60% { transform: translate(10px, 40px) scale(1.04); }
        80% { transform: translate(-40px, 10px) scale(0.98); }
    }
    .mesh-gradient-bg {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: -2;
        overflow: hidden;
    }
    .mesh-gradient-bg .blob {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.5;
    }
    .mesh-gradient-bg .blob-1 {
        width: 500px; height: 500px;
        top: -10%; left: -5%;
        background: radial-gradient(circle, rgba(37,99,235,0.12) 0%, transparent 70%);
        animation: blob-float-1 20s ease-in-out infinite;
    }
    .mesh-gradient-bg .blob-2 {
        width: 400px; height: 400px;
        top: 50%; right: -5%;
        background: radial-gradient(circle, rgba(220,38,38,0.08) 0%, transparent 70%);
        animation: blob-float-2 25s ease-in-out infinite;
    }
    .mesh-gradient-bg .blob-3 {
        width: 350px; height: 350px;
        bottom: -10%; left: 30%;
        background: radial-gradient(circle, rgba(6,182,212,0.10) 0%, transparent 70%);
        animation: blob-float-3 22s ease-in-out infinite;
    }

    /* ===== WORD-BY-WORD REVEAL ===== */
    @keyframes word-reveal {
        0% { opacity: 0; transform: translateY(20px) rotateX(-20deg); filter: blur(4px); }
        100% { opacity: 1; transform: translateY(0) rotateX(0); filter: blur(0); }
    }
    .word-reveal-container .word {
        display: inline-block;
        opacity: 0;
        animation: word-reveal 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        margin-right: 8px;
    }
    .word-reveal-container .word:nth-child(1) { animation-delay: 0.1s; }
    .word-reveal-container .word:nth-child(2) { animation-delay: 0.3s; }
    .word-reveal-container .word:nth-child(3) { animation-delay: 0.5s; }
    .word-reveal-container .word:nth-child(4) { animation-delay: 0.7s; }
    .word-reveal-container .word:nth-child(5) { animation-delay: 0.9s; }

    /* ===== SCROLL-TRIGGERED FADE-IN ===== */
    .scroll-reveal {
        opacity: 0;
        transform: translateY(30px);
        transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .scroll-reveal.visible {
        opacity: 1;
        transform: translateY(0);
    }
    .scroll-reveal.delay-1 { transition-delay: 0.1s; }
    .scroll-reveal.delay-2 { transition-delay: 0.2s; }
    .scroll-reveal.delay-3 { transition-delay: 0.3s; }
    .scroll-reveal.delay-4 { transition-delay: 0.4s; }

    /* ===== COUNT-UP COUNTER ===== */
    @keyframes count-pop {
        0% { transform: scale(1); }
        50% { transform: scale(1.15); }
        100% { transform: scale(1); }
    }
    .count-up-number {
        font-family: 'Outfit', sans-serif;
        font-weight: 900;
        font-size: 2.4rem;
        color: #0F1B2D;
        line-height: 1;
    }
    .count-up-number.animated {
        animation: count-pop 0.3s ease-out;
    }

    /* ===== GLASSMORPHISM STAT CARDS ===== */
    .glass-stat-card {
        background: rgba(255, 255, 255, 0.72);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 24px rgba(15,23,42,0.06);
    }
    .glass-stat-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--card-accent, #2563EB), var(--card-accent-end, #06B6D4));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .glass-stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(15,23,42,0.12);
    }
    .glass-stat-card:hover::before {
        opacity: 1;
    }
    .glass-stat-card .stat-icon {
        width: 48px; height: 48px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 14px;
    }
    .glass-stat-card .stat-value {
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1;
        margin-bottom: 4px;
    }
    .glass-stat-card .stat-label {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 500;
    }

    /* ===== CONFETTI ===== */
    @keyframes confetti-fall {
        0% { transform: translateY(-100vh) rotate(0deg); opacity: 1; }
        80% { opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
    }
    .confetti-container {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 9999;
        overflow: hidden;
    }
    .confetti-piece {
        position: absolute;
        width: 10px; height: 10px;
        top: -10px;
        animation: confetti-fall 3s ease-in-out forwards;
    }

    /* ===== SCORE RING ===== */
    @keyframes ring-fill {
        from { stroke-dashoffset: 283; }
    }
    .score-ring-container {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    .score-ring-container svg {
        transform: rotate(-90deg);
    }
    .score-ring-bg {
        fill: none;
        stroke: #E2E8F0;
        stroke-width: 8;
    }
    .score-ring-fill {
        fill: none;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dashoffset 1.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .score-ring-text {
        position: absolute;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        color: #0F172A;
    }

    /* ===== SKELETON LOADING ===== */
    @keyframes skeleton-sweep {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    .skeleton {
        background: linear-gradient(90deg, #E2E8F0 25%, #F1F5F9 50%, #E2E8F0 75%);
        background-size: 200% 100%;
        animation: skeleton-sweep 1.5s ease-in-out infinite;
        border-radius: 8px;
    }
    .skeleton-text { height: 14px; margin-bottom: 8px; width: 80%; }
    .skeleton-title { height: 24px; margin-bottom: 12px; width: 60%; }
    .skeleton-card {
        height: 120px;
        border-radius: 16px;
        margin-bottom: 16px;
    }

    /* ===== TOAST NOTIFICATIONS ===== */
    @keyframes toast-slide-in {
        from { transform: translateX(100%) translateY(0); opacity: 0; }
        to { transform: translateX(0) translateY(0); opacity: 1; }
    }
    @keyframes toast-slide-out {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(120%); opacity: 0; }
    }
    .toast-container {
        position: fixed;
        top: 20px; right: 20px;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .toast {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 14px 20px;
        box-shadow: 0 12px 40px rgba(15,23,42,0.15);
        border-left: 4px solid #2563EB;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.88rem;
        color: #0F172A;
        animation: toast-slide-in 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        max-width: 340px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .toast.success { border-left-color: #10B981; }
    .toast.error { border-left-color: #DC2626; }
    .toast.warning { border-left-color: #F59E0B; }
    .toast.hiding { animation: toast-slide-out 0.3s ease-in forwards; }

    /* ===== CUSTOM SCROLLBAR ===== */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #CBD5E1 0%, #94A3B8 100%);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: #64748B; }
    * { scrollbar-width: thin; scrollbar-color: #CBD5E1 transparent; }

    /* ===== FOCUS INDICATORS ===== */
    :focus-visible {
        outline: 2px solid #2563EB !important;
        outline-offset: 2px !important;
        border-radius: 4px;
    }
    ::selection {
        background: rgba(37,99,235,0.15);
        color: #0F172A;
    }

    /* ===== SIDEBAR GLASSMORPHISM ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1B2D 0%, #162D50 50%, #1E3A5F 100%) !important;
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"]::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(circle at 50% 0%, rgba(37,99,235,0.08) 0%, transparent 60%);
        pointer-events: none;
    }

    /* ===== HOVER GLOW EFFECT ===== */
    .hover-glow {
        transition: all 0.3s ease;
    }
    .hover-glow:hover {
        box-shadow: 0 0 30px rgba(37,99,235,0.15), 0 8px 24px rgba(15,23,42,0.08);
    }

    /* ===== TEST CARD ENHANCED ===== */
    .test-card-enhanced {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 18px;
        padding: 20px;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
        overflow: hidden;
    }
    .test-card-enhanced::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(37,99,235,0.02) 0%, rgba(6,182,212,0.02) 100%);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    .test-card-enhanced:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 50px rgba(15,23,42,0.12);
        border-color: rgba(37,99,235,0.2);
    }
    .test-card-enhanced:hover::after { opacity: 1; }

    /* ===== MOBILE TOUCH FEEDBACK ===== */
    @media (hover: none) and (pointer: coarse) {
        .stButton > button:active {
            transform: scale(0.97) !important;
            transition: transform 0.1s ease !important;
        }
        .test-card-enhanced:active {
            transform: scale(0.98) !important;
        }
        .chip:active {
            transform: scale(0.95);
            background: #EFF6FF;
        }
    }

    /* ===== SMOOTH SCROLL ===== */
    html { scroll-behavior: smooth; }

    /* ===== PREFERS-REDUCED-MOTION ===== */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
        .mesh-gradient-bg .blob { animation: none !important; }
        .hero-title { animation: none !important; }
        .scroll-reveal { opacity: 1 !important; transform: none !important; }
        .word-reveal-container .word { opacity: 1 !important; transform: none !important; animation: none !important; }
    }
</style>

<!-- Animated Mesh Gradient Blobs -->
<div class="mesh-gradient-bg">
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>
</div>

<!-- Scroll Reveal Observer -->
<script>
(function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

    function observeElements() {
        document.querySelectorAll('.scroll-reveal:not(.visible)').forEach(el => observer.observe(el));
    }
    observeElements();
    // MutationObserver for Streamlit dynamic content
    const mo = new MutationObserver(() => { setTimeout(observeElements, 100); });
    mo.observe(document.body, { childList: true, subtree: true });
})();
</script>

<!-- Count-Up Animation -->
<script>
(function() {
    function animateCountUp(el) {
        const target = parseInt(el.getAttribute('data-target'), 10);
        if (isNaN(target)) return;
        const duration = 1500;
        const start = performance.now();
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(update);
            else { el.textContent = target; el.classList.add('animated'); }
        }
        requestAnimationFrame(update);
    }

    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !entry.target.dataset.counted) {
                entry.target.dataset.counted = 'true';
                animateCountUp(entry.target);
            }
        });
    }, { threshold: 0.5 });

    function observeCounters() {
        document.querySelectorAll('.count-up-number:not([data-counted])').forEach(el => countObserver.observe(el));
    }
    observeCounters();
    const mo = new MutationObserver(() => { setTimeout(observeCounters, 100); });
    mo.observe(document.body, { childList: true, subtree: true });
})();
</script>

<!-- Toast System -->
<script>
window.showToast = function(message, type) {
    type = type || 'success';
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = 'toast ' + type;
    toast.innerHTML = '<span>' + (icons[type] || '') + '</span><span>' + message + '</span>';
    container.appendChild(toast);
    setTimeout(() => { toast.classList.add('hiding'); setTimeout(() => toast.remove(), 300); }, 3500);
};
</script>

<!-- Confetti System -->
<script>
window.launchConfetti = function() {
    const container = document.createElement('div');
    container.className = 'confetti-container';
    document.body.appendChild(container);
    const colors = ['#2563EB', '#DC2626', '#F59E0B', '#10B981', '#8B5CF6', '#06B6D4', '#EC4899'];
    for (let i = 0; i < 60; i++) {
        const piece = document.createElement('div');
        piece.className = 'confetti-piece';
        piece.style.left = Math.random() * 100 + '%';
        piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        piece.style.animationDelay = Math.random() * 1.5 + 's';
        piece.style.animationDuration = (2 + Math.random() * 2) + 's';
        piece.style.width = (6 + Math.random() * 8) + 'px';
        piece.style.height = (6 + Math.random() * 8) + 'px';
        piece.style.borderRadius = Math.random() > 0.5 ? '50%' : '2px';
        container.appendChild(piece);
    }
    setTimeout(() => container.remove(), 4500);
};
</script>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
for key, default in [('role', None), ('student_id', None), ('student_name', None),
                     ('login_phase', 1), ('auth_mode', 'register')]:
    if key not in st.session_state:
        st.session_state[key] = default

def go_to_login(): st.session_state.auth_mode = 'login'
def go_to_register(): st.session_state.auth_mode = 'register'
def go_to_teacher(): st.session_state.auth_mode = 'teacher'
def go_to_teacher_login(): st.session_state.auth_mode = 'teacher_login'
def go_to_forgot_password(): st.session_state.auth_mode = 'forgot_password'

def get_teacher_password():
    try:
        if "teacher_password" in st.secrets:
            return st.secrets["teacher_password"]
    except Exception:
        pass
    return os.getenv("TEACHER_PASSWORD")


# =========================================================
# HERO HEADER
# =========================================================
def render_hero_header():
    logo_b64 = get_logo_base64()
    phoenix_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="78" height="78"><defs><linearGradient id="wg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#DC2626"/><stop offset="50%" stop-color="#EF4444"/><stop offset="100%" stop-color="#F59E0B"/></linearGradient><linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="#0F1B2D"/><stop offset="100%" stop-color="#2563EB"/></linearGradient><linearGradient id="tg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#EF4444"/><stop offset="40%" stop-color="#F59E0B"/><stop offset="100%" stop-color="#FBBF24"/></linearGradient><filter id="gl"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs><ellipse cx="100" cy="95" rx="55" ry="60" fill="none" stroke="#F59E0B" stroke-width="1.5" opacity="0.15"/><path d="M100,85 Q60,40 30,55 Q45,30 65,25 Q50,15 70,10 Q80,25 85,45 Q90,60 100,85Z" fill="url(#wg)" opacity="0.9" filter="url(#gl)"/><path d="M100,85 Q140,40 170,55 Q155,30 135,25 Q150,15 130,10 Q120,25 115,45 Q110,60 100,85Z" fill="url(#wg)" opacity="0.9" filter="url(#gl)"/><path d="M100,60 Q90,80 88,110 Q90,135 100,155 Q110,135 112,110 Q110,80 100,60Z" fill="url(#bg)"/><circle cx="100" cy="58" r="14" fill="url(#bg)"/><path d="M100,68 L96,75 L100,73 L104,75Z" fill="#F59E0B"/><circle cx="93" cy="55" r="2.5" fill="#FBBF24"/><circle cx="107" cy="55" r="2.5" fill="#FBBF24"/><circle cx="93.5" cy="55" r="1" fill="#0F1B2D"/><circle cx="107.5" cy="55" r="1" fill="#0F1B2D"/><path d="M100,44 Q97,32 100,22 Q103,32 100,44Z" fill="#EF4444" opacity="0.9"/><path d="M100,44 Q93,35 91,26 Q96,33 100,44Z" fill="#F59E0B" opacity="0.7"/><path d="M100,44 Q107,35 109,26 Q104,33 100,44Z" fill="#F59E0B" opacity="0.7"/><path d="M100,155 Q90,165 80,185 Q92,175 100,165Z" fill="url(#tg)" opacity="0.8"/><path d="M100,155 Q100,170 100,190 Q100,175 100,165Z" fill="url(#tg)" opacity="0.9"/><path d="M100,155 Q110,165 120,185 Q108,175 100,165Z" fill="url(#tg)" opacity="0.8"/><circle cx="32" cy="53" r="2" fill="#F59E0B" opacity="0.5"/><circle cx="168" cy="53" r="2" fill="#F59E0B" opacity="0.5"/></svg>'

    logo_html = f'<img src="{logo_b64}" alt="Logo" style="max-height:78px;"/>' if logo_b64 else f'<div class="hero-logo-wrap">{phoenix_svg}</div>'

    st.markdown(f"""
        <div class="hero-container">
            {logo_html}
            <div class="hero-title word-reveal-container">
                <span class="word">Eğitim</span>
                <span class="word">Check</span>
                <span class="word">Up</span>
            </div>
            <div class="hero-subtitle">Kişisel Eğitim & Kariyer Analiz Merkezi</div>
        </div>
        <div class="hero-divider"></div>
    """, unsafe_allow_html=True)


# =========================================================
# ANA GİRİŞ SİSTEMİ
# =========================================================
def main_auth_flow():
    render_hero_header()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        mode = st.session_state.auth_mode

        # Tab navigation for register/login
        if mode in ('register', 'login'):
            reg_cls = "active" if mode == "register" else ""
            log_cls = "active" if mode == "login" else ""
            st.markdown(f"""
                <div style="max-width:560px;margin:0 auto;">
                <div class="auth-tabs" style="border-radius:20px 20px 0 0;border:1px solid #E2E8F0;border-bottom:none;">
                    <div class="auth-tab {reg_cls}">
                        <span class="auth-tab-icon">📝</span>Kayıt Ol
                    </div>
                    <div class="auth-tab {log_cls}">
                        <span class="auth-tab-icon">🔑</span>Giriş Yap
                    </div>
                </div></div>
            """, unsafe_allow_html=True)

        # ── KAYIT ──
        if mode == 'register':
            st.markdown('<div class="auth-card" style="border-radius:0 0 20px 20px;"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon blue">📋</div>Yeni Öğrenci Kaydı</div>
                <div class="section-desc">Testlere katılmak için profilini oluştur — sadece 1 dakika.</div>
                <div class="info-box"><div class="info-box-icon">💡</div><div class="info-box-text">Tüm bilgilerin <b>gizli ve güvende</b> tutulur. Sonuçların sadece sana ve öğretmenine görünür.</div></div>
            """, unsafe_allow_html=True)

            with st.form("register_form"):
                st.markdown('<div class="field-group-title">👤 Kişisel Bilgiler</div>', unsafe_allow_html=True)
                name = st.text_input("Ad Soyad", placeholder="Tam adını yaz...", label_visibility="collapsed")

                c1, c2, c3 = st.columns(3)
                age = c1.number_input("🎂 Yaş", min_value=5, max_value=99, step=1, value=15)
                grade = c2.selectbox("🎓 Sınıf", options=["5", "6", "7", "8", "9", "10", "11", "12", "Mezun"], index=3)
                gender = c3.selectbox("⚧ Cinsiyet", ["Kız", "Erkek"])

                st.markdown('<div class="sep-line">Hesap Bilgileri</div>', unsafe_allow_html=True)
                new_user = st.text_input("📧 E-posta Adresi", placeholder="ornek@email.com")
                new_pw = st.text_input("🔒 Şifre Belirle", type="password", placeholder="En az 4 karakter")
                secret_word = st.text_input("🛡️ Gizli Kurtarma Kelimesi", placeholder="Şifreni unutursan bu kelime lazım olacak", help="Şifreni sıfırlamak istediğinde bu kelimeyi soracağız.")

                st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                submit = st.form_submit_button("🚀  Kayıt Ol", type="primary")

                if submit:
                    import re
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not name or not new_user or not new_pw or not secret_word:
                        st.warning("⚠️ Lütfen tüm alanları doldurunuz.")
                    elif len(new_pw) < 4:
                        st.warning("⚠️ Şifre en az 4 karakter olmalıdır.")
                    elif not re.match(email_pattern, new_user.strip()):
                        st.warning("⚠️ Geçerli bir e-posta adresi giriniz.")
                    else:
                        success, result = register_student(name.title(), new_user.strip().lower(), new_pw, age, gender, secret_word.lower().strip(), grade)
                        if success:
                            st.success("✅ Kayıt Başarılı! Giriş ekranına yönlendiriliyorsun...")
                            time.sleep(1.5)
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                        else:
                            st.error(result)

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2, lc3 = st.columns(3)
            lc1.button("🔑 Zaten hesabın var mı? Giriş Yap", on_click=go_to_login)
            lc2.button("👨‍🏫 Öğretmen Girişi", on_click=go_to_teacher_login)
            lc3.button("🛡️ Yönetici Girişi", on_click=go_to_teacher)

        # ── GİRİŞ ──
        elif mode == 'login':
            st.markdown('<div class="auth-card" style="border-radius:0 0 20px 20px;"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon green">🔓</div>Tekrar Hoşgeldin!</div>
                <div class="section-desc">E-posta adresin ve şifrenle hemen testlerine devam et.</div>
            """, unsafe_allow_html=True)

            with st.form("login_form"):
                user = st.text_input("📧 E-posta Adresi", placeholder="E-posta adresini gir...")
                pw = st.text_input("🔒 Şifre", type="password", placeholder="Şifreni gir...")
                st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                submit = st.form_submit_button("Giriş Yap  ➡️", type="primary")

                if submit:
                    if not user or not pw:
                        st.warning("⚠️ E-posta ve şifre boş bırakılamaz.")
                    else:
                        status, student_obj = login_student(user.strip().lower(), pw)
                        if status:
                            st.success(f"🎉 Hoşgeldin {student_obj.name}!")
                            st.session_state.role = "student"
                            st.session_state.student_id = student_obj.id
                            st.session_state.student_name = student_obj.name
                            st.session_state.student_age = student_obj.age
                            st.session_state.student_grade = student_obj.grade
                            st.session_state.login_phase = student_obj.login_count
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("❌ E-posta adresi veya şifre hatalı.")

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2, lc3 = st.columns(3)
            lc1.button("📝 Hesabın yok mu? Kayıt Ol", on_click=go_to_register)
            lc2.button("❓ Şifremi Unuttum", on_click=go_to_forgot_password)
            lc3.button("👨‍🏫 Öğretmen / Yönetici", on_click=go_to_teacher_login)

        # ── ŞİFRE SIFIRLAMA ──
        elif mode == 'forgot_password':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon red">🔐</div>Şifre Sıfırlama</div>
                <div class="section-desc">Gizli kurtarma kelimeni kullanarak yeni şifre belirle.</div>
            """, unsafe_allow_html=True)

            with st.form("forgot_password_form"):
                user = st.text_input("📧 E-posta Adresi", placeholder="Kayıtlı e-posta adresini gir...")
                secret = st.text_input("🛡️ Gizli Kurtarma Kelimesi", type="password")
                new_pw = st.text_input("🔒 Yeni Şifre Belirle", type="password")
                st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                submit = st.form_submit_button("Şifremi Yenile  ✅", type="primary")
                if submit:
                    if not user or not secret or not new_pw:
                        st.warning("⚠️ Lütfen tüm alanları doldurunuz.")
                    elif len(new_pw) < 4:
                        st.warning("⚠️ Yeni şifre en az 4 karakter olmalıdır.")
                    else:
                        success, msg = reset_student_password(user.strip().lower(), secret.lower().strip(), new_pw)
                        if success:
                            st.success("✅ Şifren güncellendi!")
                            time.sleep(1.5)
                            st.session_state.auth_mode = 'login'
                            st.rerun()
                        else:
                            st.error(msg)

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("⬅️ Giriş Ekranına Dön", on_click=go_to_login)

        # ── ÖĞRETMEN GİRİŞİ ──
        elif mode == 'teacher_login':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon blue">👨‍🏫</div>Öğretmen / Koç Girişi</div>
                <div class="section-desc">Kendi panelinize erişmek için adınızı seçin ve şifrenizi girin.</div>
            """, unsafe_allow_html=True)

            teachers = get_all_teachers()
            if not teachers:
                st.warning("⚠️ Henüz sistemde kayıtlı öğretmen bulunmamaktadır.")
                st.info("👇 **Nasıl çözülür?**\n\n1. Aşağıdaki **🛡️ Yönetici Girişi** butonuna tıklayın\n2. Yönetici şifresi ile giriş yapın\n3. Yönetici panelinden ilk öğretmeni ekleyin\n\nVeya sayfanın en altındaki **🩺 Sistem Sağlığı** panelinden Bootstrap aracıyla hızlıca oluşturabilirsiniz.")
            else:
                with st.form("teacher_login_form"):
                    teacher_options = {t["name"]: t["id"] for t in teachers}
                    selected_teacher = st.selectbox("👤 Öğretmen Seçiniz", options=list(teacher_options.keys()), index=None, placeholder="Listeden seçin...")
                    pw = st.text_input("🔒 Şifre", type="password", placeholder="Şifrenizi girin...")
                    st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                    submit = st.form_submit_button("Giriş Yap  ➡️", type="primary")
                    if submit:
                        if not selected_teacher or not pw:
                            st.warning("⚠️ Lütfen öğretmen seçin ve şifrenizi girin.")
                        else:
                            tid = teacher_options[selected_teacher]
                            success, teacher_info = authenticate_teacher(tid, pw)
                            if success:
                                st.success(f"🎉 Hoşgeldiniz {teacher_info['name']}!")
                                st.session_state.role = "teacher_panel"
                                st.session_state.teacher_id = teacher_info["id"]
                                st.session_state.teacher_name = teacher_info["name"]
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error("❌ Hatalı şifre.")

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            lc1.button("⬅️ Öğrenci Ekranına Dön", on_click=go_to_register)
            lc2.button("🛡️ Yönetici Girişi", on_click=go_to_teacher)

        # ── YÖNETİCİ ──
        elif mode == 'teacher':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon blue">🛡️</div>Yönetici Paneli</div>
                <div class="section-desc">Bu alan yalnızca yetkili yöneticiler içindir.</div>
            """, unsafe_allow_html=True)

            with st.form("teacher_form"):
                pw = st.text_input("🔑 Yönetici Şifresi", type="password", placeholder="Şifrenizi girin...")
                st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
                submit = st.form_submit_button("Panele Git  ➡️", type="primary")
                if submit:
                    secret_pass = get_teacher_password()
                    if secret_pass is None:
                        st.error("⚠️ Yönetici şifresi yapılandırılmamış.")
                    elif pw == secret_pass:
                        st.session_state.role = "admin"
                        st.rerun()
                    else:
                        st.error("❌ Hatalı şifre.")

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            lc1, lc2 = st.columns(2)
            lc1.button("⬅️ Öğrenci Ekranına Dön", on_click=go_to_register)
            lc2.button("👨‍🏫 Öğretmen Girişi", on_click=go_to_teacher_login)

        # Feature chips
        st.markdown("""
            <div class="feature-chips">
                <span class="chip">🧬 Enneagram</span>
                <span class="chip">🧠 Beyin Dominansı</span>
                <span class="chip">👁️ P2 Dikkat</span>
                <span class="chip">📚 Akademik Analiz</span>
                <span class="chip">🧭 Kariyer Keşfi</span>
                <span class="chip">📖 Hızlı Okuma</span>
                <span class="chip">💡 Çoklu Zeka</span>
            </div>
        """, unsafe_allow_html=True)

    # =========================================================
    # 🩺 SİSTEM SAĞLIĞI PANELİ
    # =========================================================
    with st.expander("🩺 Sistem Sağlığı & Bootstrap (Yönetici)", expanded=False):
        diag = get_db_diagnostics()

        # Durum özeti
        col1, col2, col3 = st.columns(3)
        with col1:
            if diag["db_engine"] == "postgresql":
                st.success("🟢 **PostgreSQL (Supabase)**\nVeriler kalıcı")
            elif diag["db_engine"] == "sqlite":
                st.warning("🟡 **SQLite (Geçici)**\n⚠️ Veriler restart'ta silinir")
            else:
                st.error("🔴 **Bağlantı yok**")

        with col2:
            st.markdown("**🔐 Secrets Durumu**")
            st.caption(f"{'✅' if diag['db_url_present'] else '❌'} SUPABASE_DB_URL")
            st.caption(f"{'✅' if diag['teacher_password_configured'] else '❌'} teacher_password")
            st.caption(f"{'✅' if diag['anthropic_key_configured'] else '❌'} ANTHROPIC_API_KEY")

        with col3:
            st.markdown("**📊 Tablo Sayıları**")
            t_count = diag.get("teachers_count")
            a_count = diag.get("active_teachers_count")
            s_count = diag.get("students_count")
            r_count = diag.get("results_count")
            st.caption(f"👨‍🏫 Öğretmen: **{t_count}** (aktif: **{a_count}**)")
            st.caption(f"👨‍🎓 Öğrenci: **{s_count}**")
            st.caption(f"📝 Test Sonucu: **{r_count}**")

        # Hatalar
        errors = []
        if diag.get("connection_error"):
            errors.append(("Bağlantı", diag["connection_error"]))
        if diag.get("teachers_error"):
            errors.append(("Teachers tablosu", diag["teachers_error"]))
        if diag.get("students_error"):
            errors.append(("Students tablosu", diag["students_error"]))
        if diag.get("results_error"):
            errors.append(("Results tablosu", diag["results_error"]))

        if errors:
            st.markdown("---")
            st.error("❌ **Yakalanan Hatalar:**")
            for title, err in errors:
                st.code(f"{title}: {err}", language="text")

        # Runtime'da yakalanan son hata
        last_err = st.session_state.get("_last_db_error")
        if last_err:
            st.markdown("---")
            st.warning("⚠️ **Son çalışma zamanı hatası:**")
            st.code(last_err, language="text")

        # Tanı yorumu
        st.markdown("---")
        st.markdown("#### 🔎 Tanı")

        if not diag["db_url_present"]:
            st.error("🚨 **SUPABASE_DB_URL secret'ta yok.** Streamlit Cloud → Settings → Secrets kısmına ekleyin. SQLite kullanılıyor, her restart'ta veriler siliniyor.")
        elif diag["db_engine"] == "sqlite":
            st.error("🚨 **SUPABASE_DB_URL var ama bağlantı kurulamadı.** Muhtemelen: (a) Supabase projesi paused (7 gün inaktivite), (b) şifre yanlış/eski, (c) URL formatı bozuk. Supabase Dashboard'u kontrol edin.")
        elif not diag["teacher_password_configured"]:
            st.warning("⚠️ **`teacher_password` secret'ı yok.** Yönetici paneline giriş yapamazsınız. Secrets'a ekleyin: `teacher_password = \"sifre123\"`")
        elif diag["teachers_count"] == 0 or diag["active_teachers_count"] == 0:
            st.warning("⚠️ **Teachers tablosu boş veya tüm öğretmenler pasif.** Öğretmen girişi yapabilmek için önce bir öğretmen oluşturmanız gerekiyor. Aşağıdaki Bootstrap aracını kullanın ⬇️")
        elif diag["students_count"] == 0:
            st.info("ℹ️ **Students tablosu boş.** Öğrenciler henüz kayıt olmamış. Bu normal olabilir — öğrenciler 'Öğrenci Girişi / Kayıt' ekranından hesap açacak.")
        else:
            st.success(f"✅ **Sistem sağlıklı.** {diag['teachers_count']} öğretmen, {diag['students_count']} öğrenci, {diag['results_count']} test sonucu kayıtlı.")

        # Bootstrap: ilk öğretmeni oluştur
        if diag.get("connection_ok") and diag.get("teachers_count") == 0:
            st.markdown("---")
            st.markdown("#### 🛠️ İlk Öğretmen Bootstrap")
            st.caption("Teachers tablosu boş. Buradan ilk öğretmeni oluşturabilirsiniz. Bu araç sadece tablo boşken çalışır — güvenlik için.")

            with st.form("bootstrap_teacher_form"):
                bs_admin_pw = st.text_input("🔑 Yönetici Şifresi (secrets'taki teacher_password)", type="password")
                bs_name = st.text_input("👤 Öğretmen Ad Soyad", placeholder="Örn: Mehmet Eser")
                bs_pw = st.text_input("🔒 Öğretmen Şifresi", type="password", placeholder="En az 4 karakter")
                bs_submit = st.form_submit_button("🚀 İlk Öğretmeni Oluştur", type="primary")

                if bs_submit:
                    secret_admin_pw = get_teacher_password()
                    if not secret_admin_pw:
                        st.error("❌ `teacher_password` secret'ı yapılandırılmamış. Önce Streamlit Cloud Secrets'a ekleyin.")
                    elif bs_admin_pw != secret_admin_pw:
                        st.error("❌ Yönetici şifresi hatalı.")
                    elif not bs_name or not bs_pw:
                        st.warning("⚠️ Ad ve şifre boş olamaz.")
                    elif len(bs_pw) < 4:
                        st.warning("⚠️ Öğretmen şifresi en az 4 karakter olmalı.")
                    else:
                        ok, msg = bootstrap_first_teacher(bs_name.strip().title(), bs_pw)
                        if ok:
                            st.success(msg)
                            st.info("Şimdi sayfayı yenileyin ve 'Öğretmen Girişi'nden giriş yapın.")
                            st.balloons()
                        else:
                            st.error(msg)

    st.markdown('<div class="version-badge">EĞİTİM CHECK UP v2.1</div>', unsafe_allow_html=True)


# =========================================================
# YÖNLENDİRME
# =========================================================
if st.session_state.role is None:
    main_auth_flow()
elif st.session_state.role == "student":
    import student_view
    student_view.app()
elif st.session_state.role == "admin":
    import teacher_view
    teacher_view.app()
elif st.session_state.role == "teacher_panel":
    import teacher_view
    teacher_view.teacher_panel_app()

# =========================================================
# SIDEBAR
# =========================================================
if st.session_state.role:
    with st.sidebar:
        if st.session_state.role == "admin":
            role_label = "🛡️ Yönetici"
            role_icon = "🛡️"
            user_name = "Yönetici"
        elif st.session_state.role == "teacher_panel":
            role_label = "👨‍🏫 Öğretmen"
            role_icon = "👨‍🏫"
            user_name = st.session_state.get('teacher_name', 'Öğretmen')
        else:
            role_label = "🎓 Öğrenci"
            role_icon = "🎓"
            user_name = st.session_state.get('student_name', 'Öğrenci')
        st.markdown(f"""
            <div style="text-align:center; padding: 14px 0;">
                <div style="font-size: 2.2rem;">{role_icon}</div>
                <div style="font-family:'Outfit',sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 6px;">{user_name}</div>
                <div style="font-family:'Outfit',sans-serif; font-size: 0.78rem; color: rgba(255,255,255,0.6); margin-top: 3px; letter-spacing: 1px;">{role_label}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.role == "admin":
            if st.button("🔧 Veritabanını Onar", help="Veritabanı hatası alırsanız buna basın"):
                if repair_database():
                    st.success("✅ Veritabanı onarıldı!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Onarım başarısız oldu.")
            st.markdown("---")
        if st.button("🚪 Güvenli Çıkış"):
            st.session_state.clear()
            st.session_state.auth_mode = 'register'
            st.rerun()
        st.markdown("---")
        st.markdown("""
            <div style="text-align:center; font-family:'Outfit',sans-serif; font-size: 0.7rem; color: rgba(255,255,255,0.4); padding-top: 10px; letter-spacing: 0.5px;">
                EĞİTİM CHECK UP v2.1<br/>Kişisel Eğitim & Kariyer Analiz Merkezi
            </div>
        """, unsafe_allow_html=True)

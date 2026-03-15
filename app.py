import streamlit as st
import time
import os
import base64

from db_utils import init_db, login_student, register_student, reset_student_password, repair_database

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

st.markdown('<div class="bg-pattern"></div>', unsafe_allow_html=True)

# --- SESSION STATE ---
for key, default in [('role', None), ('student_id', None), ('student_name', None),
                     ('login_phase', 1), ('auth_mode', 'register')]:
    if key not in st.session_state:
        st.session_state[key] = default

def go_to_login(): st.session_state.auth_mode = 'login'
def go_to_register(): st.session_state.auth_mode = 'register'
def go_to_teacher(): st.session_state.auth_mode = 'teacher'
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
            <div class="hero-title">Eğitim Check Up</div>
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
                grade = c2.selectbox("🎓 Sınıf", options=[5, 6, 7, 8, 9, 10, 11, 12], index=3)
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
            lc1, lc2 = st.columns(2)
            lc1.button("🔑 Zaten hesabın var mı? Giriş Yap", on_click=go_to_login)
            lc2.button("👨‍🏫 Öğretmen / Yönetici Girişi", on_click=go_to_teacher)

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
            lc1, lc2 = st.columns(2)
            lc1.button("📝 Hesabın yok mu? Kayıt Ol", on_click=go_to_register)
            lc2.button("❓ Şifremi Unuttum", on_click=go_to_forgot_password)

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

        # ── ÖĞRETMEN ──
        elif mode == 'teacher':
            st.markdown('<div class="auth-card"><div class="auth-card-body">', unsafe_allow_html=True)
            st.markdown("""
                <div class="section-title"><div class="icon blue">👨‍🏫</div>Yönetici Paneli</div>
                <div class="section-desc">Bu alan yalnızca yetkili öğretmen ve yöneticiler içindir.</div>
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
                        st.session_state.role = "teacher"
                        st.rerun()
                    else:
                        st.error("❌ Hatalı şifre.")

            st.markdown('</div></div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("⬅️ Öğrenci Ekranına Dön", on_click=go_to_register)

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

    st.markdown('<div class="version-badge">EĞİTİM CHECK UP v2.1</div>', unsafe_allow_html=True)


# =========================================================
# YÖNLENDİRME
# =========================================================
if st.session_state.role is None:
    main_auth_flow()
elif st.session_state.role == "student":
    import student_view
    student_view.app()
elif st.session_state.role == "teacher":
    import teacher_view
    teacher_view.app()

# =========================================================
# SIDEBAR
# =========================================================
if st.session_state.role:
    with st.sidebar:
        role_label = "👨‍🏫 Yönetici" if st.session_state.role == "teacher" else "🎓 Öğrenci"
        user_name = st.session_state.get('student_name', 'Yönetici')
        st.markdown(f"""
            <div style="text-align:center; padding: 14px 0;">
                <div style="font-size: 2.2rem;">{'👨‍🏫' if st.session_state.role == 'teacher' else '🎓'}</div>
                <div style="font-family:'Outfit',sans-serif; font-size: 1.15rem; font-weight: 700; color: #FFFFFF; margin-top: 6px;">{user_name}</div>
                <div style="font-family:'Outfit',sans-serif; font-size: 0.78rem; color: rgba(255,255,255,0.6); margin-top: 3px; letter-spacing: 1px;">{role_label}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        if st.session_state.role == "teacher":
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

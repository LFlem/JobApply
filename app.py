import streamlit as st

from utils.auth import (
    authenticate_user,
    check_session_timeout,
    get_current_user,
    is_authenticated,
    login_user,
    logout_user,
    register_user,
    restore_session_from_cookie,
    save_session_to_cookie,
    update_last_activity,
    validate_registration,
)

THEMES = {
    "Clair": {
        "bg": "#f6f7fb",
        "surface": "#ffffff",
        "surface_muted": "#eef2f7",
        "border": "#d9e0ec",
        "text": "#182033",
        "text_muted": "#56607a",
        "accent": "#2563eb",
        "accent_soft": "#dbeafe",
        "button_bg": "#182033",
        "button_text": "#ffffff",
        "button_border": "#182033",
        "input_bg": "#ffffff",
        "link": "#2563eb",
        "shadow": "rgba(15, 23, 42, 0.08)",
    },
    "Sombre": {
        "bg": "#0f172a",
        "surface": "#111c34",
        "surface_muted": "#1a2745",
        "border": "#31415f",
        "text": "#eef2ff",
        "text_muted": "#b2bdd8",
        "accent": "#7dd3fc",
        "accent_soft": "#16314c",
        "button_bg": "#7dd3fc",
        "button_text": "#0f172a",
        "button_border": "#7dd3fc",
        "input_bg": "#15203a",
        "link": "#8bd3ff",
        "shadow": "rgba(2, 6, 23, 0.35)",
    },
}


def apply_theme(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

:root {{
    --bg: {theme['bg']};
    --surface: {theme['surface']};
    --surface-muted: {theme['surface_muted']};
    --border: {theme['border']};
    --text: {theme['text']};
    --text-muted: {theme['text_muted']};
    --accent: {theme['accent']};
    --accent-soft: {theme['accent_soft']};
    --button-bg: {theme['button_bg']};
    --button-text: {theme['button_text']};
    --button-border: {theme['button_border']};
    --input-bg: {theme['input_bg']};
    --link-color: {theme['link']};
    --shadow-color: {theme['shadow']};
}}

html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}}

body {{
    background: var(--bg);
}}

p, li, span, label, div[data-testid="stMarkdownContainer"] * {{
    color: var(--text);
}}

[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.stApp {{
    background: var(--bg);
}}

h1, h2, h3 {{
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
    color: var(--text) !important;
}}

.stat-card {{
    background: var(--surface);
    border-radius: 16px;
    padding: 20px 24px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 24px var(--shadow-color);
}}

.stat-number {{
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1;
    color: var(--text);
}}

.stat-label {{
    font-size: 0.82rem;
    color: var(--text-muted);
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

.badge {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}}

.job-card {{
    background: var(--surface);
    border-radius: 14px;
    padding: 20px 24px;
    border: 1px solid var(--border);
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
    box-shadow: 0 8px 24px var(--shadow-color);
}}

.job-card:hover {{
    box-shadow: 0 12px 28px var(--shadow-color);
}}

.job-title {{
    font-family: 'Syne', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text);
}}

.job-company {{
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 500;
}}

.stButton > button,
div[data-testid="stFormSubmitButton"] > button {{
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    background: var(--button-bg) !important;
    color: var(--button-text) !important;
    border: 1px solid var(--button-border) !important;
}}

.stButton > button p,
div[data-testid="stFormSubmitButton"] > button p,
.stButton > button span,
div[data-testid="stFormSubmitButton"] > button span {{
    color: var(--button-text) !important;
}}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {{
    filter: brightness(1.06);
}}

.stTextInput > div > div > input,
.stTextArea textarea,
.stSelectbox > div > div,
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] {{
    border-radius: 10px !important;
    border-color: var(--border) !important;
    background: var(--input-bg) !important;
    color: var(--text) !important;
}}

input::placeholder,
textarea::placeholder {{
    color: var(--text-muted) !important;
}}

.stTextInput label, .stTextArea label, .stSelectbox label,
.stMultiSelect label, .stNumberInput label, .stRadio label,
.stToggle label, .stSelectbox p {{
    color: var(--text) !important;
    font-weight: 500 !important;
}}

.stSuccess, .stInfo, .stWarning, .stError {{
    border-radius: 10px;
}}

div[data-testid="stMetric"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 16px;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    color: var(--text) !important;
}}

div[data-testid="stMetricLabel"] {{
    color: var(--text-muted) !important;
}}

div[data-testid="stExpander"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
}}

.streamlit-expanderHeader {{
    color: var(--text) !important;
    font-weight: 600;
}}

[data-testid="stTabs"] [role="tablist"] {{
    gap: 10px;
}}

[data-testid="stTabs"] [role="tab"] {{
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    color: var(--text-muted) !important;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: var(--accent) !important;
    border-color: var(--accent);
    box-shadow: 0 0 0 1px var(--accent) inset;
}}

.stProgress > div > div,
.stProgress > div > div > div > div {{
    background-color: var(--accent) !important;
}}

a {{
    color: var(--link-color) !important;
}}

hr {{
    border-color: var(--border);
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_authentication() -> None:
    st.markdown("# 💼 JobApply")
    st.caption("Connexion, creation de compte et acces securise a tes candidatures")

    login_tab, signup_tab = st.tabs(["Connexion", "Creer un compte"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="toi@exemple.com")
            password = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", type="primary", use_container_width=True)

        if submitted:
            success, message, user = authenticate_user(email, password)
            if success and user:
                login_user(user)
                save_session_to_cookie(user["id"])
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with signup_tab:
        with st.form("signup_form"):
            display_name = st.text_input("Nom d'affichage", placeholder="Nom")
            email = st.text_input("Email", placeholder="toi@exemple.com")
            password = st.text_input("Mot de passe", type="password")
            password_confirm = st.text_input("Confirmer le mot de passe", type="password")
            submitted = st.form_submit_button("Creer mon compte", type="primary", use_container_width=True)

        if submitted:
            error = validate_registration(display_name, email, password, password_confirm)
            if error:
                st.error(error)
            else:
                success, message, user = register_user(display_name, email, password)
                if success and user:
                    login_user(user)
                    save_session_to_cookie(user["id"])
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

st.set_page_config(
    page_title="JobApply",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.session_state.setdefault("theme_mode", "Clair")

# Restaurer la session depuis le cookie si elle existe
if not is_authenticated():
    restore_session_from_cookie()

# Vérifier l'inactivité et déconnecter si timeout
if is_authenticated():
    if not check_session_timeout(timeout_minutes=30):
        st.warning("Votre session a expire apres 30 minutes d'inactivite. Reconnectez-vous s'il vous plait.")
        st.rerun()
    # Mettre à jour le timestamp d'activité à chaque chargement
    update_last_activity()

top_right_spacer, top_right_theme = st.columns([6, 1.4])
with top_right_theme:
    st.selectbox("Theme", ["Clair", "Sombre"], key="theme_mode")

apply_theme(THEMES[st.session_state["theme_mode"]])

if not is_authenticated():
    render_authentication()
    st.stop()

# ── Header ───────────────────────────────────────────────────────────────────
current_user = get_current_user()
header_col, account_col = st.columns([6, 1.8])
with header_col:
    st.markdown("# 💼 JobApply")
    st.markdown(
        "<p style='color:var(--text-muted);margin-top:-12px;margin-bottom:8px;'>Suivi de candidatures</p>",
        unsafe_allow_html=True,
    )
with account_col:
    st.markdown(f"<div style='text-align:right;color:var(--text-muted);padding-top:10px;'>Connecte en tant que<br><strong style='color:var(--text)'>{current_user['display_name']}</strong><br>{current_user['email']}</div>", unsafe_allow_html=True)
    if st.button("Se deconnecter", use_container_width=True):
        logout_user()
        st.rerun()
st.markdown("---")

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab_dashboard, tab_add, tab_list = st.tabs(["🏠 Tableau de bord", "➕ Ajouter une offre", "📋 Mes candidatures"])

with tab_dashboard:
    from views.dashboard import show as show_dashboard
    show_dashboard()

with tab_add:
    from views.add_job import show as show_add
    show_add()

with tab_list:
    from views.list_jobs import show as show_list
    show_list()

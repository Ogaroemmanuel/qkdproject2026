from base64 import b64encode
from pathlib import Path

import streamlit as st
from backend.database.db_manager import (
    init_db,
    register_user,
    authenticate_user,
    create_session,
    verify_session,
    destroy_session,
)
from frontend.quantum_background import render_quantum_background

AUTH_ARTWORK = b64encode(
    (Path(__file__).parent / "frontend" / "assets" / "figma_landing" / "quantum-wave-field.png").read_bytes()
).decode("ascii")

st.set_page_config(
    page_title="SD-QKD Security Lab",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

GLOBAL_CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:wght@400;500;600;700&display=swap');
:root { --ink:#03050d; --panel:#0b1020; --panel-soft:#121a2d; --line:#293247; --white:#f3f7ff; --muted:#b0bccd; --cyan:#74f5ff; --violet:#ae8cff; --green:#63dea5; }
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
[data-testid="stAppViewContainer"] { background:var(--ink) !important; color:var(--white); }
[data-testid="stHeader"] { background:transparent !important; }
[data-testid="stSidebar"] { background:var(--panel) !important; border-right:1px solid var(--line) !important; }
[data-testid="stSidebar"] * { color:var(--white); }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:var(--muted); }
[data-testid="stSidebar"] hr { border-color:var(--line); }
.block-container { max-width:1500px; padding-top:1.7rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Inter',sans-serif !important; color:var(--white) !important; letter-spacing:-.035em; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:var(--white) !important; }
p, label, [data-testid="stMarkdownContainer"] { color:var(--muted); }
code, .small-label, .eyebrow, .auth-overline { font-family:'IBM Plex Mono',monospace !important; }
.stTextInput div[data-baseweb="input"], .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { border-radius:6px !important; background:var(--panel) !important; border:1px solid var(--line) !important; }
.stTextInput input, .stTextArea textarea, [data-baseweb="input"] input { color:var(--white) !important; -webkit-text-fill-color:var(--white) !important; caret-color:var(--cyan) !important; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color:#8290a5 !important; -webkit-text-fill-color:#8290a5 !important; opacity:1; }
.stTextInput input:-webkit-autofill, .stTextInput input:-webkit-autofill:hover, .stTextInput input:-webkit-autofill:focus { -webkit-text-fill-color:var(--white) !important; box-shadow:0 0 0 1000px var(--panel) inset !important; caret-color:var(--cyan) !important; }
.stButton > button, .stFormSubmitButton > button { border-radius:6px !important; border:1px solid var(--line) !important; font-weight:600; min-height:44px; transition:all .18s ease; background:var(--panel) !important; color:var(--white) !important; }
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] { background:var(--cyan) !important; color:var(--ink) !important; border-color:var(--cyan) !important; }
.stButton > button:hover, .stFormSubmitButton > button:hover { border-color:var(--cyan) !important; box-shadow:0 0 18px rgba(116,245,255,.12); transform:translateY(-1px); }
[data-testid="stMetric"] { background:var(--panel) !important; border:1px solid var(--line); padding:18px 20px; border-radius:10px !important; }
[data-testid="stMetricLabel"] { color:var(--muted); }
[data-testid="stMetricValue"] { color:var(--white); font-family:'Inter',sans-serif; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line) !important; border-radius:10px !important; background:var(--panel) !important; padding:10px; }
[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; }
.hero { background:linear-gradient(135deg,var(--panel),#0e1629); border:1px solid var(--line); padding:30px 34px; border-radius:12px; margin-bottom:24px; }
.hero .eyebrow { color:var(--cyan); text-transform:uppercase; letter-spacing:.13em; font-weight:500; font-size:10px; }
.hero h1 { color:var(--white) !important; margin:.55rem 0 .6rem; font-size:clamp(1.7rem,3vw,2.35rem); }
.hero p { color:var(--muted); margin:0; max-width:850px; line-height:1.65; }
.auth-brand { position:relative; isolation:isolate; overflow:hidden; background:var(--panel); border:1px solid var(--line); color:var(--white); border-radius:12px; padding:38px; min-height:450px; }
.auth-brand::before { content:""; position:absolute; inset:-10px; z-index:-1; background-image:linear-gradient(110deg,rgba(11,16,32,.94),rgba(11,16,32,.45)),var(--auth-artwork); background-position:center; background-size:cover; transform:translate(var(--auth-x,0px),var(--auth-y,0px)); animation:auth-photo-drift 28s ease-in-out infinite alternate; }
@keyframes auth-photo-drift { from { transform:translate(var(--auth-x,0px),var(--auth-y,0px)) scale(1.02) translate(-1%,0); } to { transform:translate(var(--auth-x,0px),var(--auth-y,0px)) scale(1.12) translate(1%,1%); } }
.auth-brand h1 { color:var(--white) !important; font-size:clamp(2.3rem,4vw,3.7rem); line-height:1.05; margin:.8rem 0 1rem; }
.auth-brand p { color:var(--muted); line-height:1.7; font-size:1rem; }
.auth-overline,.small-label { color:var(--cyan); text-transform:uppercase; font-size:.7rem; letter-spacing:.12em; }
.auth-chip { display:inline-block; margin:5px 5px 0 0; background:var(--panel-soft); border:1px solid var(--line); padding:7px 11px; border-radius:6px; color:var(--cyan); font-size:.78rem; }
div[data-testid="stForm"] { background:var(--panel); border:1px solid var(--line); padding:26px; border-radius:10px; }
@media (max-width: 800px) { .block-container { padding-left:1rem; padding-right:1rem; } .auth-brand { padding:26px; min-height:0; } }
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_auth_page(mode: str = "signin", expired_session: bool = False) -> None:
    if expired_session:
        st.warning("Your session expired or is no longer valid. Please sign in again.")

    left, right = st.columns([1.05, 0.95], gap="large", vertical_alignment="center")
    with left:
        st.markdown(
            f"""
            <div class="auth-brand" style="--auth-artwork:url('data:image/png;base64,{AUTH_ARTWORK}')">
              <div class="auth-overline">SOFTWARE-ONLY / ACADEMIC RESEARCH</div>
              <h1>SD‑QKD<br>Security Lab</h1>
              <p>Explore simulated key exchange, introduce controlled eavesdropping, and examine how QBER shapes an authentication decision.</p>
              <div style="margin-top:24px">
                <span class="auth-chip">Quantum simulation</span>
                <span class="auth-chip">MITM testing</span>
                <span class="auth-chip">QBER telemetry</span>
                <span class="auth-chip">Research reports</span>
              </div>
              <div style="margin-top:42px;color:#b0bccd;font-size:.82rem">A software simulation · No physical quantum channel is used</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<a href="/" target="_self">← Back to project overview</a>', unsafe_allow_html=True)
        if mode == "signup":
            st.markdown("### Create researcher account")
            st.caption("Register to enter the simulation workspace.")
            show_password = st.checkbox("Show password while typing", key="signup_show_password")
            with st.form("register_form", clear_on_submit=True):
                reg_user = st.text_input("Choose a username", placeholder="e.g. researcher01")
                password_type = "default" if show_password else "password"
                reg_pass = st.text_input("Create a password", type=password_type, placeholder="Use a strong password")
                reg_confirm = st.text_input("Confirm password", type=password_type, placeholder="Re-enter your password")
                register_submit = st.form_submit_button("Create researcher account", type="primary", width="stretch")
            if register_submit:
                user = reg_user.strip()
                if not user or not reg_pass:
                    st.warning("Enter both a username and password.")
                elif reg_pass != reg_confirm:
                    st.warning("The passwords do not match.")
                elif len(reg_pass) < 8:
                    st.warning("Use a password with at least 8 characters.")
                elif register_user(user, reg_pass):
                    st.success("Account created. Sign in to continue.")
                else:
                    st.error("That username already exists.")
            st.markdown('Already have an account? <a href="?account=signin" target="_self">Sign in</a>', unsafe_allow_html=True)
        else:
            st.markdown("### Welcome back")
            st.caption("Sign in to continue to your research workspace.")
            show_password = st.checkbox("Show password while typing", key="signin_show_password")
            with st.form("login_form", clear_on_submit=False):
                login_user = st.text_input("Username", placeholder="Enter your username")
                password_type = "default" if show_password else "password"
                login_pass = st.text_input("Password", type=password_type, placeholder="Enter your password")
                login_submit = st.form_submit_button("Sign in", type="primary", width="stretch")
            if login_submit:
                if authenticate_user(login_user.strip(), login_pass):
                    token = create_session(login_user.strip())
                    st.session_state["session_token"] = token
                    st.query_params["session"] = token
                    st.rerun()
                else:
                    st.error("The username or password is incorrect.")
            st.markdown('New to the lab? <a href="?account=signup" target="_self">Create an account</a>', unsafe_allow_html=True)

    st.markdown("<div style='text-align:center;color:#b0bccd;font-size:.78rem;margin-top:25px'>SD‑QKD Authentication Simulator · Academic prototype</div>", unsafe_allow_html=True)


current_token = st.session_state.get("session_token") or st.query_params.get("session")
expired_session = False
active_user = None

if current_token:
    active_user = verify_session(current_token, max_idle_minutes=15)
    if not active_user:
        expired_session = True
        st.session_state.pop("session_token", None)
        try:
            del st.query_params["session"]
        except KeyError:
            pass
    else:
        st.session_state["session_token"] = current_token
        st.query_params["session"] = current_token

if not active_user:
    account_mode = st.query_params.get("account", "")
    if account_mode in {"signin", "signup"}:
        def account_page():
            render_quantum_background()
            st.markdown(
                "<style>[data-testid='stSidebar']{display:none;} .block-container{max-width:1180px;padding-top:2rem}</style>",
                unsafe_allow_html=True,
            )
            render_auth_page(account_mode, expired_session)

        public_page = st.Page(account_page, title="Account", icon=":material/lock:")
    else:
        public_page = st.Page(
            "pages/00_Landing.py",
            title="Project overview",
            icon=":material/home:",
        )

    # Explicit navigation disables Streamlit's automatic pages/ sidebar on every route.
    page = st.navigation([public_page], position="hidden")
else:
    st.session_state["active_user"] = active_user

    simulation_page = st.Page(
        "pages/01_Simulation.py",
        title="Live Simulation",
        icon=":material/science:",
        default=True,
    )
    reports_page = st.Page(
        "pages/02_Reports_Analytics.py",
        title="Reports & Analytics",
        icon=":material/analytics:",
    )
    visualization_page = st.Page(
        "pages/03_Quantum_Visualization.py",
        title="3D visualization",
        icon=":material/view_in_ar:",
    )
    page = st.navigation({"WORKSPACE": [simulation_page, visualization_page, reports_page]})

    st.sidebar.markdown(
        "<div style='padding:12px 4px 18px'><div style='font-family:IBM Plex Mono,monospace;font-size:10px;letter-spacing:.14em;color:#74f5ff;font-weight:500'>SD‑QKD LAB</div><div style='font-size:20px;font-weight:600;color:#f3f7ff;margin-top:5px'>Research Console</div></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(f"Signed in as **{active_user}**")
    st.sidebar.caption("Session expires after 15 minutes of inactivity.")
    
    if st.sidebar.button("Sign out", width="stretch"):
        if current_token:
            destroy_session(current_token)
        st.session_state.pop("session_token", None)
        st.session_state.pop("active_user", None)
        try:
            del st.query_params["session"]
        except KeyError:
            pass
        try:
            del st.query_params["account"]
        except KeyError:
            pass
        st.rerun()


page.run()

"""
Shared premium CSS theme — AI Vision Face Recognition System
FutureGain.in inspired dark glassmorphism design
"""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@700;900&display=swap');

/* ── Global ─────────────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: #040810 !important;
    color: #e0eeff !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 20% 10%, rgba(0,200,255,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(110,64,242,0.07) 0%, transparent 50%);
    pointer-events: none; z-index: 0;
}
[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }

/* ── Sidebar ────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(4,10,20,0.95) !important;
    border-right: 1px solid rgba(0,200,255,0.15) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] * { color: #c8dff0 !important; }
[data-testid="stSidebarContent"] { padding-top: 1.5rem; }

/* ── Hide Streamlit chrome ───────────────────────────────────────────────────── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
header { visibility: hidden !important; height: 0 !important; min-height: 0 !important; }
[data-testid="stApp"] { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }

/* ── Tabs ───────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] button {
    color: #7a9cc0 !important;
    font-weight: 600 !important;
    letter-spacing: .03em;
    border-bottom: 2px solid transparent !important;
    transition: all .2s;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00c8ff !important;
    border-bottom: 2px solid #00c8ff !important;
}
[data-testid="stTabContent"] { padding-top: 1.5rem; }

/* ── Buttons ────────────────────────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00c8ff22, #6e40f222) !important;
    border: 1px solid rgba(0,200,255,0.35) !important;
    color: #00c8ff !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    border-radius: 8px !important;
    transition: all .25s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00c8ff44, #6e40f244) !important;
    border-color: #00c8ff !important;
    box-shadow: 0 0 20px rgba(0,200,255,0.3) !important;
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00c8ff, #6e40f2) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(0,200,255,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 30px rgba(0,200,255,0.55) !important;
    transform: translateY(-2px);
}

/* ── Inputs ─────────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(0,200,255,0.05) !important;
    border: 1px solid rgba(0,200,255,0.2) !important;
    color: #e0eeff !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #00c8ff !important;
    box-shadow: 0 0 0 2px rgba(0,200,255,0.2) !important;
}
[data-baseweb="select"] { background: rgba(0,200,255,0.05) !important; }
[data-baseweb="select"] > div {
    background: rgba(4,10,22,0.9) !important;
    border: 1px solid rgba(0,200,255,0.2) !important;
    color: #e0eeff !important;
}
[data-baseweb="popover"] { background: #0a1628 !important; }
[data-baseweb="menu"] { background: #0a1628 !important; border: 1px solid rgba(0,200,255,0.2) !important; }
[data-baseweb="option"] { background: #0a1628 !important; color: #c8e8ff !important; }
[data-baseweb="option"]:hover { background: rgba(0,200,255,0.1) !important; }

/* ── Charts ─────────────────────────────────────────────────────────────────── */
[data-testid="stVegaLiteChart"] { background: transparent !important; }
[data-testid="stVegaLiteChart"] > div { background: transparent !important; }
.vega-embed { background: transparent !important; }
.vega-embed canvas, .marks canvas { background: #040810 !important; }

/* ── Sliders ────────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #00c8ff !important;
}

/* ── Divider ────────────────────────────────────────────────────────────────── */
hr { border-color: rgba(0,200,255,0.15) !important; }

/* ── Alerts / Info ──────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(0,200,255,0.06) !important;
    border: 1px solid rgba(0,200,255,0.2) !important;
    border-radius: 10px !important;
    color: #c0e8ff !important;
}

/* ── Dataframe ──────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

/* ── Expander ───────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(0,200,255,0.04) !important;
    border: 1px solid rgba(0,200,255,0.15) !important;
    border-radius: 10px !important;
}

/* ── Custom Components ──────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(8,20,40,0.7);
    border: 1px solid rgba(0,200,255,0.18);
    border-radius: 14px;
    padding: 22px 26px;
    backdrop-filter: blur(12px);
    transition: border-color .25s, box-shadow .25s;
}
.glass-card:hover {
    border-color: rgba(0,200,255,0.45);
    box-shadow: 0 4px 30px rgba(0,200,255,0.12);
}
.glass-card.purple { border-color: rgba(110,64,242,0.25); }
.glass-card.purple:hover { border-color: rgba(110,64,242,0.55); box-shadow: 0 4px 30px rgba(110,64,242,0.15); }

.kpi-card {
    background: rgba(8,20,40,0.8);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: 14px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform .2s, box-shadow .2s;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00c8ff, transparent);
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,200,255,0.15); }
.kpi-val { font-size: 2.6rem; font-weight: 800; line-height: 1; margin-bottom: 6px; }
.kpi-lbl { font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; color: #5a8ab0; }

.gradient-text {
    background: linear-gradient(135deg, #00c8ff, #a371f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.gradient-text-green {
    background: linear-gradient(135deg, #00e676, #00c8ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}

.page-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.9rem; font-weight: 700;
    background: linear-gradient(135deg, #00c8ff, #a371f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
}
.page-sub { font-size: .85rem; color: #4a7a9b; letter-spacing: .04em; margin-bottom: 1.5rem; }

.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,230,118,0.1);
    border: 1px solid rgba(0,230,118,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: .72rem; font-weight: 700;
    letter-spacing: .1em; color: #00e676;
    text-transform: uppercase;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00e676;
    animation: blink 1.4s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;box-shadow:0 0 6px #00e676} 50%{opacity:.3;box-shadow:none} }

.ai-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,200,255,0.1);
    border: 1px solid rgba(0,200,255,0.3);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: .7rem; font-weight: 600;
    letter-spacing: .06em; color: #00c8ff;
}

.face-result-card {
    background: rgba(8,20,40,0.85);
    border: 1px solid rgba(0,200,255,0.2);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    position: relative;
}
.face-result-card.known { border-color: rgba(0,230,118,0.4); }
.face-result-card.unknown { border-color: rgba(255,23,68,0.35); }
.face-result-card .face-name { font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
.face-result-card .face-meta { font-size: .8rem; color: #5a8ab0; line-height: 1.8; }

.nav-module-card {
    background: rgba(8,20,40,0.7);
    border: 1px solid rgba(0,200,255,0.12);
    border-radius: 14px;
    padding: 24px 20px;
    height: 130px;
    display: flex; flex-direction: column; justify-content: center;
    transition: all .25s;
    position: relative; overflow: hidden;
}
.nav-module-card::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00c8ff44, transparent);
    transition: opacity .25s;
}
.nav-module-card:hover {
    border-color: rgba(0,200,255,0.4);
    box-shadow: 0 6px 28px rgba(0,200,255,0.1);
    transform: translateY(-2px);
}
.nav-module-card .m-icon { font-size: 1.8rem; margin-bottom: 10px; }
.nav-module-card .m-title { font-size: .95rem; font-weight: 700; color: #c8e8ff; margin-bottom: 4px; }
.nav-module-card .m-desc { font-size: .75rem; color: #3d6a8a; line-height: 1.4; }

.sidebar-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem; font-weight: 900;
    background: linear-gradient(135deg, #00c8ff, #a371f7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: .08em;
}
.sidebar-divider { border-top: 1px solid rgba(0,200,255,0.12); margin: 12px 0; }
.sidebar-label { font-size: .65rem; letter-spacing: .12em; text-transform: uppercase; color: #2a5570 !important; }
.sidebar-value { font-size: .82rem; color: #8ab0cc !important; font-weight: 500; }
</style>
"""

SIDEBAR_HTML = """
<div class="sidebar-logo">AI VISION</div>
<div style="font-size:.62rem;letter-spacing:.12em;color:#2a5570;margin-top:2px;text-transform:uppercase">
  Face Recognition System
</div>
<div class="sidebar-divider"></div>
<div class="sidebar-label">Researcher</div>
<div class="sidebar-value">Jyotipriya Panda</div>
<div class="sidebar-value" style="color:#3a6070!important">Reg. 2407432009</div>
<div style="margin-top:8px" class="sidebar-label">Programme</div>
<div class="sidebar-value">M.Tech CSE 2024–2026</div>
<div class="sidebar-value" style="color:#3a6070!important">GIFT Bhubaneswar · BPUT</div>
<div style="margin-top:8px" class="sidebar-label">Supervisor</div>
<div class="sidebar-value">Asst. Prof. Mohapatra</div>
<div class="sidebar-value">Girashree Shau</div>
<div class="sidebar-divider"></div>
<div class="live-badge" style="margin-top:2px">
  <div class="live-dot"></div> System Online
</div>
<div style="margin-top:8px" class="ai-badge">⚡ LightFace-Net v1.0</div>
"""

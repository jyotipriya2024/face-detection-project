"""
Shared premium CSS theme — AI Vision Face Recognition System
Cross-browser glassmorphism dark design.
"""

THEME_CSS = """
<style>
/* ── Google Fonts ──────────────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@700;900&display=swap');

/* ── CSS Custom Properties ─────────────────────────────────────────────────── */
:root {
  --c-bg:       #040810;
  --c-surface:  rgba(8,20,40,0.80);
  --c-border:   rgba(0,200,255,0.18);
  --c-cyan:     #00c8ff;
  --c-purple:   #7b61ff;
  --c-green:    #00e676;
  --c-red:      #ff4d6d;
  --c-amber:    #ffab40;
  --c-text:     #e0eeff;
  --c-muted:    #5a8ab0;
  --c-dim:      #2a5570;
  --radius-sm:  8px;
  --radius-md:  14px;
  --radius-lg:  20px;
  --blur-sm:    blur(8px);
  --blur-md:    blur(16px);
  --transition: all 0.25s ease;
}

/* ── Global Reset & Base ───────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"] {
    background: var(--c-bg) !important;
    color: var(--c-text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
}

/* Ambient gradient overlay */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background:
        radial-gradient(ellipse at 18% 8%,  rgba(0,200,255,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 82% 82%, rgba(110,64,242,0.07) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(0,230,118,0.03) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}
[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }

/* ── Sidebar ────────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: rgba(3,8,18,0.97) !important;
    border-right: 1px solid rgba(0,200,255,0.12) !important;
    -webkit-backdrop-filter: blur(24px);
    backdrop-filter: blur(24px);
}
[data-testid="stSidebar"] * { color: #c8dff0 !important; }
[data-testid="stSidebarContent"] { padding-top: 1.5rem; }

/* ── Hide Streamlit chrome ──────────────────────────────────────────────────── */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
header { visibility: hidden !important; height: 0 !important; min-height: 0 !important; }
[data-testid="stApp"]              { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }

/* ── Tabs ───────────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] button {
    color: #7a9cc0 !important;
    font-weight: 600 !important;
    letter-spacing: .03em;
    border-bottom: 2px solid transparent !important;
    -webkit-transition: var(--transition);
    -moz-transition: var(--transition);
    transition: var(--transition);
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--c-cyan) !important;
    border-bottom: 2px solid var(--c-cyan) !important;
}
[data-testid="stTabContent"] { padding-top: 1.5rem; }

/* ── Buttons ────────────────────────────────────────────────────────────────── */
.stButton > button {
    background: -webkit-linear-gradient(135deg, #00c8ff22, #6e40f222) !important;
    background:         linear-gradient(135deg, #00c8ff22, #6e40f222) !important;
    border: 1px solid rgba(0,200,255,0.35) !important;
    color: var(--c-cyan) !important;
    font-weight: 600 !important;
    letter-spacing: .04em !important;
    border-radius: var(--radius-sm) !important;
    -webkit-transition: var(--transition) !important;
    -moz-transition: var(--transition) !important;
    transition: var(--transition) !important;
    cursor: pointer;
}
.stButton > button:hover {
    background: -webkit-linear-gradient(135deg, #00c8ff44, #6e40f244) !important;
    background:         linear-gradient(135deg, #00c8ff44, #6e40f244) !important;
    border-color: var(--c-cyan) !important;
    -webkit-box-shadow: 0 0 22px rgba(0,200,255,0.28) !important;
    box-shadow: 0 0 22px rgba(0,200,255,0.28) !important;
    -webkit-transform: translateY(-1px);
    -ms-transform: translateY(-1px);
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background: -webkit-linear-gradient(135deg, #00c8ff, #6e40f2) !important;
    background:         linear-gradient(135deg, #00c8ff, #6e40f2) !important;
    border: none !important;
    color: #fff !important;
    -webkit-box-shadow: 0 4px 20px rgba(0,200,255,0.35) !important;
    box-shadow: 0 4px 20px rgba(0,200,255,0.35) !important;
}
.stButton > button[kind="primary"]:hover {
    -webkit-box-shadow: 0 6px 30px rgba(0,200,255,0.55) !important;
    box-shadow: 0 6px 30px rgba(0,200,255,0.55) !important;
    -webkit-transform: translateY(-2px);
    -ms-transform: translateY(-2px);
    transform: translateY(-2px);
}

/* ── Danger / Delete button ─────────────────────────────────────────────────── */
.btn-danger > button {
    background: rgba(255,23,68,.10) !important;
    border-color: rgba(255,23,68,.35) !important;
    color: #ff4d6d !important;
}
.btn-danger > button:hover {
    background: rgba(255,23,68,.22) !important;
    border-color: #ff4d6d !important;
    -webkit-box-shadow: 0 0 18px rgba(255,23,68,.25) !important;
    box-shadow: 0 0 18px rgba(255,23,68,.25) !important;
}

/* ── Form Inputs ────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea {
    background: rgba(0,200,255,0.05) !important;
    border: 1px solid rgba(0,200,255,0.20) !important;
    color: var(--c-text) !important;
    border-radius: var(--radius-sm) !important;
    -webkit-transition: var(--transition);
    transition: var(--transition);
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--c-cyan) !important;
    -webkit-box-shadow: 0 0 0 3px rgba(0,200,255,0.15) !important;
    box-shadow: 0 0 0 3px rgba(0,200,255,0.15) !important;
    outline: none !important;
}
[data-baseweb="select"]       { background: rgba(0,200,255,0.05) !important; }
[data-baseweb="select"] > div {
    background: rgba(4,10,22,0.95) !important;
    border: 1px solid rgba(0,200,255,0.20) !important;
    color: var(--c-text) !important;
}
[data-baseweb="popover"] { background: #0a1628 !important; }
[data-baseweb="menu"]    { background: #0a1628 !important; border: 1px solid rgba(0,200,255,0.20) !important; }
[data-baseweb="option"]  { background: #0a1628 !important; color: #c8e8ff !important; }
[data-baseweb="option"]:hover { background: rgba(0,200,255,0.10) !important; }

/* Toggle */
[data-testid="stToggleSwitch"] > div { background-color: rgba(0,200,255,0.25) !important; }
[data-testid="stToggleSwitch"][aria-checked="true"] > div { background-color: var(--c-cyan) !important; }

/* ── Sliders ────────────────────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: var(--c-cyan) !important;
    -webkit-box-shadow: 0 0 10px rgba(0,200,255,0.5);
    box-shadow: 0 0 10px rgba(0,200,255,0.5);
}

/* ── Charts ─────────────────────────────────────────────────────────────────── */
[data-testid="stVegaLiteChart"] { background: transparent !important; }
[data-testid="stVegaLiteChart"] > div { background: transparent !important; }
.vega-embed          { background: transparent !important; }
.vega-embed canvas   { background: #040810 !important; }
.marks canvas        { background: #040810 !important; }

/* ── Divider ────────────────────────────────────────────────────────────────── */
hr { border-color: rgba(0,200,255,0.12) !important; }

/* ── Alerts ─────────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(0,200,255,0.06) !important;
    border: 1px solid rgba(0,200,255,0.22) !important;
    border-radius: 10px !important;
    color: #c0e8ff !important;
}

/* ── DataFrame ──────────────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: var(--radius-md); overflow: hidden; }
[data-testid="stDataFrame"] table {
    background: rgba(4,10,22,0.90) !important;
    color: var(--c-text) !important;
}
[data-testid="stDataFrame"] th {
    background: rgba(0,200,255,0.08) !important;
    color: var(--c-cyan) !important;
    font-weight: 600;
    letter-spacing: .04em;
    text-transform: uppercase;
    font-size: .72rem;
}
[data-testid="stDataFrame"] td { border-color: rgba(0,200,255,0.08) !important; }

/* ── Expander ───────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: rgba(0,200,255,0.04) !important;
    border: 1px solid rgba(0,200,255,0.14) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #c8e8ff !important; }

/* ── Metric ─────────────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: rgba(8,20,40,0.7);
    border: 1px solid rgba(0,200,255,0.15);
    border-radius: var(--radius-sm);
    padding: 12px 16px;
}
[data-testid="stMetricValue"]  { color: var(--c-cyan) !important; font-weight: 800; }
[data-testid="stMetricLabel"]  { color: var(--c-muted) !important; font-size: .72rem !important; }

/* ── Spinner ────────────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] { color: var(--c-cyan) !important; }

/* ── Progress bar ───────────────────────────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: -webkit-linear-gradient(90deg, var(--c-cyan), var(--c-purple)) !important;
    background:         linear-gradient(90deg, var(--c-cyan), var(--c-purple)) !important;
}

/* ── File Uploader ──────────────────────────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: rgba(0,200,255,0.04) !important;
    border: 2px dashed rgba(0,200,255,0.25) !important;
    border-radius: var(--radius-md) !important;
    -webkit-transition: var(--transition);
    transition: var(--transition);
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--c-cyan) !important;
    background: rgba(0,200,255,0.08) !important;
}

/* ── Camera Input ───────────────────────────────────────────────────────────── */
[data-testid="stCameraInput"] {
    border: 2px solid rgba(0,200,255,0.22) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
}

/* ═══════════════════════════════════════════════════════════════════════════
   CUSTOM COMPONENT LIBRARY
   ═══════════════════════════════════════════════════════════════════════════ */

/* ── Glass Card ─────────────────────────────────────────────────────────────── */
.glass-card {
    background: rgba(8,20,40,0.75);
    border: 1px solid var(--c-border);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    -webkit-backdrop-filter: var(--blur-sm);
    backdrop-filter: var(--blur-sm);
    -webkit-transition: border-color .25s, -webkit-box-shadow .25s;
    transition: border-color .25s, box-shadow .25s;
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: -webkit-linear-gradient(90deg, transparent, rgba(0,200,255,0.35), transparent);
    background:         linear-gradient(90deg, transparent, rgba(0,200,255,0.35), transparent);
}
.glass-card:hover {
    border-color: rgba(0,200,255,0.40);
    -webkit-box-shadow: 0 8px 32px rgba(0,200,255,0.10);
    box-shadow: 0 8px 32px rgba(0,200,255,0.10);
}
.glass-card.purple {
    border-color: rgba(110,64,242,0.22);
    background: rgba(12,6,30,0.75);
}
.glass-card.purple::before {
    background: -webkit-linear-gradient(90deg, transparent, rgba(110,64,242,0.35), transparent);
    background:         linear-gradient(90deg, transparent, rgba(110,64,242,0.35), transparent);
}
.glass-card.purple:hover {
    border-color: rgba(110,64,242,0.50);
    -webkit-box-shadow: 0 8px 32px rgba(110,64,242,0.14);
    box-shadow: 0 8px 32px rgba(110,64,242,0.14);
}
.glass-card.green {
    border-color: rgba(0,230,118,0.22);
    background: rgba(0,20,12,0.70);
}
.glass-card.green:hover {
    border-color: rgba(0,230,118,0.50);
    -webkit-box-shadow: 0 8px 32px rgba(0,230,118,0.12);
    box-shadow: 0 8px 32px rgba(0,230,118,0.12);
}
.glass-card.red {
    border-color: rgba(255,77,109,0.25);
    background: rgba(22,4,10,0.70);
}

/* ── KPI Card ───────────────────────────────────────────────────────────────── */
.kpi-card {
    background: rgba(8,20,40,0.85);
    border: 1px solid rgba(0,200,255,0.14);
    border-radius: var(--radius-md);
    padding: 22px 18px;
    text-align: center;
    position: relative;
    overflow: hidden;
    -webkit-transition: -webkit-transform .2s, -webkit-box-shadow .2s;
    transition: transform .2s, box-shadow .2s;
    cursor: default;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: -webkit-linear-gradient(90deg, transparent, currentColor, transparent);
    background:         linear-gradient(90deg, transparent, currentColor, transparent);
    opacity: 0.6;
}
.kpi-card::after {
    content: '';
    position: absolute; bottom: 0; right: 0;
    width: 60px; height: 60px;
    background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
    border-radius: 50%;
}
.kpi-card:hover {
    -webkit-transform: translateY(-3px);
    -ms-transform: translateY(-3px);
    transform: translateY(-3px);
    -webkit-box-shadow: 0 10px 36px rgba(0,200,255,0.14);
    box-shadow: 0 10px 36px rgba(0,200,255,0.14);
}
.kpi-val  { font-size: 2.4rem; font-weight: 800; line-height: 1; margin-bottom: 6px; font-variant-numeric: tabular-nums; }
.kpi-icon { font-size: 1.3rem; margin-bottom: 4px; }
.kpi-lbl  { font-size: .72rem; letter-spacing: .10em; text-transform: uppercase; color: #4a7a9a; }

/* ── Page Header ────────────────────────────────────────────────────────────── */
.page-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.85rem; font-weight: 700;
    background: -webkit-linear-gradient(135deg, var(--c-cyan), #a371f7);
    background:         linear-gradient(135deg, var(--c-cyan), #a371f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 2px;
}
.page-sub {
    font-size: .80rem; color: #3a6a8a; letter-spacing: .06em;
    text-transform: uppercase; margin-bottom: 1.5rem;
}

/* ── Section Label ──────────────────────────────────────────────────────────── */
.section-label {
    font-size: .62rem; letter-spacing: .18em; text-transform: uppercase;
    color: var(--c-dim); font-weight: 700; margin-bottom: 12px;
}

/* ── Gradient Text ──────────────────────────────────────────────────────────── */
.gradient-text {
    background: -webkit-linear-gradient(135deg, var(--c-cyan), #a371f7);
    background:         linear-gradient(135deg, var(--c-cyan), #a371f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.gradient-text-green {
    background: -webkit-linear-gradient(135deg, var(--c-green), var(--c-cyan));
    background:         linear-gradient(135deg, var(--c-green), var(--c-cyan));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Live Badge ─────────────────────────────────────────────────────────────── */
.live-badge {
    display: -webkit-inline-flex;
    display: inline-flex;
    -webkit-align-items: center;
    align-items: center;
    gap: 6px;
    background: rgba(0,230,118,0.10);
    border: 1px solid rgba(0,230,118,0.30);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: .70rem; font-weight: 700;
    letter-spacing: .10em; color: var(--c-green);
    text-transform: uppercase;
    white-space: nowrap;
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--c-green);
    -webkit-animation: blink 1.4s ease-in-out infinite;
    animation: blink 1.4s ease-in-out infinite;
    -webkit-flex-shrink: 0;
    flex-shrink: 0;
}
@-webkit-keyframes blink {
    0%,100% { opacity:1; -webkit-box-shadow: 0 0 6px var(--c-green); box-shadow: 0 0 6px var(--c-green); }
    50%      { opacity:.3; -webkit-box-shadow: none; box-shadow: none; }
}
@keyframes blink {
    0%,100% { opacity:1; box-shadow: 0 0 6px var(--c-green); }
    50%      { opacity:.3; box-shadow: none; }
}

/* ── AI Badge ───────────────────────────────────────────────────────────────── */
.ai-badge {
    display: -webkit-inline-flex;
    display: inline-flex;
    -webkit-align-items: center;
    align-items: center;
    gap: 5px;
    background: rgba(0,200,255,0.09);
    border: 1px solid rgba(0,200,255,0.28);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: .68rem; font-weight: 600;
    letter-spacing: .06em; color: var(--c-cyan);
    white-space: nowrap;
}
.ai-badge.amber {
    background: rgba(255,171,64,0.09);
    border-color: rgba(255,171,64,0.28);
    color: var(--c-amber);
}
.ai-badge.red {
    background: rgba(255,77,109,0.09);
    border-color: rgba(255,77,109,0.28);
    color: var(--c-red);
}
.ai-badge.green {
    background: rgba(0,230,118,0.09);
    border-color: rgba(0,230,118,0.28);
    color: var(--c-green);
}
.ai-badge.purple {
    background: rgba(123,97,255,0.09);
    border-color: rgba(123,97,255,0.28);
    color: var(--c-purple);
}

/* ── Quality Score Bar ──────────────────────────────────────────────────────── */
.quality-bar-wrap {
    background: rgba(0,200,255,0.07);
    border-radius: 6px; height: 8px; overflow: hidden;
    margin: 4px 0;
}
.quality-bar-fill {
    height: 8px; border-radius: 6px;
    -webkit-transition: width .5s ease;
    transition: width .5s ease;
}

/* ── Face Result Card ───────────────────────────────────────────────────────── */
.face-result-card {
    background: rgba(8,20,40,0.90);
    border: 1px solid rgba(0,200,255,0.18);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 10px;
    -webkit-transition: var(--transition);
    transition: var(--transition);
    position: relative;
}
.face-result-card:hover {
    -webkit-transform: translateX(3px);
    -ms-transform: translateX(3px);
    transform: translateX(3px);
}
.face-result-card.known   { border-color: rgba(0,230,118,0.40); }
.face-result-card.unknown { border-color: rgba(255,77,109,0.35); }
.face-result-card .face-name { font-size: 1rem; font-weight: 700; margin-bottom: 6px; }
.face-result-card .face-meta { font-size: .78rem; color: var(--c-muted); line-height: 1.9; }

/* ── Nav Module Card ────────────────────────────────────────────────────────── */
.nav-module-card {
    background: rgba(8,20,40,0.72);
    border: 1px solid rgba(0,200,255,0.11);
    border-radius: var(--radius-md);
    padding: 22px 20px;
    min-height: 130px;
    display: -webkit-flex;
    display: flex;
    -webkit-flex-direction: column;
    flex-direction: column;
    -webkit-justify-content: center;
    justify-content: center;
    -webkit-transition: var(--transition);
    transition: var(--transition);
    position: relative; overflow: hidden;
    cursor: pointer;
}
.nav-module-card::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: -webkit-linear-gradient(90deg, transparent, rgba(0,200,255,0.35), transparent);
    background:         linear-gradient(90deg, transparent, rgba(0,200,255,0.35), transparent);
    opacity: 0;
    -webkit-transition: opacity .25s;
    transition: opacity .25s;
}
.nav-module-card:hover {
    border-color: rgba(0,200,255,0.40);
    -webkit-box-shadow: 0 8px 28px rgba(0,200,255,0.11);
    box-shadow: 0 8px 28px rgba(0,200,255,0.11);
    -webkit-transform: translateY(-3px);
    -ms-transform: translateY(-3px);
    transform: translateY(-3px);
}
.nav-module-card:hover::after { opacity: 1; }
.nav-module-card .m-icon  { font-size: 1.8rem; margin-bottom: 8px; }
.nav-module-card .m-title { font-size: .92rem; font-weight: 700; color: #c8e8ff; margin-bottom: 4px; }
.nav-module-card .m-desc  { font-size: .73rem; color: #3a6a8a; line-height: 1.4; }
.nav-module-card .m-badge { margin-top: 10px; }

/* ── Person Avatar ──────────────────────────────────────────────────────────── */
.person-avatar {
    width: 48px; height: 48px; border-radius: 50%;
    display: -webkit-flex;
    display: flex;
    -webkit-align-items: center;
    align-items: center;
    -webkit-justify-content: center;
    justify-content: center;
    font-size: 1.2rem; font-weight: 800;
    -webkit-flex-shrink: 0;
    flex-shrink: 0;
    letter-spacing: -.02em;
}

/* ── Sidebar ────────────────────────────────────────────────────────────────── */
.sidebar-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem; font-weight: 900;
    background: -webkit-linear-gradient(135deg, var(--c-cyan), #a371f7);
    background:         linear-gradient(135deg, var(--c-cyan), #a371f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: .08em;
}
.sidebar-divider { border-top: 1px solid rgba(0,200,255,0.10); margin: 12px 0; }
.sidebar-label   { font-size: .60rem; letter-spacing: .14em; text-transform: uppercase; color: var(--c-dim) !important; }
.sidebar-value   { font-size: .80rem; color: #8ab0cc !important; font-weight: 500; }

/* ── Confidence Bar ─────────────────────────────────────────────────────────── */
.conf-bar {
    background: rgba(0,200,255,0.07);
    border-radius: 4px; height: 5px; overflow: hidden; margin: 2px 0 6px;
}
.conf-bar-fill {
    height: 5px; border-radius: 4px;
    background: -webkit-linear-gradient(90deg, var(--c-cyan), var(--c-purple));
    background:         linear-gradient(90deg, var(--c-cyan), var(--c-purple));
}

/* ── Stat Row ───────────────────────────────────────────────────────────────── */
.stat-row {
    display: -webkit-flex;
    display: flex;
    -webkit-justify-content: space-between;
    justify-content: space-between;
    -webkit-align-items: center;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid rgba(0,200,255,0.08);
    font-size: .83rem;
}
.stat-row:last-child { border-bottom: none; }
.stat-row .stat-key   { color: var(--c-muted); }
.stat-row .stat-val   { color: #c8e8ff; font-weight: 600; }

/* ── Scroll Bar ─────────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
::-webkit-scrollbar-thumb { background: rgba(0,200,255,0.30); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,200,255,0.55); }

/* ── Utility spacers ────────────────────────────────────────────────────────── */
.sp8  { height: 8px; }
.sp16 { height: 16px; }
.sp24 { height: 24px; }
.sp32 { height: 32px; }
</style>
"""

SIDEBAR_HTML = """
<div class="sidebar-logo">AI VISION</div>
<div style="font-size:.60rem;letter-spacing:.13em;color:#2a5570;margin-top:2px;text-transform:uppercase">
  Face Recognition System
</div>
<div class="sidebar-divider"></div>
<div class="sidebar-label">Researcher</div>
<div class="sidebar-value">Jyotipriya Panda</div>
<div class="sidebar-value" style="color:#3a6070!important">Reg. 2407432009</div>
<div style="margin-top:8px" class="sidebar-label">Programme</div>
<div class="sidebar-value">M.Tech CSE 2024&ndash;2026</div>
<div class="sidebar-value" style="color:#3a6070!important">GIFT Bhubaneswar &middot; BPUT</div>
<div style="margin-top:8px" class="sidebar-label">Supervisor</div>
<div class="sidebar-value">Asst. Prof. Mohapatra</div>
<div class="sidebar-value">Girashree Shau</div>
<div class="sidebar-divider"></div>
<div class="live-badge" style="margin-top:2px">
  <div class="live-dot"></div>&nbsp;System Online
</div>
<div style="margin-top:8px">
  <span class="ai-badge">&#9889; LightFace-Net v2.0</span>
</div>
"""

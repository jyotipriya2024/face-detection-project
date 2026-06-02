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

/* ── Sidebar Shell ──────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b1220 !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    min-width: 220px !important;
    max-width: 240px !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; }
[data-testid="stSidebarContent"] * { color: #8ab0cc !important; }

/* ── Hide Streamlit chrome (specific selectors only — never generic 'header') ── */
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: visible !important;
}
[data-testid="stApp"]                { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }

/* ── Sidebar Navigation ─────────────────────────────────────────────────────── */
[data-testid="stSidebarNav"] {
    padding: 0 !important;
    margin-top: 0 !important;
}
/* "MAIN" section label */
[data-testid="stSidebarNav"]::before {
    content: 'MAIN';
    display: block;
    font-size: 0.60rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    color: #2a4255 !important;
    text-transform: uppercase;
    padding: 14px 16px 6px;
    font-family: 'Inter', sans-serif;
}
[data-testid="stSidebarNavItems"] {
    padding: 0 8px 4px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 1px !important;
}
[data-testid="stSidebarNavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 9px !important;
    padding: 9px 10px 9px 12px !important;
    margin: 0 !important;
    border-radius: 8px !important;
    border-left: 3px solid transparent !important;
    color: #6a8fa8 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.01em !important;
    text-decoration: none !important;
    transition: background 0.15s, color 0.15s, border-color 0.15s !important;
    background: transparent !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(255,255,255,0.055) !important;
    color: #c0daf0 !important;
    border-left-color: rgba(0,200,255,0.35) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(0,200,255,0.10) !important;
    color: #40d4ff !important;
    font-weight: 600 !important;
    border-left-color: #00c8ff !important;
}
[data-testid="stSidebarNavLink"] span,
[data-testid="stSidebarNavLink"] p {
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}
[data-testid="stSidebarNavSeparator"] {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 6px 10px !important;
}

/* ── Sidebar collapse / expand buttons ──────────────────────────────────────── */
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] * {
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}
[data-testid="collapsedControl"] {
    display: flex !important;
    z-index: 9999 !important;
    background: rgba(11,18,32,0.90) !important;
    border: 1px solid rgba(0,200,255,0.28) !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="collapsedControl"] svg { color: #00c8ff !important; fill: #00c8ff !important; }
[data-testid="collapsedControl"]:hover {
    background: rgba(0,200,255,0.12) !important;
    border-color: #00c8ff !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] * {
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
}
[data-testid="stSidebarCollapseButton"] button { background: transparent !important; }
[data-testid="stSidebarCollapseButton"] svg    { color: #3a6a8a !important; fill: #3a6a8a !important; }

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

LIGHT_CSS = """
<style>
:root {
  --c-bg:       #f0f4f8;
  --c-surface:  rgba(255,255,255,0.90);
  --c-border:   rgba(0,120,200,0.18);
  --c-cyan:     #0080c8;
  --c-purple:   #5a3fd0;
  --c-green:    #00a854;
  --c-red:      #d63050;
  --c-amber:    #d4840a;
  --c-text:     #0a1a2e;
  --c-muted:    #4a6a8a;
  --c-dim:      #7a9ab0;
  --radius-sm:  8px;
  --radius-md:  14px;
  --radius-lg:  20px;
  --blur-sm:    blur(8px);
  --blur-md:    blur(16px);
  --transition: all 0.25s ease;
}
html, body, [data-testid="stAppViewContainer"] {
    background: var(--c-bg) !important;
    color: var(--c-text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}
[data-testid="stSidebar"] {
    background: rgba(230,238,248,0.98) !important;
    border-right: 1px solid rgba(0,120,200,0.15) !important;
}
[data-testid="stSidebar"] * { color: #1a3a5a !important; }
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
}
[data-testid="stHeader"] {
    background: transparent !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: visible !important;
}
[data-testid="stApp"] { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1rem !important; }
[data-testid="collapsedControl"],
[data-testid="collapsedControl"] * { visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
[data-testid="collapsedControl"] {
    display: flex !important; z-index: 9999 !important;
    background: rgba(220,235,250,0.95) !important;
    border: 1px solid rgba(0,120,200,0.35) !important;
    border-radius: 0 10px 10px 0 !important;
}
[data-testid="collapsedControl"] svg { color: #0080c8 !important; fill: #0080c8 !important; }
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapseButton"] * { visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
[data-testid="stSidebarCollapseButton"] svg { color: #0080c8 !important; fill: #0080c8 !important; }
[data-testid="stSidebarNavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 10px 14px !important;
    margin: 3px 0 !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    color: #1a3a6a !important;
    font-size: 0.86rem !important;
    font-weight: 600 !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    background: rgba(0,120,200,0.05) !important;
}
[data-testid="stSidebarNavLink"]:hover {
    background: rgba(0,120,200,0.12) !important;
    border-color: rgba(0,120,200,0.40) !important;
    color: #0060a8 !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: linear-gradient(135deg, rgba(0,120,200,0.18), rgba(90,63,208,0.18)) !important;
    border-color: rgba(0,120,200,0.55) !important;
    color: #0060a8 !important;
}
.stButton > button {
    background: linear-gradient(135deg, #0080c822, #5a3fd022) !important;
    border: 1px solid rgba(0,120,200,0.35) !important;
    color: var(--c-cyan) !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition) !important;
}
.page-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.85rem; font-weight: 700;
    background: linear-gradient(135deg, var(--c-cyan), #7b61ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.glass-card {
    background: rgba(255,255,255,0.80);
    border: 1px solid rgba(0,120,200,0.15);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    backdrop-filter: var(--blur-sm);
}
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.05); }
::-webkit-scrollbar-thumb { background: rgba(0,120,200,0.30); border-radius: 4px; }
</style>
"""


def get_theme_css(mode: str = "Dark") -> str:
    return THEME_CSS if mode == "Dark" else LIGHT_CSS


SIDEBAR_HTML = """
<style>
/* ── Sidebar header logo area ───────────────────────────────────────────────── */
.sb-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 14px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.07);
    margin-bottom: 4px;
}
.sb-logo-icon {
    width: 32px; height: 32px; border-radius: 8px;
    background: linear-gradient(135deg, #00c8ff, #7b61ff);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.sb-logo-text { line-height: 1.2; }
.sb-logo-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.80rem; font-weight: 900;
    color: #e0eeff !important;
    letter-spacing: 0.08em;
}
.sb-logo-sub {
    font-size: 0.58rem; color: #2e4a60 !important;
    letter-spacing: 0.10em; text-transform: uppercase; margin-top: 1px;
}

/* ── Info section ───────────────────────────────────────────────────────────── */
.sb-section-label {
    font-size: 0.58rem; font-weight: 700;
    letter-spacing: 0.16em; text-transform: uppercase;
    color: #2a4255 !important; padding: 14px 16px 6px;
}
.sb-info-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 14px; font-size: 0.78rem;
}
.sb-info-key  { color: #3a5570 !important; font-size: 0.72rem; }
.sb-info-val  { color: #8ab0cc !important; font-weight: 500; font-size: 0.78rem; }
.sb-divider   { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 8px 10px; }

/* ── Status row at bottom ───────────────────────────────────────────────────── */
.sb-status {
    padding: 10px 14px 14px;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin-top: 8px;
}
.sb-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,230,118,0.10);
    border: 1px solid rgba(0,230,118,0.25);
    border-radius: 20px; padding: 3px 10px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.08em; color: #00e676 !important;
    text-transform: uppercase;
}
.sb-badge-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #00e676; flex-shrink: 0;
    animation: blink 1.4s ease-in-out infinite;
}
.sb-engine-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(0,200,255,0.08);
    border: 1px solid rgba(0,200,255,0.20);
    border-radius: 20px; padding: 3px 9px;
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.04em; color: #4a9ab8 !important;
    margin-top: 6px; white-space: nowrap;
}
</style>

<div class="sb-header">
  <div class="sb-logo-icon">🤖</div>
  <div class="sb-logo-text">
    <div class="sb-logo-title">AI VISION</div>
    <div class="sb-logo-sub">Face Recognition</div>
  </div>
</div>

<div class="sb-section-label">RESEARCHER</div>
<div class="sb-info-row">
  <span class="sb-info-key">Name</span>
  <span class="sb-info-val">Jyotipriya Panda</span>
</div>
<div class="sb-info-row">
  <span class="sb-info-key">Reg.</span>
  <span class="sb-info-val">2407432009</span>
</div>
<div class="sb-info-row">
  <span class="sb-info-key">Programme</span>
  <span class="sb-info-val">M.Tech CSE</span>
</div>
<div class="sb-info-row">
  <span class="sb-info-key">Batch</span>
  <span class="sb-info-val">2024&ndash;2026</span>
</div>
<div class="sb-info-row">
  <span class="sb-info-key">Institute</span>
  <span class="sb-info-val">GIFT Bhubaneswar</span>
</div>

<hr class="sb-divider">

<div class="sb-section-label">SUPERVISOR</div>
<div class="sb-info-row">
  <span class="sb-info-val" style="font-size:0.76rem!important">Asst. Prof. Mohapatra<br>
  <span style="color:#2e4a60!important;font-size:0.70rem">Girashree Shau</span></span>
</div>

<div class="sb-status">
  <div><span class="sb-badge"><span class="sb-badge-dot"></span>System Online</span></div>
  <div><span class="sb-engine-badge">⚡ LightFace-Net v2.0</span></div>
</div>
"""

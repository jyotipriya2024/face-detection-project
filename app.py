"""
AI Vision Face Recognition System — Main Dashboard
Jyotipriya Panda | Reg. 2407432009 | M.Tech CSE 2024-2026 | GIFT Bhubaneswar
Supervisor: Asst. Prof. Mohapatra Girashree Shau
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from database import get_person_count, get_log_stats
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(
    page_title="AI Vision — Face Recognition System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "AI Vision Face Recognition System · M.Tech CSE · GIFT Bhubaneswar"
    }
)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    theme_mode = st.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode",
                          label_visibility="collapsed")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

# ── Style page-link elements to match the dark theme ──────────────────────────
st.markdown("""
<style>
/* ── Navigation module cards (wraps st.page_link) ────────────────────────── */
.mod-card {
    background: rgba(8,20,40,0.72);
    border: 1px solid rgba(0,200,255,0.13);
    border-radius: 14px;
    padding: 20px 18px 10px;
    transition: border-color .25s, box-shadow .25s, transform .22s;
    position: relative; overflow: hidden;
    margin-bottom: 0;
}
.mod-card:hover {
    border-color: rgba(0,200,255,0.42);
    box-shadow: 0 8px 28px rgba(0,200,255,0.11);
    transform: translateY(-3px);
}
.mod-card::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,transparent,rgba(0,200,255,0.30),transparent);
}
.mod-icon  { font-size:1.9rem; margin-bottom:8px; }
.mod-title { font-size:.95rem; font-weight:700; color:#c8e8ff; margin-bottom:3px; }
.mod-desc  { font-size:.73rem; color:#3a6a8a; line-height:1.45; margin-bottom:14px; }

/* page_link anchor — full-width pill button */
[data-testid="stPageLink"] > a {
    display:block !important;
    width:100% !important;
    padding:8px 14px !important;
    border-radius:8px !important;
    border:1px solid rgba(0,200,255,0.35) !important;
    background:linear-gradient(135deg,rgba(0,200,255,0.10),rgba(110,64,242,0.10)) !important;
    color:#00c8ff !important;
    font-size:.76rem !important;
    font-weight:700 !important;
    letter-spacing:.06em !important;
    text-align:center !important;
    text-decoration:none !important;
    transition:all .22s !important;
}
[data-testid="stPageLink"] > a:hover {
    background:linear-gradient(135deg,rgba(0,200,255,0.22),rgba(110,64,242,0.22)) !important;
    border-color:#00c8ff !important;
    box-shadow:0 0 16px rgba(0,200,255,0.25) !important;
    transform:translateY(-1px) !important;
    color:#fff !important;
}
/* hide the default external-link icon that appears in some versions */
[data-testid="stPageLink"] svg { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:44px 0 12px">
  <div style="font-family:'Orbitron',sans-serif;font-size:3.4rem;font-weight:900;
              background:linear-gradient(135deg,#00c8ff,#7b61ff,#a371f7);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              background-clip:text;letter-spacing:.06em;line-height:1.1">
    AI VISION
  </div>
  <div style="font-size:1.05rem;color:#3a7a9c;letter-spacing:.20em;text-transform:uppercase;
              margin-top:8px;font-weight:500">
    Real-Time Face Recognition System
  </div>
  <div style="margin-top:16px;display:-webkit-flex;display:flex;
              -webkit-justify-content:center;justify-content:center;
              gap:10px;flex-wrap:wrap">
    <span class="live-badge"><div class="live-dot"></div>&nbsp;Live AI Engine</span>
    <span class="ai-badge">&#9889; LightFace-Net v2.0</span>
    <span class="ai-badge">&#127891; M.Tech Research</span>
    <span class="ai-badge">&#127963; GIFT Bhubaneswar</span>
    <span class="ai-badge amber">&#128273; OpenCV &middot; MediaPipe</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='sp16'></div>", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
try:
    stats     = get_log_stats()
    n_persons = get_person_count()
    recog_pct = (
        round(stats['known'] / max(stats['total'], 1) * 100, 1)
        if stats['total'] > 0 else 0
    )
except Exception:
    stats = {'total': 0, 'known': 0, 'unknown': 0, 'today': 0, 'avg_confidence': 0}
    n_persons = 0
    recog_pct = 0

kpi_data = [
    (n_persons,              "Registered",     "#00c8ff", "👥"),
    (stats['total'],         "Detections",     "#7b61ff", "📡"),
    (stats['known'],         "Recognised",     "#00e676", "✅"),
    (stats['unknown'],       "Unknown",        "#ff4d6d", "❓"),
    (stats.get('today', 0),  "Today",          "#ffab40", "📅"),
]

cols = st.columns(5)
for col, (val, lbl, color, icon) in zip(cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}22;color:{color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-val" style="color:{color}">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div class='sp24'></div>", unsafe_allow_html=True)

# ── System Status Bar ─────────────────────────────────────────────────────────
avg_c = stats.get('avg_confidence', 0)
st.markdown(f"""
<div class="glass-card" style="padding:16px 24px;margin-bottom:0">
  <div style="display:-webkit-flex;display:flex;-webkit-align-items:center;
              align-items:center;gap:20px;flex-wrap:wrap">
    <div style="font-size:.62rem;letter-spacing:.14em;text-transform:uppercase;
                color:#2a5570;font-weight:700;white-space:nowrap">◈ SYSTEM STATUS</div>
    <div style="display:-webkit-flex;display:flex;gap:14px;flex-wrap:wrap;-webkit-flex:1;flex:1">
      <div class="stat-row" style="border:none;padding:0">
        <span class="stat-key" style="margin-right:6px">Recognition Rate</span>
        <span class="stat-val" style="color:#00e676">{recog_pct}%</span>
      </div>
      <div style="width:1px;background:rgba(0,200,255,.12)"></div>
      <div class="stat-row" style="border:none;padding:0">
        <span class="stat-key" style="margin-right:6px">Avg Confidence</span>
        <span class="stat-val" style="color:#ffab40">{avg_c:.1%}</span>
      </div>
      <div style="width:1px;background:rgba(0,200,255,.12)"></div>
      <div class="stat-row" style="border:none;padding:0">
        <span class="stat-key" style="margin-right:6px">Database</span>
        <span class="stat-val" style="color:#00c8ff">{n_persons} persons enrolled</span>
      </div>
      <div style="width:1px;background:rgba(0,200,255,.12)"></div>
      <div class="stat-row" style="border:none;padding:0">
        <span class="stat-key" style="margin-right:6px">Engine</span>
        <span class="stat-val" style="color:#a371f7">LBP+HOG+YCrCb · 416-d</span>
      </div>
    </div>
    <div><span class="live-badge"><div class="live-dot"></div>&nbsp;Operational</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='sp24'></div>", unsafe_allow_html=True)

# ── Module Grid ───────────────────────────────────────────────────────────────
st.markdown("""<div class="section-label">◈ SYSTEM MODULES</div>""",
            unsafe_allow_html=True)

modules = [
    ("📝", "Register Face",
     "Enrol persons via webcam · face quality check · embedding generation",
     "pages/1_📝_Register.py"),
    ("🎥", "Live Detection",
     "Real-time recognition · emotion · age · gender estimation",
     "pages/2_🎥_Live_Detection.py"),
    ("🔍", "Face Search",
     "Upload any image — identify & match faces against the database",
     "pages/3_🔍_Search.py"),
    ("📊", "Analytics",
     "Trends · emotion charts · confidence histogram · weekday heatmap",
     "pages/4_📊_Analytics.py"),
    ("📋", "Event Logs",
     "Detection history · date range filter · CSV / JSON / TSV export",
     "pages/5_📋_Logs.py"),
    ("👥", "Person Registry",
     "Browse · edit · search · last-seen · manage enrolled persons",
     "pages/6_👥_Registry.py"),
]

r1 = st.columns(3, gap="medium")
r2 = st.columns(3, gap="medium")
for i, (icon, title, desc, page_path) in enumerate(modules):
    col = (r1 if i < 3 else r2)[i % 3]
    with col:
        st.markdown(f"""
        <div class="mod-card">
          <div class="mod-icon">{icon}</div>
          <div class="mod-title">{title}</div>
          <div class="mod-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)
        st.page_link(page_path, label=f"Open {title} →", use_container_width=True)

st.markdown("<div class='sp24'></div>", unsafe_allow_html=True)

# ── Quick Start & About Row ───────────────────────────────────────────────────
qa_col, ab_col = st.columns([1, 1], gap="large")

with qa_col:
    st.markdown("""
    <div class="glass-card" style="height:100%">
      <div class="section-label">◈ QUICK START GUIDE</div>
      <div style="font-size:.82rem;color:#5a8ab0;line-height:2.1">
        <div><span style="color:#00c8ff;font-weight:700">1.</span>
          &nbsp;Go to <b style="color:#c8e8ff">Register Face</b> to enrol persons</div>
        <div><span style="color:#00c8ff;font-weight:700">2.</span>
          &nbsp;Allow camera access when prompted</div>
        <div><span style="color:#00c8ff;font-weight:700">3.</span>
          &nbsp;Capture a clear, well-lit face photo</div>
        <div><span style="color:#00c8ff;font-weight:700">4.</span>
          &nbsp;Fill in person details &amp; click <b style="color:#c8e8ff">Register</b></div>
        <div><span style="color:#7b61ff;font-weight:700">5.</span>
          &nbsp;Go to <b style="color:#c8e8ff">Live Detection</b> to recognise faces</div>
        <div><span style="color:#7b61ff;font-weight:700">6.</span>
          &nbsp;Upload an image in <b style="color:#c8e8ff">Face Search</b> to identify anyone</div>
        <div><span style="color:#ffab40;font-weight:700">7.</span>
          &nbsp;View trends in <b style="color:#c8e8ff">Analytics</b> &amp; export logs</div>
      </div>
    </div>""", unsafe_allow_html=True)

with ab_col:
    st.markdown("""
    <div class="glass-card" style="height:100%">
      <div class="section-label">◈ TECHNOLOGY STACK</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px">
        <div class="glass-card" style="padding:12px 14px;margin:0">
          <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;letter-spacing:.08em">Detection</div>
          <div style="font-size:.82rem;color:#c8e8ff;margin-top:2px">MediaPipe + Haar</div>
        </div>
        <div class="glass-card" style="padding:12px 14px;margin:0">
          <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;letter-spacing:.08em">Embedding</div>
          <div style="font-size:.82rem;color:#c8e8ff;margin-top:2px">LBP + HOG + YCrCb</div>
        </div>
        <div class="glass-card" style="padding:12px 14px;margin:0">
          <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;letter-spacing:.08em">Matching</div>
          <div style="font-size:.82rem;color:#c8e8ff;margin-top:2px">Cosine Similarity</div>
        </div>
        <div class="glass-card" style="padding:12px 14px;margin:0">
          <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;letter-spacing:.08em">Database</div>
          <div style="font-size:.82rem;color:#c8e8ff;margin-top:2px">SQLite WAL mode</div>
        </div>
      </div>
      <div style="font-size:.70rem;color:#2a5070;line-height:1.6;text-align:center">
        Gandhi Institute for Technology &middot; Autonomous &middot; BPUT Rourkela<br>
        M.Tech CSE 2024&ndash;2026 Research Project
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div class='sp16'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;font-size:.65rem;color:#1a3a50;letter-spacing:.06em">
  AI Vision Face Recognition System &middot; M.Tech CSE 2024&ndash;2026 &middot; GIFT Bhubaneswar
  &middot; All rights reserved
</div>""", unsafe_allow_html=True)

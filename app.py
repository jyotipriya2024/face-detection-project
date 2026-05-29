"""
AI Vision Face Recognition System — Premium Dashboard
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
    initial_sidebar_state="expanded"
)

theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
  st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 10px">
  <div style="font-family:'Orbitron',sans-serif;font-size:3.2rem;font-weight:900;
              background:linear-gradient(135deg,#00c8ff,#7b61ff,#a371f7);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              background-clip:text;letter-spacing:.06em;line-height:1.1">
    AI VISION
  </div>
  <div style="font-size:1.05rem;color:#3a7a9c;letter-spacing:.18em;text-transform:uppercase;
              margin-top:8px;font-weight:500">
    Real-Time Face Recognition System
  </div>
  <div style="margin-top:14px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap">
    <span class="live-badge"><div class="live-dot"></div>Live AI Engine</span>
    <span class="ai-badge">⚡ LightFace-Net</span>
    <span class="ai-badge">🎓 M.Tech Research</span>
    <span class="ai-badge">🏛️ GIFT Bhubaneswar</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
stats     = get_log_stats()
n_persons = get_person_count()
kpi_data  = [
    (n_persons,          "Registered Persons", "#00c8ff", "👥"),
    (stats['total'],     "Total Detections",   "#7b61ff", "📡"),
    (stats['known'],     "Recognised Faces",   "#00e676", "✅"),
    (stats['unknown'],   "Unknown Faces",      "#ff4d6d", "❓"),
    (stats.get('today',0), "Detections Today", "#ffab40", "📅"),
]

cols = st.columns(5)
for col, (val, lbl, color, icon) in zip(cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}22">
          <div class="kpi-val" style="color:{color}">{val}</div>
          <div class="kpi-lbl">{icon} {lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── Module Grid ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="font-size:.65rem;letter-spacing:.18em;text-transform:uppercase;
            color:#2a5570;margin-bottom:14px;font-weight:600">
  ◈ SYSTEM MODULES
</div>""", unsafe_allow_html=True)

modules = [
    ("📝", "Register Face",      "Enroll persons via webcam + metadata",   "#00c8ff"),
    ("🎥", "Live Detection",     "Real-time recognition · emotion · age",  "#7b61ff"),
    ("🔍", "Face Search",        "Upload any image — identify faces",      "#00e676"),
    ("📊", "Analytics",          "Charts · trends · emotion statistics",   "#ffab40"),
    ("📋", "Event Logs",         "Detection history · CSV/JSON export",    "#ff4d6d"),
    ("👥", "Person Registry",    "Browse · search · manage persons",       "#00c8ff"),
]

r1 = st.columns(3)
r2 = st.columns(3)
for i, (icon, title, desc, color) in enumerate(modules):
    col = (r1 if i < 3 else r2)[i % 3]
    with col:
        st.markdown(f"""
        <div class="nav-module-card" style="border-color:{color}22">
          <div class="m-icon">{icon}</div>
          <div class="m-title">{title}</div>
          <div class="m-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

# ── About ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="glass-card" style="display:flex;justify-content:space-between;
     align-items:center;flex-wrap:wrap;gap:16px">
  <div>
    <div style="font-size:.95rem;font-weight:700;color:#c8e8ff;margin-bottom:4px">
      LightFace-Net Architecture
    </div>
    <div style="font-size:.78rem;color:#3a6a8a;line-height:1.7">
      Custom lightweight face recognition CNN · LBP + HOG feature extraction<br>
      256-d cosine similarity matching · Real-time emotion & age/gender estimation
    </div>
  </div>
  <div style="text-align:right">
    <div style="font-size:.7rem;letter-spacing:.1em;color:#2a5070;text-transform:uppercase">
      Gandhi Institute for Technology
    </div>
    <div style="font-size:.7rem;color:#2a5070">Autonomous · BPUT Rourkela</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;margin-top:18px;font-size:.68rem;color:#1a3a50;
            letter-spacing:.06em">
  AI Vision Face Recognition System · M.Tech CSE 2024–2026 · GIFT Bhubaneswar
</div>""", unsafe_allow_html=True)

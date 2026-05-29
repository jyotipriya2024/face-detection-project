"""
Event Logs — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_logs
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Event Logs · AI Vision", page_icon="📋", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ FILTER OPTIONS</div>", unsafe_allow_html=True)
    limit          = st.slider("Max Records", 50, 2000, 500, 50)
    filter_name    = st.text_input("Filter by Name / ID", "")
    emotion_opts   = ["All","happy","sad","angry","surprised","fear","disgust","neutral"]
    filter_emotion = st.selectbox("Filter by Emotion", emotion_opts)
    show_unknown   = st.toggle("Include Unknown", value=True)

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📋 Detection Event Logs</div>
  <div class="page-sub">DETECTION HISTORY · ADVANCED FILTERS · CSV / JSON EXPORT</div>
</div>""", unsafe_allow_html=True)
st.divider()

logs = get_logs(limit)
if not logs:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:60px">
      <div style="font-size:2.5rem;opacity:.3">📋</div>
      <div style="color:#2a5570;margin-top:12px">No detection events recorded yet</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Run Live Detection to generate event logs</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df              = pd.DataFrame(logs)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Filters
if filter_name.strip():
    df = df[df['person_name'].str.contains(filter_name.strip(), case=False, na=False)]
if filter_emotion != "All":
    df = df[df['emotion'] == filter_emotion]
if not show_unknown:
    df = df[df['person_name'] != 'UNKNOWN']

# ── Stats strip ───────────────────────────────────────────────────────────────
total   = len(df)
known   = len(df[df['person_name'] != 'UNKNOWN'])
unknown = total - known
st.markdown(f"""
<div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
  <div class="ai-badge">📊 {total} Records</div>
  <div class="live-badge" style="gap:5px">
    <div class="live-dot" style="background:#00e676"></div>
    {known} Recognised
  </div>
  <div class="ai-badge" style="color:#ff4d6d;border-color:rgba(255,23,68,.3);
                                background:rgba(255,23,68,.08)">
    ❓ {unknown} Unknown
  </div>
</div>""", unsafe_allow_html=True)

# ── Table ──────────────────────────────────────────────────────────────────────
display_cols = ['timestamp','person_name','confidence','emotion','age_est','gender_est','camera_id']
existing_cols = [c for c in display_cols if c in df.columns]
df_display = df[existing_cols].copy()

if 'confidence' in df_display.columns:
    df_display['confidence'] = (
        df_display['confidence'].fillna(0) * 100
    ).round(1).astype(str) + "%"

if 'timestamp' in df_display.columns:
    df_display['timestamp'] = df_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

col_rename = {
    'timestamp': 'Timestamp', 'person_name': 'Person',
    'confidence': 'Match %', 'emotion': 'Emotion',
    'age_est': 'Age', 'gender_est': 'Gender', 'camera_id': 'Camera'
}
df_display.rename(columns={k: v for k, v in col_rename.items() if k in df_display.columns},
                  inplace=True)

st.dataframe(df_display, use_container_width=True, height=420,
             column_config={
                 "Person":  st.column_config.TextColumn("Person", width="medium"),
                 "Match %": st.column_config.TextColumn("Match %", width="small"),
                 "Emotion": st.column_config.TextColumn("Emotion", width="small"),
             })

# ── Export row ────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown("""<div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
    color:#2a5570;margin-bottom:12px;font-weight:600">◈ EXPORT DATA</div>""",
    unsafe_allow_html=True)

exp1, exp2 = st.columns(2)
with exp1:
    csv = df_display.to_csv(index=False)
    st.download_button(
        "⬇️  Export as CSV", csv, "ai_vision_logs.csv", "text/csv",
        use_container_width=True, type="primary"
    )
with exp2:
    json_str = df.drop(columns=['id','person_id'], errors='ignore').to_json(
        orient='records', indent=2, date_format='iso'
    )
    st.download_button(
        "⬇️  Export as JSON", json_str, "ai_vision_logs.json",
        "application/json", use_container_width=True
    )

"""
Analytics Dashboard — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import pandas as pd
import altair as alt
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_logs, get_log_stats, get_person_count
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Analytics · AI Vision", page_icon="📊", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

# ── Dark Altair theme ─────────────────────────────────────────────────────────
DARK = {
    "background": "#070d1a",
    "view": {"fill": "#070d1a", "stroke": "transparent"},
    "axis": {"grid": False, "domain": False,
             "labelColor": "#3a6a8a", "titleColor": "#3a6a8a",
             "tickColor": "transparent", "labelFontSize": 11},
    "title": {"color": "#5a9ab0"},
    "legend": {"labelColor": "#5a9ab0", "titleColor": "#5a9ab0"},
}
alt.themes.register("dark_ai", lambda: DARK)
alt.themes.enable("dark_ai")

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ DATA RANGE</div>", unsafe_allow_html=True)
    max_logs = st.slider("Max Records", 100, 5000, 1000, 100)

stats     = get_log_stats()
n_persons = get_person_count()

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📊 Analytics Dashboard</div>
  <div class="page-sub">DETECTION TRENDS · EMOTION DISTRIBUTION · RECOGNITION STATISTICS</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.markdown("""<div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
    color:#2a5570;margin-bottom:12px;font-weight:600">◈ KEY METRICS</div>""",
    unsafe_allow_html=True)

kpis = [
    (n_persons,             "Registered",   "#00c8ff", "👥"),
    (stats['total'],        "Detections",   "#7b61ff", "📡"),
    (stats['known'],        "Recognised",   "#00e676", "✅"),
    (stats['unknown'],      "Unknown",      "#ff4d6d", "❓"),
    (stats.get('today', 0), "Today",        "#ffab40", "📅"),
]
cols = st.columns(5)
for col, (val, lbl, color, icon) in zip(cols, kpis):
    with col:
        st.markdown(f"""<div class="kpi-card" style="border-color:{color}22">
            <div class="kpi-val" style="color:{color}">{val}</div>
            <div class="kpi-lbl">{icon} {lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

logs = get_logs(max_logs)
if not logs:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:60px">
      <div style="font-size:2.5rem;opacity:.3">📊</div>
      <div style="color:#2a5570;margin-top:12px">No detection data yet</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Run Live Detection to generate analytics data</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df              = pd.DataFrame(logs)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date']      = df['timestamp'].dt.date
df['hour']      = df['timestamp'].dt.hour

# ── Row 1 ─────────────────────────────────────────────────────────────────────
r1l, r1r = st.columns(2, gap="large")

with r1l:
    st.markdown("""<div class="glass-card">
      <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                  color:#2a5570;margin-bottom:14px;font-weight:600">◈ DAILY DETECTION TREND</div>
    """, unsafe_allow_html=True)
    daily = df.groupby('date').size().reset_index(name='Detections')
    daily['date'] = daily['date'].astype(str)
    chart_daily = (
        alt.Chart(daily)
        .mark_bar(color='#00c8ff', cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X('date:O', axis=alt.Axis(labelAngle=-30, title=None)),
            y=alt.Y('Detections:Q', axis=alt.Axis(title=None)),
            tooltip=['date', 'Detections']
        )
        .properties(height=200, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(chart_daily, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r1r:
    st.markdown("""<div class="glass-card purple">
      <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                  color:#5a3a9a;margin-bottom:14px;font-weight:600">◈ EMOTION DISTRIBUTION</div>
    """, unsafe_allow_html=True)
    if 'emotion' in df.columns and not df['emotion'].isna().all():
        emo = df['emotion'].value_counts().reset_index()
        emo.columns = ['Emotion', 'Count']
        chart_emo = (
            alt.Chart(emo)
            .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
            .encode(
                x=alt.X('Emotion:O', axis=alt.Axis(title=None)),
                y=alt.Y('Count:Q', axis=alt.Axis(title=None)),
                color=alt.Color('Emotion:N', scale=alt.Scale(
                    range=['#a371f7','#00c8ff','#ff4d6d','#ffab40','#00e676','#7b61ff','#ff7eb6']
                ), legend=None),
                tooltip=['Emotion', 'Count']
            )
            .properties(height=200, background='transparent')
            .configure_view(fill='#070d1a', stroke='transparent')
        )
        st.altair_chart(chart_emo, use_container_width=True)
    else:
        st.info("No emotion data yet")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 2 ─────────────────────────────────────────────────────────────────────
r2l, r2r = st.columns(2, gap="large")

with r2l:
    st.markdown("""<div class="glass-card">
      <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                  color:#2a5570;margin-bottom:14px;font-weight:600">◈ HOURLY ACTIVITY PATTERN</div>
    """, unsafe_allow_html=True)
    hourly = df.groupby('hour').size().reset_index(name='Detections')
    chart_hourly = (
        alt.Chart(hourly)
        .mark_bar(color='#ffab40', cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X('hour:O', axis=alt.Axis(title='Hour of Day')),
            y=alt.Y('Detections:Q', axis=alt.Axis(title=None)),
            tooltip=['hour', 'Detections']
        )
        .properties(height=190, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(chart_hourly, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2r:
    st.markdown("""<div class="glass-card">
      <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                  color:#2a5570;margin-bottom:14px;font-weight:600">◈ RECOGNITION BREAKDOWN</div>
    """, unsafe_allow_html=True)
    known_cnt   = int(stats['known'])
    unknown_cnt = int(stats['unknown'])
    total       = max(known_cnt + unknown_cnt, 1)
    known_pct   = known_cnt / total * 100
    unknown_pct = unknown_cnt / total * 100

    st.markdown(f"""
    <div style="margin-top:12px">
      <div style="display:flex;justify-content:space-between;
                  font-size:.8rem;color:#5a8ab0;margin-bottom:6px">
        <span>✅ Recognised</span><span style="color:#00e676;font-weight:700">
          {known_cnt} ({known_pct:.1f}%)</span>
      </div>
      <div style="background:rgba(0,200,255,.08);border-radius:6px;height:12px;
                  margin-bottom:12px">
        <div style="background:linear-gradient(90deg,#00e676,#00c8ff);
                    width:{known_pct}%;max-width:100%;height:12px;
                    border-radius:6px"></div>
      </div>
      <div style="display:flex;justify-content:space-between;
                  font-size:.8rem;color:#5a8ab0;margin-bottom:6px">
        <span>❓ Unknown</span><span style="color:#ff4d6d;font-weight:700">
          {unknown_cnt} ({unknown_pct:.1f}%)</span>
      </div>
      <div style="background:rgba(0,200,255,.08);border-radius:6px;height:12px">
        <div style="background:linear-gradient(90deg,#ff4d6d,#ff1744);
                    width:{unknown_pct}%;max-width:100%;height:12px;
                    border-radius:6px"></div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Top Persons ───────────────────────────────────────────────────────────────
st.markdown("""<div class="glass-card">
  <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
              color:#2a5570;margin-bottom:14px;font-weight:600">◈ MOST DETECTED PERSONS</div>
""", unsafe_allow_html=True)

known_df = df[df['person_name'] != 'UNKNOWN']
if known_df.empty:
    st.markdown("<div style='color:#2a5570;font-size:.85rem'>No recognised persons yet.</div>",
                unsafe_allow_html=True)
else:
    top = (known_df.groupby('person_name').size()
           .sort_values(ascending=False).head(10)
           .reset_index(name='Detections'))
    for _, row in top.iterrows():
        pct = int(row['Detections'] / max(stats['total'], 1) * 100)
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px">
          <div style="width:140px;font-size:.82rem;color:#c8e8ff;font-weight:500">
            {row['person_name']}</div>
          <div style="flex:1;background:rgba(0,200,255,.08);border-radius:4px;height:8px">
            <div style="background:linear-gradient(90deg,#00c8ff,#7b61ff);
                        width:{min(pct*3,100)}%;height:8px;border-radius:4px"></div>
          </div>
          <div style="font-size:.78rem;color:#5a8ab0;width:40px;text-align:right">
            {row['Detections']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

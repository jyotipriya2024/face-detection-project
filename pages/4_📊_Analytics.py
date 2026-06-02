"""
Analytics Dashboard — AI Vision Face Recognition System
"""
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_logs, get_log_stats, get_person_count,
                       get_logs_by_date_range, get_person_detection_stats)
from theme import THEME_CSS, SIDEBAR_HTML

st.set_page_config(page_title="Analytics · AI Vision", page_icon="📊", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ── Altair dark theme ─────────────────────────────────────────────────────────
DARK = {
    "background": "#070d1a",
    "view": {"fill": "#070d1a", "stroke": "transparent"},
    "axis": {
        "grid": False, "domain": False,
        "labelColor": "#3a6a8a", "titleColor": "#3a6a8a",
        "tickColor": "transparent", "labelFontSize": 11,
    },
    "title":  {"color": "#5a9ab0"},
    "legend": {"labelColor": "#5a9ab0", "titleColor": "#5a9ab0"},
    "mark":   {"tooltip": True},
}
alt.themes.register("dark_ai", lambda: DARK)
alt.themes.enable("dark_ai")

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ DATE RANGE</div>", unsafe_allow_html=True)

    today    = date.today()
    defaults = (today - timedelta(days=30), today)
    date_range = st.date_input("From — To", value=defaults,
                                min_value=date(2020, 1, 1), max_value=today)
    use_all  = st.toggle("Show All Time", value=False)
    max_recs = st.slider("Max Records", 100, 10000, 2000, 100)

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    stats     = get_log_stats()
    n_persons = get_person_count()
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📊 Analytics Dashboard</div>
  <div class="page-sub">DETECTION TRENDS · EMOTION DISTRIBUTION · RECOGNITION STATISTICS</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ── KPI Row ───────────────────────────────────────────────────────────────────
st.markdown("""<div class="section-label">◈ KEY METRICS</div>""", unsafe_allow_html=True)

recog_pct = round(stats['known'] / max(stats['total'], 1) * 100, 1)
kpis = [
    (n_persons,                    "Registered",  "#00c8ff", "👥"),
    (stats['total'],               "Detections",  "#7b61ff", "📡"),
    (stats['known'],               "Recognised",  "#00e676", "✅"),
    (stats['unknown'],             "Unknown",     "#ff4d6d", "❓"),
    (stats.get('today', 0),        "Today",       "#ffab40", "📅"),
    (f"{recog_pct}%",              "Recog. Rate", "#a371f7", "🎯"),
]
cols = st.columns(6)
for col, (val, lbl, color, icon) in zip(cols, kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card" style="border-color:{color}22;color:{color}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-val" style="color:{color}">{val}</div>
          <div class="kpi-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div class='sp20'></div>", unsafe_allow_html=True)

# ── Fetch logs ────────────────────────────────────────────────────────────────
try:
    if use_all:
        logs = get_logs(max_recs)
    elif isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        logs = get_logs_by_date_range(
            str(date_range[0]), str(date_range[1]), max_recs
        )
    else:
        logs = get_logs(max_recs)
except Exception:
    logs = get_logs(max_recs)

if not logs:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:64px">
      <div style="font-size:2.5rem;opacity:.25">📊</div>
      <div style="color:#2a5570;margin-top:14px">No detection data for selected period</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Adjust date range or run Live Detection to generate data</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df              = pd.DataFrame(logs)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date']      = df['timestamp'].dt.date
df['hour']      = df['timestamp'].dt.hour
df['weekday']   = df['timestamp'].dt.day_name()

st.markdown(f"""<div class="ai-badge" style="margin-bottom:16px">
  📊 {len(df)} records loaded
  {'(all time)' if use_all else f'· {date_range[0] if isinstance(date_range,(list,tuple)) and len(date_range)>=1 else "?"} → {date_range[1] if isinstance(date_range,(list,tuple)) and len(date_range)>=2 else "?"}'}
</div>""", unsafe_allow_html=True)

# ── Row 1: Daily trend + Emotion distribution ─────────────────────────────────
r1l, r1r = st.columns(2, gap="large")

with r1l:
    st.markdown("""<div class="glass-card">
      <div class="section-label">◈ DAILY DETECTION TREND</div>""",
      unsafe_allow_html=True)
    daily = df.groupby('date').size().reset_index(name='Detections')
    daily['date'] = daily['date'].astype(str)
    chart = (
        alt.Chart(daily)
        .mark_area(
            line={'color': '#00c8ff', 'strokeWidth': 2},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#00c8ff33', offset=1),
                       alt.GradientStop(color='#00c8ff00', offset=0)],
                x1=1, x2=1, y1=1, y2=0
            )
        )
        .encode(
            x=alt.X('date:O', axis=alt.Axis(labelAngle=-30, title=None)),
            y=alt.Y('Detections:Q', axis=alt.Axis(title=None)),
            tooltip=[alt.Tooltip('date', title='Date'),
                     alt.Tooltip('Detections', title='Count')]
        )
        .properties(height=210, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(chart, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r1r:
    st.markdown("""<div class="glass-card purple">
      <div class="section-label" style="color:#5a3a9a">◈ EMOTION DISTRIBUTION</div>""",
      unsafe_allow_html=True)
    if 'emotion' in df.columns and not df['emotion'].isna().all():
        emo = df['emotion'].value_counts().reset_index()
        emo.columns = ['Emotion', 'Count']
        chart_emo = (
            alt.Chart(emo)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X('Emotion:O', axis=alt.Axis(title=None)),
                y=alt.Y('Count:Q', axis=alt.Axis(title=None)),
                color=alt.Color('Emotion:N', scale=alt.Scale(
                    range=['#a371f7','#00c8ff','#ff4d6d','#ffab40',
                           '#00e676','#7b61ff','#ff7eb6']
                ), legend=None),
                tooltip=['Emotion', 'Count']
            )
            .properties(height=210, background='transparent')
            .configure_view(fill='#070d1a', stroke='transparent')
        )
        st.altair_chart(chart_emo, use_container_width=True)
    else:
        st.info("No emotion data yet")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Row 2: Hourly heatmap + Recognition breakdown ─────────────────────────────
r2l, r2r = st.columns(2, gap="large")

with r2l:
    st.markdown("""<div class="glass-card">
      <div class="section-label">◈ HOURLY ACTIVITY PATTERN</div>""",
      unsafe_allow_html=True)
    hourly = df.groupby('hour').size().reset_index(name='Detections')
    chart_h = (
        alt.Chart(hourly)
        .mark_bar(color='#ffab40', cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X('hour:O', axis=alt.Axis(title='Hour of Day')),
            y=alt.Y('Detections:Q', axis=alt.Axis(title=None)),
            tooltip=[alt.Tooltip('hour', title='Hour'),
                     alt.Tooltip('Detections', title='Count')]
        )
        .properties(height=200, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(chart_h, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2r:
    st.markdown("""<div class="glass-card">
      <div class="section-label">◈ RECOGNITION BREAKDOWN</div>""",
      unsafe_allow_html=True)
    known_n  = int(stats['known'])
    unkn_n   = int(stats['unknown'])
    total_n  = max(known_n + unkn_n, 1)
    kn_pct   = known_n / total_n * 100
    un_pct   = unkn_n  / total_n * 100

    # Donut via Altair
    pie_data = pd.DataFrame({
        'Category': ['Recognised', 'Unknown'],
        'Count':    [known_n, unkn_n],
        'Color':    ['#00e676', '#ff4d6d']
    })
    donut = (
        alt.Chart(pie_data)
        .mark_arc(innerRadius=55, outerRadius=90)
        .encode(
            theta=alt.Theta('Count:Q'),
            color=alt.Color('Category:N', scale=alt.Scale(
                domain=['Recognised','Unknown'],
                range=['#00e676','#ff4d6d']
            )),
            tooltip=['Category', 'Count']
        )
        .properties(height=200, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(donut, use_container_width=True)

    st.markdown(f"""
    <div style="display:-webkit-flex;display:flex;gap:18px;
                -webkit-justify-content:center;justify-content:center;margin-top:4px">
      <div style="text-align:center">
        <div style="font-size:1.4rem;font-weight:800;color:#00e676">{known_n}</div>
        <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;
                    letter-spacing:.08em">Recognised</div>
      </div>
      <div style="text-align:center">
        <div style="font-size:1.4rem;font-weight:800;color:#ff4d6d">{unkn_n}</div>
        <div style="font-size:.68rem;color:#2a5570;text-transform:uppercase;
                    letter-spacing:.08em">Unknown</div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='sp8'></div>", unsafe_allow_html=True)

# ── Row 3: Confidence distribution + Weekday pattern ─────────────────────────
r3l, r3r = st.columns(2, gap="large")

with r3l:
    st.markdown("""<div class="glass-card">
      <div class="section-label">◈ CONFIDENCE DISTRIBUTION</div>""",
      unsafe_allow_html=True)
    if 'confidence' in df.columns:
        conf_df = df[df['confidence'] > 0][['confidence']].copy()
        if not conf_df.empty:
            conf_df['confidence'] = (conf_df['confidence'] * 100).round(0)
            hist_data = pd.cut(conf_df['confidence'],
                               bins=list(range(0, 105, 5))).value_counts().reset_index()
            hist_data.columns = ['Range', 'Count']
            hist_data['Mid'] = hist_data['Range'].apply(
                lambda x: float(str(x).strip('(]').split(',')[0]) + 2.5
            )
            hist_data = hist_data.sort_values('Mid')
            chart_conf = (
                alt.Chart(hist_data)
                .mark_bar(color='#a371f7', cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X('Mid:Q', axis=alt.Axis(title='Confidence %', format='.0f')),
                    y=alt.Y('Count:Q', axis=alt.Axis(title=None)),
                    tooltip=[alt.Tooltip('Mid:Q', title='Conf. %', format='.0f'),
                             alt.Tooltip('Count', title='Count')]
                )
                .properties(height=190, background='transparent')
                .configure_view(fill='#070d1a', stroke='transparent')
            )
            st.altair_chart(chart_conf, use_container_width=True)
        else:
            st.info("No confidence data yet")
    else:
        st.info("No confidence column")
    st.markdown("</div>", unsafe_allow_html=True)

with r3r:
    st.markdown("""<div class="glass-card">
      <div class="section-label">◈ WEEKDAY ACTIVITY</div>""",
      unsafe_allow_html=True)
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    wday = df.groupby('weekday').size().reset_index(name='Detections')
    wday['weekday'] = pd.Categorical(wday['weekday'], categories=day_order, ordered=True)
    wday = wday.sort_values('weekday')
    chart_wday = (
        alt.Chart(wday)
        .mark_bar(color='#00c8ff', cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X('weekday:O', sort=day_order, axis=alt.Axis(title=None, labelAngle=-20)),
            y=alt.Y('Detections:Q', axis=alt.Axis(title=None)),
            tooltip=['weekday', 'Detections']
        )
        .properties(height=190, background='transparent')
        .configure_view(fill='#070d1a', stroke='transparent')
    )
    st.altair_chart(chart_wday, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='sp8'></div>", unsafe_allow_html=True)

# ── Top Detected Persons ──────────────────────────────────────────────────────
st.markdown("""<div class="glass-card">
  <div class="section-label">◈ MOST DETECTED PERSONS</div>""",
  unsafe_allow_html=True)

try:
    person_stats = get_person_detection_stats()
except Exception:
    person_stats = []

if not person_stats:
    known_df = df[df['person_name'] != 'UNKNOWN'] if 'person_name' in df.columns else pd.DataFrame()
    if not known_df.empty:
        top = (known_df.groupby('person_name').size()
               .sort_values(ascending=False).head(10)
               .reset_index(name='count'))
        person_stats = [{'person_name': r['person_name'], 'count': r['count'],
                         'avg_conf': 0, 'last_seen': None}
                        for _, r in top.iterrows()]

if not person_stats:
    st.markdown("<div style='color:#2a5570;font-size:.85rem;padding:10px 0'>No recognised persons yet.</div>",
                unsafe_allow_html=True)
else:
    max_count = max(p['count'] for p in person_stats)
    for rank, p in enumerate(person_stats[:10], 1):
        pct  = int(p['count'] / max(max_count, 1) * 100)
        conf = p.get('avg_conf') or 0
        last = (p.get('last_seen') or '')[:16].replace('T', ' ')
        st.markdown(f"""
        <div style="display:-webkit-flex;display:flex;-webkit-align-items:center;
                    align-items:center;gap:12px;margin-bottom:8px">
          <div style="width:22px;font-size:.72rem;color:#2a5570;
                      font-weight:700;text-align:right">#{rank}</div>
          <div style="width:150px;font-size:.82rem;color:#c8e8ff;
                      font-weight:600;white-space:nowrap;overflow:hidden;
                      text-overflow:ellipsis">{p['person_name']}</div>
          <div style="flex:1;background:rgba(0,200,255,.07);border-radius:5px;height:7px">
            <div style="background:linear-gradient(90deg,#00c8ff,#7b61ff);
                        width:{pct}%;height:7px;border-radius:5px"></div>
          </div>
          <div style="font-size:.76rem;color:#5a8ab0;width:36px;
                      text-align:right;font-weight:600">{p['count']}</div>
          <div style="font-size:.70rem;color:#2a5070;width:140px;text-align:right;
                      white-space:nowrap">{last}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

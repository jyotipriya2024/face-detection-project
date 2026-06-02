"""
Event Logs — AI Vision Face Recognition System
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_logs, get_logs_by_date_range, clear_logs
from theme import THEME_CSS, SIDEBAR_HTML

st.set_page_config(page_title="Event Logs · AI Vision", page_icon="📋", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ FILTER OPTIONS</div>", unsafe_allow_html=True)

    limit = st.slider("Max Records", 50, 5000, 500, 50)

    use_date = st.toggle("Filter by Date Range", value=False)
    if use_date:
        today  = date.today()
        dr     = st.date_input("Date Range",
                                value=(today - timedelta(days=7), today),
                                min_value=date(2020,1,1), max_value=today)
    else:
        dr = None

    filter_name    = st.text_input("Filter by Name", "", placeholder="Type name...")
    emotion_opts   = ["All","happy","sad","angry","surprised","fear","disgust","neutral"]
    filter_emotion = st.selectbox("Filter by Emotion", emotion_opts)
    show_unknown   = st.toggle("Include Unknown Faces", value=True)

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚠ DANGER ZONE</div>", unsafe_allow_html=True)

    if st.button("🗑️  Clear All Logs", use_container_width=True):
        st.session_state['confirm_clear'] = True

    if st.session_state.get('confirm_clear'):
        st.warning("This will permanently delete ALL detection logs.")
        c1, c2 = st.columns(2)
        if c1.button("✅ Yes, Delete", type="primary", use_container_width=True):
            clear_logs()
            st.session_state.pop('confirm_clear', None)
            st.success("All logs cleared")
            st.rerun()
        if c2.button("❌ Cancel", use_container_width=True):
            st.session_state.pop('confirm_clear', None)
            st.rerun()

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📋 Detection Event Logs</div>
  <div class="page-sub">DETECTION HISTORY · ADVANCED FILTERS · DATE RANGE · CSV / JSON EXPORT</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ── Load logs ─────────────────────────────────────────────────────────────────
try:
    if use_date and dr and isinstance(dr, (list, tuple)) and len(dr) == 2:
        logs = get_logs_by_date_range(str(dr[0]), str(dr[1]), limit)
    else:
        logs = get_logs(limit)
except Exception as e:
    st.error(f"Database error: {e}")
    st.stop()

if not logs:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:64px">
      <div style="font-size:2.5rem;opacity:.25">📋</div>
      <div style="color:#2a5570;margin-top:14px">No detection events recorded yet</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Run Live Detection or adjust date range to see logs</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

df              = pd.DataFrame(logs)
df['timestamp'] = pd.to_datetime(df['timestamp'])

# Apply filters
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
pct_k   = round(known / max(total, 1) * 100, 1)

st.markdown(f"""
<div style="display:-webkit-flex;display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap">
  <span class="ai-badge">📊 {total} Records</span>
  <span class="live-badge">
    <div class="live-dot"></div>&nbsp;{known} Recognised ({pct_k}%)
  </span>
  <span class="ai-badge red">❓ {unknown} Unknown</span>
  {'<span class="ai-badge amber">📅 Date filtered</span>' if use_date else ''}
  {'<span class="ai-badge purple">🔍 Name filter: ' + filter_name.strip() + '</span>' if filter_name.strip() else ''}
</div>""", unsafe_allow_html=True)

# ── Per-person summary ────────────────────────────────────────────────────────
if total > 0 and not df[df['person_name'] != 'UNKNOWN'].empty:
    with st.expander("  📈  Per-Person Summary  "):
        known_df  = df[df['person_name'] != 'UNKNOWN']
        summary   = (
            known_df.groupby('person_name')
            .agg(Count=('person_name', 'count'),
                 Avg_Conf=('confidence', 'mean'),
                 Last_Seen=('timestamp', 'max'))
            .reset_index()
            .sort_values('Count', ascending=False)
        )
        summary['Avg_Conf']  = (summary['Avg_Conf'] * 100).round(1).astype(str) + '%'
        summary['Last_Seen'] = summary['Last_Seen'].dt.strftime('%Y-%m-%d %H:%M')
        summary.columns      = ['Person', 'Detections', 'Avg Match', 'Last Seen']
        st.dataframe(summary, use_container_width=True, hide_index=True)

# ── Table ─────────────────────────────────────────────────────────────────────
display_cols = ['timestamp','person_name','confidence','emotion',
                'age_est','gender_est','camera_id']
existing_cols = [c for c in display_cols if c in df.columns]
df_display    = df[existing_cols].copy()

if 'confidence' in df_display.columns:
    df_display['confidence'] = (
        df_display['confidence'].fillna(0) * 100
    ).round(1).astype(str) + "%"

if 'timestamp' in df_display.columns:
    df_display['timestamp'] = df_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

col_rename = {
    'timestamp':  'Timestamp',  'person_name': 'Person',
    'confidence': 'Match %',    'emotion':     'Emotion',
    'age_est':    'Age',         'gender_est':  'Gender',
    'camera_id':  'Camera'
}
df_display.rename(
    columns={k: v for k, v in col_rename.items() if k in df_display.columns},
    inplace=True
)

st.dataframe(
    df_display, use_container_width=True, height=430,
    column_config={
        "Person":    st.column_config.TextColumn("Person",  width="medium"),
        "Match %":   st.column_config.TextColumn("Match %", width="small"),
        "Emotion":   st.column_config.TextColumn("Emotion", width="small"),
        "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
    }
)

# ── Export row ────────────────────────────────────────────────────────────────
st.markdown("<div class='sp8'></div>", unsafe_allow_html=True)
st.markdown("""<div class="section-label">◈ EXPORT DATA</div>""", unsafe_allow_html=True)

exp1, exp2, exp3 = st.columns(3)

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
with exp3:
    # Excel-compatible TSV
    tsv = df_display.to_csv(index=False, sep='\t')
    st.download_button(
        "⬇️  Export as TSV", tsv, "ai_vision_logs.tsv", "text/tab-separated-values",
        use_container_width=True
    )

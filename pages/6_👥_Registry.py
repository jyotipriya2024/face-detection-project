"""
Person Registry — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_all_persons, delete_person, get_person_count
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Registry · AI Vision", page_icon="👥", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>🔍 SEARCH</div>", unsafe_allow_html=True)
    search_q = st.text_input("Name or Person ID", "", label_visibility="collapsed",
                              placeholder="Search name or ID...")
    st.markdown("<div class='sidebar-label' style='margin-top:10px'>⚙ FILTER</div>",
                unsafe_allow_html=True)
    gender_filter = st.selectbox("Gender", ["All", "Male", "Female", "Other"],
                                  label_visibility="collapsed")

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">👥 Person Registry</div>
  <div class="page-sub">ENROLLED PERSONS · BROWSE · SEARCH · MANAGE</div>
</div>""", unsafe_allow_html=True)
st.divider()

persons = get_all_persons()

# Filter
if search_q.strip():
    q = search_q.strip().lower()
    persons = [p for p in persons
               if q in (p['name'] or '').lower() or q in (p['person_id'] or '').lower()]
if gender_filter != "All":
    persons = [p for p in persons if p['gender'] == gender_filter]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:18px">
  <div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
              color:#2a5570;font-weight:600">◈ {len(persons)} PERSONS</div>
  <div style="display:flex;gap:8px">
    <span class="ai-badge">⚡ {get_person_count()} Total Enrolled</span>
  </div>
</div>""", unsafe_allow_html=True)

if not persons:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:60px">
      <div style="font-size:3rem;opacity:.25">👤</div>
      <div style="color:#2a5570;margin-top:12px">No persons found</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Adjust search criteria or go to Register to add persons</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Person cards grid ─────────────────────────────────────────────────────────
cols_per_row = 3
rows = [persons[i:i+cols_per_row] for i in range(0, len(persons), cols_per_row)]

for row_persons in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for col, p in zip(cols, row_persons):
        with col:
            gender_icon = "♂️" if p['gender'] == "Male" else ("♀️" if p['gender'] == "Female" else "⚧")
            st.markdown(f"""
            <div class="glass-card" style="padding:18px;position:relative;min-height:160px">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div style="font-size:1rem;font-weight:700;color:#c8e8ff;
                              margin-bottom:3px">{p['name']}</div>
                  <div class="ai-badge" style="margin-bottom:10px">{p['person_id'] or '—'}</div>
                </div>
                <div style="font-size:1.5rem;opacity:.6">{gender_icon}</div>
              </div>
              <div style="font-size:.77rem;color:#3a6a8a;line-height:2">
                🎂 Age: <span style="color:#7a9cc0">{p['age']}</span><br>
                📧 {p['email'] or '—'}<br>
                📞 {p['phone'] or '—'}<br>
                📅 <span style="color:#2a5570">{p['created_at'][:10] if p.get('created_at') else '—'}</span>
              </div>
            </div>""", unsafe_allow_html=True)

            if st.button(f"🗑️ Delete", key=f"del_{p['id']}",
                         help=f"Remove {p['name']} from system"):
                delete_person(p['id'])
                st.rerun()

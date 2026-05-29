"""
Person Registry — AI Vision Face Recognition System
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_persons, delete_person, get_person_count,
                       update_person, get_last_seen, export_persons_csv)
from theme import THEME_CSS, SIDEBAR_HTML

st.set_page_config(page_title="Registry · AI Vision", page_icon="👥", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>🔍 SEARCH</div>", unsafe_allow_html=True)
    search_q = st.text_input("Name, ID or Email", "", label_visibility="collapsed",
                              placeholder="Search…")
    st.markdown("<div class='sidebar-label' style='margin-top:10px'>⚙ FILTER</div>",
                unsafe_allow_html=True)
    gender_filter = st.selectbox("Gender", ["All","Male","Female","Other","Prefer not to say"],
                                  label_visibility="collapsed")
    sort_by = st.selectbox("Sort By", ["Newest First","Oldest First","Name A-Z","Name Z-A"],
                            label_visibility="collapsed")
    cols_per_row = st.slider("Cards Per Row", 2, 4, 3)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>📥 EXPORT</div>", unsafe_allow_html=True)
    try:
        csv_data = export_persons_csv()
        st.download_button("⬇️ Export Registry CSV", csv_data,
                           "ai_vision_persons.csv", "text/csv",
                           use_container_width=True)
    except Exception:
        pass

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">👥 Person Registry</div>
  <div class="page-sub">ENROLLED PERSONS · BROWSE · EDIT · SEARCH · MANAGE</div>
</div>""", unsafe_allow_html=True)
st.divider()

persons = get_all_persons()

# ── Sort ──────────────────────────────────────────────────────────────────────
if sort_by == "Oldest First":
    persons = sorted(persons, key=lambda p: p.get('created_at') or '')
elif sort_by == "Name A-Z":
    persons = sorted(persons, key=lambda p: (p.get('name') or '').lower())
elif sort_by == "Name Z-A":
    persons = sorted(persons, key=lambda p: (p.get('name') or '').lower(), reverse=True)

# ── Filter ────────────────────────────────────────────────────────────────────
if search_q.strip():
    q = search_q.strip().lower()
    persons = [p for p in persons
               if q in (p['name'] or '').lower()
               or q in (p['person_id'] or '').lower()
               or q in (p['email'] or '').lower()]
if gender_filter != "All":
    persons = [p for p in persons if p.get('gender') == gender_filter]

# ── Header row ────────────────────────────────────────────────────────────────
total_enrolled = get_person_count()
st.markdown(f"""
<div style="display:-webkit-flex;display:flex;
            -webkit-justify-content:space-between;justify-content:space-between;
            -webkit-align-items:center;align-items:center;margin-bottom:20px">
  <div class="section-label" style="margin:0">
    ◈ {len(persons)} of {total_enrolled} PERSONS
    {'· &quot;' + search_q.strip() + '&quot;' if search_q.strip() else ''}
  </div>
  <div style="display:-webkit-flex;display:flex;gap:8px">
    <span class="ai-badge">&#9889; {total_enrolled} Enrolled</span>
    <span class="ai-badge green">&#10003; DB Active</span>
  </div>
</div>""", unsafe_allow_html=True)

if not persons:
    st.markdown("""<div class="glass-card" style="text-align:center;padding:64px">
      <div style="font-size:3.2rem;opacity:.20">👤</div>
      <div style="color:#2a5570;margin-top:14px">No persons found</div>
      <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
        Adjust search / filter or go to Register to add persons</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ── Helper: avatar ────────────────────────────────────────────────────────────
_AVATAR_COLORS = [
    ("#00c8ff","#040b14"), ("#a371f7","#08031a"), ("#00e676","#00140a"),
    ("#ffab40","#140a00"), ("#ff4d6d","#14000a"), ("#7b61ff","#060318"),
]

def _avatar(name: str, idx: int) -> str:
    initials = "".join(w[0].upper() for w in (name or "?").split()[:2])
    fg, bg   = _AVATAR_COLORS[idx % len(_AVATAR_COLORS)]
    return f"""<div class="person-avatar"
                    style="background:{bg};border:2px solid {fg}40;color:{fg}">
                 {initials}</div>"""

def _quality_color(score: float) -> str:
    if score >= 0.75: return "#00e676"
    if score >= 0.55: return "#ffab40"
    return "#ff4d6d"

# ── Card grid ─────────────────────────────────────────────────────────────────
rows = [persons[i:i+cols_per_row] for i in range(0, len(persons), cols_per_row)]

for row_persons in rows:
    cols = st.columns(cols_per_row, gap="medium")
    for col, p in zip(cols, row_persons):
        idx      = persons.index(p)
        q_score  = p.get('quality_score') or 0
        q_color  = _quality_color(q_score)
        q_pct    = int(q_score * 100)
        avatar   = _avatar(p['name'], idx)

        # Fetch last seen (cached per person per rerun)
        cache_key = f"last_seen_{p['id']}"
        if cache_key not in st.session_state:
            st.session_state[cache_key] = get_last_seen(p['name'])
        last_seen = st.session_state[cache_key]
        last_str  = last_seen[:16].replace('T', ' ') if last_seen else "Never detected"

        with col:
            _, fg, _ = (*_AVATAR_COLORS[idx % len(_AVATAR_COLORS)], None)
            border_c = _AVATAR_COLORS[idx % len(_AVATAR_COLORS)][0]

            st.markdown(f"""
            <div class="glass-card" style="padding:18px 18px 14px;
                 border-color:{border_c}18;position:relative">
              <div style="display:-webkit-flex;display:flex;gap:12px;
                          -webkit-align-items:flex-start;align-items:flex-start;
                          margin-bottom:12px">
                {avatar}
                <div style="min-width:0;flex:1">
                  <div style="font-size:.95rem;font-weight:700;color:#c8e8ff;
                              white-space:nowrap;overflow:hidden;
                              text-overflow:ellipsis">{p['name']}</div>
                  <div class="ai-badge" style="margin-top:3px;font-size:.62rem">
                    {p['person_id'] or '—'}</div>
                </div>
              </div>
              <div style="font-size:.75rem;color:#3a6a8a;line-height:2.0">
                🎂 <span style="color:#7a9cc0">{p['age'] or '—'}</span>
                &nbsp;·&nbsp;
                {'♂️' if p.get('gender')=='Male' else '♀️' if p.get('gender')=='Female' else '⚧️'}
                <span style="color:#7a9cc0">{p.get('gender','—')}</span><br>
                📧 <span style="color:#5a8ab0;font-size:.72rem">
                  {p['email'] or '—'}</span><br>
                📞 <span style="color:#5a8ab0;font-size:.72rem">
                  {p['phone'] or '—'}</span><br>
                📅 <span style="color:#3a5a70;font-size:.68rem">
                  Enrolled: {p['created_at'][:10] if p.get('created_at') else '—'}</span><br>
                👁️ <span style="color:#3a5a70;font-size:.68rem">
                  Last seen: {last_str}</span>
              </div>
              <div style="margin-top:10px">
                <div style="display:-webkit-flex;display:flex;
                            -webkit-justify-content:space-between;
                            justify-content:space-between;
                            font-size:.68rem;color:#2a5570;margin-bottom:3px">
                  <span>Quality</span>
                  <span style="color:{q_color};font-weight:700">{q_pct}%</span>
                </div>
                <div class="quality-bar-wrap">
                  <div class="quality-bar-fill"
                       style="width:{q_pct}%;background:{q_color}"></div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Edit + Delete buttons
            e_col, d_col = st.columns([2, 1])
            with e_col:
                if st.button("✏️ Edit", key=f"edit_btn_{p['id']}",
                              use_container_width=True):
                    st.session_state[f"editing_{p['id']}"] = not st.session_state.get(
                        f"editing_{p['id']}", False
                    )

            with d_col:
                st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{p['id']}",
                              help=f"Remove {p['name']}"):
                    if st.session_state.get(f"confirm_del_{p['id']}"):
                        delete_person(p['id'])
                        st.session_state.pop(f"confirm_del_{p['id']}", None)
                        st.session_state.pop(cache_key, None)
                        st.rerun()
                    else:
                        st.session_state[f"confirm_del_{p['id']}"] = True
                st.markdown("</div>", unsafe_allow_html=True)

            if st.session_state.get(f"confirm_del_{p['id']}"):
                st.warning("Confirm deletion ↑ or click elsewhere to cancel")

            # Inline edit form
            if st.session_state.get(f"editing_{p['id']}"):
                with st.form(key=f"form_{p['id']}"):
                    st.markdown("""<div style="font-size:.72rem;letter-spacing:.10em;
                        text-transform:uppercase;color:#2a5570;margin-bottom:8px;
                        font-weight:700">✏️ EDIT PERSON</div>""",
                        unsafe_allow_html=True)
                    en  = st.text_input("Name *", p['name'])
                    ea  = st.number_input("Age", 1, 120,
                                          int(p['age'] or 25))
                    eg  = st.selectbox("Gender",
                                       ["Male","Female","Other","Prefer not to say"],
                                       index=["Male","Female","Other","Prefer not to say"]
                                             .index(p['gender'])
                                             if p.get('gender') in
                                             ["Male","Female","Other","Prefer not to say"]
                                             else 0)
                    eph = st.text_input("Phone", p['phone'] or '')
                    eem = st.text_input("Email", p['email'] or '')
                    eno = st.text_area("Notes", p['notes'] or '', height=60)
                    submitted = st.form_submit_button("💾 Save", type="primary",
                                                       use_container_width=True)
                    if submitted:
                        if not en.strip():
                            st.error("Name is required")
                        else:
                            if update_person(p['id'], en.strip(), ea, eg,
                                            eph.strip(), eem.strip(), eno.strip()):
                                st.success("Updated!")
                                st.session_state[f"editing_{p['id']}"] = False
                                st.rerun()
                            else:
                                st.error("Save failed")

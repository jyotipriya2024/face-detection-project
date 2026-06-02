"""
Face Registration — AI Vision Face Recognition System
"""
import re
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (add_person, get_all_persons, delete_person,
                      update_person, check_person_id_exists)
from face_engine import get_engine
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Register · AI Vision", page_icon="📝", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ CAPTURE SETTINGS</div>", unsafe_allow_html=True)
    quality_threshold = st.slider("Min Quality Score", 0.30, 0.90, 0.60, 0.05,
                                   help="Faces below this score will be flagged as low quality")

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📝 Face Registration</div>
  <div class="page-sub">ENROL NEW PERSONS · WEBCAM CAPTURE · QUALITY VALIDATION · FACE EMBEDDING</div>
</div>""", unsafe_allow_html=True)
st.divider()

engine = get_engine()
tab_reg, tab_list = st.tabs(["  ➕  Register New Person  ", "  👥  Enrolled Persons  "])

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
_PHONE_RE = re.compile(r"^[\+\d][\d\s\-\(\)]{6,19}$")

def _validate_email(v: str) -> bool:
    return not v.strip() or bool(_EMAIL_RE.match(v.strip()))

def _validate_phone(v: str) -> bool:
    return not v.strip() or bool(_PHONE_RE.match(v.strip().replace(" ", "")))

def _quality_color(score: float) -> str:
    if score >= 0.75: return "#00e676"
    if score >= 0.55: return "#ffab40"
    return "#ff4d6d"

def _quality_label(score: float) -> str:
    if score >= 0.75: return "Excellent"
    if score >= 0.55: return "Good"
    if score >= 0.40: return "Fair"
    return "Poor"

# ─────────────────────────────────────────────────────────────────────────────
# Register Tab
# ─────────────────────────────────────────────────────────────────────────────
with tab_reg:
    col_form, col_cam = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("""<div class="glass-card">
          <div class="section-label">◈ PERSON DETAILS</div>
        """, unsafe_allow_html=True)

        name  = st.text_input("Full Name *", placeholder="e.g. Jyotipriya Panda",
                               max_chars=100)
        pid   = st.text_input("Person / Employee ID *", placeholder="e.g. EMP-001",
                               max_chars=50)

        c1, c2 = st.columns(2)
        age    = c1.number_input("Age", 1, 120, 25, step=1)
        gender = c2.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])

        phone = st.text_input("Phone Number", placeholder="+91 9xxxxxxxxx", max_chars=20)
        email = st.text_input("Email Address", placeholder="name@example.com", max_chars=120)
        notes = st.text_area("Notes / Remarks", placeholder="Additional info...",
                              height=80, max_chars=500)

        # Inline validation hints
        if phone and not _validate_phone(phone):
            st.markdown("""<div style="color:#ff6b8a;font-size:.75rem;margin-top:-8px">
                ⚠ Invalid phone format</div>""", unsafe_allow_html=True)
        if email and not _validate_email(email):
            st.markdown("""<div style="color:#ff6b8a;font-size:.75rem;margin-top:-8px">
                ⚠ Invalid email format</div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_cam:
        st.markdown("""<div class="glass-card purple">
          <div class="section-label" style="color:#5a3a9a">◈ FACE CAPTURE &amp; QUALITY</div>
          <div style="font-size:.78rem;color:#4a5a8a;margin-bottom:14px">
            Position face clearly in frame &middot; Ensure good lighting &middot; Look directly at camera
          </div>
        """, unsafe_allow_html=True)

        photo = st.camera_input("Capture Registration Photo", key="reg_cam",
                                 label_visibility="collapsed")

        if photo:
            try:
                pil   = Image.open(photo).convert("RGB")
                bgr   = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
                faces = engine._detector.detect_faces(bgr)

                if not faces:
                    st.markdown("""<div class="glass-card red" style="padding:14px;margin-top:8px">
                        <div style="color:#ff4d6d;font-weight:600">❌ No face detected</div>
                        <div style="color:#8a4a5a;font-size:.75rem;margin-top:4px">
                          Retake in better lighting — face must be clearly visible</div>
                      </div>""", unsafe_allow_html=True)
                    st.session_state.pop('reg_crop', None)
                    st.session_state.pop('reg_quality', None)
                else:
                    x1, y1, x2, y2 = faces[0]['bbox']
                    crop = bgr[max(0, y1):y2, max(0, x1):x2]
                    det_conf = faces[0].get('confidence', 0.9)

                    if crop.size > 0:
                        q_score, q_issues = engine.face_quality(crop)
                        q_color = _quality_color(q_score)
                        q_label = _quality_label(q_score)
                        q_pct   = int(q_score * 100)

                        st.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB),
                                 caption=f"Detected · {det_conf:.0%} confidence",
                                 width=200)

                        st.markdown(f"""
                        <div style="margin-top:10px">
                          <div style="display:-webkit-flex;display:flex;
                                      -webkit-justify-content:space-between;
                                      justify-content:space-between;
                                      font-size:.75rem;margin-bottom:4px">
                            <span style="color:#5a8ab0">Face Quality</span>
                            <span style="color:{q_color};font-weight:700">
                              {q_label} · {q_pct}%</span>
                          </div>
                          <div class="quality-bar-wrap">
                            <div class="quality-bar-fill"
                                 style="width:{q_pct}%;background:{q_color}"></div>
                          </div>
                        </div>""", unsafe_allow_html=True)

                        if q_issues:
                            for issue in q_issues:
                                st.markdown(f"""<div style="font-size:.72rem;color:#ff8a6a;
                                    margin-top:3px">⚠ {issue}</div>""",
                                    unsafe_allow_html=True)

                        if q_score < quality_threshold:
                            st.warning(f"Quality {q_pct}% is below threshold {int(quality_threshold*100)}%. "
                                       "Retake for better accuracy — or lower the threshold in the sidebar.")
                        else:
                            st.markdown("""<div class="live-badge" style="margin-top:8px">
                                <div class="live-dot"></div>&nbsp;Ready to Enrol
                            </div>""", unsafe_allow_html=True)

                        st.session_state['reg_crop']    = crop
                        st.session_state['reg_quality'] = q_score
            except Exception as e:
                st.error(f"Camera error: {e}")
                st.session_state.pop('reg_crop', None)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Register Button ────────────────────────────────────────────────────────
    st.markdown("<div class='sp16'></div>", unsafe_allow_html=True)
    if st.button("💾  REGISTER PERSON  ·  ENROL INTO SYSTEM", type="primary",
                 use_container_width=True):
        errors = []
        if not name.strip():
            errors.append("Full Name is required")
        if not pid.strip():
            errors.append("Person / Employee ID is required")
        elif check_person_id_exists(pid.strip()):
            errors.append(f"Person ID '{pid.strip()}' is already registered — use a unique ID")
        if 'reg_crop' not in st.session_state:
            errors.append("Please capture a face photo first")
        if phone and not _validate_phone(phone):
            errors.append("Phone number format is invalid")
        if email and not _validate_email(email):
            errors.append("Email address format is invalid")

        if errors:
            for e in errors:
                st.error(f"⚠  {e}")
        else:
            with st.spinner("⚡ Generating face embedding..."):
                try:
                    crop      = st.session_state['reg_crop']
                    q_score   = st.session_state.get('reg_quality', 0.0)
                    emb       = engine.embed(crop)
                    person_db_id = add_person(
                        name.strip(), age, gender, pid.strip(),
                        phone.strip(), email.strip(), notes.strip(),
                        emb, q_score
                    )
                    st.markdown(f"""
                    <div class="glass-card green" style="text-align:center;padding:24px">
                      <div style="font-size:1.8rem">✅</div>
                      <div style="color:#00e676;font-weight:700;font-size:1.05rem;margin-top:8px">
                        {name.strip()} enrolled successfully</div>
                      <div style="color:#2a6a4a;font-size:.78rem;margin-top:6px">
                        ID: {pid.strip()} &middot; 416-d embedding stored
                        &middot; Quality: {int(q_score*100)}%</div>
                    </div>""", unsafe_allow_html=True)
                    st.balloons()
                    st.session_state.pop('reg_crop', None)
                    st.session_state.pop('reg_quality', None)
                except Exception as ex:
                    st.error(f"Registration failed: {ex}")

# ─────────────────────────────────────────────────────────────────────────────
# Enrolled Persons Tab
# ─────────────────────────────────────────────────────────────────────────────
with tab_list:
    persons = get_all_persons()
    if not persons:
        st.markdown("""<div class="glass-card" style="text-align:center;padding:48px">
          <div style="font-size:2.4rem">👤</div>
          <div style="color:#2a5570;margin-top:10px">No persons enrolled yet</div>
          <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
            Go to the Register tab to add the first person</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:-webkit-flex;display:flex;
                    -webkit-justify-content:space-between;justify-content:space-between;
                    -webkit-align-items:center;align-items:center;margin-bottom:16px">
          <div class="section-label" style="margin:0">◈ {len(persons)} ENROLLED PERSONS</div>
          <span class="ai-badge">&#9889; Embeddings Active</span>
        </div>""", unsafe_allow_html=True)

        search_q = st.text_input("🔍 Search by name or ID", placeholder="Type to filter...",
                                  key="reg_search")
        if search_q.strip():
            q = search_q.strip().lower()
            persons = [p for p in persons
                       if q in (p['name'] or '').lower()
                       or q in (p['person_id'] or '').lower()]
            st.caption(f"{len(persons)} result(s)")

        for p in persons:
            q_score = p.get('quality_score') or 0
            q_color = _quality_color(q_score)
            with st.expander(f"  👤  {p['name']}  ·  {p['person_id'] or '—'}"):
                # Metrics row
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Age",    p['age'] or '—')
                m2.metric("Gender", p['gender'] or '—')
                m3.metric("Phone",  p['phone'] or '—')
                m4.metric("Email",  p['email'] or '—')

                st.markdown(f"""
                <div style="display:-webkit-flex;display:flex;gap:10px;flex-wrap:wrap;
                            margin-top:8px;font-size:.75rem;color:#5a8ab0">
                  <span>📅 Registered: <b style="color:#c8e8ff">
                    {p['created_at'][:10] if p.get('created_at') else '—'}</b></span>
                  <span>·</span>
                  <span>&#127919; Quality:
                    <b style="color:{q_color}">{int(q_score*100)}%</b></span>
                </div>""", unsafe_allow_html=True)

                if p.get('notes'):
                    st.caption(f"Notes: {p['notes']}")

                edit_col, del_col = st.columns([3, 1])
                with edit_col:
                    with st.expander("  ✏️  Edit Details  "):
                        en  = st.text_input("Name",   p['name'],   key=f"en_{p['id']}")
                        ea  = st.number_input("Age",  1, 120, int(p['age'] or 25), key=f"ea_{p['id']}")
                        eg  = st.selectbox("Gender",
                                           ["Male","Female","Other","Prefer not to say"],
                                           index=["Male","Female","Other","Prefer not to say"]
                                                 .index(p['gender']) if p.get('gender') in
                                                 ["Male","Female","Other","Prefer not to say"] else 0,
                                           key=f"eg_{p['id']}")
                        eph = st.text_input("Phone",  p['phone'] or '', key=f"eph_{p['id']}")
                        eem = st.text_input("Email",  p['email'] or '', key=f"eem_{p['id']}")
                        en2 = st.text_area("Notes",  p['notes'] or '', key=f"en2_{p['id']}")
                        if st.button("💾 Save Changes", key=f"save_{p['id']}"):
                            if update_person(p['id'], en, ea, eg, eph, eem, en2):
                                st.success("Updated successfully")
                                st.rerun()
                            else:
                                st.error("Update failed")
                with del_col:
                    st.markdown("<div class='btn-danger'>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Delete", key=f"del_{p['id']}",
                                  help=f"Permanently remove {p['name']}"):
                        if st.session_state.get(f"confirm_del_{p['id']}"):
                            delete_person(p['id'])
                            st.rerun()
                        else:
                            st.session_state[f"confirm_del_{p['id']}"] = True
                            st.warning("Click Delete again to confirm")
                    st.markdown("</div>", unsafe_allow_html=True)

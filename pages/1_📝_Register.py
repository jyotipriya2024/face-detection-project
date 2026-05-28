"""
Face Registration — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import add_person, get_all_persons, delete_person
from face_engine import get_engine
from theme import THEME_CSS, SIDEBAR_HTML

st.set_page_config(page_title="Register · AI Vision", page_icon="📝", layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">📝 Face Registration</div>
  <div class="page-sub">ENROLL NEW PERSONS · WEBCAM CAPTURE · FACE EMBEDDING</div>
</div>""", unsafe_allow_html=True)
st.divider()

engine = get_engine()
tab_reg, tab_list = st.tabs(["  ➕  Register New Person  ", "  👥  Enrolled Persons  "])

# ── Register Tab ──────────────────────────────────────────────────────────────
with tab_reg:
    col_form, col_cam = st.columns([1, 1], gap="large")

    with col_form:
        st.markdown("""<div class="glass-card">
          <div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
                      color:#2a5570;margin-bottom:16px;font-weight:600">◈ PERSON DETAILS</div>
        """, unsafe_allow_html=True)

        name   = st.text_input("Full Name *", placeholder="e.g. Jyotipriya Panda")
        pid    = st.text_input("Person / Employee ID *", placeholder="e.g. EMP-001")
        c1, c2 = st.columns(2)
        age    = c1.number_input("Age", 1, 120, 25)
        gender = c2.selectbox("Gender", ["Male", "Female", "Other"])
        phone  = st.text_input("Phone Number", placeholder="+91 9xxxxxxxxx")
        email  = st.text_input("Email Address", placeholder="name@example.com")
        notes  = st.text_area("Notes / Remarks", placeholder="Additional info...", height=90)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_cam:
        st.markdown("""<div class="glass-card purple">
          <div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
                      color:#5a3a9a;margin-bottom:16px;font-weight:600">◈ FACE CAPTURE</div>
        """, unsafe_allow_html=True)
        st.markdown("""<div style="font-size:.8rem;color:#4a6a8a;margin-bottom:12px">
          Position face clearly in frame · Good lighting · Look directly at camera
        </div>""", unsafe_allow_html=True)

        photo = st.camera_input("📸 Capture Registration Photo", key="reg_cam",
                                label_visibility="collapsed")
        if photo:
            pil  = Image.open(photo).convert("RGB")
            bgr  = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
            faces = engine._detector.detect_faces(bgr)
            if faces:
                x1, y1, x2, y2 = faces[0]['bbox']
                crop  = bgr[max(0,y1):y2, max(0,x1):x2]
                conf  = faces[0].get('confidence', 0.9)
                st.image(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB),
                         caption=f"✅ Face detected · {conf:.0%} confidence", width=200)
                st.session_state['reg_crop'] = crop
                st.markdown(f"""<div class="live-badge" style="margin-top:8px">
                    <div class="live-dot"></div> Ready to Enroll
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""<div style="background:rgba(255,23,68,.08);border:1px solid
                    rgba(255,23,68,.3);border-radius:10px;padding:12px;
                    font-size:.82rem;color:#ff6b8a;margin-top:8px">
                    ❌ No face detected — retake in better lighting</div>""",
                    unsafe_allow_html=True)
                st.session_state.pop('reg_crop', None)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.button("💾  REGISTER PERSON  ·  ENROLL INTO SYSTEM", type="primary",
                 use_container_width=True):
        if not name.strip():
            st.error("⚠️  Full Name is required")
        elif not pid.strip():
            st.error("⚠️  Person ID is required")
        elif 'reg_crop' not in st.session_state:
            st.error("⚠️  Please capture a face photo first")
        else:
            with st.spinner("Generating face embedding..."):
                crop = st.session_state['reg_crop']
                emb  = engine.embed(crop)
                add_person(name.strip(), age, gender, pid.strip(),
                           phone.strip(), email.strip(), notes.strip(), emb)
            st.markdown(f"""<div class="glass-card" style="border-color:rgba(0,230,118,.35);
                background:rgba(0,230,118,.05);text-align:center;padding:20px">
                <div style="font-size:1.5rem">✅</div>
                <div style="color:#00e676;font-weight:700;font-size:1rem;margin-top:6px">
                  {name} enrolled successfully</div>
                <div style="color:#2a6a4a;font-size:.78rem;margin-top:4px">
                  256-d face embedding stored in database</div>
              </div>""", unsafe_allow_html=True)
            st.balloons()
            st.session_state.pop('reg_crop', None)

# ── List Tab ──────────────────────────────────────────────────────────────────
with tab_list:
    persons = get_all_persons()
    if not persons:
        st.markdown("""<div class="glass-card" style="text-align:center;padding:40px">
          <div style="font-size:2rem">👤</div>
          <div style="color:#2a5570;margin-top:8px">No persons enrolled yet</div>
          <div style="font-size:.78rem;color:#1a3a50;margin-top:4px">
            Go to Register tab to add the first person</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:16px">
          <div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
                      color:#2a5570;font-weight:600">
            ◈ {len(persons)} ENROLLED PERSONS
          </div>
          <span class="ai-badge">⚡ Embeddings Loaded</span>
        </div>""", unsafe_allow_html=True)

        for p in persons:
            with st.expander(f"  👤  {p['name']}  ·  {p['person_id'] or '—'}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Age",    p['age'])
                c2.metric("Gender", p['gender'])
                c3.metric("Phone",  p['phone'] or '—')
                c4.metric("Email",  p['email'] or '—')
                c1.caption(f"Registered: {p['created_at'][:10]}")
                if p['notes']:
                    st.caption(f"Notes: {p['notes']}")
                if st.button(f"🗑️  Delete {p['name']}", key=f"del_{p['id']}",
                             help="Permanently remove from system"):
                    delete_person(p['id'])
                    st.rerun()

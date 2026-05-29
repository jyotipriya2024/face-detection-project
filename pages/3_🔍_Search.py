"""
Face Search — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_all_embeddings, get_all_persons
from face_engine import get_engine, EMOTION_EMOJI
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Face Search · AI Vision", page_icon="🔍", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ SEARCH SETTINGS</div>",
                unsafe_allow_html=True)
    threshold = st.slider("Match Threshold", 0.30, 0.95, 0.55, 0.05,
                          help="Lower = more lenient · Higher = stricter match")
    st.markdown(f"""<div style="font-size:.72rem;color:#3a6a8a;margin-top:4px">
        Current threshold: <b style="color:#00c8ff">{threshold:.0%}</b></div>""",
        unsafe_allow_html=True)

engine = get_engine()

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">🔍 Face Search</div>
  <div class="page-sub">UPLOAD ANY IMAGE · AI MATCHING · IDENTITY LOOKUP</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ── Upload zone ───────────────────────────────────────────────────────────────
st.markdown("""<div class="glass-card purple" style="margin-bottom:24px">
  <div style="font-size:.65rem;letter-spacing:.15em;text-transform:uppercase;
              color:#5a3a9a;margin-bottom:10px;font-weight:600">◈ UPLOAD QUERY IMAGE</div>
  <div style="font-size:.8rem;color:#4a6a8a">
    Upload a photo to identify faces · Supported: JPG · JPEG · PNG
  </div>
</div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["jpg","jpeg","png"], label_visibility="collapsed")

if not uploaded:
    st.markdown("""
    <div style="text-align:center;padding:60px 0">
      <div style="font-size:3rem;opacity:.3">🔍</div>
      <div style="color:#1a3a50;margin-top:12px;font-size:.9rem">
        Upload an image above to begin face search
      </div>
    </div>""", unsafe_allow_html=True)
else:
    pil = Image.open(uploaded).convert("RGB")
    bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    with st.spinner("⚡ Detecting faces..."):
        faces = engine._detector.detect_faces(bgr)

    if not faces:
        st.markdown("""<div class="glass-card" style="border-color:rgba(255,23,68,.3);
            background:rgba(255,23,68,.05);text-align:center;padding:30px">
          <div style="font-size:1.5rem">❌</div>
          <div style="color:#ff4d6d;margin-top:8px">No faces detected in this image</div>
          <div style="color:#4a2a3a;font-size:.78rem;margin-top:4px">
            Try a clearer photo with proper lighting</div>
        </div>""", unsafe_allow_html=True)
    else:
        db_embs  = get_all_embeddings()
        all_pers = get_all_persons()

        col_src, col_res = st.columns([1, 2], gap="large")
        with col_src:
            st.markdown("""<div style="font-size:.65rem;letter-spacing:.12em;text-transform:
                uppercase;color:#2a5570;margin-bottom:8px;font-weight:600">
                ◈ SOURCE IMAGE</div>""", unsafe_allow_html=True)
            st.image(pil, caption=uploaded.name, use_container_width=True)

        with col_res:
            st.markdown(f"""
            <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                        color:#2a5570;margin-bottom:8px;font-weight:600">
              ◈ SEARCH RESULTS · {len(faces)} FACE(S)
            </div>""", unsafe_allow_html=True)

            if not db_embs:
                st.markdown("""<div class="glass-card" style="padding:24px">
                  <div style="color:#5a8ab0">No persons enrolled yet.</div>
                  <div style="font-size:.78rem;color:#2a4a6a;margin-top:4px">
                    Go to Register to enroll persons first.</div>
                </div>""", unsafe_allow_html=True)
            else:
                for i, face in enumerate(faces):
                    x1, y1, x2, y2 = face['bbox']
                    crop = bgr[max(0,y1):y2, max(0,x1):x2]
                    if crop.size == 0:
                        continue

                    with st.spinner(f"Matching face {i+1}..."):
                        emb         = engine.embed(crop)
                        name, score = engine.recognize(emb, db_embs, threshold=threshold)
                        emo_map     = engine._emotion.detect_emotion(crop)
                        top_emo     = max(emo_map, key=emo_map.get) if emo_map else 'neutral'
                        emoji       = EMOTION_EMOJI.get(top_emo, '😐')
                        age, gender = engine.estimate_age_gender(crop)

                    is_match   = name != 'UNKNOWN'
                    card_color = "rgba(0,230,118,.35)" if is_match else "rgba(255,23,68,.25)"
                    bg_color   = "rgba(0,230,118,.04)" if is_match else "rgba(255,23,68,.04)"
                    name_color = "#00e676" if is_match else "#ff4d6d"

                    col_face, col_info = st.columns([1, 3])
                    with col_face:
                        rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                        st.image(rgb_crop, caption=f"Face {i+1}", width=100)

                    with col_info:
                        st.markdown(f"""
                        <div class="glass-card" style="border-color:{card_color};
                             background:{bg_color};padding:16px">
                          <div style="font-weight:700;color:{name_color};font-size:1rem;
                                      margin-bottom:8px">
                            {"✅  " if is_match else "❓  "}{name}
                          </div>
                          <div style="font-size:.8rem;color:#5a8ab0;line-height:1.9">
                            🎯 Similarity: <b style="color:#c8e8ff">{score:.0%}</b>
                            &nbsp;·&nbsp; Threshold: {threshold:.0%}<br>
                            {emoji} {top_emo.capitalize()}
                            &nbsp;·&nbsp; 👤 {gender}
                            &nbsp;·&nbsp; 🎂 {age}
                          </div>
                        </div>""", unsafe_allow_html=True)

                        if is_match:
                            person = next((p for p in all_pers if p['name'] == name), None)
                            if person:
                                with st.expander("  📄  View Person Details  "):
                                    d1, d2, d3 = st.columns(3)
                                    d1.metric("ID",     person['person_id'] or '—')
                                    d2.metric("Age",    person['age'])
                                    d3.metric("Gender", person['gender'])
                                    d1.caption(f"Phone: {person['phone'] or '—'}")
                                    d2.caption(f"Email: {person['email'] or '—'}")
                                    d3.caption(f"Since: {person['created_at'][:10]}")
                                    if person['notes']:
                                        st.caption(f"Notes: {person['notes']}")

                    if i < len(faces) - 1:
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

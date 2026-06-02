"""
Face Search — AI Vision Face Recognition System
"""
import io
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
    st.markdown("<div class='sidebar-label'>⚙ SEARCH SETTINGS</div>", unsafe_allow_html=True)
    threshold = st.slider("Match Threshold", 0.30, 0.95, 0.52, 0.05,
                           help="Lower = more lenient · Higher = stricter match")
    st.markdown(f"""<div style="font-size:.72rem;color:#3a6a8a;margin-top:4px">
      Current: <b style="color:#00c8ff">{threshold:.0%}</b>
      &nbsp;&middot;&nbsp;
      {'Strict' if threshold >= 0.7 else 'Balanced' if threshold >= 0.5 else 'Lenient'}</div>""",
        unsafe_allow_html=True)

    show_emotion = st.toggle("Show Emotion Analysis", value=True)
    show_details = st.toggle("Show Person Details",   value=True)

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>📚 SEARCH HISTORY</div>", unsafe_allow_html=True)
    if 'search_history' not in st.session_state:
        st.session_state['search_history'] = []
    if st.session_state['search_history']:
        for h in st.session_state['search_history'][-5:]:
            st.markdown(f"""<div style="font-size:.72rem;color:#3a6a8a;margin-bottom:2px">
              📎 {h}</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style="font-size:.72rem;color:#1a3a50">No searches yet</div>""",
                    unsafe_allow_html=True)
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state['search_history'] = []
        st.rerun()

engine = get_engine()

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">🔍 Face Search</div>
  <div class="page-sub">UPLOAD ANY IMAGE · AI IDENTITY MATCHING · MULTI-FACE SUPPORT</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ── Upload zone ───────────────────────────────────────────────────────────────
st.markdown("""<div class="glass-card purple" style="margin-bottom:24px;padding:18px 24px">
  <div class="section-label" style="color:#5a3a9a">◈ UPLOAD QUERY IMAGE</div>
  <div style="font-size:.80rem;color:#4a5a8a">
    Upload a photo to identify faces · JPG · JPEG · PNG · BMP · WEBP supported
  </div>
</div>""", unsafe_allow_html=True)

uploaded = st.file_uploader("", type=["jpg","jpeg","png","bmp","webp"],
                              label_visibility="collapsed")

if not uploaded:
    st.markdown("""
    <div style="text-align:center;padding:64px 0">
      <div style="font-size:3.5rem;opacity:.25">🔍</div>
      <div style="color:#1a3a50;margin-top:14px;font-size:.92rem">
        Upload an image above to begin face search</div>
      <div style="font-size:.75rem;color:#0f2535;margin-top:6px">
        Supports JPG, PNG, BMP, WEBP · Multiple faces per image</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# Validate file size
if uploaded.size > 20 * 1024 * 1024:
    st.error("File too large — maximum 20 MB")
    st.stop()

try:
    pil = Image.open(uploaded).convert("RGB")
except Exception as e:
    st.error(f"Cannot open image: {e}")
    st.stop()

# Resize if necessary
max_dim = 1280
w, h = pil.size
if max(w, h) > max_dim:
    scale = max_dim / max(w, h)
    pil   = pil.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

with st.spinner("⚡ Detecting faces..."):
    faces = engine._detector.detect_faces(bgr)

if not faces:
    st.markdown("""<div class="glass-card red" style="text-align:center;padding:32px">
      <div style="font-size:1.6rem">❌</div>
      <div style="color:#ff4d6d;margin-top:8px;font-weight:600">No faces detected</div>
      <div style="color:#4a2a3a;font-size:.78rem;margin-top:4px">
        Try a clearer photo with proper lighting and forward-facing angle</div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# Track search history
fname = uploaded.name[:40]
if fname not in st.session_state['search_history']:
    st.session_state['search_history'].append(fname)
    st.session_state['search_history'] = st.session_state['search_history'][-20:]

db_embs  = get_all_embeddings()
all_pers = get_all_persons()

col_src, col_res = st.columns([1, 2], gap="large")

with col_src:
    st.markdown("""<div class="section-label">◈ SOURCE IMAGE</div>""",
                unsafe_allow_html=True)
    st.image(pil, caption=f"{uploaded.name} · {w}×{h}px · {len(faces)} face(s)",
             use_container_width=True)

    # Info strip
    st.markdown(f"""
    <div class="glass-card" style="padding:14px 18px;margin-top:12px">
      <div class="stat-row">
        <span class="stat-key">Faces found</span>
        <span class="stat-val">{len(faces)}</span>
      </div>
      <div class="stat-row">
        <span class="stat-key">DB size</span>
        <span class="stat-val">{len(db_embs)} persons</span>
      </div>
      <div class="stat-row">
        <span class="stat-key">Threshold</span>
        <span class="stat-val">{threshold:.0%}</span>
      </div>
    </div>""", unsafe_allow_html=True)

with col_res:
    st.markdown(f"""<div class="section-label">◈ SEARCH RESULTS · {len(faces)} FACE(S)</div>""",
                unsafe_allow_html=True)

    if not db_embs:
        st.markdown("""<div class="glass-card" style="padding:28px">
          <div style="color:#5a8ab0;font-weight:600">No persons enrolled yet</div>
          <div style="font-size:.78rem;color:#2a4a6a;margin-top:6px">
            Register persons first using the Register page, then search here.</div>
        </div>""", unsafe_allow_html=True)
    else:
        for i, face in enumerate(faces):
            x1, y1, x2, y2 = face['bbox']
            crop = bgr[max(0, y1):max(y2, y1+1), max(0, x1):max(x2, x1+1)]
            if crop.size == 0:
                continue

            with st.spinner(f"Matching face {i+1} of {len(faces)}..."):
                emb         = engine.embed(crop)
                name, score = engine.recognize(emb, db_embs, threshold=threshold)
                emo_map     = engine._emotion.detect_emotion(crop)
                top_emo     = max(emo_map, key=emo_map.get) if emo_map else 'neutral'
                emoji       = EMOTION_EMOJI.get(top_emo, '😐')
                age, gender = engine.estimate_age_gender(crop)
                q_score, _  = engine.face_quality(crop)

            is_match   = name != 'UNKNOWN'
            card_color = "rgba(0,230,118,.35)" if is_match else "rgba(255,77,109,.25)"
            bg_color   = "rgba(0,20,12,.50)"   if is_match else "rgba(22,4,10,.50)"
            name_color = "#00e676" if is_match else "#ff4d6d"
            score_pct  = int(score * 100)

            col_face, col_info = st.columns([1, 3])
            with col_face:
                rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
                st.image(rgb_crop, caption=f"Face {i+1}", width=110)
                # Quality mini-bar
                q_pct   = int(q_score * 100)
                q_color = "#00e676" if q_score >= 0.75 else "#ffab40" if q_score >= 0.55 else "#ff4d6d"
                st.markdown(f"""
                <div style="font-size:.65rem;color:#3a5a7a;margin-top:2px">
                  Quality <b style="color:{q_color}">{q_pct}%</b></div>
                <div class="quality-bar-wrap" style="margin:2px 0">
                  <div class="quality-bar-fill"
                       style="width:{q_pct}%;background:{q_color}"></div>
                </div>""", unsafe_allow_html=True)

            with col_info:
                st.markdown(f"""
                <div class="glass-card"
                     style="border-color:{card_color};background:{bg_color};padding:16px">
                  <div style="font-weight:700;color:{name_color};font-size:1rem;margin-bottom:10px">
                    {'✅' if is_match else '❓'}&nbsp;&nbsp;{name}
                  </div>
                  <div style="font-size:.78rem;color:#5a8ab0;margin-bottom:8px">
                    🎯 Similarity: <b style="color:#c8e8ff">{score:.0%}</b>
                    &nbsp;·&nbsp; Threshold: {threshold:.0%}
                  </div>
                  <div class="conf-bar" style="height:6px;margin-bottom:10px">
                    <div class="conf-bar-fill"
                         style="width:{score_pct}%;
                                background:{'#00e676' if is_match else '#ff4d6d'}"></div>
                  </div>""", unsafe_allow_html=True)

                if show_emotion:
                    st.markdown(f"""
                  <div style="font-size:.78rem;color:#5a8ab0">
                    {emoji}&nbsp;{top_emo.capitalize()}
                    &nbsp;·&nbsp; 👤 {gender}
                    &nbsp;·&nbsp; 🎂 {age}
                  </div>""", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                if is_match and show_details:
                    person = next((p for p in all_pers if p['name'] == name), None)
                    if person:
                        with st.expander("  📄  View Full Profile  "):
                            d1, d2, d3 = st.columns(3)
                            d1.metric("ID",     person['person_id'] or '—')
                            d2.metric("Age",    person['age'] or '—')
                            d3.metric("Gender", person['gender'] or '—')
                            st.markdown(f"""
                            <div style="font-size:.76rem;color:#4a7a9a;line-height:2;margin-top:6px">
                              📧 {person['email'] or '—'} &nbsp;·&nbsp;
                              📞 {person['phone'] or '—'} &nbsp;·&nbsp;
                              📅 Enrolled: {person['created_at'][:10] if person.get('created_at') else '—'}
                            </div>""", unsafe_allow_html=True)
                            if person.get('notes'):
                                st.caption(f"📝 {person['notes']}")

            if i < len(faces) - 1:
                st.markdown("<div class='sp8'></div>", unsafe_allow_html=True)

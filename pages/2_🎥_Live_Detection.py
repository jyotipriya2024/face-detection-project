"""
Live Detection — AI Vision Face Recognition System
Premium Edition
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_all_embeddings, log_detection
from face_engine import get_engine, EMOTION_EMOJI
from theme import get_theme_css, SIDEBAR_HTML

st.set_page_config(page_title="Live Detection · AI Vision", page_icon="🎥", layout="wide")
theme_mode = st.sidebar.radio("Theme", ["Dark", "Light"], index=0, horizontal=True, key="theme_mode")
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

with st.sidebar:
    st.markdown(SIDEBAR_HTML, unsafe_allow_html=True)
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>⚙ DETECTION SETTINGS</div>", unsafe_allow_html=True)
    do_recognition = st.toggle("Enable Recognition", value=True)
    log_events     = st.toggle("Auto-Log Events",    value=True)
    conf_thresh    = st.slider("Confidence Threshold", 0.3, 0.9, 0.45, 0.05)

engine = get_engine()
engine._detector.confidence_threshold = conf_thresh

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">🎥 Live Detection</div>
  <div class="page-sub">REAL-TIME FACE DETECTION · RECOGNITION · EMOTION ANALYSIS · AGE · GENDER</div>
</div>""", unsafe_allow_html=True)
st.divider()

tab_cam, tab_upload = st.tabs(["  📷  Webcam Capture  ", "  🖼️  Upload Image  "])

def _render_results(annotated_bgr, results, source_label):
    col_img, col_cards = st.columns([3, 2], gap="large")
    with col_img:
        st.markdown("""<div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
            color:#2a5570;margin-bottom:8px;font-weight:600">◈ ANALYSED FRAME</div>""",
            unsafe_allow_html=True)
        rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
        st.image(rgb, caption=f"{len(results)} face(s) detected · {source_label}",
                 use_container_width=True)

    with col_cards:
        st.markdown(f"""
        <div style="font-size:.65rem;letter-spacing:.12em;text-transform:uppercase;
                    color:#2a5570;margin-bottom:8px;font-weight:600">
          ◈ DETECTION RESULTS
        </div>
        <div class="live-badge" style="margin-bottom:14px">
          <div class="live-dot"></div> {len(results)} face(s) detected
        </div>""", unsafe_allow_html=True)

        if not results:
            st.markdown("""<div class="glass-card" style="text-align:center;padding:30px">
              <div style="font-size:1.5rem">🔍</div>
              <div style="color:#2a5570;margin-top:8px;font-size:.85rem">
                No faces detected in frame</div>
            </div>""", unsafe_allow_html=True)
        else:
            for f in results:
                is_known  = f['name'] != 'UNKNOWN'
                card_cls  = "known" if is_known else "unknown"
                name_disp = f['name'] if is_known else "❓ UNKNOWN"
                name_col  = "#00e676" if is_known else "#ff4d6d"
                rec_pct   = f"{f['rec_conf']:.0%}" if is_known else "—"
                emoji     = f.get('emotion_emoji', '😐')

                st.markdown(f"""
                <div class="face-result-card {card_cls}">
                  <div class="face-name" style="color:{name_col}">
                    {name_disp}
                  </div>
                  <div class="face-meta">
                    🎯 Match: <b style="color:#c8e8ff">{rec_pct}</b> &nbsp;·&nbsp;
                    📡 Det: <b style="color:#c8e8ff">{f['det_conf']:.0%}</b><br>
                    {emoji} <b>{f['emotion'].capitalize()}</b> &nbsp;·&nbsp;
                    👤 {f['gender']} &nbsp;·&nbsp;
                    🎂 {f['age']}
                  </div>
                </div>""", unsafe_allow_html=True)

                if log_events:
                    log_detection(f['name'], f['rec_conf'], f['emotion'],
                                  f['age'], f['gender'])

            # Emotion breakdown for face 1
            emo_all = results[0].get('emotions_all')
            if emo_all:
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.markdown("""<div style="font-size:.65rem;letter-spacing:.12em;
                    text-transform:uppercase;color:#2a5570;margin-bottom:10px;font-weight:600">
                    ◈ EMOTION ANALYSIS · FACE 1</div>""", unsafe_allow_html=True)
                sorted_emo = sorted(emo_all.items(), key=lambda x: x[1], reverse=True)
                for ename, score in sorted_emo:
                    pct   = int(score * 100)
                    eemoji = EMOTION_EMOJI.get(ename, '')
                    bar_w  = int(pct * 1.4)
                    st.markdown(f"""
                    <div style="margin-bottom:6px">
                      <div style="display:flex;justify-content:space-between;
                                  font-size:.75rem;color:#5a8ab0;margin-bottom:3px">
                        <span>{eemoji} {ename}</span>
                        <span style="color:#c8e8ff;font-weight:600">{pct}%</span>
                      </div>
                      <div style="background:rgba(0,200,255,.08);border-radius:4px;height:5px">
                        <div style="background:linear-gradient(90deg,#00c8ff,#7b61ff);
                                    width:{bar_w}%;max-width:100%;height:5px;
                                    border-radius:4px"></div>
                      </div>
                    </div>""", unsafe_allow_html=True)

# ── Webcam ────────────────────────────────────────────────────────────────────
with tab_cam:
    st.markdown("""<div class="glass-card" style="margin-bottom:20px">
      <div style="font-size:.8rem;color:#3a6a8a;line-height:1.7">
        📌 Allow camera access in browser &nbsp;·&nbsp;
        Click <b style="color:#00c8ff">Take Photo</b> to capture a frame &nbsp;·&nbsp;
        Results appear instantly
      </div>
    </div>""", unsafe_allow_html=True)

    photo = st.camera_input("Capture", key="live_cam", label_visibility="collapsed")
    if photo:
        db_embs = get_all_embeddings() if do_recognition else []
        pil = Image.open(photo).convert("RGB")
        bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        with st.spinner("⚡ Running AI analysis..."):
            annotated, results = engine.analyze_frame(bgr, db_embs)
        _render_results(annotated, results, "Webcam")

# ── Upload ────────────────────────────────────────────────────────────────────
with tab_upload:
    st.markdown("""<div class="glass-card" style="margin-bottom:20px">
      <div style="font-size:.8rem;color:#3a6a8a">
        📁 Supported formats: JPG · JPEG · PNG &nbsp;·&nbsp;
        Multiple faces supported
      </div>
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["jpg","jpeg","png"],
                                 label_visibility="collapsed")
    if uploaded:
        db_embs = get_all_embeddings() if do_recognition else []
        pil = Image.open(uploaded).convert("RGB")
        bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        with st.spinner("⚡ Running AI analysis..."):
            annotated, results = engine.analyze_frame(bgr, db_embs)
        _render_results(annotated, results, uploaded.name)

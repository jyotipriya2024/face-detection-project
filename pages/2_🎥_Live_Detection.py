"""
Live Detection — AI Vision Face Recognition System
"""
import io
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
    do_recognition = st.toggle("Enable Recognition",  value=True)
    log_events     = st.toggle("Auto-Log Events",     value=True)
    show_all_emo   = st.toggle("Show All Emotions",   value=True)
    conf_thresh    = st.slider("Confidence Threshold", 0.30, 0.90, 0.65, 0.05)
    rec_thresh     = st.slider("Recognition Threshold", 0.30, 0.90, 0.52, 0.05,
                                help="Higher = stricter match")

    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-label'>📊 SESSION STATS</div>", unsafe_allow_html=True)

    if 'session_detections' not in st.session_state:
        st.session_state['session_detections'] = 0
    if 'session_recognised' not in st.session_state:
        st.session_state['session_recognised'] = 0
    if 'session_frames' not in st.session_state:
        st.session_state['session_frames'] = 0

    st.markdown(f"""
    <div style="font-size:.80rem;color:#5a8ab0;line-height:2.2">
      Frames analysed: <b style="color:#c8e8ff">{st.session_state['session_frames']}</b><br>
      Faces detected:  <b style="color:#00c8ff">{st.session_state['session_detections']}</b><br>
      Recognised:      <b style="color:#00e676">{st.session_state['session_recognised']}</b>
    </div>""", unsafe_allow_html=True)

    if st.button("🔄 Reset Session", use_container_width=True):
        st.session_state['session_detections'] = 0
        st.session_state['session_recognised'] = 0
        st.session_state['session_frames'] = 0
        st.rerun()

engine = get_engine()
engine._detector.confidence_threshold = conf_thresh

st.markdown("""
<div style="padding:28px 0 6px">
  <div class="page-header">🎥 Live Detection</div>
  <div class="page-sub">REAL-TIME FACE DETECTION · RECOGNITION · EMOTION · AGE · GENDER</div>
</div>""", unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────────────────────────────────────

def _render_results(annotated_bgr: np.ndarray, results: list, source_label: str,
                    annotated_rgb: np.ndarray = None):
    col_img, col_cards = st.columns([3, 2], gap="large")

    if annotated_rgb is None:
        annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)

    with col_img:
        st.markdown("""<div class="section-label">◈ ANALYSED FRAME</div>""",
                    unsafe_allow_html=True)
        st.image(annotated_rgb,
                 caption=f"{len(results)} face(s) detected · {source_label}",
                 use_container_width=True)

        # Download annotated image
        pil_out = Image.fromarray(annotated_rgb)
        buf     = io.BytesIO()
        pil_out.save(buf, format="JPEG", quality=90)
        st.download_button(
            "⬇️  Download Annotated Image", buf.getvalue(),
            "ai_vision_detection.jpg", "image/jpeg",
            use_container_width=True
        )

    with col_cards:
        n = len(results)
        badge_color = "#00e676" if n > 0 else "#5a8ab0"
        st.markdown(f"""
        <div class="section-label">◈ DETECTION RESULTS</div>
        <div class="live-badge" style="margin-bottom:14px;
             {'background:rgba(0,230,118,.10);border-color:rgba(0,230,118,.30);' if n > 0
              else 'background:rgba(90,138,176,.10);border-color:rgba(90,138,176,.30);color:#5a8ab0'}">
          <div class="live-dot" style="background:{badge_color}"></div>&nbsp;
          {n} face(s) detected
        </div>""", unsafe_allow_html=True)

        if not results:
            st.markdown("""<div class="glass-card" style="text-align:center;padding:32px">
              <div style="font-size:1.6rem">🔍</div>
              <div style="color:#2a5570;margin-top:8px;font-size:.85rem">
                No faces detected in frame</div>
              <div style="font-size:.73rem;color:#1a3a50;margin-top:4px">
                Ensure face is well-lit and clearly visible</div>
            </div>""", unsafe_allow_html=True)
        else:
            for f in results:
                is_known  = f['name'] != 'UNKNOWN'
                card_cls  = "known" if is_known else "unknown"
                name_disp = f['name'] if is_known else "❓ UNKNOWN"
                name_col  = "#00e676" if is_known else "#ff4d6d"
                rec_pct   = f['rec_conf'] if is_known else 0.0
                emoji     = f.get('emotion_emoji', '😐')
                det_pct   = f['det_conf']

                st.markdown(f"""
                <div class="face-result-card {card_cls}">
                  <div class="face-name" style="color:{name_col}">{name_disp}</div>
                  <div class="face-meta">
                    🎯 Match:
                    <b style="color:#c8e8ff">{'%.0f%%' % (rec_pct*100) if is_known else '—'}</b>
                    &nbsp;·&nbsp;
                    📡 Det: <b style="color:#c8e8ff">{det_pct:.0%}</b>
                  </div>
                  <div class="conf-bar" style="margin:6px 0">
                    <div class="conf-bar-fill"
                         style="width:{'%.0f' % (rec_pct*100 if is_known else det_pct*100)}%">
                    </div>
                  </div>
                  <div class="face-meta">
                    {emoji} <b>{f['emotion'].capitalize()}</b>
                    &nbsp;·&nbsp; 👤 {f['gender']}
                    &nbsp;·&nbsp; 🎂 {f['age']}
                  </div>
                </div>""", unsafe_allow_html=True)

                if log_events:
                    try:
                        log_detection(f['name'], f['rec_conf'], f['emotion'],
                                      f['age'], f['gender'])
                    except Exception:
                        pass

            # Emotion breakdown for face 1
            if show_all_emo:
                emo_all = results[0].get('emotions_all')
                if emo_all:
                    st.markdown("<div class='sp8'></div>", unsafe_allow_html=True)
                    st.markdown("""<div class="section-label">◈ EMOTION ANALYSIS · FACE 1</div>""",
                                unsafe_allow_html=True)
                    for ename, score in sorted(emo_all.items(),
                                               key=lambda x: x[1], reverse=True):
                        pct   = int(score * 100)
                        eemoji = EMOTION_EMOJI.get(ename, '')
                        st.markdown(f"""
                        <div style="margin-bottom:7px">
                          <div style="display:-webkit-flex;display:flex;
                                      -webkit-justify-content:space-between;
                                      justify-content:space-between;
                                      font-size:.74rem;color:#5a8ab0;margin-bottom:3px">
                            <span>{eemoji}&nbsp;{ename}</span>
                            <span style="color:#c8e8ff;font-weight:600">{pct}%</span>
                          </div>
                          <div class="conf-bar">
                            <div class="conf-bar-fill" style="width:{pct}%"></div>
                          </div>
                        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
tab_cam, tab_upload = st.tabs(["  📷  Webcam Capture  ", "  🖼️  Upload Image  "])

with tab_cam:
    st.markdown("""<div class="glass-card" style="margin-bottom:20px;padding:14px 20px">
      <div style="font-size:.80rem;color:#3a6a8a;line-height:1.8">
        📌 Allow camera access in browser &nbsp;&middot;&nbsp;
        Click <b style="color:#00c8ff">Take Photo</b> to capture &nbsp;&middot;&nbsp;
        Results appear instantly below
      </div>
    </div>""", unsafe_allow_html=True)

    photo = st.camera_input("Capture", key="live_cam", label_visibility="collapsed")
    if photo:
        try:
            db_embs = get_all_embeddings() if do_recognition else []
            pil     = Image.open(photo).convert("RGB")
            bgr     = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

            with st.spinner("⚡ Running AI analysis..."):
                annotated, results = engine.analyze_frame(bgr, db_embs)

            st.session_state['session_frames'] += 1
            st.session_state['session_detections'] += len(results)
            st.session_state['session_recognised'] += sum(
                1 for r in results if r['name'] != 'UNKNOWN'
            )
            _render_results(annotated, results, "Webcam")
        except Exception as e:
            st.error(f"Detection error: {e}")

with tab_upload:
    st.markdown("""<div class="glass-card" style="margin-bottom:20px;padding:14px 20px">
      <div style="font-size:.80rem;color:#3a6a8a">
        📁 Supported: JPG · JPEG · PNG · BMP · WEBP &nbsp;&middot;&nbsp;
        Multiple faces supported &nbsp;&middot;&nbsp; Max 20 MB
      </div>
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader("", type=["jpg","jpeg","png","bmp","webp"],
                                 label_visibility="collapsed")
    if uploaded:
        try:
            if uploaded.size > 20 * 1024 * 1024:
                st.error("File too large — maximum 20 MB")
            else:
                db_embs = get_all_embeddings() if do_recognition else []
                pil     = Image.open(uploaded).convert("RGB")

                # Cap resolution for performance
                max_dim = 1280
                w, h = pil.size
                if max(w, h) > max_dim:
                    scale = max_dim / max(w, h)
                    pil   = pil.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

                bgr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

                with st.spinner("⚡ Running AI analysis..."):
                    annotated, results = engine.analyze_frame(bgr, db_embs)

                st.session_state['session_frames'] += 1
                st.session_state['session_detections'] += len(results)
                st.session_state['session_recognised'] += sum(
                    1 for r in results if r['name'] != 'UNKNOWN'
                )
                _render_results(annotated, results, uploaded.name)
        except Exception as e:
            st.error(f"Detection error: {e}")

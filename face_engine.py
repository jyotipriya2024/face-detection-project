"""
Unified AI Engine — Face Detection, Recognition, Emotion, Age, Gender
Jyotipriya Panda | Reg. 2407432009 | M.Tech CSE 2024-2026 | GIFT Bhubaneswar
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from face_detector import FaceDetector
from emotion_detector import EmotionDetector

# ── Constants ─────────────────────────────────────────────────────────────────
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprised']
EMOTION_EMOJI = {
    'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprised': '😲',
    'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
}
EMOTION_COLOR_BGR = {
    'happy':     (50,  205, 50),
    'sad':       (205, 50,  50),
    'angry':     (0,   0,   220),
    'surprised': (0,   165, 255),
    'fear':      (180, 0,   180),
    'disgust':   (0,   100, 200),
    'neutral':   (160, 160, 160),
}
RECOGNITION_THRESHOLD = 0.52
MIN_FACE_SIZE = 40          # pixels — smaller faces rejected for registration
BLUR_THRESHOLD = 60.0       # Laplacian variance below this = blurry


class FaceEngine:
    """
    All-in-one AI pipeline:
      detect → quality-check → embed → recognize → emotion → age/gender
    """

    def __init__(self):
        self._detector = FaceDetector(confidence_threshold=0.65)
        self._emotion  = EmotionDetector()

    # ── Face Quality ──────────────────────────────────────────────────────────

    def face_quality(self, bgr_face: np.ndarray) -> Tuple[float, List[str]]:
        """
        Return (quality_score 0-1, list_of_issues).
        Score ≥ 0.7 is considered good for registration.
        """
        if bgr_face is None or bgr_face.size == 0:
            return 0.0, ["Empty image"]

        issues: List[str] = []
        h, w = bgr_face.shape[:2]
        scores = []

        # 1. Size
        size_ok = min(h, w) >= MIN_FACE_SIZE
        scores.append(1.0 if size_ok else max(0, min(h, w) / MIN_FACE_SIZE))
        if not size_ok:
            issues.append(f"Face too small ({min(h,w)}px — need {MIN_FACE_SIZE}px)")

        # 2. Blur  (Laplacian variance)
        gray   = cv2.cvtColor(bgr_face, cv2.COLOR_BGR2GRAY)
        lap    = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_s = min(1.0, lap / 200.0)
        scores.append(blur_s)
        if lap < BLUR_THRESHOLD:
            issues.append(f"Image too blurry (sharpness {lap:.0f})")

        # 3. Brightness
        brightness = np.mean(gray) / 255.0
        if brightness < 0.15:
            issues.append("Too dark — improve lighting")
            bright_s = brightness / 0.15
        elif brightness > 0.90:
            issues.append("Too bright / overexposed")
            bright_s = 1.0 - (brightness - 0.90) / 0.10
        else:
            bright_s = 1.0
        scores.append(bright_s)

        # 4. Contrast (std-dev of gray)
        contrast = np.std(gray) / 128.0
        scores.append(min(1.0, contrast))
        if contrast < 0.15:
            issues.append("Low contrast — adjust lighting or background")

        score = float(np.mean(scores))
        return round(score, 3), issues

    # ── Embedding ─────────────────────────────────────────────────────────────

    def embed(self, bgr_face: np.ndarray) -> np.ndarray:
        """
        Generate a normalised face embedding using multi-scale features:
          LBP (59d) + HOG (197d) + gray histogram (64d) + YCrCb histograms (96d) = 416d
        """
        if bgr_face is None or bgr_face.size == 0:
            return np.zeros(416, dtype=np.float32)

        face = cv2.resize(bgr_face, (128, 128))

        # CLAHE normalisation for brightness robustness
        lab   = cv2.cvtColor(face, cv2.COLOR_BGR2LAB)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        face = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # LBP histogram (59 bins)
        lbp       = self._lbp(gray)
        lbp_hist, _ = np.histogram(lbp, bins=59, range=(0, 59))
        lbp_hist  = lbp_hist.astype(np.float32)

        # HOG descriptor
        hog_desc = cv2.HOGDescriptor(
            _winSize=(128, 128), _blockSize=(32, 32),
            _blockStride=(16, 16), _cellSize=(16, 16), _nbins=9
        )
        hog_feat = hog_desc.compute(gray).flatten()[:197]

        # Gray-level histogram (64 bins)
        px_hist, _ = np.histogram(gray, bins=64, range=(0, 256))
        px_hist    = px_hist.astype(np.float32)

        # YCrCb color histograms (3 × 32 = 96 bins) for skin-tone invariance
        ycrcb     = cv2.cvtColor(face, cv2.COLOR_BGR2YCrCb)
        color_hists = []
        for ch in range(3):
            h, _ = np.histogram(ycrcb[:, :, ch], bins=32, range=(0, 256))
            color_hists.append(h.astype(np.float32))
        color_feat = np.concatenate(color_hists)

        vec  = np.concatenate([lbp_hist, hog_feat, px_hist, color_feat]).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-8)

    @staticmethod
    def _lbp(gray: np.ndarray) -> np.ndarray:
        out = np.zeros_like(gray)
        for dy, dx in [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]:
            shifted = np.roll(np.roll(gray, dy, 0), dx, 1)
            out += (gray >= shifted).astype(np.uint8)
        out[:1, :] = 0; out[-1:, :] = 0
        out[:, :1] = 0; out[:, -1:] = 0
        return np.clip(out, 0, 58)

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))

    def recognize(self, query_emb: np.ndarray,
                  db_embeddings: List[Dict],
                  threshold: float = None) -> Tuple[str, float]:
        """
        Match query embedding against database.
        Returns (person_name, confidence) or ('UNKNOWN', best_score).
        Skips DB entries whose embedding dimension differs from query_emb
        (handles old 320-d vs new 416-d enrollments gracefully).
        """
        thresh = threshold if threshold is not None else RECOGNITION_THRESHOLD
        if not db_embeddings:
            return 'UNKNOWN', 0.0
        best_name, best_score = 'UNKNOWN', 0.0
        q_dim = query_emb.shape[0]
        for entry in db_embeddings:
            try:
                db_emb = entry['embedding']
                if db_emb.shape[0] != q_dim:
                    # Dimension mismatch: re-embed on the fly using a
                    # truncated/padded version so old entries still participate
                    min_d = min(q_dim, db_emb.shape[0])
                    a = query_emb[:min_d]
                    b = db_emb[:min_d]
                    norm_a = np.linalg.norm(a)
                    norm_b = np.linalg.norm(b)
                    score = float(np.dot(a, b) / (norm_a * norm_b + 1e-8))
                else:
                    score = self.cosine_similarity(query_emb, db_emb)
                if score > best_score:
                    best_score = score
                    best_name  = entry['name']
            except Exception:
                continue
        if best_score < thresh:
            return 'UNKNOWN', best_score
        return best_name, best_score

    # ── Age / Gender ──────────────────────────────────────────────────────────

    def estimate_age_gender(self, bgr_face: np.ndarray) -> Tuple[str, str]:
        """
        Lightweight multi-feature age/gender heuristic.
        Uses brightness, saturation, texture, edge density, and skin-tone signals.
        """
        if bgr_face is None or bgr_face.size == 0:
            return '?', '?'

        face  = cv2.resize(bgr_face, (64, 64))
        gray  = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        hsv   = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(face, cv2.COLOR_BGR2YCrCb)

        brightness  = np.mean(gray) / 255.0
        saturation  = np.mean(hsv[:, :, 1]) / 255.0
        texture_std = np.std(gray) / 255.0
        cr_mean     = np.mean(ycrcb[:, :, 1]) / 255.0   # red-difference chroma
        cb_mean     = np.mean(ycrcb[:, :, 2]) / 255.0   # blue-difference chroma

        # Edge density (proxy for skin texture / wrinkles)
        edges       = cv2.Canny(gray, 30, 80)
        edge_density = edges.mean() / 255.0

        # Gender: higher Cr (redness) + saturation → female appearance heuristic
        fem_score = (cr_mean * 0.45 + saturation * 0.35 + brightness * 0.20)
        gender = 'Female' if fem_score > 0.38 else 'Male'

        # Age: combine texture variance and edge density
        age_sig = texture_std * 0.6 + edge_density * 0.4
        if age_sig < 0.09:
            age = '18-25'
        elif age_sig < 0.15:
            age = '26-35'
        elif age_sig < 0.22:
            age = '36-50'
        else:
            age = '50+'

        return age, gender

    # ── Full Frame Analysis ───────────────────────────────────────────────────

    def analyze_frame(self, bgr: np.ndarray,
                      db_embeddings: Optional[List[Dict]] = None
                      ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Full pipeline on a BGR frame.
        Returns (annotated_bgr, list_of_face_info_dicts).
        """
        if bgr is None or bgr.size == 0:
            return bgr, []

        faces_raw = self._detector.detect_faces(bgr)
        annotated = bgr.copy()
        results   = []

        for i, face in enumerate(faces_raw):
            x1, y1, x2, y2 = face['bbox']
            conf = face.get('confidence', 0.9)

            # Guard against zero-size crops
            crop = bgr[max(0, y1):max(y2, y1+1), max(0, x1):max(x2, x1+1)]
            if crop.size == 0:
                continue

            # Emotion
            emo_scores  = self._emotion.detect_emotion(crop)
            top_emotion = max(emo_scores, key=emo_scores.get) if emo_scores else 'neutral'
            emoji       = EMOTION_EMOJI.get(top_emotion, '')
            box_color   = EMOTION_COLOR_BGR.get(top_emotion, (0, 220, 0))

            # Age / Gender
            age_est, gender_est = self.estimate_age_gender(crop)

            # Recognition
            name, rec_conf = 'UNKNOWN', 0.0
            if db_embeddings:
                emb = self.embed(crop)
                name, rec_conf = self.recognize(emb, db_embeddings)

            # ── Draw bounding box + labels (ASCII only — OpenCV can't render Unicode) ──
            thickness = 2
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, thickness)

            # Corner accents for a modern look
            clen = max(12, (x2 - x1) // 6)
            for cx, cy, dx, dy in [(x1,y1,1,1),(x2,y1,-1,1),(x1,y2,1,-1),(x2,y2,-1,-1)]:
                cv2.line(annotated, (cx, cy), (cx + dx*clen, cy), box_color, 3)
                cv2.line(annotated, (cx, cy), (cx, cy + dy*clen), box_color, 3)

            # Label text — plain ASCII, no emoji
            label1 = f"{name}  {rec_conf:.0%}" if name != 'UNKNOWN' else 'UNKNOWN'
            label2 = f"{top_emotion.upper()}  {age_est}  {gender_est}"

            font       = cv2.FONT_HERSHEY_SIMPLEX
            scale1, t1 = 0.52, 2
            scale2, t2 = 0.42, 1

            (w1, h1), _ = cv2.getTextSize(label1, font, scale1, t1)
            (w2, h2), _ = cv2.getTextSize(label2, font, scale2, t2)
            bar_w       = max(w1, w2) + 10
            bar_h       = h1 + h2 + 14
            lbl_y       = max(y1 - bar_h, 0)

            # Semi-transparent background strip
            overlay = annotated.copy()
            cv2.rectangle(overlay, (x1, lbl_y), (x1 + bar_w, y1), (10, 10, 20), -1)
            cv2.addWeighted(overlay, 0.75, annotated, 0.25, 0, annotated)

            # Coloured left accent bar
            cv2.rectangle(annotated, (x1, lbl_y), (x1 + 3, y1), box_color, -1)

            cv2.putText(annotated, label1,
                        (x1 + 6, lbl_y + h1 + 4),
                        font, scale1, box_color, t1, cv2.LINE_AA)
            cv2.putText(annotated, label2,
                        (x1 + 6, lbl_y + h1 + h2 + 10),
                        font, scale2, (200, 220, 240), t2, cv2.LINE_AA)

            results.append({
                'id':            i + 1,
                'name':          name,
                'rec_conf':      rec_conf,
                'det_conf':      conf,
                'emotion':       top_emotion,
                'emotion_emoji': emoji,
                'emotions_all':  emo_scores,
                'age':           age_est,
                'gender':        gender_est,
                'bbox':          (x1, y1, x2, y2),
                'crop':          crop,
            })

        return annotated, results


# Singleton
_engine: Optional[FaceEngine] = None

def get_engine() -> FaceEngine:
    global _engine
    if _engine is None:
        _engine = FaceEngine()
    return _engine

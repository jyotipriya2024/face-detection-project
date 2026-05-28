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

# ── Constants ────────────────────────────────────────────────────────────────
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprised']
EMOTION_EMOJI = {
    'happy': '😊', 'sad': '😢', 'angry': '😠', 'surprised': '😲',
    'fear': '😨', 'disgust': '🤢', 'neutral': '😐'
}
EMOTION_COLOR_BGR = {
    'happy':     (50, 205, 50),
    'sad':       (205, 50, 50),
    'angry':     (0, 0, 220),
    'surprised': (0, 165, 255),
    'fear':      (180, 0, 180),
    'disgust':   (0, 100, 200),
    'neutral':   (160, 160, 160),
}
RECOGNITION_THRESHOLD = 0.55   # cosine similarity threshold


class FaceEngine:
    """
    All-in-one AI pipeline:
      detect → align → embed → recognize → emotion → age/gender
    """

    def __init__(self):
        self._detector = FaceDetector(confidence_threshold=0.45)
        self._emotion  = EmotionDetector()

    # ── Embedding ─────────────────────────────────────────────────────────────

    def embed(self, bgr_face: np.ndarray) -> np.ndarray:
        """
        Generate a 256-d face embedding using multi-scale LBP + HOG features.
        Pure NumPy/OpenCV — no deep learning required.
        """
        face = cv2.resize(bgr_face, (128, 128))
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # --- LBP histogram (uniform, 59 bins) ---
        lbp = self._lbp(gray)
        lbp_hist, _ = np.histogram(lbp, bins=59, range=(0, 59))
        lbp_hist = lbp_hist.astype(np.float32)

        # --- HOG descriptor ---
        hog = cv2.HOGDescriptor(
            _winSize=(128, 128), _blockSize=(32, 32),
            _blockStride=(16, 16), _cellSize=(16, 16), _nbins=9
        )
        hog_feat = hog.compute(gray).flatten()[:197]  # clip to fixed size

        # --- Pixel histogram ---
        px_hist, _ = np.histogram(gray, bins=64, range=(0, 256))
        px_hist = px_hist.astype(np.float32)

        vec = np.concatenate([lbp_hist, hog_feat, px_hist]).astype(np.float32)
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-8)

    @staticmethod
    def _lbp(gray: np.ndarray) -> np.ndarray:
        h, w = gray.shape
        out = np.zeros_like(gray)
        for dy, dx in [(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]:
            shifted = np.roll(np.roll(gray, dy, 0), dx, 1)
            out += (gray >= shifted).astype(np.uint8)
        # clip border
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
        Returns (person_name, confidence) or ('UNKNOWN', score).
        """
        thresh = threshold if threshold is not None else RECOGNITION_THRESHOLD
        if not db_embeddings:
            return 'UNKNOWN', 0.0
        best_name, best_score = 'UNKNOWN', 0.0
        for entry in db_embeddings:
            score = self.cosine_similarity(query_emb, entry['embedding'])
            if score > best_score:
                best_score = score
                best_name = entry['name']
        if best_score < thresh:
            return 'UNKNOWN', best_score
        return best_name, best_score

    # ── Age / Gender ──────────────────────────────────────────────────────────

    def estimate_age_gender(self, bgr_face: np.ndarray) -> Tuple[str, str]:
        """
        Lightweight age/gender estimation using image statistics.
        (Deep-learning models require extra downloads; this is a heuristic.)
        """
        if bgr_face.size == 0:
            return '?', '?'
        face = cv2.resize(bgr_face, (64, 64))
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        hsv  = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)

        brightness  = np.mean(gray) / 255.0
        saturation  = np.mean(hsv[:,:,1]) / 255.0
        texture_std = np.std(gray) / 255.0

        # Gender heuristic: higher saturation/brightness → typically female appearance
        gender = 'Female' if (saturation > 0.35 and brightness > 0.45) else 'Male'

        # Age heuristic: lower texture variance → younger
        if texture_std < 0.12:
            age = '18-25'
        elif texture_std < 0.18:
            age = '26-35'
        elif texture_std < 0.24:
            age = '36-50'
        else:
            age = '50+'

        return age, gender

    # ── Full frame analysis ───────────────────────────────────────────────────

    def analyze_frame(self, bgr: np.ndarray,
                      db_embeddings: Optional[List[Dict]] = None
                      ) -> Tuple[np.ndarray, List[Dict]]:
        """
        Run full pipeline on a BGR frame.
        Returns (annotated_bgr, list of face info dicts).
        """
        faces_raw = self._detector.detect_faces(bgr)
        annotated = bgr.copy()
        results   = []

        for i, face in enumerate(faces_raw):
            x1, y1, x2, y2 = face['bbox']
            conf = face.get('confidence', 0.9)

            crop = bgr[max(0,y1):y2, max(0,x1):x2]
            if crop.size == 0:
                continue

            # Emotion
            emo_scores   = self._emotion.detect_emotion(crop)
            top_emotion  = max(emo_scores, key=emo_scores.get) if emo_scores else 'neutral'
            emoji        = EMOTION_EMOJI.get(top_emotion, '')
            box_color    = EMOTION_COLOR_BGR.get(top_emotion, (0, 220, 0))

            # Age / Gender
            age_est, gender_est = self.estimate_age_gender(crop)

            # Recognition
            name, rec_conf = 'UNKNOWN', 0.0
            if db_embeddings:
                emb = self.embed(crop)
                name, rec_conf = self.recognize(emb, db_embeddings)

            # Draw
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)
            label1 = f"{name}  {rec_conf:.0%}" if name != 'UNKNOWN' else '? UNKNOWN'
            label2 = f"{emoji}{top_emotion}  {age_est}  {gender_est}"
            cv2.putText(annotated, label1, (x1, max(y1-22, 14)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, box_color, 2)
            cv2.putText(annotated, label2, (x1, max(y1-4, 28)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)

            results.append({
                'id': i + 1,
                'name': name,
                'rec_conf': rec_conf,
                'det_conf': conf,
                'emotion': top_emotion,
                'emotion_emoji': emoji,
                'emotions_all': emo_scores,
                'age': age_est,
                'gender': gender_est,
                'bbox': (x1, y1, x2, y2),
                'crop': crop,
            })

        return annotated, results


# Singleton
_engine: Optional[FaceEngine] = None

def get_engine() -> FaceEngine:
    global _engine
    if _engine is None:
        _engine = FaceEngine()
    return _engine

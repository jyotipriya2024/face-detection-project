"""
FastAPI Backend — Enterprise Face Recognition & Attendance System
ML: MediaPipe Face Detection + OpenCV LBP+HOG hybrid with enhanced embedding
"""
import sys, base64, logging, json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import numpy as np
import cv2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database import (
    get_person_count, get_log_stats,
    add_person, get_all_persons, delete_person,
    get_logs, get_all_embeddings, log_detection,
    mark_attendance, get_attendance_today, get_attendance_stats,
    get_employee_attendance_history, get_person_full, init_db,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("enterprise-face")

init_db()
app = FastAPI(title="Enterprise Face Recognition API", version="4.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ── ML Model Initialisation ───────────────────────────────────────────────────

# Deep face stack — YuNet (detection + 5 landmarks) and SFace (128-D identity
# embedding), both from the OpenCV Zoo. SFace embeddings are identity-
# discriminative, unlike handcrafted texture/colour features, so different
# people no longer collide at a usable threshold.
MODELS_DIR = ROOT / "models"
YUNET_PATH = MODELS_DIR / "face_detection_yunet_2023mar.onnx"
SFACE_PATH = MODELS_DIR / "face_recognition_sface_2021dec.onnx"

EMB_DIM = 128  # SFace embedding dimensionality

_yunet  = None
_sface  = None
HAS_DNN = False
try:
    if YUNET_PATH.exists() and SFACE_PATH.exists():
        _yunet = cv2.FaceDetectorYN.create(
            str(YUNET_PATH), "", (320, 320),
            score_threshold=0.6, nms_threshold=0.3, top_k=5000,
        )
        _sface = cv2.FaceRecognizerSF.create(str(SFACE_PATH), "")
        HAS_DNN = True
        log.info("✓ DNN face stack loaded: YuNet + SFace (128-D embeddings)")
    else:
        log.warning("DNN model files missing in %s — using Haar fallback (low accuracy)", MODELS_DIR)
except Exception as e:
    log.warning("Failed to init DNN face stack (%s) — using Haar fallback", e)

# OpenCV Haar Cascade — safety-net fallback only (used if DNN models unavailable)
_haar         = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_haar_profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

log.info("Detection pipeline: DNN(YuNet+SFace)=%s  HaarFallback=OK", HAS_DNN)

# ── Matching policy — strict by design, to avoid false identifications ─────────
MATCH_THRESHOLD = 0.40   # min cosine similarity to accept (SFace default is 0.363)
MATCH_MARGIN    = 0.10   # winning identity must beat the runner-up by this much
MIN_FACE_PX     = 40     # ignore faces smaller than this (too small to trust)
DET_SCORE_LIVE  = 0.80   # YuNet confidence for live webcam frames (strict)
DET_SCORE_PHOTO = 0.60   # YuNet confidence for uploaded photos / registration


# ── Core face-analysis helpers ────────────────────────────────────────────────

def _decode(b64: str) -> np.ndarray:
    _, _, data = b64.partition(",")
    raw = base64.b64decode(data or b64)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(422, "Cannot decode image data")
    return img


def _yunet_detect(img: np.ndarray, score: float) -> List[np.ndarray]:
    """
    YuNet detection. Returns a list of face rows (np.float32, length 15:
    x, y, w, h, then 5 landmark x/y pairs, then detection score), sorted by
    area descending. The landmarks are what SFace uses to align the crop.
    """
    h, w = img.shape[:2]
    _yunet.setInputSize((w, h))
    _yunet.setScoreThreshold(float(score))
    _, faces = _yunet.detect(img)
    if faces is None:
        return []
    rows = [f.astype(np.float32) for f in faces
            if f[2] >= MIN_FACE_PX and f[3] >= MIN_FACE_PX]
    rows.sort(key=lambda r: float(r[2] * r[3]), reverse=True)
    return rows


def _haar_rows(img: np.ndarray) -> List[np.ndarray]:
    """Fallback detection (no DNN). Rows carry NaN landmarks so embedding aligns
    by a plain centre-crop instead of landmark warp."""
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray  = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    faces = _haar.detectMultiScale(gray, 1.08, 5, minSize=(MIN_FACE_PX, MIN_FACE_PX))
    rows: List[np.ndarray] = []
    for (x, y, w, h) in faces:
        row = np.full(15, np.nan, dtype=np.float32)
        row[0:4] = (x, y, w, h)
        rows.append(row)
    rows.sort(key=lambda r: float(r[2] * r[3]), reverse=True)
    return rows


def _detect_rows(img: np.ndarray, score: float) -> List[np.ndarray]:
    """Unified detector → list of face rows. Uses DNN when available."""
    return _yunet_detect(img, score) if HAS_DNN else _haar_rows(img)


def _row_bbox(row: np.ndarray) -> tuple:
    return tuple(int(v) for v in row[0:4])


def _embed_row(img: np.ndarray, row: np.ndarray) -> Optional[np.ndarray]:
    """
    Extract a 128-D, L2-normalised SFace identity embedding for one face row.
    Uses landmark-based alignment when available (much more robust to pose),
    otherwise a plain crop. Returns None if embedding cannot be produced.
    """
    if not HAS_DNN:
        return None
    try:
        if np.isnan(row[4:14]).any():
            # No landmarks (Haar fallback) — align by plain crop to 112×112
            x, y, w, h = _row_bbox(row)
            crop = img[max(0, y):y + h, max(0, x):x + w]
            if crop.size == 0:
                return None
            aligned = cv2.resize(crop, (112, 112))
        else:
            aligned = _sface.alignCrop(img, row)
        feat = _sface.feature(aligned).flatten().astype(np.float32)
        n = float(np.linalg.norm(feat))
        return feat / n if n > 0 else feat
    except Exception as e:
        log.warning("Embedding failed: %s", e)
        return None


def _match(query: Optional[np.ndarray],
           threshold: float = MATCH_THRESHOLD,
           margin: float = MATCH_MARGIN):
    """
    Strict 1:N identity match. Returns (db_id, name, score).

    • Compares the query against every enrolled identity. Each identity may hold
      several sample embeddings (shape (N, 128)); we take that identity's best.
    • Accepts only when the top score >= ``threshold`` AND it leads the runner-up
      identity by >= ``margin`` (ambiguous matches are rejected as Unknown).
    • Legacy embeddings whose dimensionality != EMB_DIM are skipped, so old
      enrollments simply never match (re-register them under the new model).
    """
    if query is None:
        return None, "Unknown", 0.0

    # Best score per identity (grouped by name, so multiple records / samples of
    # the same person collapse into one and never compete against each other).
    best_by_name: dict = {}   # name -> (score, id)
    for e in get_all_embeddings():
        emb = e["embedding"]
        if emb.ndim == 1:
            if emb.shape[0] != EMB_DIM:
                continue
            score = float(np.dot(query, emb))
        else:
            if emb.shape[-1] != EMB_DIM:
                continue
            score = float(np.max(emb @ query))  # best sample for this identity
        prev = best_by_name.get(e["name"])
        if prev is None or score > prev[0]:
            best_by_name[e["name"]] = (score, e["id"])

    if not best_by_name:
        return None, "Unknown", 0.0

    scored = sorted(((s, i, n) for n, (s, i) in best_by_name.items()),
                    key=lambda t: t[0], reverse=True)
    best_score, best_id, best_name = scored[0]
    runner_up = scored[1][0] if len(scored) > 1 else 0.0

    if best_score >= threshold and (best_score - runner_up) >= margin:
        return best_id, best_name, best_score
    return None, "Unknown", best_score


def _person_dict(p: dict) -> dict:
    return {
        "id":            p.get("id"),
        "name":          p.get("name", ""),
        "age":           p.get("age", 0),
        "gender":        p.get("gender", ""),
        "employee_id":   p.get("person_id", ""),
        "department":    p.get("department", ""),
        "position":      p.get("position", ""),
        "phone":         p.get("phone", ""),
        "email":         p.get("email", ""),
        "blood_group":   p.get("blood_group", ""),
        "join_date":     p.get("join_date", ""),
        "notes":         p.get("notes", ""),
        "photo_b64":     p.get("photo_b64", ""),
        "registered_at": p.get("created_at", ""),
    }


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterReq(BaseModel):
    name: str; age: int = 0; gender: str = ""; employee_id: str = ""
    department: str = ""; position: str = ""; phone: str = ""; email: str = ""
    blood_group: str = ""; join_date: str = ""; notes: str = ""
    image: str = ""                       # single-frame (backward compatible)
    images: Optional[List[str]] = None    # multi-sample enrollment (preferred)

class DetectReq(BaseModel):
    image: str; log_attendance: bool = True

class SearchReq(BaseModel):
    image: str


# ── Health + Info ─────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status":     "ok",
        "time":       datetime.utcnow().isoformat(),
        "detector":   "YuNet (DNN)" if HAS_DNN else "Haar Cascade (fallback)",
        "embedder":   "SFace 128-D (DNN)" if HAS_DNN else "unavailable",
    }


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/api/dashboard")
def api_dashboard():
    stats = get_log_stats()
    att   = get_attendance_stats()
    return {
        "total_employees":  att["total_employees"],
        "present_today":    att["present_today"],
        "absent_today":     att["absent_today"],
        "attendance_rate":  att["attendance_rate"],
        "total_detections": stats["total"],
        "recognised":       stats["known"],
        "unknown_faces":    stats["unknown"],
        "today_detections": stats.get("today", 0),
        "avg_confidence":   stats.get("avg_confidence", 0),
        "by_department":    att["by_department"],
        "weekly_trend":     att["weekly_trend"],
        "detector":         "YuNet+SFace" if HAS_DNN else "Haar",
    }


# ── Employee Registration ─────────────────────────────────────────────────────

@app.post("/api/employees/register")
def api_register(req: RegisterReq):
    # Accept a burst of frames (preferred) or a single image (backward compatible).
    images = [im for im in (req.images or []) if im] or ([req.image] if req.image else [])
    if not images:
        raise HTTPException(400, "No image provided.")

    if not HAS_DNN:
        raise HTTPException(503, "Face recognition models not loaded on the server.")

    # Build one embedding per usable frame → multi-sample identity template.
    embeddings: List[np.ndarray] = []
    thumb_row = None
    thumb_img = None
    for b64 in images:
        img  = _decode(b64)
        rows = _detect_rows(img, DET_SCORE_PHOTO)
        if not rows:
            continue
        row = rows[0]                       # largest face in this frame
        emb = _embed_row(img, row)
        if emb is None:
            continue
        embeddings.append(emb)
        if thumb_row is None:
            thumb_row, thumb_img = row, img

    if not embeddings:
        raise HTTPException(400, "No face detected. Ensure good lighting, face centred, no obstructions.")

    emb_arr = np.vstack(embeddings).astype(np.float32)   # (N, 128) multi-sample template

    # Crop and store 200×200 JPEG thumbnail from the first good frame
    x, y, w, h = _row_bbox(thumb_row)
    pad  = int(max(w,h)*0.15)
    crop = thumb_img[max(0,y-pad):y+h+pad, max(0,x-pad):x+w+pad]
    if crop.size == 0:
        crop = thumb_img[max(0,y):y+h, max(0,x):x+w]
    thumb  = cv2.resize(crop, (200, 200))
    _, buf = cv2.imencode(".jpg", thumb, [cv2.IMWRITE_JPEG_QUALITY, 82])
    photo  = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()

    person_id = add_person(
        name=req.name.strip(), age=req.age, gender=req.gender,
        person_id=req.employee_id or "",
        phone=req.phone, email=req.email,
        notes=req.notes, embedding=emb_arr, quality_score=float(len(embeddings)),
    )

    try:
        from database import get_conn
        conn = get_conn()
        conn.execute(
            "UPDATE persons SET department=?,position=?,blood_group=?,join_date=?,photo_b64=? WHERE id=?",
            (req.department, req.position, req.blood_group, req.join_date, photo, person_id)
        )
        conn.commit(); conn.close()
    except Exception as e:
        log.warning("Extended columns update: %s", e)

    return {"message": f"Employee '{req.name}' registered with {len(embeddings)} face sample(s).",
            "id": person_id, "samples": len(embeddings)}


# ── Live Detection + Attendance ───────────────────────────────────────────────

@app.post("/api/detect")
def api_detect(req: DetectReq):
    img   = _decode(req.image)
    rows  = _detect_rows(img, DET_SCORE_LIVE)
    results = []
    for i, row in enumerate(rows):
        x, y, w, h        = _row_bbox(row)
        emb               = _embed_row(img, row)
        db_id, name, conf = _match(emb)
        employee          = None
        att_info          = {}

        if name != "Unknown" and db_id:
            p = get_person_full(db_id)
            if p:
                employee = _person_dict(p)
                if req.log_attendance:
                    att_info = mark_attendance(
                        person_db_id=db_id, person_name=name,
                        employee_id=p.get("person_id",""),
                        department=p.get("department",""),
                        position=p.get("position",""),
                        confidence=conf,
                    )
        else:
            log_detection(name, conf, emotion="", age_est="", gender_est="", camera_id="WEB")

        results.append({
            "id":            i,
            "name":          name,
            "confidence":    round(conf, 3),
            "status":        "known" if name != "Unknown" else "unknown",
            "bbox":          [int(x), int(y), int(w), int(h)],
            "employee":      employee,
            "check_in_new":  att_info.get("new", False),
            "check_in_time": att_info.get("check_in", ""),
        })
    return {"detections": results, "count": len(results)}


# ── Face Search ───────────────────────────────────────────────────────────────

@app.post("/api/search")
def api_search(req: SearchReq):
    img   = _decode(req.image)
    rows  = _detect_rows(img, DET_SCORE_PHOTO)

    if len(rows) == 0:
        return {
            "matches": [], "count": 0, "no_face_detected": True,
            "message": "No face could be detected. Try a clear, well-lit, front-facing photo.",
        }

    matches = []
    for row in rows:
        emb               = _embed_row(img, row)
        db_id, name, conf = _match(emb)
        employee          = None; history = []; monthly_rate = 0

        if name != "Unknown" and db_id:
            p = get_person_full(db_id)
            if p:
                employee     = _person_dict(p)
                history      = get_employee_attendance_history(name, 30)
                days_month   = int(datetime.now().strftime("%d"))
                present      = sum(1 for h in history if h.get("date","").startswith(datetime.now().strftime("%Y-%m")))
                monthly_rate = round(present / max(days_month,1) * 100, 1)

        matches.append({
            "name":                    name,
            "confidence":              round(conf, 3),
            "status":                  "known" if name != "Unknown" else "unknown",
            "employee":                employee,
            "attendance_history":      history[:15],
            "monthly_attendance_rate": monthly_rate,
        })
    return {"matches": matches, "count": len(matches), "no_face_detected": False}


# ── Attendance ────────────────────────────────────────────────────────────────

@app.get("/api/attendance/today")
def api_attendance_today():
    return get_attendance_today()

@app.get("/api/attendance/stats")
def api_attendance_stats():
    return get_attendance_stats()

@app.get("/api/attendance/history/{employee_name}")
def api_employee_history(employee_name: str, limit: int = 30):
    return get_employee_attendance_history(employee_name, limit)


# ── Employees ─────────────────────────────────────────────────────────────────

@app.get("/api/employees")
def api_employees():
    rows   = get_all_persons()
    now_ym = datetime.now().strftime("%Y-%m")
    days_m = int(datetime.now().strftime("%d"))
    result = []
    for p in rows:
        d       = _person_dict(p)
        hist    = get_employee_attendance_history(p["name"], 30)
        present = sum(1 for h in hist if h.get("date","").startswith(now_ym))
        d["monthly_attendance"] = present
        d["monthly_total"]      = days_m
        d["attendance_rate"]    = round(present / max(days_m,1) * 100, 1)
        result.append(d)
    return result

@app.delete("/api/employees/{person_id}")
def api_delete_employee(person_id: int):
    delete_person(person_id)
    return {"message": "Employee deleted"}


# ── Logs ──────────────────────────────────────────────────────────────────────

@app.get("/api/logs")
def api_logs(limit: int = 200):
    return [
        {
            "id":         r.get("id"),
            "timestamp":  r.get("timestamp"),
            "name":       r.get("person_name","Unknown"),
            "confidence": float(r.get("confidence",0)),
            "status":     "known" if r.get("person_name","Unknown") != "Unknown" else "unknown",
            "emotion":    r.get("emotion"),
            "camera_id":  r.get("camera_id"),
        }
        for r in get_logs(limit)
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

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

# 1. MediaPipe Face Detection — Tasks API (mediapipe >= 0.10)
HAS_MEDIAPIPE = False
_mp_create    = None
try:
    from mediapipe.tasks import python as _mp_python
    from mediapipe.tasks.python import vision as _mp_vision
    # Tasks API uses model files — check if bundled asset is available
    import mediapipe.tasks.python.vision.face_detector as _mp_fd_mod
    _mp_create = _mp_vision.FaceDetector
    HAS_MEDIAPIPE = True
    log.info("✓ MediaPipe Tasks FaceDetector available")
except Exception as e:
    log.warning("MediaPipe Tasks API unavailable (%s)", e)

# 2. OpenCV Haar Cascade (always available — primary fallback)
_haar         = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
_haar_profile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

log.info("Detection pipeline: MediaPipe=%s  Haar=OK", HAS_MEDIAPIPE)


# ── Core face-analysis helpers ────────────────────────────────────────────────

def _decode(b64: str) -> np.ndarray:
    _, _, data = b64.partition(",")
    raw = base64.b64decode(data or b64)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(422, "Cannot decode image data")
    return img


def _preprocess_gray(img: np.ndarray) -> np.ndarray:
    """CLAHE contrast enhancement — improves detection in poor lighting."""
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def _nms(boxes: List[tuple], thresh: float = 0.35) -> List[tuple]:
    """Non-maximum suppression — removes overlapping duplicate detections."""
    if not boxes:
        return []
    rects  = np.array([[x, y, x+w, y+h] for x,y,w,h in boxes], dtype=float)
    areas  = (rects[:,2]-rects[:,0]) * (rects[:,3]-rects[:,1])
    order  = areas.argsort()[::-1]
    keep: List[int] = []
    while len(order):
        i = order[0]; keep.append(i)
        xx1 = np.maximum(rects[i,0], rects[order[1:],0])
        yy1 = np.maximum(rects[i,1], rects[order[1:],1])
        xx2 = np.minimum(rects[i,2], rects[order[1:],2])
        yy2 = np.minimum(rects[i,3], rects[order[1:],3])
        inter = np.maximum(0, xx2-xx1) * np.maximum(0, yy2-yy1)
        iou   = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
        order = order[1:][iou < thresh]
    return [boxes[i] for i in keep]


def _detect_faces(img: np.ndarray) -> List[tuple]:
    """
    Live detection — CLAHE-enhanced Haar frontal cascade.
    Strict parameters to minimise false positives on webcam frames.
    """
    gray  = _preprocess_gray(img)
    faces = _haar.detectMultiScale(gray, 1.08, 5, minSize=(50, 50))
    result = [tuple(map(int, f)) for f in faces] if len(faces) > 0 else []
    return sorted(_nms(result), key=lambda f: f[2]*f[3], reverse=True)


def _detect_faces_search(img: np.ndarray) -> List[tuple]:
    """
    Search / registration detection — relaxed multi-scale ensemble with
    frontal + profile cascades and NMS, for uploaded photos at various angles.
    """
    gray   = _preprocess_gray(img)
    found: List[tuple] = []

    # Frontal — try 3 scales from strict to permissive
    for scale, nbrs, msz in [(1.06, 4, (35,35)), (1.04, 3, (24,24)), (1.03, 2, (16,16))]:
        fs = _haar.detectMultiScale(gray, scale, nbrs, minSize=msz)
        if len(fs) > 0:
            found.extend([tuple(map(int, f)) for f in fs])
            break  # stop at first scale that succeeds

    # Profile face — catches slight angles
    pf = _haar_profile.detectMultiScale(gray, 1.05, 3, minSize=(25,25))
    if len(pf) > 0:
        found.extend([tuple(map(int, f)) for f in pf])

    # Mirrored profile
    w_img   = gray.shape[1]
    flipped = cv2.flip(gray, 1)
    pf2     = _haar_profile.detectMultiScale(flipped, 1.05, 3, minSize=(25,25))
    if len(pf2) > 0:
        found.extend([(w_img - fx - fw, fy, fw, fh) for fx,fy,fw,fh in pf2])

    return sorted(_nms(found), key=lambda f: f[2]*f[3], reverse=True)


def _extract_embedding(img: np.ndarray, x: int, y: int, w: int, h: int) -> np.ndarray:
    """
    Enhanced embedding — 4-channel feature fusion:
      • LBP histogram (texture, illumination-invariant)
      • HOG descriptor (shape/gradient)
      • YCrCb colour histogram (skin-tone aware)
      • Normalised pixel histogram (intensity)
    All fused and L2-normalised → 416-D vector.
    """
    # Expand bounding box by 15% for context
    pad = int(max(w, h) * 0.15)
    x0  = max(0, x - pad);  y0 = max(0, y - pad)
    x1  = min(img.shape[1], x + w + pad)
    y1  = min(img.shape[0], y + h + pad)
    face = img[y0:y1, x0:x1]
    if face.size == 0:
        face = img[max(0,y):y+h, max(0,x):x+w]

    # Resize to standard size
    face64 = cv2.resize(face, (64, 64))
    gray64 = cv2.cvtColor(face64, cv2.COLOR_BGR2GRAY)

    # ── Channel 1: LBP texture histogram (128-D) ──────────────────────────
    def _lbp(img_gray):
        rows, cols = img_gray.shape
        lbp = np.zeros_like(img_gray, dtype=np.uint8)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                centre = img_gray[i, j]
                code   = 0
                code |= (img_gray[i-1, j-1] >= centre) << 7
                code |= (img_gray[i-1, j  ] >= centre) << 6
                code |= (img_gray[i-1, j+1] >= centre) << 5
                code |= (img_gray[i,   j+1] >= centre) << 4
                code |= (img_gray[i+1, j+1] >= centre) << 3
                code |= (img_gray[i+1, j  ] >= centre) << 2
                code |= (img_gray[i+1, j-1] >= centre) << 1
                code |= (img_gray[i,   j-1] >= centre) << 0
                lbp[i, j] = code
        return lbp

    lbp_img = _lbp(gray64)
    lbp_hist = cv2.calcHist([lbp_img], [0], None, [128], [0, 256])
    lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()

    # ── Channel 2: HOG gradient histogram (128-D) ─────────────────────────
    face128 = cv2.resize(face, (128, 128))
    gray128 = cv2.cvtColor(face128, cv2.COLOR_BGR2GRAY)
    hog     = cv2.HOGDescriptor((128,128),(16,16),(8,8),(8,8),9)
    hog_vec = hog.compute(gray128).flatten()
    # Downsample HOG to 128D
    factor  = len(hog_vec) // 128
    if factor > 1:
        hog_128 = hog_vec[:128*factor].reshape(128, factor).mean(axis=1)
    else:
        hog_128 = np.pad(hog_vec, (0, max(0, 128-len(hog_vec))))[:128]
    hog_128 = hog_128 / (np.linalg.norm(hog_128) + 1e-7)

    # ── Channel 3: YCrCb colour histogram (96-D: 32 per channel) ─────────
    ycrcb  = cv2.cvtColor(face64, cv2.COLOR_BGR2YCrCb)
    ycrcb_hist = np.concatenate([
        cv2.calcHist([ycrcb], [c], None, [32], [0, 256]).flatten()
        for c in range(3)
    ])
    ycrcb_hist = ycrcb_hist / (ycrcb_hist.sum() + 1e-7)

    # ── Channel 4: Intensity histogram (64-D) ────────────────────────────
    int_hist = cv2.calcHist([gray64], [0], None, [64], [0, 256]).flatten()
    int_hist = int_hist / (int_hist.sum() + 1e-7)

    # ── Fuse all channels → 416-D, L2-normalise ──────────────────────────
    fused = np.concatenate([lbp_hist, hog_128, ycrcb_hist, int_hist]).astype(np.float32)
    norm  = np.linalg.norm(fused)
    return fused / (norm + 1e-7)


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0: return 0.0
    return float(np.dot(a / na, b / nb))


def _match(query: np.ndarray, threshold: float = 0.62):
    enrolled = get_all_embeddings()
    best_id, best_name, best_score = None, "Unknown", 0.0
    for e in enrolled:
        score = _cosine(query, e["embedding"])
        if score > best_score and score >= threshold:
            best_id, best_name, best_score = e["id"], e["name"], score
    return best_id, best_name, best_score


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
    blood_group: str = ""; join_date: str = ""; notes: str = ""; image: str

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
        "detector":   "MediaPipe" if HAS_MEDIAPIPE else "Haar Cascade",
        "embedder":   "LBP+HOG+YCrCb 416-D fused",
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
        "detector":         "MediaPipe" if HAS_MEDIAPIPE else "Haar",
    }


# ── Employee Registration ─────────────────────────────────────────────────────

@app.post("/api/employees/register")
def api_register(req: RegisterReq):
    img   = _decode(req.image)
    faces = _detect_faces(img)
    if len(faces) == 0:
        # Retry with relaxed detection for registration
        faces = _detect_faces_search(img)
    if len(faces) == 0:
        raise HTTPException(400, "No face detected. Ensure good lighting, face centred, no obstructions.")
    # Use the largest detected face (already sorted by area descending)
    x, y, w, h = faces[0]
    emb = _extract_embedding(img, x, y, w, h)

    # Crop and store 200×200 JPEG thumbnail
    pad  = int(max(w,h)*0.15)
    crop = img[max(0,y-pad):y+h+pad, max(0,x-pad):x+w+pad]
    if crop.size == 0:
        crop = img[max(0,y):y+h, max(0,x):x+w]
    thumb  = cv2.resize(crop, (200, 200))
    _, buf = cv2.imencode(".jpg", thumb, [cv2.IMWRITE_JPEG_QUALITY, 82])
    photo  = "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()

    person_id = add_person(
        name=req.name.strip(), age=req.age, gender=req.gender,
        person_id=req.employee_id or "",
        phone=req.phone, email=req.email,
        notes=req.notes, embedding=emb, quality_score=0.0,
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

    return {"message": f"Employee '{req.name}' registered successfully.", "id": person_id}


# ── Live Detection + Attendance ───────────────────────────────────────────────

@app.post("/api/detect")
def api_detect(req: DetectReq):
    img   = _decode(req.image)
    faces = _detect_faces(img)
    results = []
    for i, (x, y, w, h) in enumerate(faces):
        emb               = _extract_embedding(img, x, y, w, h)
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
    faces = _detect_faces_search(img)

    if len(faces) == 0:
        return {
            "matches": [], "count": 0, "no_face_detected": True,
            "message": "No face could be detected. Try a clear, well-lit, front-facing photo.",
        }

    matches = []
    for x, y, w, h in faces:
        emb               = _extract_embedding(img, x, y, w, h)
        db_id, name, conf = _match(emb, threshold=0.58)
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

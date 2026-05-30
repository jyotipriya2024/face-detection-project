"""
FastAPI backend — AI Vision Face Recognition System
Wraps the existing Python detection/recognition pipeline.
"""
import sys, os, base64, logging
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
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("aivision")

app = FastAPI(title="AI Vision API", version="2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ── face detection helper (uses OpenCV Haar cascades) ─────────────────────────
_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def _decode(b64: str) -> np.ndarray:
    _, _, data = b64.partition(",")
    raw = base64.b64decode(data or b64)
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(422, "Cannot decode image")
    return img

def _detect_faces(img: np.ndarray):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return _cascade.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

def _extract_embedding(img: np.ndarray, x, y, w, h) -> np.ndarray:
    face = img[max(0,y):y+h, max(0,x):x+w]
    face = cv2.resize(face, (64, 64))
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [416], [0, 256])
    hist = cv2.normalize(hist, hist).flatten().astype(np.float32)
    return hist

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0: return 0.0
    return float(np.dot(a/na, b/nb))

def _match(query: np.ndarray, threshold: float = 0.70):
    enrolled = get_all_embeddings()
    best_name, best_score = "Unknown", 0.0
    for e in enrolled:
        score = _cosine(query, e["embedding"])
        if score > best_score and score >= threshold:
            best_name, best_score = e["name"], score
    return best_name, best_score


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterReq(BaseModel):
    name: str
    roll: Optional[str] = ""
    dept: Optional[str] = ""
    notes: Optional[str] = ""
    image: str

class DetectReq(BaseModel):
    image: str

class SearchReq(BaseModel):
    image: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.get("/api/stats")
def api_stats():
    stats = get_log_stats()
    n = get_person_count()
    rate = round(stats["known"] / max(stats["total"], 1) * 100, 1) if stats["total"] else 0.0
    return {
        "total":   stats["total"],
        "known":   stats["known"],
        "unknown": stats["unknown"],
        "today":   stats.get("today", 0),
        "rate":    rate,
        "avgConf": stats.get("avg_confidence", 0),
        "persons": n,
    }


@app.post("/api/register")
def api_register(req: RegisterReq):
    img = _decode(req.image)
    faces = _detect_faces(img)
    if len(faces) == 0:
        raise HTTPException(400, "No face detected. Please recapture in good lighting.")
    # Use the largest detected face (already sorted by area descending)
    x, y, w, h = faces[0]
    emb = _extract_embedding(img, x, y, w, h)

    person_id = add_person(
        name=req.name.strip(),
        age=0, gender="", person_id=req.roll or "",
        phone="", email="", notes=req.notes or "",
        embedding=emb, quality_score=0.0,
    )
    return {"message": f"'{req.name}' registered successfully.", "id": person_id}


@app.post("/api/detect")
def api_detect(req: DetectReq):
    img = _decode(req.image)
    faces = _detect_faces(img)
    results = []
    for i, (x, y, w, h) in enumerate(faces):
        emb = _extract_embedding(img, x, y, w, h)
        name, conf = _match(emb)
        results.append({
            "id": i, "name": name, "confidence": round(conf, 3),
            "status": "known" if name != "Unknown" else "unknown",
            "bbox": [int(x), int(y), int(w), int(h)],
        })
        log_detection(name, conf, emotion="", age_est="", gender_est="", camera_id="WEB")
    return {"detections": results, "count": len(results)}


@app.post("/api/search")
def api_search(req: SearchReq):
    img = _decode(req.image)
    faces = _detect_faces(img)
    matches = []
    for x, y, w, h in faces:
        emb = _extract_embedding(img, x, y, w, h)
        name, conf = _match(emb)
        matches.append({
            "name": name, "confidence": round(conf, 3),
            "status": "known" if name != "Unknown" else "unknown",
        })
    return {"matches": matches, "count": len(matches)}


@app.get("/api/logs")
def api_logs(limit: int = 100):
    rows = get_logs(limit)
    return [
        {
            "id":         r.get("id"),
            "timestamp":  r.get("timestamp"),
            "name":       r.get("person_name", "Unknown"),
            "confidence": float(r.get("confidence", 0)),
            "status":     "known" if r.get("person_name", "Unknown") != "Unknown" else "unknown",
            "emotion":    r.get("emotion"),
        }
        for r in rows
    ]


@app.get("/api/persons")
def api_persons():
    rows = get_all_persons()
    return [
        {
            "id":               r.get("id"),
            "name":             r.get("name"),
            "roll":             r.get("person_id", ""),
            "dept":             r.get("notes", ""),
            "registered_at":    r.get("created_at", ""),
            "last_seen":        None,
            "total_detections": 0,
        }
        for r in rows
    ]


@app.delete("/api/persons/{person_id}")
def api_delete(person_id: int):
    delete_person(person_id)
    return {"message": "Deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000, reload=True)

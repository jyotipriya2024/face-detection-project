"""
SQLite Database Layer — AI Vision Face Recognition System
Jyotipriya Panda | Reg. 2407432009 | M.Tech CSE 2024-2026 | GIFT Bhubaneswar
"""

import sqlite3
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

DB_PATH = Path(__file__).parent / "face_recognition.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS persons (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            age         INTEGER,
            gender      TEXT,
            person_id   TEXT    UNIQUE,
            phone       TEXT,
            email       TEXT,
            notes       TEXT,
            embedding   TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS detection_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id   INTEGER,
            person_name TEXT    DEFAULT 'UNKNOWN',
            confidence  REAL    DEFAULT 0.0,
            emotion     TEXT    DEFAULT 'neutral',
            age_est     TEXT,
            gender_est  TEXT,
            camera_id   TEXT    DEFAULT 'CAM-01',
            timestamp   TEXT    DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


# ── Persons ─────────────────────────────────────────────────────────────────

def add_person(name: str, age: int, gender: str, person_id: str,
               phone: str, email: str, notes: str, embedding: np.ndarray) -> int:
    conn = get_conn()
    emb_json = json.dumps(embedding.tolist())
    cur = conn.execute(
        "INSERT INTO persons (name,age,gender,person_id,phone,email,notes,embedding) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (name, age, gender, person_id, phone, email, notes, emb_json)
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_all_persons() -> List[Dict]:
    conn = get_conn()
    rows = conn.execute("SELECT * FROM persons ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_person_count() -> int:
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM persons").fetchone()[0]
    conn.close()
    return count


def delete_person(person_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM persons WHERE id=?", (person_id,))
    conn.commit()
    conn.close()


def get_all_embeddings() -> List[Dict]:
    """Return [{name, embedding_array}] for all persons."""
    conn = get_conn()
    rows = conn.execute("SELECT id, name, embedding FROM persons").fetchall()
    conn.close()
    result = []
    for r in rows:
        if r['embedding']:
            emb = np.array(json.loads(r['embedding']), dtype=np.float32)
            result.append({'id': r['id'], 'name': r['name'], 'embedding': emb})
    return result


# ── Detection Logs ────────────────────────────────────────────────────────────

def log_detection(person_name: str, confidence: float, emotion: str,
                  age_est: str = '', gender_est: str = '', camera_id: str = 'CAM-01'):
    conn = get_conn()
    conn.execute(
        "INSERT INTO detection_logs (person_name,confidence,emotion,age_est,gender_est,camera_id) "
        "VALUES (?,?,?,?,?,?)",
        (person_name, confidence, emotion, age_est, gender_est, camera_id)
    )
    conn.commit()
    conn.close()


def get_logs(limit: int = 200) -> List[Dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM detection_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_log_stats() -> Dict:
    conn = get_conn()
    total     = conn.execute("SELECT COUNT(*) FROM detection_logs").fetchone()[0]
    known     = conn.execute("SELECT COUNT(*) FROM detection_logs WHERE person_name != 'UNKNOWN'").fetchone()[0]
    unknown   = conn.execute("SELECT COUNT(*) FROM detection_logs WHERE person_name  = 'UNKNOWN'").fetchone()[0]
    today_str = datetime.now().strftime('%Y-%m-%d')
    today     = conn.execute(
        "SELECT COUNT(*) FROM detection_logs WHERE timestamp LIKE ?", (f"{today_str}%",)
    ).fetchone()[0]
    emotion_rows = conn.execute(
        "SELECT emotion, COUNT(*) as cnt FROM detection_logs GROUP BY emotion ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {
        'total': total, 'known': known, 'unknown': unknown, 'today': today,
        'emotions': {r['emotion']: r['cnt'] for r in emotion_rows}
    }


# Initialize on import
init_db()

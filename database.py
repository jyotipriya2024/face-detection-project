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
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "face_recognition.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def init_db():
    conn = get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS persons (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                name          TEXT    NOT NULL,
                age           INTEGER,
                gender        TEXT,
                person_id     TEXT    UNIQUE,
                phone         TEXT,
                email         TEXT,
                notes         TEXT,
                embedding     TEXT,
                quality_score REAL    DEFAULT 0.0,
                sample_count  INTEGER DEFAULT 1,
                created_at    TEXT    DEFAULT (datetime('now')),
                updated_at    TEXT    DEFAULT (datetime('now'))
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

            CREATE INDEX IF NOT EXISTS idx_logs_timestamp   ON detection_logs(timestamp);
            CREATE INDEX IF NOT EXISTS idx_logs_person_name ON detection_logs(person_name);
            CREATE INDEX IF NOT EXISTS idx_logs_emotion     ON detection_logs(emotion);
            CREATE INDEX IF NOT EXISTS idx_persons_name     ON persons(name);
            CREATE INDEX IF NOT EXISTS idx_persons_pid      ON persons(person_id);
        """)
        # Add new columns when upgrading from older schema
        for col, defn in [
            ("quality_score", "REAL DEFAULT 0.0"),
            ("sample_count",  "INTEGER DEFAULT 1"),
            ("updated_at",    "TEXT DEFAULT (datetime('now'))"),
        ]:
            try:
                conn.execute(f"ALTER TABLE persons ADD COLUMN {col} {defn}")
                conn.commit()
            except Exception:
                pass
    finally:
        conn.close()


# ── Persons ──────────────────────────────────────────────────────────────────

def add_person(name: str, age: int, gender: str, person_id: str,
               phone: str, email: str, notes: str, embedding: np.ndarray,
               quality_score: float = 0.0) -> int:
    conn = get_conn()
    try:
        emb_json = json.dumps(embedding.tolist())
        cur = conn.execute(
            "INSERT INTO persons "
            "(name,age,gender,person_id,phone,email,notes,embedding,quality_score) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (name, age, gender, person_id or None, phone, email, notes,
             emb_json, quality_score)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_person(person_db_id: int, name: str, age: int, gender: str,
                  phone: str, email: str, notes: str) -> bool:
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE persons SET name=?,age=?,gender=?,phone=?,email=?,notes=?,"
            "updated_at=datetime('now') WHERE id=?",
            (name, age, gender, phone, email, notes, person_db_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logger.error("update_person failed: %s", e)
        return False
    finally:
        conn.close()


def get_all_persons() -> List[Dict]:
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM persons ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_person_count() -> int:
    conn = get_conn()
    try:
        return conn.execute("SELECT COUNT(*) FROM persons").fetchone()[0]
    finally:
        conn.close()


def get_person_by_id(person_db_id: int) -> Optional[Dict]:
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM persons WHERE id=?", (person_db_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def check_person_id_exists(person_id: str, exclude_id: int = None) -> bool:
    """Return True if person_id is already taken (optionally ignore exclude_id row)."""
    conn = get_conn()
    try:
        if exclude_id is not None:
            row = conn.execute(
                "SELECT id FROM persons WHERE person_id=? AND id!=?",
                (person_id, exclude_id)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT id FROM persons WHERE person_id=?", (person_id,)
            ).fetchone()
        return row is not None
    finally:
        conn.close()


def delete_person(person_db_id: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM persons WHERE id=?", (person_db_id,))
        conn.commit()
    finally:
        conn.close()


def get_all_embeddings() -> List[Dict]:
    """Return [{id, name, embedding}] for all enrolled persons."""
    conn = get_conn()
    try:
        rows = conn.execute("SELECT id, name, embedding FROM persons").fetchall()
        result = []
        for r in rows:
            if r['embedding']:
                try:
                    emb = np.array(json.loads(r['embedding']), dtype=np.float32)
                    result.append({'id': r['id'], 'name': r['name'], 'embedding': emb})
                except Exception:
                    pass
        return result
    finally:
        conn.close()


def search_persons(query: str) -> List[Dict]:
    conn = get_conn()
    try:
        q = f"%{query}%"
        rows = conn.execute(
            "SELECT * FROM persons WHERE name LIKE ? OR person_id LIKE ? OR email LIKE ? "
            "ORDER BY name",
            (q, q, q)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def export_persons_csv() -> str:
    """Return CSV string of all persons (without embeddings)."""
    persons = get_all_persons()
    if not persons:
        return "id,name,age,gender,person_id,phone,email,notes,quality_score,created_at\n"
    lines = ["id,name,age,gender,person_id,phone,email,notes,quality_score,created_at"]
    for p in persons:
        row = [
            str(p.get('id', '')),
            f'"{p.get("name","")}"',
            str(p.get('age', '')),
            p.get('gender', ''),
            p.get('person_id', '') or '',
            p.get('phone', '') or '',
            p.get('email', '') or '',
            f'"{p.get("notes","") or ""}"',
            str(p.get('quality_score', 0)),
            p.get('created_at', '')[:19] if p.get('created_at') else '',
        ]
        lines.append(','.join(row))
    return '\n'.join(lines)


# ── Detection Logs ────────────────────────────────────────────────────────────

def log_detection(person_name: str, confidence: float, emotion: str,
                  age_est: str = '', gender_est: str = '', camera_id: str = 'CAM-01'):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO detection_logs "
            "(person_name,confidence,emotion,age_est,gender_est,camera_id) "
            "VALUES (?,?,?,?,?,?)",
            (person_name, confidence, emotion, age_est, gender_est, camera_id)
        )
        conn.commit()
    finally:
        conn.close()


def get_logs(limit: int = 200) -> List[Dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM detection_logs ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_logs_by_date_range(start_date: str, end_date: str,
                           limit: int = 5000) -> List[Dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM detection_logs "
            "WHERE date(timestamp) BETWEEN ? AND ? "
            "ORDER BY timestamp DESC LIMIT ?",
            (start_date, end_date, limit)
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_log_stats() -> Dict:
    conn = get_conn()
    try:
        total   = conn.execute("SELECT COUNT(*) FROM detection_logs").fetchone()[0]
        known   = conn.execute(
            "SELECT COUNT(*) FROM detection_logs WHERE person_name != 'UNKNOWN'"
        ).fetchone()[0]
        unknown = conn.execute(
            "SELECT COUNT(*) FROM detection_logs WHERE person_name = 'UNKNOWN'"
        ).fetchone()[0]
        today_str = datetime.now().strftime('%Y-%m-%d')
        today = conn.execute(
            "SELECT COUNT(*) FROM detection_logs WHERE timestamp LIKE ?",
            (f"{today_str}%",)
        ).fetchone()[0]
        emotion_rows = conn.execute(
            "SELECT emotion, COUNT(*) as cnt FROM detection_logs "
            "GROUP BY emotion ORDER BY cnt DESC"
        ).fetchall()
        avg_conf_row = conn.execute(
            "SELECT AVG(confidence) FROM detection_logs WHERE person_name != 'UNKNOWN'"
        ).fetchone()[0]
        avg_conf = round(avg_conf_row or 0.0, 3)
        return {
            'total': total, 'known': known, 'unknown': unknown, 'today': today,
            'avg_confidence': avg_conf,
            'emotions': {r['emotion']: r['cnt'] for r in emotion_rows}
        }
    finally:
        conn.close()


def get_person_detection_stats() -> List[Dict]:
    """Per-person detection counts, avg confidence, last seen."""
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT person_name, COUNT(*) as count, "
            "AVG(confidence) as avg_conf, MAX(timestamp) as last_seen "
            "FROM detection_logs WHERE person_name != 'UNKNOWN' "
            "GROUP BY person_name ORDER BY count DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_last_seen(person_name: str) -> Optional[str]:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT timestamp FROM detection_logs "
            "WHERE person_name=? ORDER BY timestamp DESC LIMIT 1",
            (person_name,)
        ).fetchone()
        return row['timestamp'] if row else None
    finally:
        conn.close()


def clear_logs():
    conn = get_conn()
    try:
        conn.execute("DELETE FROM detection_logs")
        conn.commit()
    finally:
        conn.close()


# Initialize on import
init_db()

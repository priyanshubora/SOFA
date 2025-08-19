# backend/db.py
import sqlite3
from pathlib import Path
from datetime import datetime

# ✅ Point to /data/uploads.db
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "uploads.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)  # make sure /data exists
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        raw_text TEXT,
        cleaned_text TEXT,
        original_path TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def save_upload(filename: str, raw_text: str, cleaned_text: str, original_path: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO uploads (filename, raw_text, cleaned_text, original_path, uploaded_at)
        VALUES (?, ?, ?, ?, ?)
    """, (filename, raw_text, cleaned_text, original_path, datetime.utcnow().isoformat()))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def list_uploads():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, uploaded_at FROM uploads ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1], "uploaded_at": r[2]} for r in rows]

def get_upload(file_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, filename, raw_text, cleaned_text, original_path, uploaded_at FROM uploads WHERE id=?", (file_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "filename": row[1],
        "raw_text": row[2],
        "cleaned_text": row[3],
        "original_path": row[4],
        "uploaded_at": row[5]
    }

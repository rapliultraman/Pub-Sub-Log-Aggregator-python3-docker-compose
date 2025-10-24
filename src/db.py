import sqlite3
import threading
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DB_PATH = "/app/data/dedub.db"
_lock = threading.Lock()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")  # Faster concurrent writes
    conn.execute("PRAGMA synchronous = NORMAL;") # Reduce fsync overhead
    conn.execute("PRAGMA temp_store = MEMORY;")  # Faster temp tables
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                event_id TEXT,
                timestamp TEXT,
                source TEXT,
                UNIQUE(topic, event_id)
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT,
                event_id TEXT,
                timestamp TEXT,
                source TEXT,
                payload TEXT
            )
        """)
        conn.commit()

def try_mark_processed_bulk(events: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Masukkan batch event dan return hanya yang berhasil (belum duplikat)."""
    inserted = []
    with _lock, get_db_connection() as conn:
        cur = conn.cursor()
        for ev in events:
            try:
                cur.execute(
                    "INSERT INTO processed_events (topic, event_id, timestamp, source) VALUES (?, ?, ?, ?)",
                    (ev["topic"], ev["event_id"], ev["timestamp"], ev["source"])
                )
                inserted.append(ev)
            except sqlite3.IntegrityError:
                continue
        conn.commit()
    return inserted

def store_events_bulk(events: List[Dict[str, Any]]):
    """Batch insert events ke tabel utama."""
    if not events:
        return
    with _lock, get_db_connection() as conn:
        cur = conn.cursor()
        cur.executemany("""
            INSERT INTO events (topic, event_id, timestamp, source, payload)
            VALUES (?, ?, ?, ?, ?)
        """, [(ev["topic"], ev["event_id"], ev["timestamp"], ev["source"], ev["payload"]) for ev in events])
        conn.commit()

def get_events(topic: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        if topic:
            cur.execute("SELECT * FROM events WHERE topic=? ORDER BY id ASC", (topic,))
        else:
            cur.execute("SELECT * FROM events ORDER BY id ASC")
        rows = cur.fetchall()
    return [dict(r) for r in rows]

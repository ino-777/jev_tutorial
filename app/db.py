"""SQLite storage for todos (stdlib only, kept intentionally simple for the tutorial)."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "todos.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                deadline TEXT,
                category TEXT,
                category_confidence REAL,
                is_urgent INTEGER,
                urgent_probability REAL,
                priority INTEGER,
                priority_confidence REAL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        # Migrate DBs created before the `deadline` column existed.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(todos)")}
        if "deadline" not in columns:
            conn.execute("ALTER TABLE todos ADD COLUMN deadline TEXT")

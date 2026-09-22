"""FastAPI app: a todo list where the jev model tags each new todo."""

import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from typesafe_sdk import TypeSafeError

from . import db
from .ai import analyze_todo
from .schemas import Todo, TodoCreate, TodoUpdate

app = FastAPI(title="jev TODO tutorial")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.on_event("startup")
def on_startup() -> None:
    db.init_db()


def _row_to_todo(row: sqlite3.Row) -> Todo:
    return Todo(
        id=row["id"],
        text=row["text"],
        done=bool(row["done"]),
        deadline=row["deadline"],
        category=row["category"],
        category_confidence=row["category_confidence"],
        is_urgent=bool(row["is_urgent"]) if row["is_urgent"] is not None else None,
        urgent_probability=row["urgent_probability"],
        priority=row["priority"],
        priority_confidence=row["priority_confidence"],
        created_at=row["created_at"],
    )


@app.get("/api/todos", response_model=list[Todo])
def list_todos() -> list[Todo]:
    with db.get_connection() as conn:
        rows = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    return [_row_to_todo(row) for row in rows]


@app.post("/api/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoCreate) -> Todo:
    text = payload.text.strip()
    if not text:
        raise HTTPException(400, "text must not be empty")

    try:
        analysis = analyze_todo(text, payload.deadline)
    except TypeSafeError as exc:
        raise HTTPException(502, f"TypeSafe AI request failed: {exc}") from exc

    with db.get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO todos
                (text, deadline, category, category_confidence, is_urgent, urgent_probability, priority, priority_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                text,
                payload.deadline,
                analysis.category,
                analysis.category_confidence,
                int(analysis.is_urgent),
                analysis.urgent_probability,
                analysis.priority,
                analysis.priority_confidence,
            ),
        )
        todo_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return _row_to_todo(row)


@app.patch("/api/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    with db.get_connection() as conn:
        conn.execute("UPDATE todos SET done = ? WHERE id = ?", (int(payload.done), todo_id))
        row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "todo not found")
    return _row_to_todo(row)


@app.delete("/api/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    with db.get_connection() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))


# Registered after the /api routes above, so those still match first.
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

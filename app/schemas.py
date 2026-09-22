"""Pydantic models for the HTTP API (separate from the AI question/answer types in ai.py)."""

from pydantic import BaseModel


class TodoCreate(BaseModel):
    text: str
    deadline: str | None = None
    """ISO 8601 (e.g. "2026-09-25T18:00")。<input type="datetime-local"> の値をそのまま受け取る。"""


class TodoUpdate(BaseModel):
    done: bool


class Todo(BaseModel):
    id: int
    text: str
    done: bool
    deadline: str | None = None
    category: str | None = None
    category_confidence: float | None = None
    is_urgent: bool | None = None
    urgent_probability: float | None = None
    priority: int | None = None
    priority_confidence: float | None = None
    created_at: str

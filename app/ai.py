"""Asks TypeSafe AI's System One model (jev) to analyze a todo's text.

System One takes a `state` (the content) plus a set of typed `questions`, and returns
typed, structured answers instead of free text:

- Choice -> pick one label from a fixed set, with per-label probabilities
- Noul   -> a yes/no probability (0..1)
- Score  -> a value on an ordered rubric, with per-level probabilities

See https://docs.typesafe.ai/concepts/system-one for details.
"""

from datetime import datetime

from pydantic import BaseModel
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

CATEGORIES = {
    "work": "A task tied to a job, project, or professional responsibility.",
    "personal": "A personal errand, chore, or private matter.",
    "shopping": "Buying, ordering, or picking up something.",
    "health": "Exercise, medical appointments, or wellbeing.",
    "other": None,
}

PRIORITY_LEVELS = [
    "Low priority: no deadline pressure, purely optional.",
    "Medium priority: should get done soon, but nothing breaks if it waits.",
    "High priority: time-sensitive or blocking something important.",
]


class TodoAnalysis(BaseModel):
    category: str
    category_confidence: float
    is_urgent: bool
    urgent_probability: float
    priority: int
    priority_confidence: float


def _build_state(text: str, deadline: str | None) -> str:
    """Build the `state` string passed to jev, including the deadline (if any) and
    the current time, so urgency/priority judgments can account for time pressure."""
    if not deadline:
        return text
    now = datetime.now().isoformat(timespec="minutes")
    return f"タスク: {text}\n締切: {deadline}\n現在日時: {now}"


def analyze_todo(text: str, deadline: str | None = None) -> TodoAnalysis:
    """Classify a todo's category, urgency, and priority using the jev model."""
    state = _build_state(text, deadline)
    with TypeSafeClient() as client:
        result = client.system_one(
            state=state,
            questions={
                "category": Choice(
                    instructions="What category does this todo belong to?",
                    criteria=CATEGORIES,
                ),
                "urgent": Noul(
                    instructions="Does this todo need to be done very soon (today or tomorrow)?",
                ),
                "priority": Score(
                    instructions="How high priority is this todo?",
                    criteria=PRIORITY_LEVELS,
                ),
            },
        )

    choice = result.choices["category"]
    noul = result.nouls["urgent"]
    score = result.scores["priority"]

    return TodoAnalysis(
        category=choice.choice,
        category_confidence=choice.confidence,
        is_urgent=noul.noul >= 0.5,
        urgent_probability=noul.noul,
        priority=round(score.score),
        priority_confidence=score.confidence,
    )

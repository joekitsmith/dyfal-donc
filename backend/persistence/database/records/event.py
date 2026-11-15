import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class EventRecord:
    """An event row, read out of the database, with its place in the learner's log."""

    sequence: int
    selection_id: uuid.UUID
    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None
    outcome: str
    reviewed_at: datetime

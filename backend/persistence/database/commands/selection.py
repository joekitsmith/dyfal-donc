import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class IssueSelection:
    """Remember that an exercise was issued to a learner."""

    learner_id: uuid.UUID
    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None
    issued_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ConsumeSelection:
    """Mark a learner's selection as answered at the given time."""

    learner_id: uuid.UUID
    selection_id: uuid.UUID
    at: datetime

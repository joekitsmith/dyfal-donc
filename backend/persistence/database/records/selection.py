import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class IssuedSelectionRecord:
    """An issued selection row, read out of the database."""

    id: uuid.UUID
    learner_id: uuid.UUID
    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None

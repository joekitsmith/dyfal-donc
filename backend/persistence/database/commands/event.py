import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AppendEvent:
    """Add an event to the end of a learner's log.

    ``outcome`` is text, and the database only accepts the outcomes it knows.
    """

    learner_id: uuid.UUID
    selection_id: uuid.UUID
    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None
    outcome: str
    reviewed_at: datetime

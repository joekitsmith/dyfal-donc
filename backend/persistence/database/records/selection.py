import uuid
from dataclasses import dataclass
from datetime import datetime

from engine.learner import Outcome, ReviewEvent


@dataclass(frozen=True, slots=True, kw_only=True)
class IssuedSelectionRecord:
    """An issued selection row, with what is needed to record its outcome."""

    id: uuid.UUID
    learner_id: uuid.UUID
    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None
    issued_at: datetime
    expires_at: datetime
    consumed_at: datetime | None

    def as_event(self, outcome: Outcome, reviewed_at: datetime) -> ReviewEvent:
        """The event to record once the learner has done this exercise."""
        return ReviewEvent(
            exercise_id=self.exercise_id,
            item_ids=self.item_ids,
            new_item=self.new_item,
            outcome=outcome,
            reviewed_at=reviewed_at,
        )

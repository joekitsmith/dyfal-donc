import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerRecord:
    """A learner row, read out of the database."""

    id: uuid.UUID
    course_release: str
    created_at: datetime

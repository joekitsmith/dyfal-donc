import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ProblemReportRecord:
    """A problem report, read out of the database."""

    id: int
    user_id: uuid.UUID
    exercise_id: str | None
    item_id: str | None
    release_hash: str
    source: str
    category: str
    description: str
    created_at: datetime
    resolved_at: datetime | None

import uuid
from enum import StrEnum

from pydantic import BaseModel


class ReportedOutcome(StrEnum):
    """How the learner says an exercise went."""

    GOT_IT = "got_it"
    MISSED_IT = "missed_it"


class OutcomeRequest(BaseModel):
    selection_id: uuid.UUID
    outcome: ReportedOutcome


class OutcomeResponse(BaseModel):
    """``recorded`` is false when this outcome had already been recorded."""

    sequence: int
    recorded: bool

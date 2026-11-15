import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AddLearner:
    """Add the user's learner, who starts on the given course release."""

    user_id: uuid.UUID
    course_release: str

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class SaveUserSettings:
    """Save all of a user's settings, replacing any saved before."""

    user_id: uuid.UUID
    think_time_multiplier: float
    slow_welsh_enabled: bool
    learning_session_minutes: int | None
    updated_at: datetime

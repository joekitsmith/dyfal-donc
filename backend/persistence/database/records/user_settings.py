import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class UserSettingsRecord:
    """A user's saved settings, read out of the database."""

    user_id: uuid.UUID
    think_time_multiplier: float
    slow_welsh_enabled: bool
    learning_session_minutes: int | None
    updated_at: datetime

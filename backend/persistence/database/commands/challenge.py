import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AddChallenge:
    """Remember a challenge given to a browser, until the given time."""

    challenge: bytes
    purpose: str
    user_id: uuid.UUID | None
    created_at: datetime
    expires_at: datetime

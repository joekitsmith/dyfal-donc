import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class ChallengeRecord:
    """A challenge that was used, as it was stored."""

    challenge: bytes
    purpose: str
    user_id: uuid.UUID | None

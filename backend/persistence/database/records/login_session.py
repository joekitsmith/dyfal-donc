import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginSessionRecord:
    """A login session row, read out of the database."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    authenticated_at: datetime
    last_seen_at: datetime
    expires_at: datetime

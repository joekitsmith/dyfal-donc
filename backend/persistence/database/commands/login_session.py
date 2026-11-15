import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AddLoginSession:
    """Sign a browser in as a user, identified by the hash of its token."""

    user_id: uuid.UUID
    token_hash: bytes
    created_at: datetime
    authenticated_at: datetime
    expires_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ExtendLoginSession:
    """Note that the session was used, and move its expiry."""

    login_session_id: uuid.UUID
    seen_at: datetime
    expires_at: datetime

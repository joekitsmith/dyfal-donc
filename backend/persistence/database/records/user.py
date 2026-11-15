import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class UserRecord:
    """A user row, read out of the database. ``is_guest`` means no passkeys."""

    id: uuid.UUID
    display_name: str | None
    is_guest: bool
    created_at: datetime

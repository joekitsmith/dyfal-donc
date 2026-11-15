import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class CredentialRecord:
    """A passkey row, read out of the database."""

    id: uuid.UUID
    user_id: uuid.UUID
    credential_id: bytes
    public_key: bytes
    sign_count: int
    transports: tuple[str, ...]
    label: str
    created_at: datetime
    last_used_at: datetime | None

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class AddCredential:
    """Add a passkey to a user."""

    user_id: uuid.UUID
    credential_id: bytes
    public_key: bytes
    sign_count: int
    transports: tuple[str, ...]
    label: str
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class RecordCredentialUse:
    """Note that a passkey was used to sign in."""

    credential_id: bytes
    sign_count: int
    used_at: datetime

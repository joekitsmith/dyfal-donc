import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplaceRecoveryCodes:
    """Give the user a new set of recovery codes, and delete the old ones."""

    user_id: uuid.UUID
    code_hashes: tuple[bytes, ...]
    created_at: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class UseRecoveryCode:
    """Use up the recovery code with this hash, at the given time."""

    code_hash: bytes
    at: datetime

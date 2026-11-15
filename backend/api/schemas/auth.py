import uuid
from datetime import datetime

from pydantic import BaseModel, Field

type PasskeyJson = dict[str, object]


class UserResponse(BaseModel):
    id: uuid.UUID
    is_guest: bool
    created_at: datetime


class PasskeyResponse(BaseModel):
    id: uuid.UUID
    label: str
    created_at: datetime
    last_used_at: datetime | None


class RegistrationVerifyRequest(BaseModel):
    """The browser's new passkey, as its WebAuthn API produced it."""

    credential: PasskeyJson
    label: str | None = Field(default=None, min_length=1, max_length=128)


class AuthenticationVerifyRequest(BaseModel):
    """The browser's signed answer, as its WebAuthn API produced it."""

    credential: PasskeyJson

from api.schemas import PasskeyResponse, UserResponse
from persistence.database import CredentialRecord, UserRecord


def to_user_response(record: UserRecord) -> UserResponse:
    return UserResponse(
        id=record.id, is_guest=record.is_guest, created_at=record.created_at
    )


def to_passkey_response(record: CredentialRecord) -> PasskeyResponse:
    return PasskeyResponse(
        id=record.id,
        label=record.label,
        created_at=record.created_at,
        last_used_at=record.last_used_at,
    )

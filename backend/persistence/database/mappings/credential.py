from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import CredentialRecord


def to_credential_record(row: models.WebauthnCredential) -> CredentialRecord:
    return CredentialRecord(
        id=row.id,
        user_id=row.user_id,
        credential_id=row.credential_id,
        public_key=row.public_key,
        sign_count=row.sign_count,
        transports=tuple(row.transports),
        label=row.label,
        created_at=to_utc(row.created_at),
        last_used_at=None if row.last_used_at is None else to_utc(row.last_used_at),
    )

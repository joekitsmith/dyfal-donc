import uuid

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import AddCredential, RecordCredentialUse
from persistence.database.errors import CredentialAlreadyRegisteredError
from persistence.database.mappings import to_credential_record
from persistence.database.records import CredentialRecord


class CredentialRepository:
    """The passkeys users sign in with. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddCredential) -> CredentialRecord:
        if self.by_credential_id(command.credential_id) is not None:
            raise CredentialAlreadyRegisteredError("Passkey is already registered")

        row = models.WebauthnCredential(
            user_id=command.user_id,
            credential_id=command.credential_id,
            public_key=command.public_key,
            sign_count=command.sign_count,
            transports=list(command.transports),
            label=command.label,
            created_at=command.created_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_credential_record(row)

    def for_user(self, user_id: uuid.UUID) -> tuple[CredentialRecord, ...]:
        """The user's passkeys, oldest first."""
        return tuple(
            to_credential_record(row)
            for row in self._session.scalars(
                select(models.WebauthnCredential)
                .where(models.WebauthnCredential.user_id == user_id)
                .order_by(
                    models.WebauthnCredential.created_at,
                    models.WebauthnCredential.id,
                )
            )
        )

    def by_credential_id(self, credential_id: bytes) -> CredentialRecord | None:
        row = self._session.scalars(
            select(models.WebauthnCredential).where(
                models.WebauthnCredential.credential_id == credential_id
            )
        ).one_or_none()
        return None if row is None else to_credential_record(row)

    def record_use(self, command: RecordCredentialUse) -> None:
        self._session.execute(
            update(models.WebauthnCredential)
            .where(models.WebauthnCredential.credential_id == command.credential_id)
            .values(sign_count=command.sign_count, last_used_at=command.used_at)
        )

    def delete(self, user_id: uuid.UUID, credential_pk: uuid.UUID) -> bool:
        """Delete one of the user's passkeys. Another user's is never found."""
        row = self._session.scalars(
            select(models.WebauthnCredential).where(
                models.WebauthnCredential.id == credential_pk,
                models.WebauthnCredential.user_id == user_id,
            )
        ).one_or_none()
        if row is None:
            return False

        self._session.delete(row)
        self._session.flush()
        return True

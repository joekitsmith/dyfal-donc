import uuid

from sqlalchemy import delete, exists, select
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import AddUser
from persistence.database.mappings import to_user_record
from persistence.database.records import UserRecord


class UserRepository:
    """Users. Repositories never commit: the caller owns the transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddUser) -> UserRecord:
        row = models.User(display_name=command.display_name)
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return to_user_record(row, is_guest=True)

    def get(self, user_id: uuid.UUID) -> UserRecord | None:
        row = self._session.get(models.User, user_id)
        if row is None:
            return None

        has_passkey = self._session.scalar(
            select(exists().where(models.WebauthnCredential.user_id == user_id))
        )
        return to_user_record(row, is_guest=not has_passkey)

    def delete(self, user_id: uuid.UUID) -> bool:
        """Delete the user and, with them, everything that belongs to them.

        The database does the rest: every table that refers to a user is
        deleted from when the user goes. Returns whether there was a user.
        """
        deleted = self._session.scalars(
            delete(models.User)
            .where(models.User.id == user_id)
            .returning(models.User.id)
        ).all()
        return len(deleted) > 0

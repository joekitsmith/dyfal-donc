import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import ReplaceRecoveryCodes, UseRecoveryCode
from persistence.database.errors import RecoveryCodeNotFoundError


class RecoveryCodeRepository:
    """Recovery codes, by hash only. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def replace(self, command: ReplaceRecoveryCodes) -> None:
        self._session.execute(
            delete(models.RecoveryCode).where(
                models.RecoveryCode.user_id == command.user_id
            )
        )
        self._session.add_all(
            models.RecoveryCode(
                user_id=command.user_id,
                code_hash=code_hash,
                created_at=command.created_at,
            )
            for code_hash in command.code_hashes
        )
        self._session.flush()

    def remaining(self, user_id: uuid.UUID) -> int:
        """How many of the user's codes are unused."""
        return (
            self._session.scalar(
                select(func.count())
                .select_from(models.RecoveryCode)
                .where(
                    models.RecoveryCode.user_id == user_id,
                    models.RecoveryCode.used_at.is_(None),
                )
            )
            or 0
        )

    def use(self, command: UseRecoveryCode) -> uuid.UUID:
        """Use the code up and return whose it was.

        Finding and marking it is one statement, so two requests with the same
        code cannot both succeed.
        """
        user_id = self._session.scalars(
            update(models.RecoveryCode)
            .where(
                models.RecoveryCode.code_hash == command.code_hash,
                models.RecoveryCode.used_at.is_(None),
            )
            .values(used_at=command.at)
            .returning(models.RecoveryCode.user_id)
        ).one_or_none()
        if user_id is None:
            raise RecoveryCodeNotFoundError("Recovery code is unknown or already used")

        return user_id

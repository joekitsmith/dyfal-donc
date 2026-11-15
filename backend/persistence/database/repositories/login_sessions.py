import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import AddLoginSession, ExtendLoginSession
from persistence.database.mappings import to_login_session_record
from persistence.database.records import LoginSessionRecord


class LoginSessionRepository:
    """Who is signed in, by the hash of their token. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddLoginSession) -> LoginSessionRecord:
        row = models.LoginSession(
            user_id=command.user_id,
            token_hash=command.token_hash,
            created_at=command.created_at,
            last_seen_at=command.created_at,
            expires_at=command.expires_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_login_session_record(row)

    def by_token_hash(self, token_hash: bytes) -> LoginSessionRecord | None:
        row = self._session.scalars(
            select(models.LoginSession).where(
                models.LoginSession.token_hash == token_hash
            )
        ).one_or_none()
        return None if row is None else to_login_session_record(row)

    def extend(self, command: ExtendLoginSession) -> None:
        self._session.execute(
            update(models.LoginSession)
            .where(models.LoginSession.id == command.login_session_id)
            .values(last_seen_at=command.seen_at, expires_at=command.expires_at)
        )

    def delete(self, login_session_id: uuid.UUID) -> None:
        self._session.execute(
            delete(models.LoginSession).where(
                models.LoginSession.id == login_session_id
            )
        )

    def delete_expired(self, now: datetime) -> int:
        return len(
            self._session.scalars(
                delete(models.LoginSession)
                .where(models.LoginSession.expires_at <= now)
                .returning(models.LoginSession.id)
            ).all()
        )

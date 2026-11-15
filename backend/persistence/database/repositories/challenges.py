from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import AddChallenge
from persistence.database.errors import ChallengeNotFoundError
from persistence.database.mappings import to_challenge_record
from persistence.database.records import ChallengeRecord


class ChallengeRepository:
    """Challenges handed out for passkey ceremonies. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddChallenge) -> None:
        self._session.add(
            models.WebauthnChallenge(
                challenge=command.challenge,
                purpose=command.purpose,
                user_id=command.user_id,
                created_at=command.created_at,
                expires_at=command.expires_at,
            )
        )
        self._session.flush()

    def consume(self, challenge: bytes, purpose: str, now: datetime) -> ChallengeRecord:
        """Use the challenge up: it is deleted, so it can only be used once.

        Deleting and reading it back is one statement, so two requests with the
        same challenge cannot both get it.
        """
        row = self._session.scalars(
            delete(models.WebauthnChallenge)
            .where(
                models.WebauthnChallenge.challenge == challenge,
                models.WebauthnChallenge.purpose == purpose,
                models.WebauthnChallenge.expires_at > now,
            )
            .returning(models.WebauthnChallenge)
        ).one_or_none()
        if row is None:
            raise ChallengeNotFoundError("Challenge is unknown, used or expired")

        return to_challenge_record(row)

    def delete_expired(self, now: datetime) -> int:
        return len(
            self._session.scalars(
                delete(models.WebauthnChallenge)
                .where(models.WebauthnChallenge.expires_at <= now)
                .returning(models.WebauthnChallenge.id)
            ).all()
        )

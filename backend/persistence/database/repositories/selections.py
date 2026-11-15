import uuid
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from engine.scheduler import Selection
from persistence.database.errors import (
    SelectionAlreadyAnsweredError,
    SelectionExpiredError,
    SelectionNotFoundError,
)
from persistence.database import models
from persistence.database.mappings import to_issued_selection_record
from persistence.database.records import IssuedSelectionRecord


class SelectionRepository:
    """The exercises issued to learners. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def issue(
        self,
        learner_id: uuid.UUID,
        selection: Selection,
        issued_at: datetime,
        lifetime: timedelta,
    ) -> IssuedSelectionRecord:
        row = models.IssuedSelection(
            learner_id=learner_id,
            exercise_id=selection.exercise_id,
            item_ids=list(selection.exercise.declared_items),
            new_item=selection.introduces,
            issued_at=issued_at,
            expires_at=issued_at + lifetime,
        )
        self._session.add(row)
        self._session.flush()
        return to_issued_selection_record(row)

    def consume(
        self, learner_id: uuid.UUID, selection_id: uuid.UUID, at: datetime
    ) -> IssuedSelectionRecord:
        """Mark the selection answered, so the outcome is recorded only once.

        The row is locked until the transaction ends, so two answers arriving
        together cannot both succeed.
        """
        row = self._session.scalars(
            select(models.IssuedSelection)
            .where(
                models.IssuedSelection.id == selection_id,
                models.IssuedSelection.learner_id == learner_id,
            )
            .with_for_update()
        ).one_or_none()
        if row is None:
            raise SelectionNotFoundError(f"Selection {selection_id} was not issued")

        if row.consumed_at is not None:
            raise SelectionAlreadyAnsweredError(
                f"Selection {selection_id} has already been answered"
            )

        if at >= row.expires_at:
            raise SelectionExpiredError(f"Selection {selection_id} has expired")

        row.consumed_at = at
        self._session.flush()
        return to_issued_selection_record(row)

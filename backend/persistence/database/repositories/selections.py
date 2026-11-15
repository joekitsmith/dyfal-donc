from sqlalchemy import select
from sqlalchemy.orm import Session

from persistence.database.errors import (
    SelectionAlreadyAnsweredError,
    SelectionExpiredError,
    SelectionNotFoundError,
)
from persistence.database import models
from persistence.database.mappings import to_issued_selection_record
from persistence.database.commands import ConsumeSelection, IssueSelection
from persistence.database.records import IssuedSelectionRecord


class SelectionRepository:
    """The exercises issued to learners. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def issue(self, command: IssueSelection) -> IssuedSelectionRecord:
        row = models.IssuedSelection(
            learner_id=command.learner_id,
            exercise_id=command.exercise_id,
            item_ids=list(command.item_ids),
            new_item=command.new_item,
            issued_at=command.issued_at,
            expires_at=command.expires_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_issued_selection_record(row)

    def consume(self, command: ConsumeSelection) -> IssuedSelectionRecord:
        """Mark the selection answered, so the outcome is recorded only once.

        The row is locked until the transaction ends, so two answers arriving
        together cannot both succeed.
        """
        row = self._session.scalars(
            select(models.IssuedSelection)
            .where(
                models.IssuedSelection.id == command.selection_id,
                models.IssuedSelection.learner_id == command.learner_id,
            )
            .with_for_update()
        ).one_or_none()
        if row is None:
            raise SelectionNotFoundError(
                f"Selection {command.selection_id} was not issued"
            )

        if row.consumed_at is not None:
            raise SelectionAlreadyAnsweredError(
                f"Selection {command.selection_id} has already been answered"
            )

        if command.at >= row.expires_at:
            raise SelectionExpiredError(f"Selection {command.selection_id} has expired")

        row.consumed_at = command.at
        self._session.flush()
        return to_issued_selection_record(row)

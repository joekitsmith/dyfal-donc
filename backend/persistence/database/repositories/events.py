import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from persistence.database.errors import EventOutOfOrderError, LearnerNotFoundError
from persistence.database import models
from persistence.database.mappings import to_event_record
from persistence.database.commands import AppendEvent
from persistence.database.records import EventRecord


class EventRepository:
    """The append-only log of what each learner did. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, command: AppendEvent) -> int:
        """Add the event to the learner's log, and return its sequence number.

        The learner's row is locked until the transaction ends, so appends for
        one learner happen one at a time and sequence numbers have no gaps.
        """
        locked = self._session.scalars(
            select(models.Learner.id)
            .where(models.Learner.id == command.learner_id)
            .with_for_update()
        ).one_or_none()
        if locked is None:
            raise LearnerNotFoundError(f"Learner {command.learner_id} does not exist")

        last = self._session.execute(
            select(models.ReviewEvent.sequence, models.ReviewEvent.reviewed_at)
            .where(models.ReviewEvent.learner_id == command.learner_id)
            .order_by(models.ReviewEvent.sequence.desc())
            .limit(1)
        ).one_or_none()
        if last is not None and command.reviewed_at < last.reviewed_at:
            raise EventOutOfOrderError(
                f"{command.exercise_id}: Events must be in chronological order"
            )

        sequence = 1 if last is None else last.sequence + 1
        self._session.add(
            models.ReviewEvent(
                learner_id=command.learner_id,
                sequence=sequence,
                selection_id=command.selection_id,
                exercise_id=command.exercise_id,
                item_ids=list(command.item_ids),
                new_item=command.new_item,
                outcome=command.outcome,
                reviewed_at=command.reviewed_at,
            )
        )
        self._session.flush()
        return sequence

    def events(self, learner_id: uuid.UUID) -> tuple[EventRecord, ...]:
        """The learner's events in the order they happened."""
        return tuple(
            to_event_record(row)
            for row in self._session.scalars(
                select(models.ReviewEvent)
                .where(models.ReviewEvent.learner_id == learner_id)
                .order_by(models.ReviewEvent.sequence)
            )
        )

    def for_selection(
        self, learner_id: uuid.UUID, selection_id: uuid.UUID
    ) -> EventRecord | None:
        """The event recorded for the selection, if it has been answered."""
        row = self._session.scalars(
            select(models.ReviewEvent).where(
                models.ReviewEvent.learner_id == learner_id,
                models.ReviewEvent.selection_id == selection_id,
            )
        ).one_or_none()
        return None if row is None else to_event_record(row)

import uuid
from datetime import datetime

from api.schemas import OutcomeRequest, OutcomeResponse, ReportedOutcome
from engine.learner import Outcome, ReviewEvent
from persistence.database import (
    AppendEvent,
    ConsumeSelection,
    EventRecord,
    IssuedSelectionRecord,
)


def to_outcome(reported: ReportedOutcome) -> Outcome:
    return Outcome(reported.value)


def to_append_event(
    issued: IssuedSelectionRecord, outcome: Outcome, reviewed_at: datetime
) -> AppendEvent:
    """The event for the outcome of an exercise that was issued."""
    return AppendEvent(
        learner_id=issued.learner_id,
        selection_id=issued.id,
        exercise_id=issued.exercise_id,
        item_ids=issued.item_ids,
        new_item=issued.new_item,
        outcome=outcome.value,
        reviewed_at=reviewed_at,
    )


def to_review_event(record: EventRecord) -> ReviewEvent:
    return ReviewEvent(
        exercise_id=record.exercise_id,
        item_ids=record.item_ids,
        new_item=record.new_item,
        outcome=Outcome(record.outcome),
        reviewed_at=record.reviewed_at,
    )


def to_review_events(records: tuple[EventRecord, ...]) -> tuple[ReviewEvent, ...]:
    return tuple(to_review_event(record) for record in records)


def to_consume_selection(
    learner_id: uuid.UUID, request: OutcomeRequest, at: datetime
) -> ConsumeSelection:
    return ConsumeSelection(
        learner_id=learner_id, selection_id=request.selection_id, at=at
    )


def to_outcome_response(sequence: int, *, recorded: bool) -> OutcomeResponse:
    return OutcomeResponse(sequence=sequence, recorded=recorded)

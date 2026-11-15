import uuid
from datetime import datetime, timedelta

from api.schemas import (
    ExercisePurpose,
    ExerciseResponse,
    NothingEligibleReason,
    NothingEligibleResponse,
)
from engine.scheduler import NoExerciseReason, NothingEligible, Purpose, Selection
from persistence.database import IssuedSelectionRecord, IssueSelection


def to_issue_selection(
    learner_id: uuid.UUID,
    selection: Selection,
    issued_at: datetime,
    lifetime: timedelta,
) -> IssueSelection:
    return IssueSelection(
        learner_id=learner_id,
        exercise_id=selection.exercise_id,
        item_ids=selection.exercise.declared_items,
        new_item=selection.introduces,
        issued_at=issued_at,
        expires_at=issued_at + lifetime,
    )


def to_exercise_response(
    selection: Selection, issued: IssuedSelectionRecord
) -> ExerciseResponse:
    return ExerciseResponse(
        selection_id=issued.id,
        english=selection.exercise.english,
        welsh=selection.exercise.welsh,
        item_ids=issued.item_ids,
        introduces=issued.new_item,
        purpose=to_exercise_purpose(selection.purpose),
    )


def to_nothing_eligible_response(nothing: NothingEligible) -> NothingEligibleResponse:
    return NothingEligibleResponse(reason=to_nothing_eligible_reason(nothing.reason))


def to_exercise_purpose(purpose: Purpose) -> ExercisePurpose:
    return ExercisePurpose(purpose.value)


def to_nothing_eligible_reason(reason: NoExerciseReason) -> NothingEligibleReason:
    return NothingEligibleReason(reason.value)

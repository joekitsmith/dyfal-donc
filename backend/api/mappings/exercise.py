import uuid
from datetime import datetime, timedelta

from api.mappings.audio import to_audio_links
from api.schemas import (
    ExercisePurpose,
    ExerciseResponse,
    NothingEligibleResponse,
)
from engine.scheduler import Purpose, Selection
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
        exercise_id=selection.exercise_id,
        english=selection.exercise.english,
        welsh=selection.exercise.welsh,
        audio=to_audio_links(selection.exercise_id),
        item_ids=issued.item_ids,
        introduces=issued.new_item,
        purpose=to_exercise_purpose(selection.purpose),
    )


def to_nothing_eligible_response() -> NothingEligibleResponse:
    return NothingEligibleResponse()


def to_exercise_purpose(purpose: Purpose) -> ExercisePurpose:
    return ExercisePurpose(purpose.value)

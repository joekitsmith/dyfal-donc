import uuid
from datetime import datetime, timedelta

from api.course import CourseRelease
from api.mappings import (
    to_exercise_response,
    to_append_event,
    to_consume_selection,
    to_issue_selection,
    to_nothing_eligible_response,
    to_outcome,
    to_outcome_response,
    to_progress_response,
    to_review_events,
)
from api.schemas import (
    NextExerciseResponse,
    OutcomeRequest,
    OutcomeResponse,
    ProgressResponse,
)
from engine.learner import (
    DEFAULT_SETTINGS,
    learning_items_due,
    recent_error_rate,
    replay,
    review_items_due,
)
from engine.scheduler import (
    DEFAULT_SCHEDULER_SETTINGS,
    NothingEligible,
    next_exercise,
)
from persistence.database import UnitOfWork
from persistence.database.errors import (
    LearnerNotFoundError,
    SelectionAlreadyAnsweredError,
)


def offer_exercise(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    learner_id: uuid.UUID,
    now: datetime,
    lifetime: timedelta,
) -> NextExerciseResponse:
    """Choose the learner's next exercise and remember that it was issued."""
    _require_learner(unit_of_work, learner_id)
    events = to_review_events(unit_of_work.events.events(learner_id))

    chosen = next_exercise(
        release.exercises, release.curriculum, replay(events), events, now
    )
    if isinstance(chosen, NothingEligible):
        return to_nothing_eligible_response()

    issued = unit_of_work.selections.issue(
        to_issue_selection(learner_id, chosen, now, lifetime)
    )
    unit_of_work.commit()
    return to_exercise_response(chosen, issued)


def record_outcome(
    unit_of_work: UnitOfWork,
    learner_id: uuid.UUID,
    request: OutcomeRequest,
    now: datetime,
) -> OutcomeResponse:
    """Record how the learner got on, once per issued selection.

    Sending the same outcome again returns the original result, so a retry is
    safe. A different outcome for an answered selection is a conflict.
    """
    outcome = to_outcome(request.outcome)
    try:
        issued = unit_of_work.selections.consume(
            to_consume_selection(learner_id, request, now)
        )
    except SelectionAlreadyAnsweredError:
        earlier = unit_of_work.events.for_selection(learner_id, request.selection_id)
        if earlier is not None and earlier.outcome == outcome.value:
            return to_outcome_response(earlier.sequence, recorded=False)

        raise

    sequence = unit_of_work.events.append(to_append_event(issued, outcome, now))
    unit_of_work.commit()
    return to_outcome_response(sequence, recorded=True)


def describe_progress(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    learner_id: uuid.UUID,
    now: datetime,
) -> ProgressResponse:
    _require_learner(unit_of_work, learner_id)
    events = to_review_events(unit_of_work.events.events(learner_id))
    state = replay(events)

    return to_progress_response(
        state=state,
        learning_due=learning_items_due(state),
        review_due=review_items_due(state, now, DEFAULT_SETTINGS),
        recent_error_rate=recent_error_rate(
            events, DEFAULT_SCHEDULER_SETTINGS.error_rate_window
        ),
        course_items=len(release.curriculum.items),
    )


def _require_learner(unit_of_work: UnitOfWork, learner_id: uuid.UUID) -> None:
    if unit_of_work.learners.get(learner_id) is None:
        raise LearnerNotFoundError(f"Learner {learner_id} does not exist")

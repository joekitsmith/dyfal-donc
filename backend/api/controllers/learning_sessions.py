import uuid
from datetime import datetime

from api.course import CourseRelease
from api.errors import LearningSessionNotFoundError
from api.mappings import (
    to_overview_response,
    to_review_events,
    to_session_recap_response,
    to_session_summary_response,
)
from api.schemas import OverviewResponse, SessionSummaryResponse
from engine.learner import (
    DEFAULT_SETTINGS,
    introduced_items,
    is_ongoing,
    learning_items_due,
    replay,
    review_items_due,
    split_sessions,
    summarise_session,
)
from engine.scheduler import frontier
from persistence.database import UnitOfWork
from persistence.database.errors import LearnerNotFoundError


def describe_session_summary(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    learner_id: uuid.UUID,
    session_id: int,
    now: datetime,
) -> SessionSummaryResponse:
    """The summary of the learner's session that began with answer number ``session_id``."""
    _require_learner(unit_of_work, learner_id)
    records = unit_of_work.events.events(learner_id)
    events = to_review_events(records)
    runs = split_sessions(events)
    run = next((run for run in runs if records[run.start].sequence == session_id), None)
    if run is None:
        raise LearningSessionNotFoundError(
            f"Learning session {session_id} does not exist"
        )

    summary = summarise_session(events[: run.start], events[run.start : run.end])
    return to_session_summary_response(
        session_id,
        summary,
        ongoing=run is runs[-1] and is_ongoing(summary.ended_at, now),
        curriculum=release.curriculum,
        exercises=release.exercises,
    )


def describe_overview(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    learner_id: uuid.UUID,
    now: datetime,
) -> OverviewResponse:
    _require_learner(unit_of_work, learner_id)
    records = unit_of_work.events.events(learner_id)
    events = to_review_events(records)
    state = replay(events)
    runs = split_sessions(events)
    latest = None
    if runs:
        run = runs[-1]
        summary = summarise_session(events[: run.start], events[run.start :])
        latest = to_session_recap_response(
            records[run.start].sequence,
            summary,
            ongoing=is_ongoing(summary.ended_at, now),
            curriculum=release.curriculum,
        )

    next_item = frontier(release.curriculum, introduced_items(state))
    return to_overview_response(
        now=now,
        review_due=len(review_items_due(state, now, DEFAULT_SETTINGS)),
        learning_due=len(learning_items_due(state)),
        topic=None if next_item is None else release.curriculum.get(next_item).topic,
        introduced=len(state.memories),
        course_items=len(release.curriculum.items),
        latest_session=latest,
    )


def _require_learner(unit_of_work: UnitOfWork, learner_id: uuid.UUID) -> None:
    if unit_of_work.learners.get(learner_id) is None:
        raise LearnerNotFoundError(f"Learner {learner_id} does not exist")

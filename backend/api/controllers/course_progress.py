import uuid

from api.course import CourseRelease
from api.errors import ItemNotFoundError
from api.mappings import (
    to_course_progress_response,
    to_item_detail_response,
    to_review_events,
    to_sentence_responses,
)
from api.schemas import CourseProgressResponse, ItemDetailResponse
from engine.learner import replay
from engine.scheduler import course_progress, example_exercise_ids, first_met_at
from persistence.database import UnitOfWork
from persistence.database.errors import LearnerNotFoundError

MAX_EXAMPLES = 5


def describe_course_progress(
    unit_of_work: UnitOfWork, release: CourseRelease, learner_id: uuid.UUID
) -> CourseProgressResponse:
    _require_learner(unit_of_work, learner_id)
    events = to_review_events(unit_of_work.events.events(learner_id))
    progress = course_progress(
        release.curriculum,
        release.exercises,
        release.exercise_topics,
        replay(events),
        events,
    )

    return to_course_progress_response(release.curriculum, release.exercises, progress)


def describe_item(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    learner_id: uuid.UUID,
    item_id: str,
) -> ItemDetailResponse:
    """An item the learner has met. One they have not, or that does not exist, is not found."""
    _require_learner(unit_of_work, learner_id)
    events = to_review_events(unit_of_work.events.events(learner_id))
    item = next((item for item in release.curriculum.items if item.id == item_id), None)
    met = first_met_at(events, item_id)
    if item is None or met is None:
        raise ItemNotFoundError(f"Item {item_id} does not exist")

    examples = to_sentence_responses(
        release.exercises,
        example_exercise_ids(release.exercises, events, item_id, MAX_EXAMPLES),
    )

    return to_item_detail_response(item, met, examples)


def _require_learner(unit_of_work: UnitOfWork, learner_id: uuid.UUID) -> None:
    if unit_of_work.learners.get(learner_id) is None:
        raise LearnerNotFoundError(f"Learner {learner_id} does not exist")

import uuid

from fastapi import APIRouter, status

from api.controllers import (
    create_learner,
    describe_progress,
    offer_exercise,
    record_outcome,
)
from api.dependencies import (
    ClockDependency,
    CourseReleaseDependency,
    SelectionLifetimeDependency,
    UnitOfWorkDependency,
)
from api.schemas import (
    LearnerResponse,
    NextExerciseResponse,
    OutcomeRequest,
    OutcomeResponse,
    ProgressResponse,
)

router = APIRouter(prefix="/learners")


@router.post("", status_code=status.HTTP_201_CREATED)
def post_learner(
    unit_of_work: UnitOfWorkDependency, release: CourseReleaseDependency
) -> LearnerResponse:
    return create_learner(unit_of_work, release)


@router.get("/{learner_id}/next")
def get_next(
    learner_id: uuid.UUID,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
    lifetime: SelectionLifetimeDependency,
) -> NextExerciseResponse:
    return offer_exercise(unit_of_work, release, learner_id, clock(), lifetime)


@router.post("/{learner_id}/outcomes")
def post_outcome(
    learner_id: uuid.UUID,
    request: OutcomeRequest,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
) -> OutcomeResponse:
    return record_outcome(unit_of_work, learner_id, request, clock())


@router.get("/{learner_id}/progress")
def get_progress(
    learner_id: uuid.UUID,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
) -> ProgressResponse:
    return describe_progress(unit_of_work, release, learner_id, clock())

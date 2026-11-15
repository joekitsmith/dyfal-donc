from fastapi import APIRouter, Depends

from api.controllers import describe_progress, offer_exercise, record_outcome
from api.dependencies import (
    ClockDependency,
    CourseReleaseDependency,
    LearnerIdDependency,
    SelectionLifetimeDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import (
    NextExerciseResponse,
    OutcomeRequest,
    OutcomeResponse,
    ProgressResponse,
)

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.post("/next")
def post_next(
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
    lifetime: SelectionLifetimeDependency,
) -> NextExerciseResponse:
    """Issues an exercise to the signed-in learner, so it is not a safe request."""
    return offer_exercise(unit_of_work, release, learner_id, clock(), lifetime)


@router.post("/outcomes")
def post_outcome(
    request: OutcomeRequest,
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
) -> OutcomeResponse:
    return record_outcome(unit_of_work, learner_id, request, clock())


@router.get("/progress")
def get_progress(
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
) -> ProgressResponse:
    return describe_progress(unit_of_work, release, learner_id, clock())

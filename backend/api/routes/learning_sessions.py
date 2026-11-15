from fastapi import APIRouter, Depends

from api.controllers import describe_session_summary
from api.dependencies import (
    ClockDependency,
    CourseReleaseDependency,
    LearnerIdDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import SessionSummaryResponse

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("/learning-sessions/{session_id}/summary")
def get_session_summary(
    session_id: int,
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
) -> SessionSummaryResponse:
    return describe_session_summary(
        unit_of_work, release, learner_id, session_id, clock()
    )

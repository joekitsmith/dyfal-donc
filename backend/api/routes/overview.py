from fastapi import APIRouter, Depends

from api.controllers import describe_overview
from api.dependencies import (
    ClockDependency,
    CourseReleaseDependency,
    LearnerIdDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import OverviewResponse

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("/overview")
def get_overview(
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
) -> OverviewResponse:
    return describe_overview(unit_of_work, release, learner_id, clock())

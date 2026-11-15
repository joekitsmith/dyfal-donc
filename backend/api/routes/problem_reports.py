from fastapi import APIRouter, Depends, Response, status

from api.controllers import report_problem
from api.dependencies import (
    AuthenticatedDependency,
    ClockDependency,
    CourseReleaseDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import ProblemReportRequest

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.post("/problem-reports", status_code=status.HTTP_204_NO_CONTENT)
def post_problem_report(
    request: ProblemReportRequest,
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
) -> Response:
    report_problem(unit_of_work, release, authenticated.user.id, request, clock())
    return Response(status_code=status.HTTP_204_NO_CONTENT)

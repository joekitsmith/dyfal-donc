import uuid
from datetime import datetime

from api.course import CourseRelease
from api.errors import UnknownReportSubjectError
from api.mappings import to_add_problem_report
from api.schemas import ProblemReportRequest
from persistence.database import UnitOfWork


def report_problem(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    user_id: uuid.UUID,
    request: ProblemReportRequest,
    now: datetime,
) -> None:
    """Store the report. The sentence or word need not be one the learner has met."""
    if request.exercise_id is not None and request.exercise_id not in release.exercises:
        raise UnknownReportSubjectError(
            f"Exercise {request.exercise_id} does not exist"
        )

    if request.item_id is not None and not any(
        item.id == request.item_id for item in release.curriculum.items
    ):
        raise UnknownReportSubjectError(f"Item {request.item_id} does not exist")

    unit_of_work.problem_reports.add(
        to_add_problem_report(user_id, request, release.hash, now)
    )
    unit_of_work.commit()

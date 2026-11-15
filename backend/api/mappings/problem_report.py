import uuid
from datetime import datetime

from api.schemas import ProblemReportRequest
from persistence.database import AddProblemReport


def to_add_problem_report(
    user_id: uuid.UUID,
    request: ProblemReportRequest,
    release_hash: str,
    now: datetime,
) -> AddProblemReport:
    return AddProblemReport(
        user_id=user_id,
        exercise_id=request.exercise_id,
        item_id=request.item_id,
        release_hash=release_hash,
        source=request.source.value,
        category=request.category.value,
        description=request.description,
        created_at=now,
    )

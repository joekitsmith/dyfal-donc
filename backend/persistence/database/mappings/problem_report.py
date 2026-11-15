from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import ProblemReportRecord


def to_problem_report_record(row: models.ProblemReport) -> ProblemReportRecord:
    return ProblemReportRecord(
        id=row.id,
        user_id=row.user_id,
        exercise_id=row.exercise_id,
        item_id=row.item_id,
        release_hash=row.release_hash,
        source=row.source,
        category=row.category,
        description=row.description,
        created_at=to_utc(row.created_at),
        resolved_at=None if row.resolved_at is None else to_utc(row.resolved_at),
    )

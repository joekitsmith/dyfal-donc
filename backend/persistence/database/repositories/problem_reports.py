from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import AddProblemReport
from persistence.database.errors import ProblemReportNotFoundError
from persistence.database.mappings import to_problem_report_record
from persistence.database.records import ProblemReportRecord


class ProblemReportRepository:
    """Learners' problem reports. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddProblemReport) -> ProblemReportRecord:
        row = models.ProblemReport(
            user_id=command.user_id,
            exercise_id=command.exercise_id,
            item_id=command.item_id,
            release_hash=command.release_hash,
            source=command.source,
            category=command.category,
            description=command.description,
            created_at=command.created_at,
        )
        self._session.add(row)
        self._session.flush()
        return to_problem_report_record(row)

    def list(self, *, include_resolved: bool) -> tuple[ProblemReportRecord, ...]:
        """Reports oldest first. Resolved ones are left out unless asked for."""
        query = select(models.ProblemReport).order_by(
            models.ProblemReport.created_at, models.ProblemReport.id
        )
        if not include_resolved:
            query = query.where(models.ProblemReport.resolved_at.is_(None))

        return tuple(
            to_problem_report_record(row) for row in self._session.scalars(query)
        )

    def resolve(self, report_id: int, resolved_at: datetime) -> bool:
        """Mark a report resolved. False if it already was."""
        row = self._session.get(models.ProblemReport, report_id)
        if row is None:
            raise ProblemReportNotFoundError(
                f"Problem report {report_id} does not exist"
            )

        if row.resolved_at is not None:
            return False

        row.resolved_at = resolved_at
        self._session.flush()
        return True

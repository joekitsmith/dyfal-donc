import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from persistence.database import (
    AddProblemReport,
    AddUser,
    ProblemReportRepository,
    UserRepository,
)
from persistence.database.errors import ProblemReportNotFoundError

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)


def new_report(user_id: uuid.UUID, **changes: object) -> AddProblemReport:
    values: dict[str, object] = {
        "user_id": user_id,
        "exercise_id": None,
        "item_id": None,
        "release_hash": "hash",
        "source": "lesson",
        "category": "grammar",
        "description": "Wrong",
        "created_at": NOW,
    }
    return AddProblemReport(**{**values, **changes})  # type: ignore[arg-type]


@pytest.fixture
def user_id(session: Session) -> uuid.UUID:
    return UserRepository(session).add(AddUser()).id


class TestProblemReportRepository:
    def test_lists_open_reports_oldest_first(
        self, session: Session, user_id: uuid.UUID
    ) -> None:
        reports = ProblemReportRepository(session)
        later = reports.add(new_report(user_id, created_at=NOW + timedelta(hours=1)))
        earlier = reports.add(new_report(user_id))

        listed = reports.list(include_resolved=False)

        assert [report.id for report in listed] == [earlier.id, later.id]

    def test_resolving_hides_a_report_unless_asked_for(
        self, session: Session, user_id: uuid.UUID
    ) -> None:
        reports = ProblemReportRepository(session)
        report = reports.add(new_report(user_id))

        changed = reports.resolve(report.id, NOW)

        assert changed is True
        assert reports.list(include_resolved=False) == ()
        [shown] = reports.list(include_resolved=True)
        assert shown.resolved_at == NOW

    def test_resolving_twice_changes_nothing(
        self, session: Session, user_id: uuid.UUID
    ) -> None:
        reports = ProblemReportRepository(session)
        report = reports.add(new_report(user_id))
        reports.resolve(report.id, NOW)

        assert reports.resolve(report.id, NOW + timedelta(hours=1)) is False
        assert reports.list(include_resolved=True)[0].resolved_at == NOW

    def test_resolving_an_unknown_report_fails(self, session: Session) -> None:
        with pytest.raises(ProblemReportNotFoundError, match="Problem report 99"):
            ProblemReportRepository(session).resolve(99, NOW)


class TestConstraints:
    @pytest.mark.parametrize(
        "changes",
        [
            {"source": "elsewhere"},
            {"category": "rude"},
            {"exercise_id": "a", "item_id": "b"},
        ],
    )
    def test_rejects_what_the_api_would_not_send(
        self, session: Session, user_id: uuid.UUID, changes: dict[str, object]
    ) -> None:
        with pytest.raises(IntegrityError):
            ProblemReportRepository(session).add(new_report(user_id, **changes))

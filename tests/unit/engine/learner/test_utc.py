from datetime import UTC, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from engine.learner import LearnerError
from engine.learner.utc import as_utc, require_utc


class TestRequireUtc:
    def test_accepts_utc(self) -> None:
        require_utc(datetime(2026, 1, 1, tzinfo=UTC), "now")

    def test_accepts_another_name_for_utc(self) -> None:
        require_utc(datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC")), "now")

    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(LearnerError, match="now must be timezone-aware"):
            require_utc(datetime(2026, 1, 1), "now")

    def test_rejects_other_offset(self) -> None:
        moment = datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=1)))
        with pytest.raises(LearnerError, match="now must be in UTC"):
            require_utc(moment, "now")


class TestAsUtc:
    def test_returns_a_standard_utc_datetime(self) -> None:
        moment = as_utc(datetime(2026, 1, 1, tzinfo=ZoneInfo("UTC")), "now")

        assert moment.tzinfo is UTC

    def test_rejects_naive_datetime(self) -> None:
        with pytest.raises(LearnerError):
            as_utc(datetime(2026, 1, 1), "now")

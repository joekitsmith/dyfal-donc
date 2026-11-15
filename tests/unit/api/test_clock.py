from datetime import timedelta

from api.clock import system_clock


class TestSystemClock:
    def test_is_timezone_aware_and_in_utc(self) -> None:
        assert system_clock().utcoffset() == timedelta(0)

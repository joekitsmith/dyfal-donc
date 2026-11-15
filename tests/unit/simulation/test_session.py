from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import pytest

from simulation.errors import SimulationError
from simulation.session import DEFAULT_START, SessionSettings


class TestSessionSettings:
    def test_each_day_starts_a_day_after_the_last(self) -> None:
        settings = SessionSettings()

        assert settings.day_start(3) == DEFAULT_START + timedelta(days=3)

    @pytest.mark.parametrize(
        "make",
        (
            lambda: SessionSettings(days=0),
            lambda: SessionSettings(session_minutes=0),
            lambda: SessionSettings(exercise_seconds=0),
            lambda: SessionSettings(exercise_jitter=1),
            lambda: SessionSettings(exercise_jitter=-0.1),
            lambda: SessionSettings(skip_day_probability=1.5),
        ),
    )
    def test_invalid_values_are_rejected(
        self, make: Callable[[], SessionSettings]
    ) -> None:
        with pytest.raises(SimulationError):
            make()

    def test_a_naive_start_is_rejected(self) -> None:
        with pytest.raises(SimulationError, match="UTC"):
            SessionSettings(start=datetime(2026, 1, 5, 9))

    def test_a_non_utc_start_is_rejected(self) -> None:
        with pytest.raises(SimulationError, match="UTC"):
            SessionSettings(
                start=datetime(2026, 1, 5, 9, tzinfo=timezone(timedelta(hours=1)))
            )

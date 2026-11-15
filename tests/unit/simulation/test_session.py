from collections.abc import Callable
from datetime import datetime, timedelta, timezone

import pytest

from simulation.errors import SimulationError
from simulation.session import DEFAULT_START, Break, SessionSettings


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


class TestBreak:
    def test_it_ends_on_the_first_day_back(self) -> None:
        assert Break(start_day=5, length_days=3).end_day == 8

    def test_it_covers_its_days_but_not_the_day_back(self) -> None:
        period = Break(start_day=5, length_days=3)

        assert [period.covers(day) for day in (4, 5, 6, 7, 8)] == [
            False,
            True,
            True,
            True,
            False,
        ]

    @pytest.mark.parametrize(
        "make",
        (
            lambda: Break(start_day=-1, length_days=3),
            lambda: Break(start_day=5, length_days=0),
        ),
    )
    def test_invalid_values_are_rejected(self, make: Callable[[], Break]) -> None:
        with pytest.raises(SimulationError):
            make()


class TestOnBreak:
    def test_is_true_only_inside_a_break(self) -> None:
        settings = SessionSettings(
            breaks=(
                Break(start_day=2, length_days=2),
                Break(start_day=10, length_days=1),
            )
        )

        assert [settings.on_break(day) for day in (1, 2, 3, 4, 10, 11)] == [
            False,
            True,
            True,
            False,
            True,
            False,
        ]

    def test_there_are_no_breaks_by_default(self) -> None:
        assert not SessionSettings().on_break(0)

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from simulation.errors import SimulationError

DEFAULT_START = datetime(2026, 1, 5, 9, tzinfo=UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class Break:
    """A stretch of days when the learner puts the app down: ``length_days`` days from ``start_day``."""

    start_day: int
    length_days: int

    def __post_init__(self) -> None:
        if self.start_day < 0:
            raise SimulationError("Break start day must not be negative")

        if self.length_days < 1:
            raise SimulationError("Break length must be at least 1 day")

    @property
    def end_day(self) -> int:
        """The first day back."""
        return self.start_day + self.length_days

    def covers(self, day: int) -> bool:
        return self.start_day <= day < self.end_day


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionSettings:
    """When and for how long the simulated learner practises.

    One session a day starting at ``start`` plus the day number, lasting
    ``session_minutes``. Each exercise takes ``exercise_seconds``, varying by up
    to ``exercise_jitter`` either way. On a day the learner skips, which happens
    with probability ``skip_day_probability``, they do nothing, and neither do
    they on any day inside a break.
    """

    days: int = 60
    start: datetime = DEFAULT_START
    session_minutes: float = 20.0
    exercise_seconds: float = 20.0
    exercise_jitter: float = 0.3
    skip_day_probability: float = 0.1
    breaks: tuple[Break, ...] = ()

    def __post_init__(self) -> None:
        if self.days < 1:
            raise SimulationError("Days must be at least 1")

        if self.start.utcoffset() != timedelta(0):
            raise SimulationError("Start must be a UTC datetime")

        if self.session_minutes <= 0 or self.exercise_seconds <= 0:
            raise SimulationError("Session and exercise durations must be positive")

        if not 0 <= self.exercise_jitter < 1:
            raise SimulationError("Exercise jitter must be at least 0 and below 1")

        if not 0 <= self.skip_day_probability <= 1:
            raise SimulationError("Skip-day probability must be between 0 and 1")

    def day_start(self, day: int) -> datetime:
        return self.start + timedelta(days=day)

    def on_break(self, day: int) -> bool:
        return any(period.covers(day) for period in self.breaks)


DEFAULT_SESSION_SETTINGS = SessionSettings()

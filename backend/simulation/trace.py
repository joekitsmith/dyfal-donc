from dataclasses import dataclass
from datetime import datetime

from engine.learner import ReviewEvent
from engine.scheduler import NoExerciseReason, Purpose


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulatedStep:
    """One exercise the learner was given: what the engine saw and what really happened."""

    event: ReviewEvent
    purpose: Purpose
    truly_correct: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemTruth:
    """What the simulated learner really remembers of one item."""

    item_id: str
    stability_days: float
    recall_probability: float


@dataclass(frozen=True, slots=True, kw_only=True)
class DaySnapshot:
    """The learner's real memory at the end of a day, just before the next one starts."""

    day: int
    measured_at: datetime
    skipped: bool
    items: tuple[ItemTruth, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Stall:
    """A session that ended early because the scheduler had nothing to give."""

    day: int
    at: datetime
    reason: NoExerciseReason


@dataclass(frozen=True, slots=True, kw_only=True)
class SimulationTrace:
    """Everything a run produced. The same seed and settings give the same trace."""

    seed: int
    steps: tuple[SimulatedStep, ...]
    snapshots: tuple[DaySnapshot, ...]
    stalls: tuple[Stall, ...]

    @property
    def events(self) -> tuple[ReviewEvent, ...]:
        return tuple(step.event for step in self.steps)

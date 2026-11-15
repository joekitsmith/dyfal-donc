from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from engine.learner.errors import LearnerError
from engine.learner.memory import ReviewMemory
from engine.learner.outcome import Outcome
from engine.learner.utc import require_utc

type ItemMemory = Learning | Review


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewEvent:
    """One exercise the learner was given, and how it went.

    ``item_ids`` are every item the exercise practised, including ``new_item``
    if it introduced one.
    """

    exercise_id: str
    item_ids: tuple[str, ...]
    new_item: str | None = None
    outcome: Outcome
    reviewed_at: datetime

    def __post_init__(self) -> None:
        require_utc(self.reviewed_at, "reviewed_at")
        if not self.item_ids:
            raise LearnerError(f"{self.exercise_id}: An exercise must practise an item")

        if len(set(self.item_ids)) != len(self.item_ids):
            raise LearnerError(f"{self.exercise_id}: Item ids must be unique")

        if self.new_item is not None and self.new_item not in self.item_ids:
            raise LearnerError(
                f"{self.exercise_id}: The new item {self.new_item} must be one of the item ids"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class Learning:
    """Short-term phase: the item is repeated after a few exercises.

    ``exercises_until_due`` counts down by one for every exercise; at zero the
    item is due.
    """

    step_index: int
    exercises_until_due: int

    def __post_init__(self) -> None:
        if self.step_index < 0 or self.exercises_until_due < 0:
            raise LearnerError("A learning step and its countdown cannot be negative")


@dataclass(frozen=True, slots=True, kw_only=True)
class Review:
    """Long-term phase: the item is scheduled by the memory model."""

    memory: ReviewMemory


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerState:
    """What the learner knows, derived by replaying review events.

    An item with no entry in ``memories`` has never been introduced.
    """

    memories: Mapping[str, ItemMemory] = field(default_factory=dict)
    last_reviewed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.last_reviewed_at is not None:
            require_utc(self.last_reviewed_at, "last_reviewed_at")

        object.__setattr__(self, "memories", MappingProxyType(dict(self.memories)))

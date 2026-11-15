from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from engine.learner.errors import LearnerError
from engine.learner.outcome import Outcome
from engine.learner.utc import require_utc


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewMemory:
    """Long-term memory of an item: how stable it is, when last seen, when due."""

    stability: float
    difficulty: float
    last_reviewed_at: datetime
    due_at: datetime

    def __post_init__(self) -> None:
        require_utc(self.last_reviewed_at, "last_reviewed_at")
        require_utc(self.due_at, "due_at")
        if self.stability <= 0:
            raise LearnerError(f"Stability must be positive, not {self.stability}")

        if self.due_at < self.last_reviewed_at:
            raise LearnerError("An item cannot be due before it was last reviewed")


class MemoryModel(Protocol):
    """A model of long-term memory. Pure: every moment is passed in."""

    def initial(self, now: datetime) -> ReviewMemory:
        """The memory of an item first recalled successfully at ``now``."""
        ...

    def review(
        self, memory: ReviewMemory, outcome: Outcome, now: datetime
    ) -> ReviewMemory:
        """The memory after a review at ``now``."""
        ...

    def retrievability(self, memory: ReviewMemory, now: datetime) -> float:
        """The chance, from 0 to 1, that the item is recalled at ``now``."""
        ...

    def due_at(self, memory: ReviewMemory) -> datetime:
        """When the item next needs reviewing."""
        ...

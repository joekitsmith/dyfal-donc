from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from engine.exercises import Exercise
from engine.learner import Outcome, ReviewEvent
from engine.scheduler.errors import SchedulerError

type NextExercise = Selection | NothingEligible


class Purpose(StrEnum):
    """Why an exercise was chosen."""

    LEARNING_DUE = "learning_due"
    REVIEW_DUE = "review_due"
    INTRODUCTION = "introduction"
    PRACTICE = "practice"


class NoExerciseReason(StrEnum):
    """Why there is nothing to give the learner."""

    NO_EXERCISE_INTRODUCES_FRONTIER = "no_exercise_introduces_frontier"
    NOTHING_ELIGIBLE = "nothing_eligible"


@dataclass(frozen=True, slots=True, kw_only=True)
class Selection:
    """The exercise to give next.

    ``introduces`` is the item this exercise introduces to this learner, if any.
    It is not the same as ``exercise.new_item``: an exercise that once introduced
    an item is ordinary practice once the learner knows it.
    """

    exercise_id: str
    exercise: Exercise
    purpose: Purpose
    introduces: str | None = None

    def as_event(self, outcome: Outcome, reviewed_at: datetime) -> ReviewEvent:
        """The event to record once the learner has done this exercise."""
        return ReviewEvent(
            exercise_id=self.exercise_id,
            item_ids=self.exercise.declared_items,
            new_item=self.introduces,
            outcome=outcome,
            reviewed_at=reviewed_at,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class NothingEligible:
    """No exercise can be given, and why. ``NO_EXERCISE_INTRODUCES_FRONTIER`` is a content gap."""

    reason: NoExerciseReason


@dataclass(frozen=True, slots=True, kw_only=True)
class SchedulerSettings:
    """How the next exercise is chosen.

    Nothing stops the learner going on. If ``error_rate_threshold`` or more of
    the last ``error_rate_window`` exercises were missed, new items are
    introduced more slowly, at least ``slowed_introduction_gap`` exercises
    apart, and the exercises between them practise what they already know.
    Until there are ``pacing_minimum_events`` of them, one early miss does not
    slow the course. Time only brings refreshers: every ``refresher_period``th
    exercise practises an item that is due for review, if there is one.
    Among exercises that serve the same purpose, each item that is due adds
    ``due_item_weight`` and each item shared with the previous exercise adds
    ``overlap_weight``. Repeating the previous exercise costs
    ``repeat_penalty``.
    """

    error_rate_threshold: float = 0.15
    error_rate_window: int = 20
    pacing_minimum_events: int = 5
    due_item_weight: int = 10
    overlap_weight: int = 2
    repeat_penalty: int = 100
    slowed_introduction_gap: int = 4
    refresher_period: int = 4

    def __post_init__(self) -> None:
        if not 0 < self.error_rate_threshold <= 1:
            raise SchedulerError(
                f"Error rate threshold must be above 0 and at most 1, not {self.error_rate_threshold}"
            )

        if self.error_rate_window < 1:
            raise SchedulerError(
                f"Error rate window must be at least 1, not {self.error_rate_window}"
            )

        if not 1 <= self.pacing_minimum_events <= self.error_rate_window:
            raise SchedulerError(
                "Pacing minimum events must be between 1 and the error rate window, "
                f"not {self.pacing_minimum_events}"
            )

        if min(self.due_item_weight, self.overlap_weight, self.repeat_penalty) < 0:
            raise SchedulerError("Weights and penalties cannot be negative")

        if self.slowed_introduction_gap < 1:
            raise SchedulerError(
                f"Slowed introduction gap must be at least 1, not {self.slowed_introduction_gap}"
            )

        if self.refresher_period < 2:
            raise SchedulerError(
                f"Refresher period must be at least 2, not {self.refresher_period}"
            )


DEFAULT_SCHEDULER_SETTINGS = SchedulerSettings()

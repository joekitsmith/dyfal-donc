from collections.abc import Mapping, Sequence
from collections.abc import Set as AbstractSet
from datetime import datetime

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import (
    DEFAULT_SETTINGS,
    LearnerSettings,
    LearnerState,
    ReviewEvent,
    introduced_items,
    learning_items_due,
    recent_error_rate,
    review_items_due,
)
from engine.scheduler.eligibility import Candidate, candidates, frontier
from engine.scheduler.models import (
    DEFAULT_SCHEDULER_SETTINGS,
    NextExercise,
    NoExerciseReason,
    NothingEligible,
    Purpose,
    SchedulerSettings,
    Selection,
)
from engine.scheduler.scoring import score


def next_exercise(
    pool: Mapping[str, Exercise],
    curriculum: Curriculum,
    state: LearnerState,
    recent_events: Sequence[ReviewEvent],
    now: datetime,
    settings: SchedulerSettings = DEFAULT_SCHEDULER_SETTINGS,
    learner_settings: LearnerSettings = DEFAULT_SETTINGS,
) -> NextExercise:
    """Choose the exercise to give next, or say why there is none.

    ``pool`` maps exercise ids to published exercises, and ``recent_events``
    are in chronological order. In priority order, the choice is:

    1. an exercise practising a ``Learning`` item that is due;
    2. an exercise practising a ``Review`` item that is due;
    3. the exercise introducing the frontier item, if recent errors are low;
    4. any exercise at all, as extra practice.

    Within a priority the best-scoring exercise wins, and the lowest exercise
    id breaks a tie, so the same inputs always give the same answer.
    """
    introduced = introduced_items(state)
    frontier_item = frontier(curriculum, introduced)
    available = candidates(pool, introduced, frontier_item)
    practice = tuple(
        candidate for candidate in available if candidate.introduces is None
    )
    introducing = tuple(candidate for candidate in available if candidate.introduces)

    learning_due = frozenset(learning_items_due(state))
    review_due = frozenset(review_items_due(state, now, learner_settings))
    due = learning_due | review_due
    previous = recent_events[-1] if recent_events else None

    for purpose, due_items in (
        (Purpose.LEARNING_DUE, learning_due),
        (Purpose.REVIEW_DUE, review_due),
    ):
        covering = tuple(
            candidate
            for candidate in practice
            if due_items & set(candidate.exercise.declared_items)
        )
        if covering:
            return _best(covering, purpose, due, previous, settings)

    if introducing and _may_introduce(recent_events, settings):
        return _best(introducing, Purpose.INTRODUCTION, due, previous, settings)

    if practice:
        return _best(practice, Purpose.PRACTICE, due, previous, settings)

    return NothingEligible(
        reason=_why_nothing(pool, frontier_item, introducing_exists=bool(introducing))
    )


def _best(
    options: tuple[Candidate, ...],
    purpose: Purpose,
    due: AbstractSet[str],
    previous: ReviewEvent | None,
    settings: SchedulerSettings,
) -> Selection:
    chosen = min(
        options,
        key=lambda option: (
            -score(option, due, previous, settings),
            option.exercise_id,
        ),
    )
    return Selection(
        exercise_id=chosen.exercise_id,
        exercise=chosen.exercise,
        purpose=purpose,
        introduces=chosen.introduces,
    )


def _may_introduce(
    recent_events: Sequence[ReviewEvent], settings: SchedulerSettings
) -> bool:
    recent = recent_events[-settings.error_rate_window :]
    if len(recent) < settings.pacing_minimum_events:
        return True

    return (
        recent_error_rate(recent, settings.error_rate_window)
        < settings.error_rate_threshold
    )


def _why_nothing(
    pool: Mapping[str, Exercise],
    frontier_item: str | None,
    *,
    introducing_exists: bool,
) -> NoExerciseReason:
    if introducing_exists:
        return NoExerciseReason.ERROR_RATE_TOO_HIGH

    if frontier_item is not None and not any(
        exercise.new_item == frontier_item for exercise in pool.values()
    ):
        return NoExerciseReason.NO_EXERCISE_INTRODUCES_FRONTIER

    return NoExerciseReason.NOTHING_ELIGIBLE

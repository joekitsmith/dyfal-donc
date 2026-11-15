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
    events: Sequence[ReviewEvent],
    now: datetime,
    settings: SchedulerSettings = DEFAULT_SCHEDULER_SETTINGS,
    learner_settings: LearnerSettings = DEFAULT_SETTINGS,
) -> NextExercise:
    """Choose the exercise to give next, or say why there is none.

    ``events`` is everything the learner has done, in chronological order.
    The learner can always go on: time only decides when a refresher is
    due, and a high error rate only spaces new items out. In priority order,
    the choice is:

    1. on every ``refresher_period``th exercise, one practising a ``Review``
       item that is due;
    2. an exercise practising a ``Learning`` item that is due;
    3. the exercise introducing the frontier item, unless recent errors are
       high and one was introduced too recently;
    4. any exercise at all, as extra practice;
    5. the exercise introducing the frontier item after all, if there is
       nothing to practise.

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
    previous = events[-1] if events else None

    priorities: tuple[tuple[Purpose, AbstractSet[str]], ...] = (
        (Purpose.LEARNING_DUE, learning_due),
    )
    if _refresher_turn(events, settings):
        priorities = ((Purpose.REVIEW_DUE, review_due), *priorities)

    for purpose, due_items in priorities:
        covering = tuple(
            candidate
            for candidate in practice
            if due_items & set(candidate.exercise.declared_items)
        )
        if covering:
            return _best(covering, purpose, due, previous, settings)

    if introducing and _may_introduce(events, settings):
        return _best(introducing, Purpose.INTRODUCTION, due, previous, settings)

    if practice:
        return _best(practice, Purpose.PRACTICE, due, previous, settings)

    if introducing:
        return _best(introducing, Purpose.INTRODUCTION, due, previous, settings)

    return NothingEligible(reason=_why_nothing(pool, frontier_item))


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


def _refresher_turn(events: Sequence[ReviewEvent], settings: SchedulerSettings) -> bool:
    return len(events) % settings.refresher_period == settings.refresher_period - 1


def _may_introduce(events: Sequence[ReviewEvent], settings: SchedulerSettings) -> bool:
    recent = events[-settings.error_rate_window :]
    going_badly = (
        len(recent) >= settings.pacing_minimum_events
        and recent_error_rate(recent, settings.error_rate_window)
        >= settings.error_rate_threshold
    )

    return (
        not going_badly
        or _exercises_since_introduction(events) >= settings.slowed_introduction_gap
    )


def _exercises_since_introduction(events: Sequence[ReviewEvent]) -> int:
    for count, event in enumerate(reversed(events)):
        if event.new_item is not None:
            return count

    return len(events)


def _why_nothing(
    pool: Mapping[str, Exercise], frontier_item: str | None
) -> NoExerciseReason:
    if frontier_item is not None and not any(
        exercise.new_item == frontier_item for exercise in pool.values()
    ):
        return NoExerciseReason.NO_EXERCISE_INTRODUCES_FRONTIER

    return NoExerciseReason.NOTHING_ELIGIBLE

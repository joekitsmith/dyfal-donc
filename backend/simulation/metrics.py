from dataclasses import dataclass

from engine.learner import (
    DEFAULT_SETTINGS,
    LearnerSettings,
    introduced_items,
    learning_items_due,
    replay,
    review_items_due,
)
from engine.scheduler import DEFAULT_SCHEDULER_SETTINGS, SchedulerSettings
from simulation.errors import SimulationError
from simulation.session import Break, SessionSettings
from simulation.trace import DaySnapshot, SimulatedStep, SimulationTrace

RECOVERY_WINDOW = 10
RETENTION_OFFSETS = (0, 1, 3, 7)


@dataclass(frozen=True, slots=True, kw_only=True)
class Retention:
    """True retention at the end of the day ``days_after`` days after the first day back."""

    days_after: int
    retention: float


@dataclass(frozen=True, slots=True, kw_only=True)
class BreakMetrics:
    """What putting the app down cost the learner, measured against their real memory.

    ``due_reviews`` and ``due_learning`` are the items the engine wants practised
    on the first day back, out of ``introduced``. ``practised_share`` is the share
    of introduced items seen in the first session back. Retention is the mean
    probability of recalling an introduced item: ``retention_before`` at the end
    of the last day of practice, ``retention_on_return`` just before the first
    session back. ``recovery_exercises`` is how many exercises passed before the
    true error rate over ``RECOVERY_WINDOW`` exercises was back under the pacing
    threshold (0 means no disruption, ``None`` means it never was).
    ``days_to_new_item`` is how many days after the first day back the first new
    item was introduced.
    """

    period: Break
    introduced: int
    due_reviews: int
    due_learning: int
    practised_share: float
    retention_before: float
    retention_on_return: float
    retention_after: tuple[Retention, ...]
    recovery_exercises: int | None
    days_to_new_item: int | None

    @property
    def backlog_share(self) -> float:
        return (self.due_reviews + self.due_learning) / self.introduced

    def render(self) -> str:
        after = ", ".join(
            f"{point.retention:.0%} (+{point.days_after}d)"
            for point in self.retention_after
        )
        recovery = (
            "never" if self.recovery_exercises is None else str(self.recovery_exercises)
        )
        new_item = (
            "none" if self.days_to_new_item is None else f"day +{self.days_to_new_item}"
        )
        return "\n".join(
            (
                f"Break: {self.period.length_days} days from day {self.period.start_day}",
                f"Due on return: {self.due_reviews} reviews and {self.due_learning} "
                f"learning of {self.introduced} items ({self.backlog_share:.0%})",
                f"Items practised in the first session back: {self.practised_share:.0%}",
                f"True retention: {self.retention_before:.0%} before, "
                f"{self.retention_on_return:.0%} on return, then {after}",
                f"Exercises before the error rate recovered: {recovery}",
                f"First new item: {new_item}",
            )
        )


def break_metrics(
    trace: SimulationTrace,
    period: Break,
    session: SessionSettings,
    *,
    learner_settings: LearnerSettings = DEFAULT_SETTINGS,
    scheduler_settings: SchedulerSettings = DEFAULT_SCHEDULER_SETTINGS,
) -> BreakMetrics:
    """Measure one break in a trace, which must have been run with ``session``.

    The engine's state on the first day back is rebuilt by replaying the events,
    so nothing here needs the engine to change.
    """
    back = period.end_day
    if period.start_day < 1:
        raise SimulationError("A break must start after the first day")

    if back >= session.days:
        raise SimulationError("The break does not end before the run does")

    return_time = session.day_start(back)
    state = replay(
        tuple(event for event in trace.events if event.reviewed_at < return_time),
        learner_settings,
    )
    introduced = introduced_items(state)
    if not introduced:
        raise SimulationError("Nothing was learned before the break")

    steps_back = tuple(
        step for step in trace.steps if step.event.reviewed_at >= return_time
    )
    return BreakMetrics(
        period=period,
        introduced=len(introduced),
        due_reviews=len(review_items_due(state, return_time, learner_settings)),
        due_learning=len(learning_items_due(state)),
        practised_share=_practised_share(steps_back, introduced, session),
        retention_before=_retention(trace.snapshots[period.start_day - 1]),
        retention_on_return=_retention(trace.snapshots[back - 1]),
        retention_after=tuple(
            Retention(
                days_after=offset, retention=_retention(trace.snapshots[back + offset])
            )
            for offset in RETENTION_OFFSETS
            if back + offset < len(trace.snapshots)
        ),
        recovery_exercises=_recovery_exercises(
            steps_back, scheduler_settings.error_rate_threshold
        ),
        days_to_new_item=_days_to_new_item(steps_back, back, session),
    )


def _retention(snapshot: DaySnapshot) -> float:
    if not snapshot.items:
        return 0.0

    return sum(item.recall_probability for item in snapshot.items) / len(snapshot.items)


def _day_of(step: SimulatedStep, session: SessionSettings) -> int:
    return (step.event.reviewed_at - session.start).days


def _practised_share(
    steps_back: tuple[SimulatedStep, ...],
    introduced: frozenset[str],
    session: SessionSettings,
) -> float:
    if not steps_back:
        return 0.0

    first_day = _day_of(steps_back[0], session)
    practised = {
        item_id
        for step in steps_back
        if _day_of(step, session) == first_day
        for item_id in step.event.item_ids
    }
    return len(practised & introduced) / len(introduced)


def _recovery_exercises(
    steps_back: tuple[SimulatedStep, ...], threshold: float
) -> int | None:
    for start in range(len(steps_back) - RECOVERY_WINDOW + 1):
        window = steps_back[start : start + RECOVERY_WINDOW]
        if sum(not step.truly_correct for step in window) / RECOVERY_WINDOW < threshold:
            return start

    return None


def _days_to_new_item(
    steps_back: tuple[SimulatedStep, ...], back: int, session: SessionSettings
) -> int | None:
    for step in steps_back:
        if step.event.new_item is not None:
            return _day_of(step, session) - back

    return None

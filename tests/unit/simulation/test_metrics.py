from collections.abc import Mapping, Sequence
from datetime import timedelta

import pytest

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import Outcome, ReviewEvent
from engine.scheduler import Purpose
from simulation.errors import SimulationError
from simulation.metrics import RECOVERY_WINDOW, Retention, break_metrics
from simulation.runner import simulate
from simulation.session import Break, SessionSettings
from simulation.trace import (
    DaySnapshot,
    ItemTruth,
    SimulatedStep,
    SimulationTrace,
)
from tests.unit.simulation.helpers import FORGETFUL, PERFECT

SESSION = SessionSettings(days=10, skip_day_probability=0.0)
PERIOD = Break(start_day=2, length_days=3)
ITEM = "lex:item"
OTHER_ITEM = "lex:other"


def step(
    day: int,
    minute: int,
    *,
    item_ids: tuple[str, ...] = (ITEM,),
    new_item: str | None = None,
    correct: bool = True,
) -> SimulatedStep:
    return SimulatedStep(
        event=ReviewEvent(
            exercise_id=f"ex:{day}-{minute}",
            item_ids=item_ids,
            new_item=new_item,
            outcome=Outcome.GOT_IT,
            reviewed_at=SESSION.day_start(day) + timedelta(minutes=minute),
        ),
        purpose=Purpose.PRACTICE,
        truly_correct=correct,
    )


def trace_of(
    steps: Sequence[SimulatedStep],
    recalls: Sequence[float] = (1.0,) * 10,
    items: tuple[str, ...] = (ITEM,),
) -> SimulationTrace:
    snapshots = tuple(
        DaySnapshot(
            day=day,
            measured_at=SESSION.day_start(day + 1),
            skipped=False,
            items=tuple(
                ItemTruth(
                    item_id=item_id, stability_days=1.0, recall_probability=recall
                )
                for item_id in items
            ),
        )
        for day, recall in enumerate(recalls)
    )
    return SimulationTrace(seed=1, steps=tuple(steps), snapshots=snapshots, stalls=())


def learned_first() -> list[SimulatedStep]:
    return [step(0, 0, new_item=ITEM)]


class TestBreakMetrics:
    def test_retention_is_read_from_the_snapshots_around_the_break(self) -> None:
        recalls = (1.0, 0.9, 0.8, 0.7, 0.6, 0.7, 0.8, 0.8, 0.85, 0.9)
        trace = trace_of([*learned_first(), step(5, 0)], recalls)

        metrics = break_metrics(trace, PERIOD, SESSION)

        assert metrics.retention_before == 0.9
        assert metrics.retention_on_return == 0.6
        assert metrics.retention_after == (
            Retention(days_after=0, retention=0.7),
            Retention(days_after=1, retention=0.8),
            Retention(days_after=3, retention=0.85),
        )

    def test_retention_after_leaves_out_days_beyond_the_run(self) -> None:
        trace = trace_of([*learned_first(), step(5, 0)])

        metrics = break_metrics(trace, PERIOD, SESSION)

        assert [point.days_after for point in metrics.retention_after] == [0, 1, 3]

    def test_retention_is_the_mean_over_the_items(self) -> None:
        steps = [
            step(0, 0, new_item=ITEM),
            step(0, 1, item_ids=(OTHER_ITEM,), new_item=OTHER_ITEM),
            step(5, 0),
        ]
        trace = trace_of(steps, (0.5,) * 10, items=(ITEM, OTHER_ITEM))

        assert break_metrics(trace, PERIOD, SESSION).retention_before == 0.5

    def test_a_learning_item_is_due_on_return_once_its_countdown_is_over(self) -> None:
        steps = [*learned_first(), step(1, 0), step(5, 0)]

        metrics = break_metrics(trace_of(steps), PERIOD, SESSION)

        assert (metrics.introduced, metrics.due_learning, metrics.due_reviews) == (
            1,
            1,
            0,
        )
        assert metrics.backlog_share == 1.0

    def test_nothing_is_due_when_no_countdown_is_over(self) -> None:
        metrics = break_metrics(
            trace_of([*learned_first(), step(5, 0)]), PERIOD, SESSION
        )

        assert metrics.backlog_share == 0.0

    def test_practised_share_is_the_share_of_introduced_items_seen_on_the_first_day_back(
        self,
    ) -> None:
        steps = [
            step(0, 0, new_item=ITEM),
            step(0, 1, item_ids=(OTHER_ITEM,), new_item=OTHER_ITEM),
            step(5, 0),
            step(6, 0, item_ids=(OTHER_ITEM,)),
        ]
        trace = trace_of(steps, items=(ITEM, OTHER_ITEM))

        assert break_metrics(trace, PERIOD, SESSION).practised_share == 0.5

    def test_the_first_day_back_may_be_a_later_day(self) -> None:
        steps = [
            step(0, 0, new_item=ITEM),
            step(0, 1, item_ids=(OTHER_ITEM,), new_item=OTHER_ITEM),
            step(7, 0, item_ids=(ITEM, OTHER_ITEM)),
        ]
        trace = trace_of(steps, items=(ITEM, OTHER_ITEM))

        assert break_metrics(trace, PERIOD, SESSION).practised_share == 1.0

    def test_practised_share_is_zero_when_nothing_is_practised_after_the_break(
        self,
    ) -> None:
        assert (
            break_metrics(trace_of(learned_first()), PERIOD, SESSION).practised_share
            == 0.0
        )

    def test_days_to_new_item_counts_from_the_first_day_back(self) -> None:
        steps = [
            *learned_first(),
            step(5, 0),
            step(7, 0, item_ids=("lex:c",), new_item="lex:c"),
        ]

        metrics = break_metrics(trace_of(steps), PERIOD, SESSION)

        assert metrics.days_to_new_item == 2

    def test_there_is_no_days_to_new_item_when_nothing_new_follows(self) -> None:
        metrics = break_metrics(
            trace_of([*learned_first(), step(5, 0)]), PERIOD, SESSION
        )

        assert metrics.days_to_new_item is None


class TestRecovery:
    @staticmethod
    def recovery(pattern: str) -> int | None:
        """``pattern`` is one letter per exercise after the break: ``.`` right, ``x`` wrong."""
        after = [
            step(5, minute, correct=letter == ".")
            for minute, letter in enumerate(pattern)
        ]

        return break_metrics(
            trace_of([*learned_first(), *after]), PERIOD, SESSION
        ).recovery_exercises

    def test_no_disruption_is_zero(self) -> None:
        assert self.recovery("." * (RECOVERY_WINDOW + 2)) == 0

    def test_counts_the_exercises_before_a_window_back_under_the_threshold(
        self,
    ) -> None:
        assert self.recovery("xxx" + "." * 9) == 2

    def test_a_window_with_errors_at_the_threshold_is_not_recovered(self) -> None:
        assert self.recovery("xx" + "." * 8) is None

    def test_never_recovering_is_none(self) -> None:
        assert self.recovery("x" * 15) is None

    def test_too_few_exercises_for_a_window_is_none(self) -> None:
        assert self.recovery("." * (RECOVERY_WINDOW - 1)) is None


class TestBreakMetricsErrors:
    def test_a_break_that_does_not_end_before_the_run_is_an_error(self) -> None:
        with pytest.raises(SimulationError, match="does not end before the run"):
            break_metrics(
                trace_of(learned_first()), Break(start_day=7, length_days=3), SESSION
            )

    def test_a_break_must_start_after_the_first_day(self) -> None:
        with pytest.raises(SimulationError, match="after the first day"):
            break_metrics(
                trace_of(learned_first()), Break(start_day=0, length_days=3), SESSION
            )

    def test_nothing_learned_before_the_break_is_an_error(self) -> None:
        with pytest.raises(SimulationError, match="Nothing was learned"):
            break_metrics(trace_of([]), PERIOD, SESSION)


class TestBreakMetricsRender:
    def test_mentions_each_measure(self) -> None:
        text = break_metrics(
            trace_of([*learned_first(), step(1, 0), step(5, 0)]), PERIOD, SESSION
        ).render()

        for label in (
            "Break: 3 days from day 2",
            "Due on return: 0 reviews and 1 learning of 1 items (100%)",
            "Items practised in the first session back: 100%",
            "True retention:",
            "Exercises before the error rate recovered: never",
            "First new item: none",
        ):
            assert label in text


class TestBreakMetricsOfASimulation:
    SESSION = SessionSettings(
        days=12, skip_day_probability=0.0, breaks=(Break(start_day=3, length_days=5),)
    )

    def test_a_perfect_memory_loses_nothing_by_putting_the_app_down(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, PERFECT, seed=1, session=self.SESSION)

        metrics = break_metrics(trace, self.SESSION.breaks[0], self.SESSION)

        assert metrics.introduced == len(curriculum.order)
        assert metrics.retention_before == metrics.retention_on_return == 1.0
        assert metrics.recovery_exercises == 0
        assert metrics.days_to_new_item is None

    def test_a_forgetful_learner_has_nothing_left_on_return(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, FORGETFUL, seed=1, session=self.SESSION)

        metrics = break_metrics(trace, self.SESSION.breaks[0], self.SESSION)

        assert metrics.retention_on_return == 0.0

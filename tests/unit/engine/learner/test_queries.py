from datetime import datetime, timedelta

import pytest

from engine.learner import (
    FsrsMemoryModel,
    LearnerError,
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
    introduced_items,
    learning_items_due,
    recent_error_rate,
    review_items_due,
)
from tests.unit.engine.learner.helpers import START

DAY = timedelta(days=1)


def events_with(*outcomes: Outcome) -> tuple[ReviewEvent, ...]:
    return tuple(
        ReviewEvent(
            exercise_id=f"ex:{number}",
            item_ids=("lex:a",),
            outcome=outcome,
            reviewed_at=START + timedelta(minutes=number),
        )
        for number, outcome in enumerate(outcomes)
    )


class TestIntroducedItems:
    def test_nothing_is_introduced_at_the_start(self) -> None:
        assert introduced_items(LearnerState()) == frozenset()

    def test_includes_both_phases(self, memory_model: FsrsMemoryModel) -> None:
        state = LearnerState(
            memories={
                "lex:a": Learning(step_index=0, exercises_until_due=1),
                "lex:b": Review(memory=memory_model.initial(START)),
            }
        )

        assert introduced_items(state) == {"lex:a", "lex:b"}


class TestLearningItemsDue:
    def test_lists_only_items_whose_countdown_is_over_by_id(self) -> None:
        state = LearnerState(
            memories={
                "lex:b": Learning(step_index=0, exercises_until_due=0),
                "lex:waiting": Learning(step_index=0, exercises_until_due=1),
                "lex:a": Learning(step_index=2, exercises_until_due=0),
            }
        )

        assert learning_items_due(state) == ("lex:a", "lex:b")

    def test_ignores_review_items(self, memory_model: FsrsMemoryModel) -> None:
        state = LearnerState(
            memories={"lex:a": Review(memory=memory_model.initial(START - 9 * DAY))}
        )

        assert learning_items_due(state) == ()


class TestReviewItemsDue:
    def test_lists_due_items_longest_overdue_first(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        state = LearnerState(
            memories={
                "lex:recent": Review(memory=memory_model.initial(START - 3 * DAY)),
                "lex:oldest": Review(memory=memory_model.initial(START - 9 * DAY)),
                "lex:not-due": Review(memory=memory_model.initial(START)),
                "lex:learning": Learning(step_index=0, exercises_until_due=0),
            }
        )

        assert review_items_due(state, START) == ("lex:oldest", "lex:recent")

    def test_an_item_is_due_at_its_due_time(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memory = memory_model.initial(START)
        state = LearnerState(memories={"lex:a": Review(memory=memory)})

        assert review_items_due(state, memory.due_at - timedelta(seconds=1)) == ()
        assert review_items_due(state, memory.due_at) == ("lex:a",)

    def test_ties_go_by_id(self, memory_model: FsrsMemoryModel) -> None:
        memory = memory_model.initial(START - 5 * DAY)
        state = LearnerState(
            memories={"lex:b": Review(memory=memory), "lex:a": Review(memory=memory)}
        )

        assert review_items_due(state, START) == ("lex:a", "lex:b")

    def test_rejects_a_naive_time(self) -> None:
        with pytest.raises(LearnerError, match="now must be timezone-aware"):
            review_items_due(LearnerState(), datetime(2026, 1, 1))


class TestRecentErrorRate:
    def test_no_events_is_no_errors(self) -> None:
        assert recent_error_rate((), 10) == 0.0

    def test_share_of_misses(self) -> None:
        events = events_with(
            Outcome.GOT_IT, Outcome.MISSED_IT, Outcome.GOT_IT, Outcome.GOT_IT
        )

        assert recent_error_rate(events, 10) == 0.25

    def test_only_the_last_events_in_the_window_count(self) -> None:
        events = events_with(
            Outcome.MISSED_IT, Outcome.MISSED_IT, Outcome.GOT_IT, Outcome.GOT_IT
        )

        assert recent_error_rate(events, 2) == 0.0

    def test_a_window_larger_than_the_history_uses_all_of_it(self) -> None:
        events = events_with(Outcome.MISSED_IT, Outcome.GOT_IT)

        assert recent_error_rate(events, 100) == 0.5

    def test_every_miss_is_an_error(self) -> None:
        assert recent_error_rate(events_with(Outcome.MISSED_IT), 5) == 1.0

    @pytest.mark.parametrize("window", [0, -3])
    def test_rejects_a_window_under_one(self, window: int) -> None:
        with pytest.raises(LearnerError, match="at least 1"):
            recent_error_rate((), window)

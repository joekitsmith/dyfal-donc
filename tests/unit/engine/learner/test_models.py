from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from engine.learner import (
    FsrsMemoryModel,
    LearnerError,
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
    ReviewMemory,
)
from tests.unit.engine.learner.helpers import START


def make_event(
    *,
    item_ids: tuple[str, ...] = ("lex:a", "lex:b"),
    new_item: str | None = None,
    reviewed_at: datetime = START,
) -> ReviewEvent:
    return ReviewEvent(
        exercise_id="ex:1",
        item_ids=item_ids,
        new_item=new_item,
        outcome=Outcome.GOT_IT,
        reviewed_at=reviewed_at,
    )


class TestReviewEvent:
    def test_valid_event(self) -> None:
        event = make_event(new_item="lex:b")

        assert event.new_item == "lex:b"

    def test_rejects_naive_time(self) -> None:
        with pytest.raises(LearnerError, match="reviewed_at must be timezone-aware"):
            make_event(reviewed_at=datetime(2026, 1, 1))

    def test_rejects_no_items(self) -> None:
        with pytest.raises(LearnerError, match="must practise an item"):
            make_event(item_ids=())

    def test_rejects_duplicate_items(self) -> None:
        with pytest.raises(LearnerError, match="Item ids must be unique"):
            make_event(item_ids=("lex:a", "lex:a"))

    def test_rejects_new_item_outside_item_ids(self) -> None:
        with pytest.raises(LearnerError, match="must be one of the item ids"):
            make_event(new_item="lex:c")

    def test_is_frozen(self) -> None:
        with pytest.raises(FrozenInstanceError):
            make_event().outcome = Outcome.MISSED_IT  # type: ignore[misc]


class TestOutcome:
    def test_values(self) -> None:
        assert [outcome.value for outcome in Outcome] == ["got_it", "missed_it"]


class TestLearning:
    def test_rejects_negative_step(self) -> None:
        with pytest.raises(LearnerError):
            Learning(step_index=-1, exercises_until_due=0)

    def test_rejects_negative_countdown(self) -> None:
        with pytest.raises(LearnerError):
            Learning(step_index=0, exercises_until_due=-1)


class TestReviewMemory:
    def test_rejects_non_positive_stability(self) -> None:
        with pytest.raises(LearnerError, match="Stability must be positive"):
            ReviewMemory(
                stability=0, difficulty=5, last_reviewed_at=START, due_at=START
            )

    def test_rejects_due_before_last_review(self) -> None:
        with pytest.raises(LearnerError, match="cannot be due before"):
            ReviewMemory(
                stability=1,
                difficulty=5,
                last_reviewed_at=START,
                due_at=datetime(2025, 1, 1, tzinfo=UTC),
            )

    def test_rejects_naive_times(self) -> None:
        with pytest.raises(LearnerError):
            ReviewMemory(
                stability=1,
                difficulty=5,
                last_reviewed_at=datetime(2026, 1, 1),
                due_at=START,
            )


class TestLearnerState:
    def test_starts_empty(self) -> None:
        state = LearnerState()

        assert dict(state.memories) == {}
        assert state.last_reviewed_at is None

    def test_memories_are_read_only(self) -> None:
        state = LearnerState(
            memories={"lex:a": Learning(step_index=0, exercises_until_due=1)}
        )

        with pytest.raises(TypeError):
            state.memories["lex:b"] = Learning(step_index=0, exercises_until_due=1)  # type: ignore[index]

    def test_does_not_share_the_dictionary_it_was_given(self) -> None:
        memories = {"lex:a": Learning(step_index=0, exercises_until_due=1)}
        state = LearnerState(memories=memories)

        memories["lex:b"] = Learning(step_index=0, exercises_until_due=1)

        assert set(state.memories) == {"lex:a"}

    def test_equal_when_memories_equal(self) -> None:
        learning = Learning(step_index=1, exercises_until_due=3)

        assert LearnerState(memories={"lex:a": learning}) == LearnerState(
            memories={"lex:a": learning}
        )

    def test_rejects_naive_last_review(self) -> None:
        with pytest.raises(LearnerError):
            LearnerState(last_reviewed_at=datetime(2026, 1, 1))

    def test_holds_both_phases(self, memory_model: FsrsMemoryModel) -> None:
        state = LearnerState(
            memories={
                "lex:a": Learning(step_index=0, exercises_until_due=1),
                "lex:b": Review(memory=memory_model.initial(START)),
            }
        )

        assert isinstance(state.memories["lex:a"], Learning)
        assert isinstance(state.memories["lex:b"], Review)

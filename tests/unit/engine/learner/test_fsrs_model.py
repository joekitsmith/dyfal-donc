from datetime import datetime, timedelta, timezone

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.learner import FsrsMemoryModel, LearnerError, Outcome, ReviewMemory
from tests.unit.engine.learner.helpers import START

DAY = timedelta(days=1)


@st.composite
def memories_with_a_review_time(
    draw: st.DrawFn,
) -> tuple[ReviewMemory, datetime]:
    """A memory built by a history of reviews, and a moment not before the last."""
    model = FsrsMemoryModel()
    moment = START
    memory = model.initial(moment)
    for _ in range(draw(st.integers(min_value=0, max_value=8))):
        moment += timedelta(
            minutes=draw(st.integers(min_value=0, max_value=20 * 24 * 60))
        )
        memory = model.review(memory, draw(st.sampled_from(Outcome)), moment)

    return memory, moment + timedelta(
        minutes=draw(st.integers(min_value=0, max_value=30 * 24 * 60))
    )


class TestInitial:
    def test_first_recall_is_due_in_two_days(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memory = memory_model.initial(START)

        assert memory.last_reviewed_at == START
        assert memory_model.due_at(memory) == START + 2 * DAY

    def test_is_deterministic(self, memory_model: FsrsMemoryModel) -> None:
        assert memory_model.initial(START) == memory_model.initial(START)

    def test_rejects_naive_time(self, memory_model: FsrsMemoryModel) -> None:
        with pytest.raises(LearnerError, match="timezone-aware"):
            memory_model.initial(datetime(2026, 1, 1))

    def test_rejects_other_offset(self, memory_model: FsrsMemoryModel) -> None:
        with pytest.raises(LearnerError, match="in UTC"):
            memory_model.initial(
                datetime(2026, 1, 1, tzinfo=timezone(timedelta(hours=2)))
            )


class TestReview:
    def test_got_it_on_the_due_date_lengthens_the_interval(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        first = memory_model.initial(START)
        due = memory_model.due_at(first)

        second = memory_model.review(first, Outcome.GOT_IT, due)

        assert second.stability > first.stability
        assert memory_model.due_at(second) - due > due - START

    def test_missed_it_cuts_stability_and_is_due_the_next_day(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        first = memory_model.initial(START)
        due = memory_model.due_at(first)

        second = memory_model.review(first, Outcome.MISSED_IT, due)

        assert second.stability < first.stability
        assert memory_model.due_at(second) == due + DAY

    def test_is_deterministic(self, memory_model: FsrsMemoryModel) -> None:
        first = memory_model.initial(START)
        later = START + 2 * DAY

        assert memory_model.review(first, Outcome.GOT_IT, later) == memory_model.review(
            first, Outcome.GOT_IT, later
        )

    def test_rejects_review_before_the_last_one(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memory = memory_model.initial(START)

        with pytest.raises(LearnerError, match="earlier than the previous"):
            memory_model.review(memory, Outcome.GOT_IT, START - DAY)

    def test_rejects_naive_time(self, memory_model: FsrsMemoryModel) -> None:
        memory = memory_model.initial(START)

        with pytest.raises(LearnerError, match="timezone-aware"):
            memory_model.review(memory, Outcome.GOT_IT, datetime(2026, 1, 3))


class TestRetrievability:
    def test_is_certain_at_the_moment_of_review(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memory = memory_model.initial(START)

        assert memory_model.retrievability(memory, START) == pytest.approx(1.0)

    def test_falls_over_time(self, memory_model: FsrsMemoryModel) -> None:
        memory = memory_model.initial(START)

        soon = memory_model.retrievability(memory, START + DAY)
        later = memory_model.retrievability(memory, START + 10 * DAY)

        assert 1.0 > soon > later > 0.0

    def test_is_close_to_desired_retention_on_the_due_date(self) -> None:
        model = FsrsMemoryModel(desired_retention=0.9)
        memory = model.initial(START)

        assert model.retrievability(memory, model.due_at(memory)) == pytest.approx(
            0.9, abs=0.05
        )

    def test_rejects_a_moment_before_the_last_review(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memory = memory_model.initial(START)

        with pytest.raises(LearnerError):
            memory_model.retrievability(memory, START - DAY)


class TestConfiguration:
    @pytest.mark.parametrize("retention", [0.0, 1.0, -0.1, 1.5])
    def test_rejects_retention_outside_zero_and_one(self, retention: float) -> None:
        with pytest.raises(LearnerError, match="between 0 and 1"):
            FsrsMemoryModel(desired_retention=retention)

    def test_rejects_maximum_interval_under_a_day(self) -> None:
        with pytest.raises(LearnerError, match="at least one day"):
            FsrsMemoryModel(maximum_interval_days=0)

    def test_higher_retention_means_shorter_intervals(self) -> None:
        strict = FsrsMemoryModel(desired_retention=0.97)
        relaxed = FsrsMemoryModel(desired_retention=0.8)

        def second_interval(model: FsrsMemoryModel) -> timedelta:
            first = model.initial(START)
            due = model.due_at(first)
            return model.due_at(model.review(first, Outcome.GOT_IT, due)) - due

        assert second_interval(strict) < second_interval(relaxed)

    def test_maximum_interval_caps_the_schedule(self) -> None:
        model = FsrsMemoryModel(maximum_interval_days=3)
        memory = model.initial(START)
        for _ in range(5):
            memory = model.review(memory, Outcome.GOT_IT, model.due_at(memory))

        assert model.due_at(memory) - memory.last_reviewed_at <= 3 * DAY


class TestProperties:
    @settings(deadline=None)
    @given(history=memories_with_a_review_time(), outcome=st.sampled_from(Outcome))
    def test_due_is_never_before_the_review(
        self, history: tuple[ReviewMemory, datetime], outcome: Outcome
    ) -> None:
        memory, moment = history
        model = FsrsMemoryModel()

        reviewed = model.review(memory, outcome, moment)

        assert model.due_at(reviewed) >= moment

    @settings(deadline=None)
    @given(history=memories_with_a_review_time())
    def test_got_it_never_makes_an_item_due_sooner(
        self, history: tuple[ReviewMemory, datetime]
    ) -> None:
        memory, moment = history
        model = FsrsMemoryModel()

        reviewed = model.review(memory, Outcome.GOT_IT, moment)

        assert model.due_at(reviewed) >= model.due_at(memory)

    @settings(deadline=None)
    @given(history=memories_with_a_review_time())
    def test_retrievability_is_a_probability(
        self, history: tuple[ReviewMemory, datetime]
    ) -> None:
        memory, moment = history

        assert 0.0 <= FsrsMemoryModel().retrievability(memory, moment) <= 1.0

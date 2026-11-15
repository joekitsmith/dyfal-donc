from datetime import timedelta

import pytest

from engine.learner import Outcome, ReviewEvent
from engine.scheduler import (
    DEFAULT_SCHEDULER_SETTINGS,
    NoExerciseReason,
    NothingEligible,
    Purpose,
    SchedulerError,
    SchedulerSettings,
    Selection,
)
from tests.unit.engine.learner.helpers import START
from tests.unit.engine.scheduler.helpers import COFFI_ID, SIARAD_ID, exercise


class TestSchedulerSettings:
    def test_defaults(self) -> None:
        assert DEFAULT_SCHEDULER_SETTINGS.error_rate_threshold == 0.15

    @pytest.mark.parametrize("threshold", [0.0, -0.1, 1.5])
    def test_rejects_a_threshold_outside_zero_to_one(self, threshold: float) -> None:
        with pytest.raises(SchedulerError, match="Error rate threshold"):
            SchedulerSettings(error_rate_threshold=threshold)

    def test_rejects_a_window_under_one(self) -> None:
        with pytest.raises(SchedulerError, match="window must be at least 1"):
            SchedulerSettings(error_rate_window=0, pacing_minimum_events=1)

    @pytest.mark.parametrize("minimum", [0, 21])
    def test_rejects_minimum_events_outside_the_window(self, minimum: int) -> None:
        with pytest.raises(SchedulerError, match="between 1 and the error rate window"):
            SchedulerSettings(error_rate_window=20, pacing_minimum_events=minimum)

    @pytest.mark.parametrize(
        "field", ["due_item_weight", "overlap_weight", "repeat_penalty"]
    )
    def test_rejects_negative_weights(self, field: str) -> None:
        with pytest.raises(SchedulerError, match="cannot be negative"):
            SchedulerSettings(**{field: -1})

    def test_the_daily_limit_is_off_by_default(self) -> None:
        assert DEFAULT_SCHEDULER_SETTINGS.new_items_per_day is None

    @pytest.mark.parametrize("limit", [0, -1])
    def test_rejects_a_daily_limit_under_one(self, limit: int) -> None:
        with pytest.raises(
            SchedulerError, match="New items per day must be at least 1"
        ):
            SchedulerSettings(new_items_per_day=limit)


class TestSelection:
    def test_event_records_the_outcome_and_the_items_of_the_exercise(self) -> None:
        selection = Selection(
            exercise_id="ex:1",
            exercise=exercise(SIARAD_ID),
            purpose=Purpose.PRACTICE,
        )

        event = selection.as_event(Outcome.MISSED_IT, START)

        assert event == ReviewEvent(
            exercise_id="ex:1",
            item_ids=(SIARAD_ID,),
            outcome=Outcome.MISSED_IT,
            reviewed_at=START,
        )

    def test_event_introduces_only_what_the_selection_introduces(self) -> None:
        selection = Selection(
            exercise_id="ex:1",
            exercise=exercise(SIARAD_ID, new_item=COFFI_ID),
            purpose=Purpose.INTRODUCTION,
            introduces=COFFI_ID,
        )

        event = selection.as_event(Outcome.GOT_IT, START + timedelta(minutes=1))

        assert event.new_item == COFFI_ID
        assert event.item_ids == (SIARAD_ID, COFFI_ID)

    def test_an_exercise_that_once_introduced_an_item_is_not_introducing_it_now(
        self,
    ) -> None:
        selection = Selection(
            exercise_id="ex:1",
            exercise=exercise(SIARAD_ID, new_item=SIARAD_ID),
            purpose=Purpose.PRACTICE,
        )

        assert selection.as_event(Outcome.GOT_IT, START).new_item is None


class TestNothingEligible:
    def test_carries_a_reason(self) -> None:
        result = NothingEligible(reason=NoExerciseReason.NOTHING_ELIGIBLE)

        assert result.reason is NoExerciseReason.NOTHING_ELIGIBLE

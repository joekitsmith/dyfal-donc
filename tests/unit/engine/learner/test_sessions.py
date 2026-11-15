from datetime import timedelta

import pytest

from engine.learner import (
    SESSION_GAP,
    LearnerError,
    LearnerSettings,
    Outcome,
    Review,
    ReviewEvent,
    SessionRun,
    is_ongoing,
    replay,
    split_sessions,
    summarise_session,
)
from tests.unit.engine.learner.helpers import START

ITEM = "lex:coffi"
OTHER = "lex:te"


def event(
    minutes: float,
    *item_ids: str,
    new_item: str | None = None,
    outcome: Outcome = Outcome.GOT_IT,
    exercise_id: str | None = None,
) -> ReviewEvent:
    return ReviewEvent(
        exercise_id=exercise_id or f"ex:{minutes}",
        item_ids=item_ids,
        new_item=new_item,
        outcome=outcome,
        reviewed_at=START + timedelta(minutes=minutes),
    )


def events_until_review(
    item_id: str, settings: LearnerSettings, *, first_minute: float = 0
) -> tuple[ReviewEvent, ...]:
    """Introduces the item and practises it, a minute apart, until it is in long-term review."""
    events = [event(first_minute, item_id, new_item=item_id)]
    for number in range(1, 40):
        if isinstance(replay(events, settings).memories[item_id], Review):
            return tuple(events)

        events.append(event(first_minute + number, item_id))

    raise AssertionError("The item never reached review")


class TestSplitSessions:
    def test_no_events_make_no_sessions(self) -> None:
        assert split_sessions(()) == ()

    def test_one_event_is_one_session(self) -> None:
        assert split_sessions((event(0, ITEM),)) == (SessionRun(start=0, end=1),)

    def test_answers_close_together_are_one_session(self) -> None:
        events = tuple(event(minute, ITEM) for minute in (0, 3, 9, 15))

        assert split_sessions(events) == (SessionRun(start=0, end=4),)

    def test_a_pause_of_exactly_the_gap_does_not_end_the_session(self) -> None:
        events = (event(0, ITEM), event(10, ITEM))

        assert split_sessions(events) == (SessionRun(start=0, end=2),)

    def test_a_pause_a_second_longer_than_the_gap_does(self) -> None:
        events = (event(0, ITEM), event(10 + 1 / 60, ITEM))

        assert split_sessions(events) == (
            SessionRun(start=0, end=1),
            SessionRun(start=1, end=2),
        )

    def test_several_long_pauses_make_several_sessions(self) -> None:
        events = (
            event(0, ITEM),
            event(1, ITEM),
            event(60, ITEM),
            event(24 * 60, ITEM),
            event(24 * 60 + 2, ITEM),
        )

        assert split_sessions(events) == (
            SessionRun(start=0, end=2),
            SessionRun(start=2, end=3),
            SessionRun(start=3, end=5),
        )

    def test_the_gap_can_be_changed(self) -> None:
        events = (event(0, ITEM), event(3, ITEM))

        assert len(split_sessions(events, timedelta(minutes=2))) == 2

    @pytest.mark.parametrize("gap", [timedelta(0), timedelta(minutes=-1)])
    def test_a_gap_that_is_not_positive_is_refused(self, gap: timedelta) -> None:
        with pytest.raises(LearnerError, match="must be positive"):
            split_sessions((), gap)


class TestSessionRun:
    @pytest.mark.parametrize(("start", "end"), [(-1, 2), (2, 2), (3, 2)])
    def test_must_hold_at_least_one_event(self, start: int, end: int) -> None:
        with pytest.raises(LearnerError, match="at least one event"):
            SessionRun(start=start, end=end)


class TestIsOngoing:
    def test_is_ongoing_within_the_gap(self) -> None:
        assert is_ongoing(START, START + SESSION_GAP)

    def test_is_over_after_the_gap(self) -> None:
        assert not is_ongoing(START, START + SESSION_GAP + timedelta(seconds=1))


class TestSummariseSession:
    def test_a_session_with_no_events_is_refused(self) -> None:
        with pytest.raises(LearnerError, match="at least one event"):
            summarise_session((), ())

    def test_counts_the_exercises_and_times_the_session(self) -> None:
        during = (
            event(0, ITEM, new_item=ITEM),
            event(2, ITEM),
            event(5, ITEM),
        )

        summary = summarise_session((), during)

        assert summary.exercises_completed == 3
        assert (summary.started_at, summary.ended_at) == (
            during[0].reviewed_at,
            during[-1].reviewed_at,
        )
        assert summary.duration == timedelta(minutes=5)

    def test_a_single_exercise_has_no_duration(self) -> None:
        assert summarise_session((), (event(0, ITEM, new_item=ITEM),)).duration == (
            timedelta(0)
        )

    def test_lists_the_items_introduced_in_order(self) -> None:
        during = (
            event(0, ITEM, new_item=ITEM),
            event(1, ITEM, OTHER, new_item=OTHER),
        )

        summary = summarise_session((), during)

        assert summary.items_introduced == (ITEM, OTHER)
        assert summary.items_reviewed == ()

    def test_an_item_met_in_the_session_is_not_a_review(self) -> None:
        during = (event(0, ITEM, new_item=ITEM),) + tuple(
            event(minute, ITEM) for minute in range(1, 6)
        )

        summary = summarise_session((), during)

        assert summary.items_introduced == (ITEM,)
        assert summary.items_reviewed == ()
        assert summary.items_lapsed == ()

    def test_an_item_known_before_and_counted_in_the_session_is_reviewed(
        self,
    ) -> None:
        before = (
            event(-30, ITEM, new_item=ITEM),
            event(-29, OTHER, new_item=OTHER),
        )
        during = (event(0, ITEM),)

        summary = summarise_session(before, during)

        assert summary.items_reviewed == (ITEM,)
        assert summary.items_introduced == ()

    def test_an_item_practised_before_it_is_due_is_not_counted_as_reviewed(
        self,
    ) -> None:
        before = (event(-1, ITEM, new_item=ITEM),)
        during = (event(0, ITEM),)

        summary = summarise_session(before, during)

        assert summary.items_reviewed == ()

    def test_each_reviewed_item_is_listed_once(self) -> None:
        before = (
            event(-30, ITEM, new_item=ITEM),
            event(-29, OTHER, ITEM, new_item=OTHER),
        )
        during = tuple(event(minute, ITEM, OTHER) for minute in range(0, 6))

        summary = summarise_session(before, during)

        assert len(summary.items_reviewed) == len(set(summary.items_reviewed))

    def test_a_miss_on_an_item_in_long_term_review_is_a_lapse(
        self, learner_settings: LearnerSettings
    ) -> None:
        before = events_until_review(ITEM, learner_settings, first_minute=-120)
        during = (event(0, ITEM, outcome=Outcome.MISSED_IT, exercise_id="ex:miss"),)

        summary = summarise_session(before, during, learner_settings)

        assert summary.items_lapsed == (ITEM,)
        assert summary.items_reviewed == (ITEM,)

    def test_a_miss_on_an_item_still_being_learned_is_not_a_lapse(self) -> None:
        before = (event(-30, ITEM, new_item=ITEM),)
        during = (event(0, ITEM, outcome=Outcome.MISSED_IT),)

        summary = summarise_session(before, during)

        assert summary.items_lapsed == ()
        assert summary.items_reviewed == (ITEM,)

    def test_a_missed_introduction_is_a_missed_exercise_but_not_a_lapse(self) -> None:
        during = (event(0, ITEM, new_item=ITEM, outcome=Outcome.MISSED_IT),)

        summary = summarise_session((), during)

        assert summary.items_lapsed == ()
        assert summary.missed_exercises == ("ex:0",)

    def test_missed_exercises_are_listed_once_each_in_order(self) -> None:
        during = (
            event(0, ITEM, new_item=ITEM, exercise_id="ex:a"),
            event(1, ITEM, outcome=Outcome.MISSED_IT, exercise_id="ex:b"),
            event(2, ITEM, exercise_id="ex:c"),
            event(3, ITEM, outcome=Outcome.MISSED_IT, exercise_id="ex:b"),
            event(4, ITEM, outcome=Outcome.MISSED_IT, exercise_id="ex:d"),
        )

        summary = summarise_session((), during)

        assert summary.missed_exercises == ("ex:b", "ex:d")

    def test_what_happened_before_does_not_count(self) -> None:
        before = (
            event(-60, ITEM, new_item=ITEM, exercise_id="ex:old"),
            event(-59, ITEM, outcome=Outcome.MISSED_IT, exercise_id="ex:old-miss"),
        )
        during = (event(0, OTHER, new_item=OTHER),)

        summary = summarise_session(before, during)

        assert summary.exercises_completed == 1
        assert summary.missed_exercises == ()
        assert summary.items_introduced == (OTHER,)

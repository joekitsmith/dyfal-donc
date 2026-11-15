from datetime import timedelta
from functools import reduce

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from engine.learner import (
    FsrsMemoryModel,
    LearnerError,
    LearnerSettings,
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
    apply_event,
    replay,
)
from tests.unit.engine.learner.helpers import FILLER, START, Session, event_sequences

ITEM = "lex:coffi"


def learning(step_index: int, exercises_until_due: int) -> Learning:
    return Learning(step_index=step_index, exercises_until_due=exercises_until_due)


class TestIntroduction:
    def test_a_new_item_enters_the_first_step(self, session: Session) -> None:
        state = session.introduce(ITEM)

        assert state.memories[ITEM] == learning(0, 1)

    def test_a_missed_introduction_enters_the_same_way(self, session: Session) -> None:
        state = session.introduce(ITEM, Outcome.MISSED_IT)

        assert state.memories[ITEM] == learning(0, 1)

    def test_an_introduction_does_not_count_the_new_item_down(
        self, session: Session
    ) -> None:
        session.introduce(ITEM)

        assert session.state.memories[ITEM] == learning(0, 1)

    def test_other_items_in_the_introducing_exercise_are_practised(
        self, session: Session
    ) -> None:
        session.introduce("lex:a")
        session.fillers(1)

        state = session.give("lex:a", "lex:b", new_item="lex:b")

        assert state.memories["lex:a"] == learning(1, 3)
        assert state.memories["lex:b"] == learning(0, 1)


class TestLearningSteps:
    def test_walks_every_step_then_graduates(
        self, session: Session, memory_model: FsrsMemoryModel
    ) -> None:
        session.introduce(ITEM)
        session.fillers(1)
        assert session.state.memories[ITEM] == learning(0, 0)

        session.give(ITEM)
        assert session.state.memories[ITEM] == learning(1, 3)

        session.fillers(3)
        session.give(ITEM)
        assert session.state.memories[ITEM] == learning(2, 8)

        session.fillers(8)
        session.give(ITEM)

        assert session.state.memories[ITEM] == Review(
            memory=memory_model.initial(session.now)
        )

    def test_counts_down_with_every_exercise(self, session: Session) -> None:
        session.introduce(ITEM)
        session.fillers(1)
        session.give(ITEM)

        counts = []
        for _ in range(3):
            session.fillers(1)
            memory = session.state.memories[ITEM]
            assert isinstance(memory, Learning)
            counts.append(memory.exercises_until_due)

        assert counts == [2, 1, 0]

    def test_the_countdown_stops_at_zero(self, session: Session) -> None:
        session.introduce(ITEM)

        session.fillers(5)

        assert session.state.memories[ITEM] == learning(0, 0)

    def test_a_miss_returns_to_the_first_step(self, session: Session) -> None:
        session.introduce(ITEM)
        session.fillers(1)
        session.give(ITEM)
        session.fillers(3)
        session.give(ITEM)
        assert session.state.memories[ITEM] == learning(2, 8)

        session.fillers(8)
        session.give(ITEM, outcome=Outcome.MISSED_IT)

        assert session.state.memories[ITEM] == learning(0, 1)

    def test_a_miss_before_due_still_returns_to_the_first_step(
        self, session: Session
    ) -> None:
        session.introduce(ITEM)
        session.fillers(1)
        session.give(ITEM)

        session.give(ITEM, outcome=Outcome.MISSED_IT)

        assert session.state.memories[ITEM] == learning(0, 1)

    def test_a_success_before_due_counts_down_but_does_not_advance(
        self, session: Session
    ) -> None:
        session.introduce(ITEM)

        session.give(ITEM)

        assert session.state.memories[ITEM] == learning(0, 0)

    def test_a_missed_exercise_resets_every_learning_item_in_it(
        self, session: Session
    ) -> None:
        session.introduce("lex:a")
        session.fillers(1)
        session.give("lex:a")
        session.introduce("lex:b")

        session.give("lex:a", "lex:b", outcome=Outcome.MISSED_IT)

        assert session.state.memories["lex:a"] == learning(0, 1)
        assert session.state.memories["lex:b"] == learning(0, 1)

    def test_learning_items_outside_the_exercise_count_down(
        self, session: Session
    ) -> None:
        session.introduce("lex:a")
        session.fillers(1)
        session.give("lex:a")
        session.introduce("lex:b")
        assert session.state.memories["lex:a"] == learning(1, 2)
        assert session.state.memories["lex:b"] == learning(0, 1)

        state = session.give(FILLER)

        assert state.memories["lex:a"] == learning(1, 1)
        assert state.memories["lex:b"] == learning(0, 0)

    def test_custom_steps(self, learner_settings: LearnerSettings) -> None:
        custom = LearnerSettings(
            learning_steps=(2, 5), memory_model=learner_settings.memory_model
        )
        session = Session(custom)

        session.introduce(ITEM)
        assert session.state.memories[ITEM] == learning(0, 2)

        session.fillers(2)
        session.give(ITEM)
        assert session.state.memories[ITEM] == learning(1, 5)

    def test_a_single_step_graduates_after_one_success(
        self, learner_settings: LearnerSettings
    ) -> None:
        session = Session(
            LearnerSettings(
                learning_steps=(1,), memory_model=learner_settings.memory_model
            )
        )
        session.introduce(ITEM)
        session.fillers(1)

        session.give(ITEM)

        assert isinstance(session.state.memories[ITEM], Review)


class TestReviewItems:
    def make_session(
        self, learner_settings: LearnerSettings, memory_model: FsrsMemoryModel
    ) -> Session:
        return Session(
            learner_settings, {ITEM: Review(memory=memory_model.initial(START))}
        )

    def test_a_due_item_takes_a_success(
        self, learner_settings: LearnerSettings, memory_model: FsrsMemoryModel
    ) -> None:
        session = self.make_session(learner_settings, memory_model)
        before = memory_model.initial(START)
        session.wait(days=3)

        session.give(ITEM)

        assert session.state.memories[ITEM] == Review(
            memory=memory_model.review(before, Outcome.GOT_IT, session.now)
        )

    def test_an_item_not_yet_due_is_left_untouched_by_a_success(
        self, learner_settings: LearnerSettings, memory_model: FsrsMemoryModel
    ) -> None:
        session = self.make_session(learner_settings, memory_model)

        session.give(ITEM)

        assert session.state.memories[ITEM] == Review(
            memory=memory_model.initial(START)
        )

    def test_a_miss_goes_to_the_weakest_review_item_only(
        self, learner_settings: LearnerSettings, memory_model: FsrsMemoryModel
    ) -> None:
        session = Session(
            learner_settings,
            {
                "lex:old": Review(
                    memory=memory_model.initial(START - timedelta(days=4))
                ),
                "lex:recent": Review(memory=memory_model.initial(START)),
            },
        )
        old_before = session.state.memories["lex:old"]
        recent_before = session.state.memories["lex:recent"]
        assert isinstance(old_before, Review)

        session.give("lex:old", "lex:recent", outcome=Outcome.MISSED_IT)

        assert session.state.memories["lex:old"] == Review(
            memory=memory_model.review(
                old_before.memory, Outcome.MISSED_IT, session.now
            )
        )
        assert session.state.memories["lex:recent"] == recent_before

    def test_review_items_never_count_down_or_change_phase(
        self, learner_settings: LearnerSettings, memory_model: FsrsMemoryModel
    ) -> None:
        session = self.make_session(learner_settings, memory_model)

        session.introduce("lex:new")
        session.fillers(3)

        assert session.state.memories[ITEM] == Review(
            memory=memory_model.initial(START)
        )


class TestEarlyCredit:
    def test_a_success_part_way_through_the_interval_reviews_the_item(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        settings = LearnerSettings(
            memory_model=memory_model, review_credit_fraction=0.5
        )
        before = memory_model.initial(START)
        session = Session(settings, {ITEM: Review(memory=before)})
        session.wait(days=1)

        session.give(ITEM)

        assert session.state.memories[ITEM] == Review(
            memory=memory_model.review(before, Outcome.GOT_IT, session.now)
        )


class TestApplyEvent:
    def test_records_the_time_of_the_last_event(self, session: Session) -> None:
        session.introduce(ITEM)

        assert session.state.last_reviewed_at == session.now

    def test_does_not_change_the_state_it_was_given(self, session: Session) -> None:
        session.introduce(ITEM)
        before = session.state
        snapshot = dict(before.memories)

        session.fillers(2)

        assert dict(before.memories) == snapshot

    def test_rejects_an_item_that_was_never_introduced(self, session: Session) -> None:
        with pytest.raises(LearnerError, match="lex:unseen has not been introduced"):
            session.give("lex:unseen")

    def test_rejects_introducing_an_item_twice(self, session: Session) -> None:
        session.introduce(ITEM)

        with pytest.raises(LearnerError, match="has already been introduced"):
            session.introduce(ITEM)

    def test_rejects_an_event_before_the_previous_one(
        self, session: Session, learner_settings: LearnerSettings
    ) -> None:
        session.introduce(ITEM)
        earlier = ReviewEvent(
            exercise_id="ex:early",
            item_ids=(FILLER,),
            outcome=Outcome.GOT_IT,
            reviewed_at=START,
        )

        with pytest.raises(LearnerError, match="chronological"):
            apply_event(session.state, earlier, learner_settings)

    def test_accepts_events_at_the_same_moment(
        self, session: Session, learner_settings: LearnerSettings
    ) -> None:
        session.introduce(ITEM)
        simultaneous = ReviewEvent(
            exercise_id="ex:same",
            item_ids=(FILLER,),
            outcome=Outcome.GOT_IT,
            reviewed_at=session.now,
        )

        state = apply_event(session.state, simultaneous, learner_settings)

        assert state.last_reviewed_at == session.now

    def test_uses_the_default_settings_when_none_are_given(self) -> None:
        event = ReviewEvent(
            exercise_id="ex:1",
            item_ids=(ITEM,),
            new_item=ITEM,
            outcome=Outcome.GOT_IT,
            reviewed_at=START,
        )

        state = apply_event(LearnerState(), event)

        assert state.memories[ITEM] == learning(0, 1)


class TestReplay:
    def test_no_events_gives_an_empty_state(self) -> None:
        assert replay(()) == LearnerState()

    def test_replays_events_in_order(
        self, session: Session, learner_settings: LearnerSettings
    ) -> None:
        session.introduce("lex:a")
        session.introduce("lex:b")
        session.fillers(2)
        session.give("lex:a")

        events = tuple(session.events)
        initial = Session(learner_settings).state

        replayed = reduce(
            lambda state, event: apply_event(state, event, learner_settings),
            events,
            initial,
        )

        assert replayed == session.state

    def test_rejects_events_out_of_order(
        self, learner_settings: LearnerSettings
    ) -> None:
        first = ReviewEvent(
            exercise_id="ex:1",
            item_ids=("lex:a",),
            new_item="lex:a",
            outcome=Outcome.GOT_IT,
            reviewed_at=START + timedelta(hours=1),
        )
        second = ReviewEvent(
            exercise_id="ex:2",
            item_ids=("lex:b",),
            new_item="lex:b",
            outcome=Outcome.GOT_IT,
            reviewed_at=START,
        )

        with pytest.raises(LearnerError, match="chronological"):
            replay((first, second), learner_settings)


class TestEarlyCreditProperties:
    @settings(deadline=None)
    @given(events=event_sequences())
    def test_a_success_still_never_makes_a_review_item_due_sooner(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        early = LearnerSettings(review_credit_fraction=0.25)
        state = LearnerState()
        for event in events:
            after = apply_event(state, event, early)
            if event.outcome is Outcome.GOT_IT:
                for item_id, before in state.memories.items():
                    now = after.memories[item_id]
                    if isinstance(before, Review) and isinstance(now, Review):
                        assert now.memory.due_at >= before.memory.due_at

            state = after


class TestReplayProperties:
    @settings(deadline=None)
    @given(events=event_sequences())
    def test_replay_equals_applying_events_one_at_a_time(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        stepwise = reduce(apply_event, events, LearnerState())

        assert replay(events) == stepwise

    @settings(deadline=None)
    @given(events=event_sequences(), data=st.data())
    def test_replaying_a_prefix_then_the_rest_equals_replaying_everything(
        self, events: tuple[ReviewEvent, ...], data: st.DataObject
    ) -> None:
        split = data.draw(st.integers(min_value=0, max_value=len(events)))

        resumed = reduce(apply_event, events[split:], replay(events[:split]))

        assert resumed == replay(events)

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_replaying_the_same_events_twice_gives_equal_states(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        assert replay(events) == replay(events)

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_introduced_items_are_exactly_those_in_the_events(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        practised = {item_id for event in events for item_id in event.item_ids}

        assert set(replay(events).memories) == practised

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_a_review_item_is_never_due_before_it_was_reviewed(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        for memory in replay(events).memories.values():
            if isinstance(memory, Review):
                assert memory.memory.due_at >= memory.memory.last_reviewed_at

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_a_success_never_makes_a_review_item_due_sooner(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        state = LearnerState()
        for event in events:
            after = apply_event(state, event)
            if event.outcome is Outcome.GOT_IT:
                for item_id, before in state.memories.items():
                    now = after.memories[item_id]
                    if isinstance(before, Review) and isinstance(now, Review):
                        assert now.memory.due_at >= before.memory.due_at

            state = after

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_review_items_outside_an_event_are_untouched(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        state = LearnerState()
        for event in events:
            after = apply_event(state, event)
            for item_id, before in state.memories.items():
                if isinstance(before, Review) and item_id not in event.item_ids:
                    assert after.memories[item_id] == before

            state = after

    @settings(deadline=None)
    @given(events=event_sequences())
    def test_learning_steps_never_skip_ahead(
        self, events: tuple[ReviewEvent, ...]
    ) -> None:
        state = LearnerState()
        for event in events:
            after = apply_event(state, event)
            for item_id, before in state.memories.items():
                now = after.memories[item_id]
                if isinstance(before, Learning) and isinstance(now, Learning):
                    assert now.step_index in (
                        0,
                        before.step_index,
                        before.step_index + 1,
                    )

            state = after

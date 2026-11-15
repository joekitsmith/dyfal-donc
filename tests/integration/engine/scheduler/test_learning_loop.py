from datetime import datetime, timedelta

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import (
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
    apply_event,
    replay,
)
from engine.scheduler import NothingEligible, Purpose, Selection, next_exercise
from tests.unit.engine.learner.helpers import START
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    MYND_ID,
    SIARAD_ID,
    course,
    exercise,
)

POOL = {
    "ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID),
    "ex:2": exercise(SIARAD_ID, DYSGU_ID, new_item=DYSGU_ID),
    "ex:3": exercise(DYSGU_ID),
    "ex:4": exercise(MYND_ID, SIARAD_ID, new_item=MYND_ID),
    "ex:5": exercise(COFFI_ID, MYND_ID, new_item=COFFI_ID),
    "ex:6": exercise(SIARAD_ID, DYSGU_ID, MYND_ID, COFFI_ID),
}


def run(
    pool: dict[str, Exercise],
    curriculum: Curriculum,
    steps: int,
    *,
    step: timedelta,
    misses_on: frozenset[str] = frozenset(),
) -> tuple[LearnerState, tuple[Selection, ...], tuple[ReviewEvent, ...]]:
    """A learner who gets everything except the exercises in ``misses_on``."""
    state = LearnerState()
    events: list[ReviewEvent] = []
    selections: list[Selection] = []
    now: datetime = START
    for _ in range(steps):
        result = next_exercise(pool, curriculum, state, events, now)
        if isinstance(result, NothingEligible):
            break

        outcome = (
            Outcome.MISSED_IT if result.exercise_id in misses_on else Outcome.GOT_IT
        )
        event = result.as_event(outcome, now)
        state = apply_event(state, event)
        events.append(event)
        selections.append(result)
        now += step

    return state, tuple(selections), tuple(events)


class TestLearningLoop:
    def test_items_are_introduced_in_curriculum_order(self) -> None:
        _, selections, _ = run(POOL, course(), 40, step=timedelta(minutes=1))

        introduced = [s.introduces for s in selections if s.introduces]

        assert introduced == [SIARAD_ID, DYSGU_ID, MYND_ID, COFFI_ID]

    def test_a_learner_who_gets_everything_graduates_every_item(self) -> None:
        state, selections, _ = run(POOL, course(), 120, step=timedelta(hours=6))

        assert {type(memory) for memory in state.memories.values()} == {Review}
        assert Purpose.LEARNING_DUE in {s.purpose for s in selections}
        assert Purpose.REVIEW_DUE in {s.purpose for s in selections}

    def test_a_due_learning_item_is_always_practised_when_possible(self) -> None:
        state = LearnerState()
        events: list[ReviewEvent] = []
        now = START
        for _ in range(60):
            result = next_exercise(POOL, course(), state, events, now)
            assert isinstance(result, Selection)
            if any(
                isinstance(memory, Learning) and memory.exercises_until_due == 0
                for memory in state.memories.values()
            ):
                assert result.purpose is Purpose.LEARNING_DUE

            event = result.as_event(Outcome.GOT_IT, now)
            state = apply_event(state, event)
            events.append(event)
            now += timedelta(minutes=1)

    def test_the_same_run_twice_is_identical(self) -> None:
        first = run(POOL, course(), 60, step=timedelta(hours=3))
        second = run(POOL, course(), 60, step=timedelta(hours=3))

        assert first == second

    def test_the_state_equals_a_replay_of_the_events(self) -> None:
        state, _, events = run(POOL, course(), 60, step=timedelta(hours=3))

        assert replay(events) == state

    def test_a_learner_who_keeps_missing_is_slowed_but_never_stuck_or_out_of_order(
        self,
    ) -> None:
        state, selections, _ = run(
            POOL,
            course(),
            80,
            step=timedelta(minutes=1),
            misses_on=frozenset({"ex:2", "ex:3", "ex:6"}),
        )

        introduced = [s.introduces for s in selections if s.introduces]

        assert len(selections) == 80
        assert introduced == [SIARAD_ID, DYSGU_ID, MYND_ID, COFFI_ID][: len(introduced)]
        assert set(state.memories) == set(introduced)

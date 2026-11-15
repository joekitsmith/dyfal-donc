from datetime import datetime, timedelta

import pytest

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import (
    FsrsMemoryModel,
    ItemMemory,
    LearnerError,
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
)
from engine.scheduler import (
    DEFAULT_SCHEDULER_SETTINGS,
    NoExerciseReason,
    NothingEligible,
    Purpose,
    SchedulerSettings,
    Selection,
    next_exercise,
)
from tests.unit.engine.learner.helpers import START
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    MYND_ID,
    SIARAD_ID,
    event,
    exercise,
)

DAY = timedelta(days=1)


def choose(
    pool: dict[str, Exercise],
    curriculum: Curriculum,
    memories: dict[str, ItemMemory] | None = None,
    events: tuple[ReviewEvent, ...] = (),
    *,
    now: datetime = START,
    settings: SchedulerSettings | None = None,
) -> Selection | NothingEligible:
    return next_exercise(
        pool,
        curriculum,
        LearnerState(memories=memories or {}),
        events,
        now,
        settings=settings or DEFAULT_SCHEDULER_SETTINGS,
    )


def selected(result: Selection | NothingEligible) -> Selection:
    assert isinstance(result, Selection)
    return result


def misses(count: int, *, of: int) -> tuple[ReviewEvent, ...]:
    return tuple(
        event(
            f"ex:{number}",
            SIARAD_ID,
            outcome=Outcome.MISSED_IT if number < count else Outcome.GOT_IT,
            minutes=number,
        )
        for number in range(of)
    )


def learning_due(step_index: int = 0) -> Learning:
    return Learning(step_index=step_index, exercises_until_due=0)


def review_due(memory_model: FsrsMemoryModel) -> Review:
    return Review(memory=memory_model.initial(START - 3 * DAY))


def review_not_due(memory_model: FsrsMemoryModel) -> Review:
    return Review(memory=memory_model.initial(START))


class TestPriority:
    def test_a_new_learner_is_given_the_exercise_that_introduces_the_first_item(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID)}

        result = selected(choose(pool, curriculum))

        assert (result.exercise_id, result.purpose, result.introduces) == (
            "ex:1",
            Purpose.INTRODUCTION,
            SIARAD_ID,
        )

    def test_a_due_learning_item_comes_before_a_due_review_and_an_introduction(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {
            "ex:introduce": exercise(DYSGU_ID, SIARAD_ID, new_item=DYSGU_ID),
            "ex:review": exercise(COFFI_ID),
            "ex:learning": exercise(SIARAD_ID),
        }
        memories: dict[str, ItemMemory] = {
            SIARAD_ID: learning_due(),
            COFFI_ID: review_due(memory_model),
        }

        result = selected(choose(pool, curriculum, memories))

        assert (result.exercise_id, result.purpose) == (
            "ex:learning",
            Purpose.LEARNING_DUE,
        )

    def test_a_due_review_comes_before_an_introduction(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {
            "ex:introduce": exercise(DYSGU_ID, new_item=DYSGU_ID),
            "ex:review": exercise(SIARAD_ID),
        }
        memories: dict[str, ItemMemory] = {SIARAD_ID: review_due(memory_model)}

        result = selected(choose(pool, curriculum, memories))

        assert (result.exercise_id, result.purpose) == ("ex:review", Purpose.REVIEW_DUE)

    def test_nothing_due_means_the_next_item_is_introduced(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {
            "ex:practice": exercise(SIARAD_ID),
            "ex:introduce": exercise(DYSGU_ID, new_item=DYSGU_ID),
        }
        memories: dict[str, ItemMemory] = {SIARAD_ID: review_not_due(memory_model)}

        result = selected(choose(pool, curriculum, memories))

        assert (result.exercise_id, result.purpose, result.introduces) == (
            "ex:introduce",
            Purpose.INTRODUCTION,
            DYSGU_ID,
        )

    def test_with_nothing_to_introduce_it_gives_extra_practice(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {"ex:practice": exercise(SIARAD_ID)}
        memories: dict[str, ItemMemory] = {SIARAD_ID: review_not_due(memory_model)}

        result = selected(choose(pool, curriculum, memories))

        assert (result.exercise_id, result.purpose, result.introduces) == (
            "ex:practice",
            Purpose.PRACTICE,
            None,
        )

    def test_a_due_item_no_exercise_covers_falls_through_to_the_next_priority(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:introduce": exercise(SIARAD_ID, new_item=SIARAD_ID)}
        memories: dict[str, ItemMemory] = {COFFI_ID: learning_due()}

        result = selected(choose(pool, curriculum, memories))

        assert result.purpose is Purpose.INTRODUCTION

    def test_an_introducing_exercise_never_counts_as_due_practice(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {"ex:introduce": exercise(SIARAD_ID, DYSGU_ID, new_item=DYSGU_ID)}
        memories: dict[str, ItemMemory] = {SIARAD_ID: learning_due()}

        result = choose(pool, curriculum, memories, misses(10, of=10))

        assert result == NothingEligible(reason=NoExerciseReason.ERROR_RATE_TOO_HIGH)

    def test_an_exercise_that_once_introduced_an_item_is_practice_afterwards(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID)}
        memories: dict[str, ItemMemory] = {SIARAD_ID: learning_due()}

        result = selected(choose(pool, curriculum, memories))

        assert (result.purpose, result.introduces) == (Purpose.LEARNING_DUE, None)


class TestPacing:
    POOL = {
        "ex:practice": exercise(SIARAD_ID),
        "ex:introduce": exercise(SIARAD_ID, DYSGU_ID, new_item=DYSGU_ID),
    }

    def memories(self, memory_model: FsrsMemoryModel) -> dict[str, ItemMemory]:
        return {SIARAD_ID: review_not_due(memory_model)}

    def test_a_low_error_rate_allows_introductions(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        result = selected(
            choose(self.POOL, curriculum, self.memories(memory_model), misses(1, of=20))
        )

        assert result.purpose is Purpose.INTRODUCTION

    def test_a_high_error_rate_holds_introductions_back_in_favour_of_practice(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        result = selected(
            choose(self.POOL, curriculum, self.memories(memory_model), misses(6, of=20))
        )

        assert (result.exercise_id, result.purpose) == ("ex:practice", Purpose.PRACTICE)

    def test_an_error_rate_exactly_at_the_threshold_holds_introductions_back(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        result = selected(
            choose(self.POOL, curriculum, self.memories(memory_model), misses(3, of=20))
        )

        assert result.purpose is Purpose.PRACTICE

    def test_only_the_recent_window_counts(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        old_misses = tuple(
            event(f"ex:old-{n}", SIARAD_ID, outcome=Outcome.MISSED_IT, minutes=n)
            for n in range(10)
        )
        recent_successes = tuple(
            event(f"ex:new-{n}", SIARAD_ID, minutes=100 + n) for n in range(20)
        )

        result = selected(
            choose(
                self.POOL,
                curriculum,
                self.memories(memory_model),
                old_misses + recent_successes,
            )
        )

        assert result.purpose is Purpose.INTRODUCTION

    def test_a_few_early_misses_do_not_hold_the_course_back(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        result = selected(
            choose(self.POOL, curriculum, self.memories(memory_model), misses(4, of=4))
        )

        assert result.purpose is Purpose.INTRODUCTION

    def test_the_threshold_is_configurable(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        lenient = SchedulerSettings(error_rate_threshold=0.5)

        result = selected(
            choose(
                self.POOL,
                curriculum,
                self.memories(memory_model),
                misses(6, of=20),
                settings=lenient,
            )
        )

        assert result.purpose is Purpose.INTRODUCTION


class TestNothingEligible:
    def test_nothing_is_eligible_with_an_empty_pool_once_everything_is_known(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            item_id: review_not_due(memory_model) for item_id in curriculum.order
        }

        result = choose({}, curriculum, memories)

        assert result == NothingEligible(reason=NoExerciseReason.NOTHING_ELIGIBLE)

    def test_a_missing_introduction_is_reported_as_a_content_gap(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:1": exercise(DYSGU_ID, new_item=DYSGU_ID)}

        result = choose(pool, curriculum)

        assert result == NothingEligible(
            reason=NoExerciseReason.NO_EXERCISE_INTRODUCES_FRONTIER
        )

    def test_held_back_with_nothing_else_to_do_says_the_error_rate_is_too_high(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID)}

        result = choose(pool, curriculum, events=misses(10, of=10))

        assert result == NothingEligible(reason=NoExerciseReason.ERROR_RATE_TOO_HIGH)

    def test_an_introducing_exercise_that_needs_a_later_item_is_not_eligible(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, COFFI_ID, new_item=SIARAD_ID)}

        result = choose(pool, curriculum)

        assert result == NothingEligible(reason=NoExerciseReason.NOTHING_ELIGIBLE)


class TestScoring:
    def test_the_exercise_covering_more_due_items_wins(
        self, curriculum: Curriculum
    ) -> None:
        pool = {
            "ex:a": exercise(SIARAD_ID),
            "ex:b": exercise(SIARAD_ID, DYSGU_ID),
        }
        memories: dict[str, ItemMemory] = {
            SIARAD_ID: learning_due(),
            DYSGU_ID: learning_due(),
        }

        assert selected(choose(pool, curriculum, memories)).exercise_id == "ex:b"

    def test_an_exercise_building_on_the_previous_one_wins(
        self, curriculum: Curriculum
    ) -> None:
        pool = {
            "ex:a": exercise(SIARAD_ID),
            "ex:b": exercise(SIARAD_ID, MYND_ID),
        }
        memories: dict[str, ItemMemory] = {
            SIARAD_ID: learning_due(),
            MYND_ID: Learning(step_index=0, exercises_until_due=4),
            DYSGU_ID: Learning(step_index=0, exercises_until_due=4),
        }
        previous = (event("ex:previous", MYND_ID, DYSGU_ID),)

        assert (
            selected(choose(pool, curriculum, memories, previous)).exercise_id == "ex:b"
        )

    def test_the_previous_exercise_is_not_repeated_when_another_will_do(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:a": exercise(SIARAD_ID), "ex:b": exercise(SIARAD_ID)}
        memories: dict[str, ItemMemory] = {SIARAD_ID: learning_due()}
        previous = (event("ex:a", SIARAD_ID),)

        assert (
            selected(choose(pool, curriculum, memories, previous)).exercise_id == "ex:b"
        )

    def test_the_previous_exercise_is_repeated_if_it_is_the_only_one(
        self, curriculum: Curriculum
    ) -> None:
        pool = {"ex:a": exercise(SIARAD_ID)}
        memories: dict[str, ItemMemory] = {SIARAD_ID: learning_due()}
        previous = (event("ex:a", SIARAD_ID),)

        assert (
            selected(choose(pool, curriculum, memories, previous)).exercise_id == "ex:a"
        )

    def test_ties_go_to_the_lowest_id_whatever_order_the_pool_is_in(
        self, curriculum: Curriculum
    ) -> None:
        memories: dict[str, ItemMemory] = {SIARAD_ID: learning_due()}
        ids = ("ex:c", "ex:a", "ex:b")

        for order in (ids, ids[::-1], tuple(sorted(ids))):
            pool = {exercise_id: exercise(SIARAD_ID) for exercise_id in order}

            assert selected(choose(pool, curriculum, memories)).exercise_id == "ex:a"


class TestPurity:
    def test_the_same_inputs_give_the_same_answer(
        self, curriculum: Curriculum, memory_model: FsrsMemoryModel
    ) -> None:
        pool = {
            "ex:a": exercise(SIARAD_ID, DYSGU_ID),
            "ex:b": exercise(DYSGU_ID),
            "ex:c": exercise(MYND_ID, new_item=MYND_ID),
        }
        memories: dict[str, ItemMemory] = {
            SIARAD_ID: review_due(memory_model),
            DYSGU_ID: learning_due(),
        }

        assert choose(pool, curriculum, memories) == choose(pool, curriculum, memories)

    def test_rejects_a_naive_time(self, curriculum: Curriculum) -> None:
        with pytest.raises(LearnerError, match="now must be timezone-aware"):
            choose({}, curriculum, now=datetime(2026, 1, 1))

import random
from dataclasses import replace
from datetime import timedelta

from engine.learner import Outcome
from simulation.memory import ExponentialMemory
from simulation.outcome import (
    TrueMemory,
    attempt_exercise,
    item_ease,
    recall_probability,
)
from simulation.profile import AVERAGE
from tests.unit.engine.learner.helpers import START
from tests.unit.simulation.helpers import FORGETFUL, PERFECT, ShakyMemory

A = "lex:a"
B = "lex:b"


def known(*item_ids: str) -> dict[str, TrueMemory]:
    return {
        item_id: TrueMemory(stability_days=1.0, last_seen=START) for item_id in item_ids
    }


class TestItemEase:
    def test_is_the_same_for_the_same_seed_and_item(self) -> None:
        assert item_ease(1, A, 0.4) == item_ease(1, A, 0.4)

    def test_differs_between_items_and_seeds(self) -> None:
        assert item_ease(1, A, 0.4) != item_ease(1, B, 0.4)
        assert item_ease(1, A, 0.4) != item_ease(2, A, 0.4)

    def test_has_no_spread_when_the_spread_is_zero(self) -> None:
        assert item_ease(1, A, 0.0) == 1.0

    def test_averages_about_one(self) -> None:
        eases = [item_ease(seed, A, 0.4) for seed in range(2000)]

        assert abs(sum(eases) / len(eases) - 1) < 0.05


class TestAttemptExercise:
    def test_a_perfect_memory_is_always_truly_right(self) -> None:
        attempt = attempt_exercise(
            known(A, B), (A, B), None, START, PERFECT, 1, random.Random(1)
        )

        assert attempt.truly_correct
        assert attempt.reported is Outcome.GOT_IT

    def test_one_forgotten_item_makes_the_exercise_wrong(self) -> None:
        memories = {
            A: TrueMemory(stability_days=1.0, last_seen=START),
            B: TrueMemory(stability_days=0.1, last_seen=START),
        }
        profile = PERFECT.with_memory(ShakyMemory())

        attempt = attempt_exercise(
            memories, (A, B), None, START, profile, 1, random.Random(1)
        )

        assert not attempt.truly_correct
        assert attempt.reported is Outcome.MISSED_IT

    def test_every_item_updates_on_its_own_result(self) -> None:
        profile = AVERAGE.with_memory(ExponentialMemory())
        memories = {A: TrueMemory(stability_days=10.0, last_seen=START)}
        later = START + timedelta(days=30)

        attempt = attempt_exercise(
            memories, (A,), None, later, profile, 1, random.Random(1)
        )

        assert attempt.memories[A].last_seen == later
        assert attempt.memories[A].stability_days != memories[A].stability_days

    def test_an_item_being_introduced_is_seen_not_recalled(self) -> None:
        attempt = attempt_exercise({}, (A,), A, START, FORGETFUL, 1, random.Random(1))

        assert attempt.truly_correct
        assert attempt.memories[A].stability_days == (
            FORGETFUL.memory.initial_stability_days
            * FORGETFUL.learning_rate
            * item_ease(1, A, FORGETFUL.difficulty_spread)
        )
        assert attempt.memories[A].last_seen == START

    def test_untouched_items_are_unchanged(self) -> None:
        memories = known(A, B)

        attempt = attempt_exercise(
            memories, (A,), None, START, PERFECT, 1, random.Random(1)
        )

        assert attempt.memories[B] == memories[B]

    def test_the_input_memories_are_not_modified(self) -> None:
        memories = known(A)

        attempt_exercise(memories, (A,), None, START, FORGETFUL, 1, random.Random(1))

        assert memories == known(A)

    def test_a_miss_is_never_reported_when_the_learner_never_speaks_up(self) -> None:
        profile = replace(FORGETFUL, under_report_rate=1.0)

        attempt = attempt_exercise(
            known(A), (A,), None, START, profile, 1, random.Random(1)
        )

        assert not attempt.truly_correct
        assert attempt.reported is Outcome.GOT_IT


class TestRecallProbability:
    def test_falls_as_time_passes(self) -> None:
        memory = TrueMemory(stability_days=1.0, last_seen=START)
        profile = AVERAGE

        assert recall_probability(memory, START, profile) == 1
        assert recall_probability(
            memory, START + timedelta(days=5), profile
        ) < recall_probability(memory, START + timedelta(days=1), profile)

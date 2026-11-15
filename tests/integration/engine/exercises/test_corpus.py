from collections import Counter

import pytest

from engine.curriculum import load_curriculum
from engine.exercises import (
    Exercise,
    ExerciseEntry,
    load_exercises,
    validate_exercise,
)
from tests.integration.engine.exercises.corpus_checks import (
    FEWER_INTRODUCING_EXERCISES,
    MINIMUM_INTRODUCING_EXERCISES,
    known_before,
    slot_mutation_problems,
)
from tests.integration.engine.exercises.exercise_fixtures import CURRICULUM_DIRECTORY

CURRICULUM = load_curriculum(CURRICULUM_DIRECTORY)
ENTRIES = load_exercises(CURRICULUM_DIRECTORY / "exercises")


class TestCorpusExercises:
    @pytest.mark.parametrize("entry", ENTRIES, ids=lambda entry: entry.id)
    def test_every_exercise_validates(self, entry: ExerciseEntry) -> None:
        result = validate_exercise(
            entry.exercise, CURRICULUM, known_before(entry, CURRICULUM)
        )

        assert result.issues == ()

    @pytest.mark.parametrize("entry", ENTRIES, ids=lambda entry: entry.id)
    def test_slot_words_show_the_mutation_their_pattern_requires(
        self, entry: ExerciseEntry
    ) -> None:
        result = validate_exercise(
            entry.exercise, CURRICULUM, known_before(entry, CURRICULUM)
        )

        assert slot_mutation_problems(result, CURRICULUM) == ()

    def test_a_new_item_is_the_latest_item_in_the_exercise(self) -> None:
        position = {item_id: index for index, item_id in enumerate(CURRICULUM.order)}

        for entry in ENTRIES:
            new_item = entry.exercise.new_item
            if new_item is not None:
                assert all(
                    position[item_id] <= position[new_item]
                    for item_id in entry.exercise.declared_items
                ), entry.id


class TestCorpusCoverage:
    def test_every_item_has_enough_introducing_exercises(self) -> None:
        introducing = Counter(
            entry.exercise.new_item for entry in ENTRIES if entry.exercise.new_item
        )

        short = {
            item_id: introducing[item_id]
            for item_id in CURRICULUM.order
            if introducing[item_id]
            < FEWER_INTRODUCING_EXERCISES.get(item_id, MINIMUM_INTRODUCING_EXERCISES)
        }

        assert short == {}

    def test_no_item_is_exempt_that_no_longer_needs_to_be(self) -> None:
        introducing = Counter(
            entry.exercise.new_item for entry in ENTRIES if entry.exercise.new_item
        )

        assert [
            item_id
            for item_id in FEWER_INTRODUCING_EXERCISES
            if introducing[item_id] >= MINIMUM_INTRODUCING_EXERCISES
        ] == []


class TestSlotMutationProblems:
    @staticmethod
    def problems(welsh: str, items: tuple[str, ...]) -> tuple[str, ...]:
        exercise = Exercise(english="", welsh=welsh, items=items)
        result = validate_exercise(exercise, CURRICULUM, frozenset(CURRICULUM.order))

        return slot_mutation_problems(result, CURRICULUM)

    def test_a_correctly_mutated_slot_word_passes(self) -> None:
        assert self.problems("Galla i fynd", ("pat:galla-i", "lex:mynd")) == ()

    def test_a_missing_mutation_is_reported(self) -> None:
        assert self.problems("Galla i mynd", ("pat:galla-i", "lex:mynd")) == (
            "pat:galla-i: lex:mynd should be soft, not unmutated",
        )

    def test_a_word_that_cannot_mutate_stays_unmutated(self) -> None:
        assert self.problems("Galla i siarad", ("pat:galla-i", "lex:siarad")) == ()

    def test_patterns_without_a_requirement_are_left_alone(self) -> None:
        assert self.problems("Dw i'n mynd", ("pat:dw-in", "lex:mynd")) == ()

    def test_an_adjective_after_n_must_be_soft_mutated(self) -> None:
        assert self.problems("Dw i'n blinedig", ("pat:dw-in-adj", "lex:blinedig")) == (
            "pat:dw-in-adj: lex:blinedig should be soft, not unmutated",
        )

    def test_a_soft_mutated_adjective_passes(self) -> None:
        assert self.problems("Dw i'n flinedig", ("pat:dw-in-adj", "lex:blinedig")) == ()

    def test_an_adjective_that_cannot_mutate_stays_unmutated(self) -> None:
        assert self.problems("Dw i'n hapus", ("pat:dw-in-adj", "lex:hapus")) == ()

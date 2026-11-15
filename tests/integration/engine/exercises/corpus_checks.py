from collections.abc import Mapping

from cymraeg import Mutation, mutate
from engine.curriculum import Curriculum, Lexeme
from engine.exercises import ExerciseEntry, ValidationResult

SLOT_MUTATIONS: Mapping[str, Mutation] = {
    "pat:galla-i": Mutation.SOFT,
    "pat:dw-in-adj": Mutation.SOFT,
    "pat:mae-e-yn-adj": Mutation.SOFT,
}
"""The mutation each pattern's slot words must show, if their first letter can mutate."""

MINIMUM_INTRODUCING_EXERCISES = 3

FEWER_INTRODUCING_EXERCISES: Mapping[str, int] = {
    "lex:siarad": 1,
    "lex:cymraeg": 2,
    "pat:dw-in-moyn": 2,
    "lex:mynd": 2,
    "lex:dod": 2,
}
"""Early items, for which almost no distinct exercise can be built from what is known so far."""


def known_before(entry: ExerciseEntry, curriculum: Curriculum) -> frozenset[str]:
    """The items taught before an exercise: those before its new item, or all of them."""
    new_item = entry.exercise.new_item
    if new_item is None:
        return frozenset(curriculum.order)

    return frozenset(curriculum.order[: curriculum.order.index(new_item)])


def slot_mutation_problems(
    result: ValidationResult, curriculum: Curriculum
) -> tuple[str, ...]:
    """Slot words that do not show the mutation their pattern requires.

    Validation accepts a slot word whether or not it is mutated, so a wrong
    sentence such as ``Galla i mynd`` passes it. This is the check that catches it.
    """
    problems: list[str] = []
    for pattern in result.detected:
        required = SLOT_MUTATIONS.get(pattern.item_id)
        if required is None:
            continue

        for item in result.detected:
            if item.item_id == pattern.item_id:
                continue

            if item.start < pattern.start or item.end > pattern.end:
                continue

            lexeme = curriculum.get(item.item_id)
            if not isinstance(lexeme, Lexeme):
                continue

            mutates = mutate(lexeme.welsh, required) != lexeme.welsh
            expected = required if mutates else None
            if item.mutation != expected:
                problems.append(
                    f"{pattern.item_id}: {item.item_id} should be "
                    f"{expected.value if expected else 'unmutated'}, "
                    f"not {item.mutation.value if item.mutation else 'unmutated'}"
                )

    return tuple(problems)

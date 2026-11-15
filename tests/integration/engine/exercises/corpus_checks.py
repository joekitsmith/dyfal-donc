from collections.abc import Mapping
from dataclasses import dataclass

from cymraeg import Mutation, mutate
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech
from engine.exercises import ExerciseEntry, ValidationResult


SOFT = Mutation.SOFT


@dataclass(frozen=True, slots=True, kw_only=True)
class SlotMutation:
    """A mutation a pattern requires, of the words of ``part_of_speech`` (any word if ``None``)."""

    mutation: Mutation
    part_of_speech: PartOfSpeech | None = None


SLOT_MUTATIONS: Mapping[str, SlotMutation] = {
    "pat:galla-i": SlotMutation(mutation=SOFT),
    "pat:dw-in-adj": SlotMutation(mutation=SOFT),
    "pat:mae-e-yn-adj": SlotMutation(mutation=SOFT),
    "pat:nes-i": SlotMutation(mutation=SOFT),
    "pat:ces-i": SlotMutation(mutation=SOFT),
    "pat:nest-ti": SlotMutation(mutation=SOFT),
    "pat:gest-ti": SlotMutation(mutation=SOFT),
    "pat:wna-i": SlotMutation(mutation=SOFT),
    "pat:mae-hi-yn-adj": SlotMutation(mutation=SOFT),
    "pat:bydd-hi-yn-adj": SlotMutation(mutation=SOFT),
    "pat:rodd-hi-yn-adj": SlotMutation(mutation=SOFT),
    "pat:mae-noun-yn-adj": SlotMutation(
        mutation=SOFT, part_of_speech=PartOfSpeech.ADJECTIVE
    ),
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
    """The items known before an exercise: those its new item can rely on, or all of them."""
    new_item = entry.exercise.new_item
    if new_item is None:
        return frozenset(curriculum.order)

    return curriculum.known_before(new_item)


def slot_mutation_problems(
    result: ValidationResult, curriculum: Curriculum
) -> tuple[str, ...]:
    """Slot words that do not show the mutation their pattern requires.

    Validation accepts a slot word whether or not it is mutated, so a wrong
    sentence such as ``Galla i mynd`` passes it. This is the check that catches it.
    """
    problems: list[str] = []
    for pattern in result.detected:
        requirement = SLOT_MUTATIONS.get(pattern.item_id)
        if requirement is None:
            continue

        required = requirement.mutation

        for item in result.detected:
            if item.item_id == pattern.item_id:
                continue

            if item.start < pattern.start or item.end > pattern.end:
                continue

            lexeme = curriculum.get(item.item_id)
            if not isinstance(lexeme, Lexeme):
                continue

            if (
                requirement.part_of_speech is not None
                and lexeme.part_of_speech is not requirement.part_of_speech
            ):
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

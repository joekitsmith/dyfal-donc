from pathlib import Path

from engine.curriculum import Curriculum, Lexeme, Pattern, load_curriculum

CURRICULUM_DIRECTORY = Path(__file__).parents[4] / "curriculum"


def test_seed_curriculum_loads_and_validates() -> None:
    curriculum = load_curriculum(CURRICULUM_DIRECTORY)

    assert len(curriculum.order) == len(curriculum.items)


def test_every_pattern_slot_can_be_filled_by_an_earlier_lexeme() -> None:
    curriculum = load_curriculum(CURRICULUM_DIRECTORY)

    for position, item_id in enumerate(curriculum.order):
        item = curriculum.get(item_id)
        if not isinstance(item, Pattern):
            continue

        earlier = _lexemes(curriculum, curriculum.order[:position])
        for slot, part_of_speech in item.slots.items():
            assert any(lexeme.part_of_speech == part_of_speech for lexeme in earlier), (
                f"{item.id} slot {slot} has no {part_of_speech.value} introduced before it"
            )


def _lexemes(curriculum: Curriculum, item_ids: tuple[str, ...]) -> tuple[Lexeme, ...]:
    items = (curriculum.get(item_id) for item_id in item_ids)
    return tuple(item for item in items if isinstance(item, Lexeme))

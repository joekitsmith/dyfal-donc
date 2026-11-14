from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import TypeAdapter

from cymraeg import Mutation
from engine.curriculum import Curriculum, PartOfSpeech, Pattern, load_curriculum
from engine.exercises import Exercise, ValidationResult, validate_exercise

TESTS_DIRECTORY = Path(__file__).parents[3]
CURRICULUM_DIRECTORY = TESTS_DIRECTORY.parent / "curriculum"
FIXTURES_FILE = TESTS_DIRECTORY / "fixtures" / "exercises.yaml"

# Patterns the seed curriculum doesn't have yet, so the fixtures can cover mutated fillers
FIXTURE_ONLY_PATTERNS = (
    Pattern(
        id="pat:galla-i",
        template="Galla i [VERB]",
        english="I can [VERB]",
        slots={"VERB": PartOfSpeech.VERB},
        prerequisites=("pat:dw-in",),
    ),
    Pattern(
        id="pat:dw-in-hoffi-r",
        template="Dw i'n hoffi'r [NOUN]",
        english="I like the [NOUN]",
        slots={"NOUN": PartOfSpeech.NOUN},
        prerequisites=("pat:dw-in-hoffi",),
    ),
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ExerciseFixture:
    id: str
    english: str
    welsh: str
    items: tuple[str, ...]
    new_item: str | None = None
    known_before: str | None = None
    expect: tuple[str, ...] = ()
    mutations: Mapping[str, Mutation] = field(default_factory=dict)


def load_fixtures() -> tuple[ExerciseFixture, ...]:
    raw = yaml.safe_load(FIXTURES_FILE.read_text(encoding="utf-8"))
    return tuple(TypeAdapter(list[ExerciseFixture]).validate_python(raw))


def curriculum_with_fixture_only_patterns() -> Curriculum:
    seed = load_curriculum(CURRICULUM_DIRECTORY)
    return Curriculum(
        items=seed.items + FIXTURE_ONLY_PATTERNS,
        order=seed.order + tuple(pattern.id for pattern in FIXTURE_ONLY_PATTERNS),
    )


def validate_fixture(
    fixture: ExerciseFixture, curriculum: Curriculum
) -> ValidationResult:
    exercise = Exercise(
        english=fixture.english,
        welsh=fixture.welsh,
        items=fixture.items,
        new_item=fixture.new_item,
    )
    return validate_exercise(exercise, curriculum, known_items(fixture, curriculum))


def known_items(fixture: ExerciseFixture, curriculum: Curriculum) -> frozenset[str]:
    boundary = fixture.known_before or fixture.new_item
    if boundary is None:
        return frozenset(curriculum.order)
    return frozenset(curriculum.order[: curriculum.order.index(boundary)])

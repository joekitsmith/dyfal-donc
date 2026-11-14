from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import TypeAdapter

from cymraeg import Mutation
from engine.curriculum import Curriculum
from engine.exercises import Exercise, ValidationResult, validate_exercise

TESTS_DIRECTORY = Path(__file__).parents[3]
CURRICULUM_DIRECTORY = TESTS_DIRECTORY.parent / "curriculum"
FIXTURES_FILE = TESTS_DIRECTORY / "fixtures" / "exercises.yaml"


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

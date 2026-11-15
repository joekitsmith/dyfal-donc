from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from engine.curriculum import Curriculum
from engine.exercises import Exercise, load_exercises, validate_exercise
from simulation.errors import SimulationError

EXERCISES_DIRECTORY = Path(__file__).parents[2] / "curriculum" / "exercises"


@dataclass(frozen=True, slots=True, kw_only=True)
class PoolCoverage:
    """How well the pool covers the curriculum.

    ``introducing`` counts the exercises that can introduce each item and
    ``practising`` the exercises that use it. ``blocking`` is the first item in
    the course no exercise can introduce: a learner can never get past it.
    """

    introducing: Mapping[str, int]
    practising: Mapping[str, int]
    without_introduction: tuple[str, ...]

    @property
    def blocking(self) -> str | None:
        return self.without_introduction[0] if self.without_introduction else None


def build_pool(
    curriculum: Curriculum, exercises_directory: str | Path = EXERCISES_DIRECTORY
) -> Mapping[str, Exercise]:
    """The course's own exercises, by id.

    An exercise that does not validate against the curriculum is an error, and
    so is one that introduces an item outside the course order.
    """
    position = {item_id: index for index, item_id in enumerate(curriculum.order)}
    exercises: dict[str, Exercise] = {}
    for entry in load_exercises(exercises_directory):
        if not _is_valid(entry.exercise, curriculum, position):
            raise SimulationError(f"{entry.id}: Exercise does not validate")

        exercises[entry.id] = entry.exercise

    return exercises


def coverage(pool: Mapping[str, Exercise], curriculum: Curriculum) -> PoolCoverage:
    introducing = {item_id: 0 for item_id in curriculum.order}
    practising = {item_id: 0 for item_id in curriculum.order}
    for exercise in pool.values():
        if exercise.new_item in introducing:
            introducing[exercise.new_item] += 1

        for item_id in exercise.declared_items:
            if item_id in practising:
                practising[item_id] += 1

    return PoolCoverage(
        introducing=introducing,
        practising=practising,
        without_introduction=tuple(
            item_id for item_id in curriculum.order if introducing[item_id] == 0
        ),
    )


def _is_valid(
    exercise: Exercise, curriculum: Curriculum, position: Mapping[str, int]
) -> bool:
    if exercise.new_item is None:
        known = frozenset(curriculum.order)
    elif exercise.new_item in position:
        known = curriculum.known_before(exercise.new_item)
    else:
        return False

    return validate_exercise(exercise, curriculum, known).is_valid

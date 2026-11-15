from collections.abc import Mapping
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from engine.curriculum import Curriculum
from engine.exercises import Exercise


@dataclass(frozen=True, slots=True, kw_only=True)
class Candidate:
    """An exercise the learner could be given now."""

    exercise_id: str
    exercise: Exercise
    introduces: str | None = None


def frontier(curriculum: Curriculum, introduced: AbstractSet[str]) -> str | None:
    """The first item in curriculum order the learner has not met, if any."""
    return next(
        (item_id for item_id in curriculum.order if item_id not in introduced), None
    )


def frontier_topic(curriculum: Curriculum, introduced: AbstractSet[str]) -> str | None:
    """The topic of the first item the learner has not met, if any."""
    item_id = frontier(curriculum, introduced)

    return None if item_id is None else curriculum.get(item_id).topic


def candidates(
    pool: Mapping[str, Exercise],
    introduced: AbstractSet[str],
    frontier_item: str | None,
) -> tuple[Candidate, ...]:
    """The exercises that can be given, by id.

    An exercise qualifies if the learner has met every item in it. It also
    qualifies if the only item they have not met is the frontier item and the
    exercise is the one that introduces it.
    """
    found = tuple(
        _candidate(exercise_id, exercise, introduced, frontier_item)
        for exercise_id, exercise in sorted(pool.items())
    )
    return tuple(candidate for candidate in found if candidate is not None)


def _candidate(
    exercise_id: str,
    exercise: Exercise,
    introduced: AbstractSet[str],
    frontier_item: str | None,
) -> Candidate | None:
    if not exercise.declared_items:
        return None

    unmet = tuple(item for item in exercise.declared_items if item not in introduced)
    if not unmet:
        return Candidate(exercise_id=exercise_id, exercise=exercise)

    if unmet == (frontier_item,) and exercise.new_item == frontier_item:
        return Candidate(
            exercise_id=exercise_id, exercise=exercise, introduces=frontier_item
        )

    return None

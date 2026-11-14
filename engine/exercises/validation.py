from collections.abc import Sequence
from collections.abc import Set as AbstractSet

from engine.curriculum import Curriculum
from engine.detection import CurriculumIndex, detect_items
from engine.exercises.models import (
    DeclaredItemNotFound,
    Exercise,
    Issue,
    MissingNewItem,
    MultipleNewItems,
    UndeclaredItem,
    UnknownDeclaredItem,
    ValidationResult,
    WrongNewItem,
)


def validate_exercise(
    exercise: Exercise, curriculum: Curriculum, known_items: AbstractSet[str]
) -> ValidationResult:
    """Check an exercise's Welsh against the curriculum and what the learner knows.

    ``known_items`` are the item ids taught before this exercise. Any detected
    item outside it is new, and an exercise may introduce at most one.
    """
    index = CurriculumIndex.from_curriculum(curriculum)
    declared = _declared_item_ids(exercise)
    preferred = frozenset(known_items) | frozenset(declared)

    detection = detect_items(exercise.welsh, index, preferred)
    issues = (
        detection.problems
        + _declaration_issues(declared, detection.item_ids, index.item_ids)
        + _new_item_issues(exercise.new_item, detection.item_ids, known_items)
    )
    return ValidationResult(detected=detection.items, issues=issues)


def _declared_item_ids(exercise: Exercise) -> tuple[str, ...]:
    if exercise.new_item is None:
        return exercise.items

    return tuple(dict.fromkeys((*exercise.items, exercise.new_item)))


def _declaration_issues(
    declared: Sequence[str],
    detected_ids: Sequence[str],
    curriculum_ids: AbstractSet[str],
) -> tuple[Issue, ...]:
    issues: list[Issue] = []
    for item_id in declared:
        if item_id not in curriculum_ids:
            issues.append(UnknownDeclaredItem(item_id=item_id))
        elif item_id not in detected_ids:
            issues.append(DeclaredItemNotFound(item_id=item_id))

    issues.extend(
        UndeclaredItem(item_id=item_id)
        for item_id in detected_ids
        if item_id not in declared
    )
    return tuple(issues)


def _new_item_issues(
    new_item: str | None, detected_ids: Sequence[str], known_items: AbstractSet[str]
) -> tuple[Issue, ...]:
    new_ids = tuple(item_id for item_id in detected_ids if item_id not in known_items)
    if len(new_ids) > 1:
        return (MultipleNewItems(item_ids=new_ids),)

    if len(new_ids) == 1:
        if new_item is None:
            return (MissingNewItem(item_id=new_ids[0]),)

        if new_item != new_ids[0]:
            return (WrongNewItem(declared=new_item, detected=new_ids[0]),)

        return ()

    if new_item is not None:
        return (WrongNewItem(declared=new_item, detected=None),)

    return ()

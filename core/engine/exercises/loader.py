import re
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path

import yaml
from pydantic import TypeAdapter, ValidationError

from engine.exercises.errors import ExerciseError
from engine.exercises.models import Exercise

EXERCISE_FILE_SUFFIX = ".yaml"
_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@dataclass(frozen=True, slots=True, kw_only=True)
class ExerciseEntry:
    """An exercise as authored: its id, and the pack (file) it came from."""

    id: str
    pack: str
    exercise: Exercise


def load_exercises(directory: str | Path) -> tuple[ExerciseEntry, ...]:
    """Load every ``*.yaml`` pack in the directory, in file name then file order.

    Each file is one pack, named by its file name, holding a list of exercises
    with ``id``, ``english``, ``welsh``, ``items`` and an optional ``new_item``. Ids must be unique across all the packs. This
    checks the shape of the files only: ``validate_exercise`` checks the Welsh.
    """
    root = Path(directory)
    if not root.is_dir():
        raise ExerciseError(f"Missing directory: {root}")

    entries: list[ExerciseEntry] = []
    for path in sorted(root.glob(f"*{EXERCISE_FILE_SUFFIX}")):
        entries.extend(_load_pack(path))

    _check_unique_ids(entries)

    return tuple(entries)


def exercise_pool(entries: tuple[ExerciseEntry, ...]) -> Mapping[str, Exercise]:
    """The exercises by id, in the form the scheduler takes."""
    return {entry.id: entry.exercise for entry in entries}


@dataclass(frozen=True, slots=True, kw_only=True)
class _Row:
    id: str
    english: str
    welsh: str
    items: tuple[str, ...] = ()
    new_item: str | None = None


def _load_pack(path: Path) -> tuple[ExerciseEntry, ...]:
    try:
        data: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ExerciseError(f"{path}: Invalid YAML: {exc}") from exc

    if not isinstance(data, list):
        raise ExerciseError(f"{path}: Expected a YAML list at top level")

    adapter = TypeAdapter(_Row)
    known_fields = {field.name for field in fields(_Row)}
    entries: list[ExerciseEntry] = []
    for index, raw in enumerate(data):
        if not isinstance(raw, dict):
            raise ExerciseError(f"{path}[{index}]: Expected a mapping")

        label = f"{path} ({raw.get('id', f'#{index}')})"
        unknown = sorted(str(key) for key in raw if key not in known_fields)
        if unknown:
            raise ExerciseError(f"{label}: Unknown field(s): {', '.join(unknown)}")

        try:
            row = adapter.validate_python(raw)
        except ValidationError as exc:
            details = "; ".join(
                f"{'.'.join(map(str, error['loc'])) or 'exercise'}: {error['msg']}"
                for error in exc.errors()
            )
            raise ExerciseError(f"{label}: {details}") from exc

        entries.append(_entry(row, path.stem, label))

    return tuple(entries)


def _entry(row: _Row, pack: str, label: str) -> ExerciseEntry:
    if not _ID_PATTERN.match(row.id):
        raise ExerciseError(
            f"{label}: Invalid id: expected lowercase letters, digits or hyphens"
        )

    for name, value in (("english", row.english), ("welsh", row.welsh)):
        if not value.strip():
            raise ExerciseError(f"{label}: {name.capitalize()} must not be blank")

    exercise = Exercise(
        english=row.english, welsh=row.welsh, items=row.items, new_item=row.new_item
    )
    if not exercise.declared_items:
        raise ExerciseError(f"{label}: At least one item is required")

    return ExerciseEntry(id=row.id, pack=pack, exercise=exercise)


def _check_unique_ids(entries: list[ExerciseEntry]) -> None:
    ids = [entry.id for entry in entries]
    duplicates = sorted({entry_id for entry_id in ids if ids.count(entry_id) > 1})
    if duplicates:
        raise ExerciseError(f"Duplicate exercise ids: {', '.join(duplicates)}")

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from engine.curriculum import Curriculum, load_curriculum
from engine.exercises import (
    Exercise,
    ExerciseEntry,
    ExerciseError,
    exercise_pool,
    load_exercises,
)

EXERCISES_DIRECTORY = "exercises"


@dataclass(frozen=True, slots=True, kw_only=True)
class CourseRelease:
    """The course as loaded from a directory, and a hash of its content.

    The hash changes whenever any file in the directory does, so a learner's
    events can be tied to the exact course they were produced on.
    ``exercise_topics`` is the topic each exercise is registered under: its pack.
    """

    hash: str
    curriculum: Curriculum
    exercises: Mapping[str, Exercise]
    exercise_topics: Mapping[str, str]


def load_course_release(directory: Path) -> CourseRelease:
    curriculum = load_curriculum(directory)
    entries = load_exercises(directory / EXERCISES_DIRECTORY)
    _check_packs(curriculum, entries)

    return CourseRelease(
        hash=content_hash(directory),
        curriculum=curriculum,
        exercises=exercise_pool(entries),
        exercise_topics={entry.id: entry.pack for entry in entries},
    )


def _check_packs(curriculum: Curriculum, entries: Sequence[ExerciseEntry]) -> None:
    """Each pack is a topic, taught no earlier than any item its exercises use."""
    items = {item.id: item for item in curriculum.items}
    topics = tuple(dict.fromkeys(items[item_id].topic for item_id in curriculum.order))
    unknown = sorted({entry.pack for entry in entries} - set(topics))
    if unknown:
        raise ExerciseError(f"Exercise packs that are not topics: {', '.join(unknown)}")

    too_early = sorted(
        f"{entry.id} (in {entry.pack}) uses {item_id}"
        for entry in entries
        for item_id in entry.exercise.declared_items
        if item_id in items
        and topics.index(items[item_id].topic) > topics.index(entry.pack)
    )
    if too_early:
        raise ExerciseError(
            "Exercises use items of topics taught after their pack:\n  "
            + "\n  ".join(too_early)
        )


def content_hash(directory: Path) -> str:
    """A SHA-256 of the names and bytes of every file under the directory."""
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")

    return digest.hexdigest()

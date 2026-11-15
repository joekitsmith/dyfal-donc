import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from engine.curriculum import Curriculum, load_curriculum
from engine.exercises import Exercise, exercise_pool, load_exercises

EXERCISES_DIRECTORY = "exercises"


@dataclass(frozen=True, slots=True, kw_only=True)
class CourseRelease:
    """The course as loaded from a directory, and a hash of its content.

    The hash changes whenever any file in the directory does, so a learner's
    events can be tied to the exact course they were produced on.
    """

    hash: str
    curriculum: Curriculum
    exercises: Mapping[str, Exercise]


def load_course_release(directory: Path) -> CourseRelease:
    return CourseRelease(
        hash=content_hash(directory),
        curriculum=load_curriculum(directory),
        exercises=exercise_pool(load_exercises(directory / EXERCISES_DIRECTORY)),
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

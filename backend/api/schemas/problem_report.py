from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, StringConstraints, model_validator

DESCRIPTION_MAXIMUM_LENGTH = 1000


class ProblemSource(StrEnum):
    """Where in the app the learner was when they reported."""

    LESSON = "lesson"
    SUMMARY = "summary"
    COURSE = "course"
    ITEM = "item"
    GENERAL = "general"


class ProblemCategory(StrEnum):
    """What kind of problem it is, in the learner's words rather than a linguist's."""

    WRONG_TRANSLATION = "wrong_translation"
    UNNATURAL = "unnatural"
    GRAMMAR = "grammar"
    MUTATION = "mutation"
    SPELLING_OR_PUNCTUATION = "spelling_or_punctuation"
    NOT_SOUTH_WALES = "not_south_wales"
    SOUNDS_WRONG = "sounds_wrong"
    AUDIO_BROKEN = "audio_broken"
    ENGLISH_WORDING = "english_wording"
    OTHER = "other"


class ProblemReportRequest(BaseModel):
    """A learner's report. ``exercise_id`` and ``item_id`` are both left out for a problem that is not about one sentence or word."""

    source: ProblemSource
    category: ProblemCategory
    exercise_id: str | None = None
    item_id: str | None = None
    description: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, min_length=1, max_length=DESCRIPTION_MAXIMUM_LENGTH
        ),
    ]

    @model_validator(mode="after")
    def _about_one_subject_at_most(self) -> Self:
        if self.exercise_id is not None and self.item_id is not None:
            raise ValueError("A report is about a sentence or a word, not both")

        return self

import uuid
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from api.schemas.audio import AudioLinks


class ExercisePurpose(StrEnum):
    """Why an exercise was chosen."""

    LEARNING_DUE = "learning_due"
    REVIEW_DUE = "review_due"
    INTRODUCTION = "introduction"
    PRACTICE = "practice"


class ExerciseResponse(BaseModel):
    """An exercise to do. Quote ``selection_id`` back when reporting the outcome.

    ``exercise_id`` is the exercise itself, which a problem report names.
    """

    kind: Literal["exercise"] = "exercise"
    selection_id: uuid.UUID
    exercise_id: str
    english: str
    welsh: str
    audio: AudioLinks
    item_ids: tuple[str, ...]
    introduces: str | None
    purpose: ExercisePurpose


class NothingEligibleResponse(BaseModel):
    """There is no exercise to give: the course has a gap or is empty."""

    kind: Literal["nothing_eligible"] = "nothing_eligible"


type NextExerciseResponse = Annotated[
    ExerciseResponse | NothingEligibleResponse, Field(discriminator="kind")
]

import uuid
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ExercisePurpose(StrEnum):
    """Why an exercise was chosen."""

    LEARNING_DUE = "learning_due"
    REVIEW_DUE = "review_due"
    INTRODUCTION = "introduction"
    PRACTICE = "practice"


class NothingEligibleReason(StrEnum):
    """Why there is nothing to give the learner."""

    ERROR_RATE_TOO_HIGH = "error_rate_too_high"
    NEW_ITEM_LIMIT_REACHED = "new_item_limit_reached"
    NO_EXERCISE_INTRODUCES_FRONTIER = "no_exercise_introduces_frontier"
    NOTHING_ELIGIBLE = "nothing_eligible"


class ExerciseResponse(BaseModel):
    """An exercise to do. Quote ``selection_id`` back when reporting the outcome."""

    kind: Literal["exercise"] = "exercise"
    selection_id: uuid.UUID
    english: str
    welsh: str
    item_ids: tuple[str, ...]
    introduces: str | None
    purpose: ExercisePurpose


class NothingEligibleResponse(BaseModel):
    """There is no exercise to give right now, and why."""

    kind: Literal["nothing_eligible"] = "nothing_eligible"
    reason: NothingEligibleReason


type NextExerciseResponse = Annotated[
    ExerciseResponse | NothingEligibleResponse, Field(discriminator="kind")
]

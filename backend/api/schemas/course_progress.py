from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from api.schemas.learning_session import ItemResponse, SentenceResponse


class ItemKind(StrEnum):
    """A single word, or a way of saying things with a slot to fill."""

    WORD = "word"
    PHRASE = "phrase"


class TopicProgressResponse(BaseModel):
    """What the learner has met in one topic.

    A topic that has not been started has no words, phrases or sentences. The
    sentences are some the learner has got right.
    """

    name: str
    started: bool
    is_current: bool
    exercises_answered: int
    words: tuple[ItemResponse, ...]
    phrases: tuple[ItemResponse, ...]
    sayable: tuple[SentenceResponse, ...]


class CourseProgressResponse(BaseModel):
    """Every topic in the order it is taught."""

    topics: tuple[TopicProgressResponse, ...]


class ItemDetailResponse(BaseModel):
    """An item the learner has met, with sentences they got right.

    ``audio`` is where to hear a word, and is null for a phrase, whose sentences
    carry the audio instead.
    """

    id: str
    kind: ItemKind
    welsh: str
    english: str
    topic: str
    forms: tuple[str, ...]
    notes: str
    first_met_at: datetime
    audio: str | None
    examples: tuple[SentenceResponse, ...]

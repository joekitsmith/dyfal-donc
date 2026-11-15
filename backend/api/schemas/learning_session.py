from datetime import datetime

from pydantic import BaseModel

from api.schemas.audio import AudioLinks


class ItemResponse(BaseModel):
    """A word or pattern the learner met, in both languages."""

    id: str
    welsh: str
    english: str
    forms: tuple[str, ...]


class SentenceResponse(BaseModel):
    """An exercise as a sentence in both languages, with its audio."""

    id: str
    english: str
    welsh: str
    audio: AudioLinks


class SessionRecapResponse(BaseModel):
    """A short account of one learning session.

    ``id`` is the number of the session's first answer in the learner's log, and
    ``ongoing`` says the last answer was recent enough that it may carry on.
    """

    id: int
    started_at: datetime
    ended_at: datetime
    duration_seconds: int
    ongoing: bool
    exercises_completed: int
    items_introduced: tuple[ItemResponse, ...]


class SessionSummaryResponse(SessionRecapResponse):
    """All of a learning session: the recap, and what was reviewed, forgotten and missed."""

    items_reviewed: int
    items_lapsed: tuple[ItemResponse, ...]
    missed_exercises: tuple[SentenceResponse, ...]


class OverviewResponse(BaseModel):
    """What the home screen shows, as of ``now`` on the server's clock.

    ``new_words_ready`` says the course has more words to introduce. The scheduler may
    still slow them down after recent misses. ``topic`` is the topic the next new word
    belongs to, and is null when the course is finished.
    """

    now: datetime
    review_due: int
    learning_due: int
    new_words_ready: bool
    topic: str | None
    introduced: int
    course_items: int
    latest_session: SessionRecapResponse | None

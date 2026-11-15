from enum import StrEnum

from pydantic import BaseModel


class AudioTrack(StrEnum):
    """What can be heard for an exercise: the English prompt, then the Welsh twice."""

    ENGLISH = "english"
    WELSH = "welsh"
    WELSH_SLOW = "welsh-slow"


class AudioLinks(BaseModel):
    """Where to fetch each track of an exercise, as paths on this API."""

    english: str
    welsh: str
    welsh_slow: str

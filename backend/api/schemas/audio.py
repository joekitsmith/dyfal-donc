from enum import StrEnum

from pydantic import BaseModel


class AudioTrack(StrEnum):
    """What can be heard for an exercise, as the speech service names it."""

    ENGLISH = "english"
    WELSH_STANDARD = "welsh-standard"
    WELSH_SLOW = "welsh-slow"


class WelshPace(StrEnum):
    """How fast the Welsh is spoken: by a woman at a standard pace, or by a man slowly."""

    STANDARD = "standard"
    SLOW = "slow"


class WelshAudioLinks(BaseModel):
    standard: str
    slow: str


class AudioLinks(BaseModel):
    """Where to fetch each track of an exercise, as paths on this API."""

    english: str
    welsh: WelshAudioLinks

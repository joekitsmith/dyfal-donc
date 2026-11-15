from enum import StrEnum


class Track(StrEnum):
    """What can be spoken: the English prompt, then the Welsh answer twice."""

    ENGLISH = "english"
    WELSH = "welsh"
    WELSH_SLOW = "welsh-slow"

from enum import StrEnum


class Track(StrEnum):
    """What can be spoken: the English prompt, then the Welsh answer at a standard pace, then slowly."""

    ENGLISH = "english"
    WELSH_STANDARD = "welsh-standard"
    WELSH_SLOW = "welsh-slow"

from enum import StrEnum

from pydantic import BaseModel, Field

THINK_TIME_MULTIPLIER_MINIMUM = 0.5
THINK_TIME_MULTIPLIER_MAXIMUM = 3.0


class WelshPlayback(StrEnum):
    STANDARD = "standard"
    SLOW = "slow"
    BOTH = "both"


class UserSettingsResponse(BaseModel):
    """The settings in force. A user has ``DEFAULT_USER_SETTINGS`` until they save some.

    ``welsh_playback`` is which Welsh recordings play: the woman's at a standard pace,
    the man's slowly, or hers and then his.
    """

    think_time_multiplier: float = Field(
        ge=THINK_TIME_MULTIPLIER_MINIMUM, le=THINK_TIME_MULTIPLIER_MAXIMUM
    )
    welsh_playback: WelshPlayback


DEFAULT_USER_SETTINGS = UserSettingsResponse(
    think_time_multiplier=1.0, welsh_playback=WelshPlayback.BOTH
)


class UserSettingsPatch(BaseModel):
    """Settings to change. A field that is left out stays as it is."""

    think_time_multiplier: float = Field(
        default=DEFAULT_USER_SETTINGS.think_time_multiplier,
        ge=THINK_TIME_MULTIPLIER_MINIMUM,
        le=THINK_TIME_MULTIPLIER_MAXIMUM,
    )
    welsh_playback: WelshPlayback = DEFAULT_USER_SETTINGS.welsh_playback

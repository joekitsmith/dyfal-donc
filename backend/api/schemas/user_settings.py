from typing import Literal

from pydantic import BaseModel, Field

THINK_TIME_MULTIPLIER_MINIMUM = 0.5
THINK_TIME_MULTIPLIER_MAXIMUM = 3.0

type LearningSessionMinutes = Literal[10, 20, 30]


class UserSettingsResponse(BaseModel):
    """The settings in force. A user has ``DEFAULT_USER_SETTINGS`` until they save some."""

    think_time_multiplier: float = Field(
        ge=THINK_TIME_MULTIPLIER_MINIMUM, le=THINK_TIME_MULTIPLIER_MAXIMUM
    )
    slow_welsh_enabled: bool
    learning_session_minutes: LearningSessionMinutes | None


DEFAULT_USER_SETTINGS = UserSettingsResponse(
    think_time_multiplier=1.0, slow_welsh_enabled=True, learning_session_minutes=20
)


class UserSettingsPatch(BaseModel):
    """Settings to change. A field that is left out stays as it is.

    ``learning_session_minutes`` of null is a change, to no limit.
    """

    think_time_multiplier: float = Field(
        default=DEFAULT_USER_SETTINGS.think_time_multiplier,
        ge=THINK_TIME_MULTIPLIER_MINIMUM,
        le=THINK_TIME_MULTIPLIER_MAXIMUM,
    )
    slow_welsh_enabled: bool = DEFAULT_USER_SETTINGS.slow_welsh_enabled
    learning_session_minutes: LearningSessionMinutes | None = (
        DEFAULT_USER_SETTINGS.learning_session_minutes
    )

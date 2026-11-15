import uuid
from datetime import datetime

from api.schemas import DEFAULT_USER_SETTINGS, UserSettingsPatch, UserSettingsResponse
from persistence.database import SaveUserSettings, UserSettingsRecord


def to_user_settings_response(
    record: UserSettingsRecord | None,
) -> UserSettingsResponse:
    """The saved settings, or the defaults if there are none."""
    if record is None:
        return DEFAULT_USER_SETTINGS

    return UserSettingsResponse.model_validate(
        {
            "think_time_multiplier": record.think_time_multiplier,
            "slow_welsh_enabled": record.slow_welsh_enabled,
            "learning_session_minutes": record.learning_session_minutes,
        }
    )


def apply_user_settings_patch(
    current: UserSettingsResponse, patch: UserSettingsPatch
) -> UserSettingsResponse:
    """The current settings with just the fields the patch names changed."""
    return current.model_copy(update=patch.model_dump(exclude_unset=True))


def to_save_user_settings(
    user_id: uuid.UUID, settings: UserSettingsResponse, now: datetime
) -> SaveUserSettings:
    return SaveUserSettings(
        user_id=user_id,
        think_time_multiplier=settings.think_time_multiplier,
        slow_welsh_enabled=settings.slow_welsh_enabled,
        learning_session_minutes=settings.learning_session_minutes,
        updated_at=now,
    )

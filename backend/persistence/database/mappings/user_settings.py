from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import UserSettingsRecord


def to_user_settings_record(row: models.UserSettings) -> UserSettingsRecord:
    return UserSettingsRecord(
        user_id=row.user_id,
        think_time_multiplier=row.think_time_multiplier,
        welsh_playback=row.welsh_playback,
        updated_at=to_utc(row.updated_at),
    )

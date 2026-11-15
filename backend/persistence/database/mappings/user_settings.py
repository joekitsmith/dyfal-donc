from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import UserSettingsRecord


def to_user_settings_record(row: models.UserSettings) -> UserSettingsRecord:
    return UserSettingsRecord(
        user_id=row.user_id,
        think_time_multiplier=row.think_time_multiplier,
        slow_welsh_enabled=row.slow_welsh_enabled,
        learning_session_minutes=row.learning_session_minutes,
        updated_at=to_utc(row.updated_at),
    )

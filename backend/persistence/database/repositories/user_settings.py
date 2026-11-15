import uuid

from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.commands import SaveUserSettings
from persistence.database.mappings import to_user_settings_record
from persistence.database.records import UserSettingsRecord


class UserSettingsRepository:
    """Users' saved settings. Repositories never commit."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: uuid.UUID) -> UserSettingsRecord | None:
        """The user's settings, or None if they have never saved any."""
        row = self._session.get(models.UserSettings, user_id)
        return None if row is None else to_user_settings_record(row)

    def save(self, command: SaveUserSettings) -> UserSettingsRecord:
        row = self._session.get(models.UserSettings, command.user_id)
        if row is None:
            row = models.UserSettings(user_id=command.user_id)
            self._session.add(row)

        row.think_time_multiplier = command.think_time_multiplier
        row.slow_welsh_enabled = command.slow_welsh_enabled
        row.learning_session_minutes = command.learning_session_minutes
        row.updated_at = command.updated_at
        self._session.flush()
        return to_user_settings_record(row)

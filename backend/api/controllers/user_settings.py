import uuid
from datetime import datetime

from api.mappings import (
    apply_user_settings_patch,
    to_save_user_settings,
    to_user_settings_response,
)
from api.schemas import UserSettingsPatch, UserSettingsResponse
from persistence.database import UnitOfWork


def describe_user_settings(
    unit_of_work: UnitOfWork, user_id: uuid.UUID
) -> UserSettingsResponse:
    return to_user_settings_response(unit_of_work.user_settings.get(user_id))


def change_user_settings(
    unit_of_work: UnitOfWork,
    user_id: uuid.UUID,
    patch: UserSettingsPatch,
    now: datetime,
) -> UserSettingsResponse:
    """Change the fields the patch names. The first change saves the defaults for the rest."""
    changed = apply_user_settings_patch(
        describe_user_settings(unit_of_work, user_id), patch
    )
    unit_of_work.user_settings.save(to_save_user_settings(user_id, changed, now))
    unit_of_work.commit()
    return changed

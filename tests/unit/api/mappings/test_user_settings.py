import uuid
from datetime import UTC, datetime
import pytest
from pydantic import ValidationError

from api.mappings import (
    apply_user_settings_patch,
    to_save_user_settings,
    to_user_settings_response,
)
from api.schemas import DEFAULT_USER_SETTINGS, UserSettingsPatch
from persistence.database import UserSettingsRecord

MOMENT = datetime(2026, 1, 1, tzinfo=UTC)


class TestToUserSettingsResponse:
    def test_no_record_gives_the_defaults(self) -> None:
        assert to_user_settings_response(None) == DEFAULT_USER_SETTINGS

    def test_a_record_gives_its_values(self) -> None:
        record = UserSettingsRecord(
            user_id=uuid.uuid4(),
            think_time_multiplier=2.0,
            slow_welsh_enabled=False,
            learning_session_minutes=None,
            updated_at=MOMENT,
        )

        response = to_user_settings_response(record)

        assert response.model_dump() == {
            "think_time_multiplier": 2.0,
            "slow_welsh_enabled": False,
            "learning_session_minutes": None,
        }


class TestApplyUserSettingsPatch:
    def test_only_the_fields_that_were_sent_change(self) -> None:
        current = DEFAULT_USER_SETTINGS.model_copy(update={"slow_welsh_enabled": False})

        changed = apply_user_settings_patch(
            current, UserSettingsPatch.model_validate({"think_time_multiplier": 2})
        )

        assert changed.think_time_multiplier == 2
        assert changed.slow_welsh_enabled is False

    def test_a_sent_null_for_minutes_is_a_change(self) -> None:
        changed = apply_user_settings_patch(
            DEFAULT_USER_SETTINGS,
            UserSettingsPatch.model_validate({"learning_session_minutes": None}),
        )

        assert changed.learning_session_minutes is None

    def test_a_null_for_a_setting_that_cannot_be_null_is_refused(self) -> None:
        with pytest.raises(ValidationError):
            UserSettingsPatch.model_validate({"slow_welsh_enabled": None})


class TestToSaveUserSettings:
    def test_carries_every_setting(self) -> None:
        user_id = uuid.uuid4()

        command = to_save_user_settings(user_id, DEFAULT_USER_SETTINGS, MOMENT)

        assert (command.user_id, command.updated_at) == (user_id, MOMENT)
        assert command.learning_session_minutes == 20

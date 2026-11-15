import uuid
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from api.mappings import (
    apply_user_settings_patch,
    to_save_user_settings,
    to_user_settings_response,
)
from api.schemas import DEFAULT_USER_SETTINGS, UserSettingsPatch, WelshPlayback
from persistence.database import UserSettingsRecord
from persistence.database.models import WELSH_PLAYBACKS

MOMENT = datetime(2026, 1, 1, tzinfo=UTC)


class TestToUserSettingsResponse:
    def test_no_record_gives_the_defaults(self) -> None:
        assert to_user_settings_response(None) == DEFAULT_USER_SETTINGS

    def test_a_record_gives_its_values(self) -> None:
        record = UserSettingsRecord(
            user_id=uuid.uuid4(),
            think_time_multiplier=2.0,
            welsh_playback="slow",
            updated_at=MOMENT,
        )

        response = to_user_settings_response(record)

        assert response.model_dump() == {
            "think_time_multiplier": 2.0,
            "welsh_playback": WelshPlayback.SLOW,
        }


class TestApplyUserSettingsPatch:
    def test_only_the_fields_that_were_sent_change(self) -> None:
        current = DEFAULT_USER_SETTINGS.model_copy(
            update={"welsh_playback": WelshPlayback.SLOW}
        )

        changed = apply_user_settings_patch(
            current, UserSettingsPatch.model_validate({"think_time_multiplier": 2})
        )

        assert changed.think_time_multiplier == 2
        assert changed.welsh_playback == WelshPlayback.SLOW

    def test_a_null_is_refused(self) -> None:
        with pytest.raises(ValidationError):
            UserSettingsPatch.model_validate({"welsh_playback": None})


class TestToSaveUserSettings:
    def test_carries_every_setting(self) -> None:
        user_id = uuid.uuid4()

        command = to_save_user_settings(user_id, DEFAULT_USER_SETTINGS, MOMENT)

        assert (command.user_id, command.updated_at) == (user_id, MOMENT)
        assert command.welsh_playback == DEFAULT_USER_SETTINGS.welsh_playback


def test_the_api_and_the_database_agree_on_the_playbacks() -> None:
    assert {playback.value for playback in WelshPlayback} == set(WELSH_PLAYBACKS)

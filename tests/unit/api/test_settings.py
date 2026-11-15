from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from api.settings import (
    DEFAULT_CURRICULUM_DIRECTORY,
    DEFAULT_TTS_URL,
    LoginSessionSettings,
    PasskeySettings,
    Settings,
)


@pytest.mark.usefixtures("database_url")
class TestSettings:
    def test_defaults_to_the_repository_curriculum(self) -> None:
        assert (DEFAULT_CURRICULUM_DIRECTORY / "topics.yaml").is_file()

    def test_a_selection_lasts_an_hour_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("SELECTION_LIFETIME_SECONDS", raising=False)

        assert Settings().selection_lifetime == timedelta(hours=1)

    def test_the_selection_lifetime_is_read_in_seconds(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SELECTION_LIFETIME_SECONDS", "90")

        assert Settings().selection_lifetime == timedelta(seconds=90)

    def test_the_selection_lifetime_must_be_positive(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SELECTION_LIFETIME_SECONDS", "0")

        with pytest.raises(ValidationError, match="selection_lifetime_seconds"):
            Settings()

    def test_the_speech_service_is_local_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("TTS_URL", raising=False)

        assert Settings().tts_url == DEFAULT_TTS_URL

    def test_the_speech_timeout_must_be_positive(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("TTS_TIMEOUT_SECONDS", "0")

        with pytest.raises(ValidationError, match="tts_timeout_seconds"):
            Settings()

    def test_reads_the_environment(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("CURRICULUM_DIRECTORY", str(tmp_path))
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://other/db")
        monkeypatch.setenv("TTS_URL", "http://tts:8001")

        settings = Settings()

        assert settings.curriculum_directory == tmp_path
        assert settings.database.url == "postgresql+psycopg://other/db"
        assert settings.tts_url == "http://tts:8001"

    def test_the_passkey_and_login_session_settings_are_included(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("WEBAUTHN_RP_ID", "example.org")
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")

        settings = Settings()

        assert settings.passkeys.rp_id == "example.org"
        assert not settings.login_session.cookie_secure


class TestPasskeySettings:
    def test_suits_local_development_by_default(self) -> None:
        settings = PasskeySettings(_env_file=None)

        assert settings.rp_id == "localhost"
        assert settings.rp_name == "dyfal-donc"
        assert settings.origins == ("http://localhost:8080", "http://localhost:3000")

    def test_reads_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEBAUTHN_RP_ID", "example.org")
        monkeypatch.setenv("WEBAUTHN_RP_NAME", "Example")
        monkeypatch.setenv(
            "WEBAUTHN_ORIGINS", "https://example.org, https://www.example.org"
        )

        settings = PasskeySettings(_env_file=None)

        assert settings.rp_id == "example.org"
        assert settings.rp_name == "Example"
        assert settings.origins == ("https://example.org", "https://www.example.org")

    def test_needs_at_least_one_origin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("WEBAUTHN_ORIGINS", " , ")

        with pytest.raises(ValidationError):
            PasskeySettings(_env_file=None)


class TestLoginSessionSettings:
    def test_the_cookie_is_secure_by_default(self) -> None:
        assert LoginSessionSettings(_env_file=None).cookie_secure

    def test_an_account_stays_signed_in_a_day_and_a_guest_thirty(self) -> None:
        settings = LoginSessionSettings(_env_file=None)

        assert settings.lifetime_for(is_guest=False) == timedelta(days=1)
        assert settings.lifetime_for(is_guest=True) == timedelta(days=30)

    def test_an_account_session_ends_after_thirty_days_and_changes_need_a_recent_sign_in(
        self,
    ) -> None:
        settings = LoginSessionSettings(_env_file=None)

        assert settings.max_age == timedelta(days=30)
        assert settings.recent_sign_in == timedelta(minutes=10)

    def test_reads_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        monkeypatch.setenv("SESSION_LIFETIME_SECONDS", "60")
        monkeypatch.setenv("SESSION_GUEST_LIFETIME_SECONDS", "120")

        settings = LoginSessionSettings(_env_file=None)

        assert not settings.cookie_secure
        assert settings.lifetime_for(is_guest=False) == timedelta(minutes=1)
        assert settings.lifetime_for(is_guest=True) == timedelta(minutes=2)

    @pytest.mark.parametrize(
        "name",
        (
            "SESSION_LIFETIME_SECONDS",
            "SESSION_GUEST_LIFETIME_SECONDS",
            "SESSION_MAX_AGE_SECONDS",
            "SESSION_RECENT_SIGN_IN_SECONDS",
        ),
    )
    def test_the_lifetimes_must_be_positive(
        self, monkeypatch: pytest.MonkeyPatch, name: str
    ) -> None:
        monkeypatch.setenv(name, "0")

        with pytest.raises(ValidationError):
            LoginSessionSettings(_env_file=None)

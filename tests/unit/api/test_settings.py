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
    def test_the_cookie_is_secure_and_lasts_thirty_days_by_default(self) -> None:
        settings = LoginSessionSettings(_env_file=None)

        assert settings.cookie_secure
        assert settings.lifetime == timedelta(days=30)

    def test_reads_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
        monkeypatch.setenv("SESSION_LIFETIME_SECONDS", "60")

        settings = LoginSessionSettings(_env_file=None)

        assert not settings.cookie_secure
        assert settings.lifetime == timedelta(minutes=1)

    def test_the_lifetime_must_be_positive(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SESSION_LIFETIME_SECONDS", "0")

        with pytest.raises(ValidationError):
            LoginSessionSettings(_env_file=None)

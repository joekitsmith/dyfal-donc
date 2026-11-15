from datetime import timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from api.settings import DEFAULT_CURRICULUM_DIRECTORY, DEFAULT_TTS_URL, Settings


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

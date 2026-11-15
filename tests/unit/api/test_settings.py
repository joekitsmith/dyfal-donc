from pathlib import Path

import pytest

from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings


class TestSettings:
    def test_defaults_to_the_repository_curriculum(self) -> None:
        assert (DEFAULT_CURRICULUM_DIRECTORY / "topics.yaml").is_file()

    def test_reads_the_environment(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("CURRICULUM_DIRECTORY", str(tmp_path))
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://other/db")

        settings = Settings()

        assert settings.curriculum_directory == tmp_path
        assert settings.database.url == "postgresql+psycopg://other/db"

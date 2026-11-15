from pathlib import Path

import pytest
from pydantic import ValidationError

from persistence.database.settings import DatabaseSettings


class TestDatabaseSettings:
    def test_reads_database_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://other/db")

        assert DatabaseSettings().url == "postgresql+psycopg://other/db"

    def test_the_url_is_required(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("DATABASE_URL", raising=False)

        with pytest.raises(ValidationError, match="url"):
            DatabaseSettings(_env_file=None)

    def test_reads_the_env_file_and_ignores_other_variables_in_it(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.delenv("DATABASE_URL", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("DATABASE_URL=postgresql+psycopg://file/db\nOTHER=1\n")

        assert (
            DatabaseSettings(_env_file=env_file).url == "postgresql+psycopg://file/db"
        )

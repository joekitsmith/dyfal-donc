from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings
from persistence.database import DatabaseSettings


@pytest.fixture
def database_url(monkeypatch: pytest.MonkeyPatch) -> str:
    url = "postgresql+psycopg://test@unreachable/db"
    monkeypatch.setenv("DATABASE_URL", url)
    return url


@pytest.fixture(scope="session")
def curriculum_directory() -> Path:
    return DEFAULT_CURRICULUM_DIRECTORY


@pytest.fixture(scope="session")
def client(curriculum_directory: Path) -> Iterator[TestClient]:
    app = create_app(
        Settings(
            curriculum_directory=curriculum_directory,
            database=DatabaseSettings(url="postgresql+psycopg://test@unreachable/db"),
        )
    )
    with TestClient(app) as test_client:
        yield test_client

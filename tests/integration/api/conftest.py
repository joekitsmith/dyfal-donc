from collections.abc import Iterator
from pathlib import Path
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from api.app import create_app
from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings
from persistence.database import DatabaseSettings

START = datetime(2026, 1, 1, 9, tzinfo=UTC)


class FakeClock:
    """A clock that only moves when the test says so."""

    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: float) -> None:
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def client(engine: Engine, clock: FakeClock) -> Iterator[TestClient]:
    settings = Settings(
        curriculum_directory=DEFAULT_CURRICULUM_DIRECTORY,
        database=DatabaseSettings(url=engine.url.render_as_string(hide_password=False)),
    )
    with TestClient(create_app(settings, clock)) as test_client:
        yield test_client


@pytest.fixture
def course_without_exercises(tmp_path: Path) -> Path:
    """A one-word course with no exercises, so there is never anything to offer."""
    (tmp_path / "patterns").mkdir()
    (tmp_path / "lexemes").mkdir()
    (tmp_path / "order").mkdir()
    (tmp_path / "exercises").mkdir()
    (tmp_path / "patterns" / "spine.yaml").write_text("[]\n", encoding="utf-8")
    (tmp_path / "lexemes" / "spine.yaml").write_text(
        "- id: lex:siarad\n  welsh: siarad\n  english: to speak\n  part_of_speech: verb\n",
        encoding="utf-8",
    )
    (tmp_path / "order" / "spine.yaml").write_text("- lex:siarad\n", encoding="utf-8")
    (tmp_path / "topics.yaml").write_text("- name: spine\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def client_without_exercises(
    engine: Engine, clock: FakeClock, course_without_exercises: Path
) -> Iterator[TestClient]:
    settings = Settings(
        curriculum_directory=course_without_exercises,
        database=DatabaseSettings(url=engine.url.render_as_string(hide_password=False)),
    )
    with TestClient(create_app(settings, clock)) as test_client:
        yield test_client

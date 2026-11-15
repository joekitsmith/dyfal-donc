from collections.abc import Callable, Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from api.app import create_app
from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings
from api.settings import LoginSessionSettings, PasskeySettings
from persistence.database import DatabaseSettings
from tests.support.authenticator import SoftwareAuthenticator

START = datetime(2026, 1, 1, 9, tzinfo=UTC)
ORIGIN = "http://localhost:8080"


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


def build_app(engine: Engine, clock: FakeClock, curriculum_directory: Path) -> FastAPI:
    return create_app(
        Settings(
            curriculum_directory=curriculum_directory,
            database=DatabaseSettings(
                url=engine.url.render_as_string(hide_password=False)
            ),
            passkeys=PasskeySettings(_env_file=None),
            login_session=LoginSessionSettings(cookie_secure=False, _env_file=None),
        ),
        clock,
    )


@pytest.fixture
def app(engine: Engine, clock: FakeClock) -> Iterator[FastAPI]:
    application = build_app(engine, clock, DEFAULT_CURRICULUM_DIRECTORY)
    with TestClient(application):
        yield application


@pytest.fixture
def make_client(app: FastAPI) -> Callable[[], TestClient]:
    """Makes browsers: each has its own cookies and sends the app's own Origin."""

    def make() -> TestClient:
        return TestClient(app, headers={"Origin": ORIGIN})

    return make


@pytest.fixture
def client(make_client: Callable[[], TestClient]) -> TestClient:
    return make_client()


@pytest.fixture
def authenticator() -> SoftwareAuthenticator:
    return SoftwareAuthenticator()


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
    application = build_app(engine, clock, course_without_exercises)
    with TestClient(application, headers={"Origin": ORIGIN}) as test_client:
        yield test_client

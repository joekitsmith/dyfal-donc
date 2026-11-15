from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import create_app
from api.errors import SpeechUnavailableError
from api.schemas import AudioTrack
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


class FakeSpeechClient:
    """Answers with the text and track it was asked for, or fails when told to."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, AudioTrack]] = []
        self.unavailable = False

    def synthesise(self, text: str, track: AudioTrack) -> bytes:
        if self.unavailable:
            raise SpeechUnavailableError("Speech synthesis is unavailable")

        self.calls.append((text, track))
        return b"RIFF" + f"{track.value}:{text}".encode()


@pytest.fixture
def speech_client() -> FakeSpeechClient:
    return FakeSpeechClient()


@pytest.fixture
def audio_client(
    curriculum_directory: Path, speech_client: FakeSpeechClient
) -> Iterator[TestClient]:
    app = create_app(
        Settings(
            curriculum_directory=curriculum_directory,
            database=DatabaseSettings(url="postgresql+psycopg://test@unreachable/db"),
        ),
        speech_client=speech_client,
    )
    with TestClient(app) as test_client:
        yield test_client

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from api.app import create_app
from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings
from persistence.database import DatabaseSettings
from tests.integration.api.conftest import FakeClock
from tests.integration.api.test_learner_loop import create_learner, offer


@pytest.fixture
def client_with_speech(
    engine: Engine, clock: FakeClock, tts_url: str
) -> Iterator[TestClient]:
    settings = Settings(
        curriculum_directory=DEFAULT_CURRICULUM_DIRECTORY,
        database=DatabaseSettings(url=engine.url.render_as_string(hide_password=False)),
        tts_url=tts_url,
    )
    with TestClient(create_app(settings, clock)) as test_client:
        yield test_client


class TestAudioOfTheLearnLoop:
    def test_every_audio_link_of_an_offered_exercise_gives_wav(
        self, client_with_speech: TestClient
    ) -> None:
        body = offer(client_with_speech, create_learner(client_with_speech))
        links = body["audio"]
        assert isinstance(links, dict)

        for track in ("english", "welsh", "welsh_slow"):
            response = client_with_speech.get(str(links[track]))

            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"
            assert response.content.startswith(b"RIFF")
            assert len(response.content) > 1000

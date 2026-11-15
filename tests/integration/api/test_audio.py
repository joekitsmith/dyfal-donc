from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from api.app import create_app
from api.settings import DEFAULT_CURRICULUM_DIRECTORY, Settings
from api.settings import LoginSessionSettings, PasskeySettings
from persistence.database import DatabaseSettings
from tests.integration.api.conftest import ORIGIN, FakeClock
from tests.integration.api.helpers import offer, start_guest


@pytest.fixture
def client_with_speech(
    engine: Engine, clock: FakeClock, tts_url: str
) -> Iterator[TestClient]:
    settings = Settings(
        curriculum_directory=DEFAULT_CURRICULUM_DIRECTORY,
        database=DatabaseSettings(url=engine.url.render_as_string(hide_password=False)),
        tts_url=tts_url,
        passkeys=PasskeySettings(_env_file=None),
        login_session=LoginSessionSettings(cookie_secure=False, _env_file=None),
    )
    with TestClient(
        create_app(settings, clock), headers={"Origin": ORIGIN}
    ) as test_client:
        yield test_client


class TestAudioOfTheLearnLoop:
    def test_every_audio_link_of_an_offered_exercise_gives_wav(
        self, client_with_speech: TestClient
    ) -> None:
        start_guest(client_with_speech)
        body = offer(client_with_speech)
        links = body["audio"]
        assert isinstance(links, dict)

        welsh = links["welsh"]
        assert isinstance(welsh, dict)

        for link in (links["english"], welsh["standard"], welsh["slow"]):
            response = client_with_speech.get(str(link))

            assert response.status_code == 200
            assert response.headers["content-type"] == "audio/wav"
            assert response.content.startswith(b"RIFF")
            assert len(response.content) > 1000

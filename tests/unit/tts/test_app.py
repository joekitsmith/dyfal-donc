from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from tts.app import MAXIMUM_TEXT_LENGTH, create_app
from tts.tracks import Track
from tests.unit.tts.conftest import FakeSynthesiser


@pytest.fixture
def client(synthesiser: FakeSynthesiser) -> Iterator[TestClient]:
    with TestClient(create_app(synthesiser)) as test_client:
        yield test_client


class TestHealth:
    def test_says_it_is_ready(self, client: TestClient) -> None:
        assert client.get("/health").json() == {"status": "ok"}


class TestSynthesise:
    def test_returns_the_audio_as_wav(self, client: TestClient) -> None:
        response = client.post(
            "/synthesise", json={"text": "Galla i fynd", "track": "welsh"}
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"RIFFwelsh:Galla i fynd"

    @pytest.mark.parametrize("track", Track)
    def test_speaks_the_text_on_the_requested_track(
        self, client: TestClient, synthesiser: FakeSynthesiser, track: Track
    ) -> None:
        client.post("/synthesise", json={"text": "Hello", "track": track.value})

        assert synthesiser.calls == [("Hello", track)]

    def test_rejects_an_unknown_track(self, client: TestClient) -> None:
        response = client.post("/synthesise", json={"text": "Hello", "track": "french"})

        assert response.status_code == 422

    def test_rejects_empty_text(self, client: TestClient) -> None:
        response = client.post("/synthesise", json={"text": "", "track": "english"})

        assert response.status_code == 422

    def test_rejects_text_that_is_too_long(self, client: TestClient) -> None:
        text = "a" * (MAXIMUM_TEXT_LENGTH + 1)

        response = client.post("/synthesise", json={"text": text, "track": "english"})

        assert response.status_code == 422

from fastapi.testclient import TestClient

from tests.unit.api.conftest import FakeSpeechClient


class TestAudio:
    def test_returns_the_spoken_exercise_as_wav(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/welsh")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"RIFFwelsh:Galla i fynd"

    def test_serves_all_three_tracks(
        self, audio_client: TestClient, speech_client: FakeSpeechClient
    ) -> None:
        for track in ("english", "welsh", "welsh-slow"):
            assert (
                audio_client.get(f"/exercises/i-can-go/audio/{track}").status_code
                == 200
            )

        assert [text for text, _track in speech_client.calls] == [
            "I can go",
            "Galla i fynd",
            "Galla i fynd",
        ]

    def test_an_unknown_exercise_is_a_404(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/nonsense/audio/english")

        assert response.status_code == 404
        assert "nonsense" in response.json()["detail"]

    def test_an_unknown_track_is_a_422(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/french")

        assert response.status_code == 422

    def test_an_unavailable_speech_service_is_a_503(
        self, audio_client: TestClient, speech_client: FakeSpeechClient
    ) -> None:
        speech_client.unavailable = True

        response = audio_client.get("/exercises/i-can-go/audio/english")

        assert response.status_code == 503
        assert response.json() == {"detail": "Speech synthesis is unavailable"}

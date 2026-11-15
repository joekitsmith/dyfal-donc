from fastapi.testclient import TestClient

from tests.unit.api.conftest import FakeSpeechClient


class TestAudio:
    def test_returns_the_spoken_exercise_as_wav(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/welsh/standard")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"RIFFwelsh-standard:Galla i fynd"

    def test_serves_all_three_tracks(
        self, audio_client: TestClient, speech_client: FakeSpeechClient
    ) -> None:
        for track in ("english", "welsh/standard", "welsh/slow"):
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

    def test_an_unknown_language_is_a_404(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/french")

        assert response.status_code == 404

    def test_an_unknown_pace_is_a_422(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/welsh/medium")

        assert response.status_code == 422

    def test_english_has_no_pace(self, audio_client: TestClient) -> None:
        response = audio_client.get("/exercises/i-can-go/audio/english/slow")

        assert response.status_code == 404

    def test_an_unavailable_speech_service_is_a_503(
        self, audio_client: TestClient, speech_client: FakeSpeechClient
    ) -> None:
        speech_client.unavailable = True

        response = audio_client.get("/exercises/i-can-go/audio/english")

        assert response.status_code == 503
        assert response.json() == {"detail": "Speech synthesis is unavailable"}


class TestItemAudio:
    def test_returns_a_word_at_a_standard_pace_as_wav(
        self, audio_client: TestClient, speech_client: FakeSpeechClient
    ) -> None:
        response = audio_client.get("/items/lex:mynd/audio")

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        assert response.content == b"RIFFwelsh-standard:mynd"
        assert [text for text, _track in speech_client.calls] == ["mynd"]

    def test_a_phrase_has_no_audio(self, audio_client: TestClient) -> None:
        response = audio_client.get("/items/pat:galla-i/audio")

        assert response.status_code == 404

    def test_an_unknown_item_is_a_404(self, audio_client: TestClient) -> None:
        response = audio_client.get("/items/lex:nonsense/audio")

        assert response.status_code == 404

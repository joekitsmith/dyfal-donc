import io
import wave

import httpx2
import pytest

TRACK_TEXT = {
    "english": "I can go",
    "welsh": "Galla i fynd",
    "welsh-slow": "Galla i fynd",
}


def synthesise(url: str, track: str) -> bytes:
    response = httpx2.post(
        f"{url}/synthesise",
        json={"text": TRACK_TEXT[track], "track": track},
        timeout=60,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"
    return response.content


def seconds(wav_bytes: bytes) -> float:
    with wave.open(io.BytesIO(wav_bytes)) as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()


class TestSpeechContainer:
    @pytest.mark.parametrize("track", TRACK_TEXT)
    def test_speaks_each_track_as_wav(self, tts_url: str, track: str) -> None:
        audio = synthesise(tts_url, track)

        assert audio.startswith(b"RIFF")
        assert seconds(audio) > 0.3

    def test_the_slow_welsh_track_takes_longer_than_the_welsh_track(
        self, tts_url: str
    ) -> None:
        assert seconds(synthesise(tts_url, "welsh-slow")) > seconds(
            synthesise(tts_url, "welsh")
        )

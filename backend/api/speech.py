from typing import Protocol

import httpx2

from api.errors import SpeechUnavailableError
from api.schemas import AudioTrack

SYNTHESISE_PATH = "/synthesise"


class SpeechClient(Protocol):
    def synthesise(self, text: str, track: AudioTrack) -> bytes:
        """The text spoken for the track, as a WAV file."""
        ...


class HttpSpeechClient:
    """Asks the ``tts`` service to speak, over HTTP only."""

    def __init__(self, client: httpx2.Client) -> None:
        self._client = client

    def synthesise(self, text: str, track: AudioTrack) -> bytes:
        try:
            response = self._client.post(
                SYNTHESISE_PATH, json={"text": text, "track": track.value}
            )
            response.raise_for_status()
        except httpx2.HTTPError as error:
            raise SpeechUnavailableError("Speech synthesis is unavailable") from error

        return response.content

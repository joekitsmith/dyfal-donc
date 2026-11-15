import json

import httpx2
import pytest

from api.errors import SpeechUnavailableError
from api.schemas import AudioTrack
from api.speech import HttpSpeechClient


def client_answering(handler: httpx2.MockTransport) -> HttpSpeechClient:
    return HttpSpeechClient(httpx2.Client(base_url="http://tts", transport=handler))


class TestHttpSpeechClient:
    def test_asks_the_service_to_speak_the_text_on_the_track(self) -> None:
        requests: list[httpx2.Request] = []

        def handle(request: httpx2.Request) -> httpx2.Response:
            requests.append(request)
            return httpx2.Response(200, content=b"RIFFaudio")

        audio = client_answering(httpx2.MockTransport(handle)).synthesise(
            "Galla i fynd", AudioTrack.WELSH_SLOW
        )

        assert audio == b"RIFFaudio"
        assert requests[0].method == "POST"
        assert str(requests[0].url) == "http://tts/synthesise"
        assert json.loads(requests[0].content) == {
            "text": "Galla i fynd",
            "track": "welsh-slow",
        }

    def test_an_error_from_the_service_means_it_is_unavailable(self) -> None:
        client = client_answering(
            httpx2.MockTransport(lambda _request: httpx2.Response(500))
        )

        with pytest.raises(SpeechUnavailableError):
            client.synthesise("Hello", AudioTrack.ENGLISH)

    def test_not_reaching_the_service_means_it_is_unavailable(self) -> None:
        def refuse(request: httpx2.Request) -> httpx2.Response:
            raise httpx2.ConnectError("Connection refused", request=request)

        client = client_answering(httpx2.MockTransport(refuse))

        with pytest.raises(SpeechUnavailableError):
            client.synthesise("Hello", AudioTrack.ENGLISH)

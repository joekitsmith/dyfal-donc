from typing import Annotated

from fastapi import Depends, Request

from api.speech import SpeechClient


def get_speech_client(request: Request) -> SpeechClient:
    client: SpeechClient = request.app.state.speech_client
    return client


SpeechClientDependency = Annotated[SpeechClient, Depends(get_speech_client)]

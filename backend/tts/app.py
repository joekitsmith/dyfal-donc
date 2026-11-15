from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field

from tts.settings import TtsSettings
from tts.synthesiser import PiperSynthesiser, Synthesiser
from tts.tracks import Track

MAXIMUM_TEXT_LENGTH = 500
WAV_MEDIA_TYPE = "audio/wav"


class SynthesiseRequest(BaseModel):
    text: str = Field(min_length=1, max_length=MAXIMUM_TEXT_LENGTH)
    track: Track


class HealthResponse(BaseModel):
    status: str


def create_app(
    synthesiser: Synthesiser | None = None, settings: TtsSettings | None = None
) -> FastAPI:
    """The speech service. The voices are loaded when it starts.

    ``synthesiser`` replaces Piper, so tests do not need the voice files.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        app.state.synthesiser = synthesiser or PiperSynthesiser(
            (settings or TtsSettings()).models_directory
        )
        yield

    app = FastAPI(title="Dyfal donc speech", lifespan=lifespan)

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/synthesise", responses={200: {"content": {WAV_MEDIA_TYPE: {}}}})
    def synthesise(request: SynthesiseRequest, http_request: Request) -> Response:
        wav = http_request.app.state.synthesiser.synthesise(request.text, request.track)
        return Response(content=wav, media_type=WAV_MEDIA_TYPE)

    return app

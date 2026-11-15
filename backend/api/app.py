from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx2
from fastapi import FastAPI

from api.clock import Clock, system_clock
from api.course import load_course_release
from api.error_handlers import register_error_handlers
from api.routes import (
    account_router,
    audio_router,
    auth_router,
    course_router,
    health_router,
    learners_router,
)
from api.settings import Settings
from api.speech import HttpSpeechClient, SpeechClient
from persistence.database import create_database_engine, create_session_factory


def create_app(
    settings: Settings | None = None,
    clock: Clock = system_clock,
    speech_client: SpeechClient | None = None,
) -> FastAPI:
    """The API. The course is loaded when it starts, the database on first use.

    ``clock`` gives the time every recorded timestamp comes from, so tests can
    control it. ``speech_client`` replaces the real speech service.
    """
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        engine = create_database_engine(app_settings.database.url)
        http_client = httpx2.Client(
            base_url=app_settings.tts_url, timeout=app_settings.tts_timeout_seconds
        )
        app.state.course_release = load_course_release(
            app_settings.curriculum_directory
        )
        app.state.session_factory = create_session_factory(engine)
        app.state.clock = clock
        app.state.selection_lifetime = app_settings.selection_lifetime
        app.state.passkey_settings = app_settings.passkeys
        app.state.login_session_settings = app_settings.login_session
        app.state.speech_client = speech_client or HttpSpeechClient(http_client)
        yield
        http_client.close()
        engine.dispose()

    app = FastAPI(title="Dyfal donc", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(course_router)
    app.include_router(auth_router)
    app.include_router(account_router)
    app.include_router(learners_router)
    app.include_router(audio_router)
    return app

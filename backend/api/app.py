from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.clock import Clock, system_clock
from api.course import load_course_release
from api.error_handlers import register_error_handlers
from api.routes import course_router, health_router, learners_router
from api.settings import Settings
from persistence.database import create_database_engine, create_session_factory


def create_app(
    settings: Settings | None = None, clock: Clock = system_clock
) -> FastAPI:
    """The API. The course is loaded when it starts, the database on first use.

    ``clock`` gives the time every recorded timestamp comes from, so tests can
    control it.
    """
    app_settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        engine = create_database_engine(app_settings.database.url)
        app.state.course_release = load_course_release(
            app_settings.curriculum_directory
        )
        app.state.session_factory = create_session_factory(engine)
        app.state.clock = clock
        app.state.selection_lifetime = app_settings.selection_lifetime
        yield
        engine.dispose()

    app = FastAPI(title="Dyfal donc", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(health_router)
    app.include_router(course_router)
    app.include_router(learners_router)
    return app

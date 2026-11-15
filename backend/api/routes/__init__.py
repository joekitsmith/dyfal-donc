from api.routes.account import router as account_router
from api.routes.audio import router as audio_router
from api.routes.auth import router as auth_router
from api.routes.course import router as course_router
from api.routes.course_progress import router as course_progress_router
from api.routes.health import router as health_router
from api.routes.learners import router as learners_router
from api.routes.learning_sessions import router as learning_sessions_router
from api.routes.overview import router as overview_router
from api.routes.problem_reports import router as problem_reports_router
from api.routes.user_settings import router as user_settings_router

__all__ = [
    "account_router",
    "audio_router",
    "auth_router",
    "course_progress_router",
    "course_router",
    "health_router",
    "learners_router",
    "learning_sessions_router",
    "overview_router",
    "problem_reports_router",
    "user_settings_router",
]

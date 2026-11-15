from api.routes.course import router as course_router
from api.routes.health import router as health_router
from api.routes.learners import router as learners_router

__all__ = ["course_router", "health_router", "learners_router"]

import uuid
from typing import Annotated

from fastapi import Depends, Request, Response

from api.controllers import Authenticated, authenticate
from api.dependencies.clock import ClockDependency
from api.dependencies.database import UnitOfWorkDependency
from api.dependencies.settings import (
    LoginSessionSettingsDependency,
    PasskeySettingsDependency,
)
from api.errors import ForeignOriginError
from api.session_cookie import SESSION_COOKIE_NAME, set_session_cookie
from persistence.database.errors import LearnerNotFoundError

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def get_session_token(request: Request) -> str | None:
    return request.cookies.get(SESSION_COOKIE_NAME)


SessionTokenDependency = Annotated[str | None, Depends(get_session_token)]


def require_known_origin(request: Request, settings: PasskeySettingsDependency) -> None:
    """Refuse a request that changes something unless it came from the app's own address.

    Browsers always send ``Origin`` on these requests, so a missing one is refused too.
    """
    if request.method in SAFE_METHODS:
        return

    if request.headers.get("origin") not in settings.origins:
        raise ForeignOriginError("Origin is not allowed")


def get_authenticated(
    response: Response,
    token: SessionTokenDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    settings: LoginSessionSettingsDependency,
) -> Authenticated:
    """Who is signed in. The cookie is sent again when the session's expiry moves."""
    authenticated = authenticate(unit_of_work, token, clock(), settings.lifetime)
    if authenticated.extended and token is not None:
        set_session_cookie(response, token, settings)

    return authenticated


AuthenticatedDependency = Annotated[Authenticated, Depends(get_authenticated)]


def get_learner_id(
    authenticated: AuthenticatedDependency, unit_of_work: UnitOfWorkDependency
) -> uuid.UUID:
    learner = unit_of_work.learners.for_user(authenticated.user.id)
    if learner is None:
        raise LearnerNotFoundError(f"User {authenticated.user.id} has no learner")

    return learner.id


LearnerIdDependency = Annotated[uuid.UUID, Depends(get_learner_id)]

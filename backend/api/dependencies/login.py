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
from api.errors import ForeignOriginError, RecentSignInRequiredError
from api.login_sessions import signed_in_recently
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
    authenticated = authenticate(unit_of_work, token, clock(), settings)
    if authenticated.extended and token is not None:
        set_session_cookie(
            response, token, settings, is_guest=authenticated.user.is_guest
        )

    return authenticated


AuthenticatedDependency = Annotated[Authenticated, Depends(get_authenticated)]


def get_confirmed(
    authenticated: AuthenticatedDependency,
    clock: ClockDependency,
    settings: LoginSessionSettingsDependency,
) -> Authenticated:
    """Who is signed in, for something that changes the account.

    An account must have proved who they are recently, so a stolen session
    cannot add its own passkey or delete the account. A guest has nothing to
    prove it with but the session.
    """
    if not authenticated.user.is_guest and not signed_in_recently(
        authenticated.login_session.authenticated_at, clock(), settings.recent_sign_in
    ):
        raise RecentSignInRequiredError("Confirm it is you with your passkey")

    return authenticated


ConfirmedDependency = Annotated[Authenticated, Depends(get_confirmed)]


def get_learner_id(
    authenticated: AuthenticatedDependency, unit_of_work: UnitOfWorkDependency
) -> uuid.UUID:
    learner = unit_of_work.learners.for_user(authenticated.user.id)
    if learner is None:
        raise LearnerNotFoundError(f"User {authenticated.user.id} has no learner")

    return learner.id


LearnerIdDependency = Annotated[uuid.UUID, Depends(get_learner_id)]

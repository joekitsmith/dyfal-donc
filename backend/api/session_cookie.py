from fastapi import Response

from api.settings import LoginSessionSettings

SESSION_COOKIE_NAME = "session"


def set_session_cookie(
    response: Response, token: str, settings: LoginSessionSettings, *, is_guest: bool
) -> None:
    """Send the token, kept by the browser for as long as the session lasts."""
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=int(settings.lifetime_for(is_guest=is_guest).total_seconds()),
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )


def clear_session_cookie(response: Response, settings: LoginSessionSettings) -> None:
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        path="/",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",
    )

from fastapi import Response

from api.session_cookie import clear_session_cookie, set_session_cookie
from api.settings import LoginSessionSettings


def settings(*, secure: bool) -> LoginSessionSettings:
    return LoginSessionSettings(
        cookie_secure=secure, lifetime_seconds=3600, _env_file=None
    )


class TestSetSessionCookie:
    def test_the_cookie_cannot_be_read_by_scripts_or_sent_cross_site(self) -> None:
        response = Response()

        set_session_cookie(response, "token", settings(secure=True))

        cookie = response.headers["set-cookie"].lower()
        assert cookie.startswith("session=token")
        assert "httponly" in cookie
        assert "samesite=lax" in cookie
        assert "secure" in cookie
        assert "path=/" in cookie
        assert "max-age=3600" in cookie

    def test_secure_can_be_turned_off_for_local_http(self) -> None:
        response = Response()

        set_session_cookie(response, "token", settings(secure=False))

        assert "secure" not in response.headers["set-cookie"].lower()


class TestClearSessionCookie:
    def test_expires_the_cookie(self) -> None:
        response = Response()

        clear_session_cookie(response, settings(secure=True))

        cookie = response.headers["set-cookie"].lower()
        assert cookie.startswith("session=")
        assert "max-age=0" in cookie

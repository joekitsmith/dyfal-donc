from datetime import UTC, datetime, timedelta

from api.login_sessions import expiry, is_expired, needs_extending

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)
LIFETIME = timedelta(days=30)


class TestExpiry:
    def test_is_the_lifetime_after_use(self) -> None:
        assert expiry(NOW, LIFETIME) == NOW + LIFETIME


class TestIsExpired:
    def test_a_session_is_live_until_its_expiry(self) -> None:
        expires_at = NOW + LIFETIME

        assert not is_expired(expires_at, expires_at - timedelta(seconds=1))
        assert is_expired(expires_at, expires_at)
        assert is_expired(expires_at, expires_at + timedelta(seconds=1))


class TestNeedsExtending:
    def test_a_recently_seen_session_is_left_alone(self) -> None:
        assert not needs_extending(NOW, NOW + timedelta(minutes=59))

    def test_a_session_not_seen_for_an_hour_is_extended(self) -> None:
        assert needs_extending(NOW, NOW + timedelta(hours=1))

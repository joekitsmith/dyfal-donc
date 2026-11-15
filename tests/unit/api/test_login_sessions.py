from datetime import UTC, datetime, timedelta

from api.login_sessions import (
    expiry,
    is_expired,
    is_past_maximum_age,
    needs_extending,
    signed_in_recently,
)

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


class TestIsPastMaximumAge:
    def test_a_session_is_limited_by_its_age_not_its_use(self) -> None:
        maximum = timedelta(days=30)

        assert not is_past_maximum_age(
            NOW, NOW + maximum - timedelta(seconds=1), maximum
        )
        assert is_past_maximum_age(NOW, NOW + maximum, maximum)


class TestSignedInRecently:
    def test_is_true_only_within_the_window(self) -> None:
        window = timedelta(minutes=10)

        assert signed_in_recently(NOW, NOW + timedelta(minutes=9, seconds=59), window)
        assert not signed_in_recently(NOW, NOW + window, window)

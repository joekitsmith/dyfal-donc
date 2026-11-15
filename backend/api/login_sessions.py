from datetime import datetime, timedelta

EXTEND_INTERVAL = timedelta(hours=1)


def expiry(now: datetime, lifetime: timedelta) -> datetime:
    """When a session used at ``now`` stops working if it is not used again."""
    return now + lifetime


def is_expired(expires_at: datetime, now: datetime) -> bool:
    return now >= expires_at


def needs_extending(last_seen_at: datetime, now: datetime) -> bool:
    """Whether the expiry should move. Doing it once an hour saves a write per request."""
    return now - last_seen_at >= EXTEND_INTERVAL

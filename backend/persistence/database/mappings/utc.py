from datetime import UTC, datetime


def to_utc(moment: datetime) -> datetime:
    """The moment in UTC. The database returns it in the session's time zone."""
    return moment.astimezone(UTC)

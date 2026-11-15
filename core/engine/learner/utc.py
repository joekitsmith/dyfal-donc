from datetime import UTC, datetime, timedelta

from engine.learner.errors import LearnerError


def require_utc(moment: datetime, name: str) -> None:
    """Raise unless the moment is timezone-aware and in UTC."""
    offset = moment.utcoffset()
    if offset is None:
        raise LearnerError(f"{name} must be timezone-aware")

    if offset != timedelta(0):
        raise LearnerError(f"{name} must be in UTC")


def as_utc(moment: datetime, name: str) -> datetime:
    """The moment as a standard-library UTC datetime, after checking it is UTC."""
    require_utc(moment, name)
    return moment.astimezone(UTC)

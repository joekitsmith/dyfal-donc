from collections.abc import Callable
from datetime import UTC, datetime

type Clock = Callable[[], datetime]


def system_clock() -> datetime:
    """The current time in UTC. Every timestamp the server records comes from here."""
    return datetime.now(UTC)

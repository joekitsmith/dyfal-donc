from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AddUser:
    """Add a user, who is a guest until a passkey is added."""

    display_name: str | None = None

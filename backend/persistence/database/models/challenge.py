import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.models.base import Base

CHALLENGE_PURPOSES = ("registration", "authentication")


class WebauthnChallenge(Base):
    """A challenge given to a browser for one passkey ceremony.

    It is deleted when used, so it works once. A registration challenge belongs
    to the user registering, and an authentication one has no user yet.
    """

    __tablename__ = "webauthn_challenges"
    __table_args__ = (
        CheckConstraint(
            "purpose IN ({})".format(", ".join(f"'{p}'" for p in CHALLENGE_PURPOSES)),
            name="purpose_known",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    challenge: Mapped[bytes] = mapped_column(LargeBinary, unique=True)
    purpose: Mapped[str] = mapped_column(String(16))
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

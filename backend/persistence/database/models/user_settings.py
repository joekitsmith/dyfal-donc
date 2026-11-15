import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.models.base import Base

WELSH_PLAYBACKS = ("standard", "slow", "both")


class UserSettings(Base):
    """A user's settings. The row is made the first time they save any.

    Which defaults apply until then is the caller's business.
    """

    __tablename__ = "user_settings"
    __table_args__ = (
        CheckConstraint(
            "welsh_playback IN ({})".format(
                ", ".join(f"'{playback}'" for playback in WELSH_PLAYBACKS)
            ),
            name="welsh_playback_known",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    think_time_multiplier: Mapped[float]
    welsh_playback: Mapped[str] = mapped_column(String(8))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

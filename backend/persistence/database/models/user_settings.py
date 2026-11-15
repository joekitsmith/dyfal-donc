import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.models.base import Base


class UserSettings(Base):
    """A user's settings. The row is made the first time they save any.

    Which defaults apply until then is the caller's business.
    """

    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    think_time_multiplier: Mapped[float]
    slow_welsh_enabled: Mapped[bool]
    learning_session_minutes: Mapped[int | None]
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.models.base import Base


class IssuedSelection(Base):
    """An exercise the server gave a learner.

    Outcomes are only accepted for selections issued here, so a client cannot
    make up events. ``item_ids`` and ``new_item`` are what is needed to build
    the review event once the outcome is known.
    """

    __tablename__ = "issued_selections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("learners.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[str] = mapped_column(String(128))
    item_ids: Mapped[list[str]] = mapped_column(ARRAY(String(128)))
    new_item: Mapped[str | None] = mapped_column(String(128))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

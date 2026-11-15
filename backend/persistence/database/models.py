import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

OUTCOMES = ("got_it", "missed_it")


class Base(DeclarativeBase):
    """Base of the tables. Timestamps are stored in UTC."""


class Learner(Base):
    """Someone using the course, and the course release they started on."""

    __tablename__ = "learners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    course_release: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class IssuedSelection(Base):
    """An exercise the server gave a learner.

    Outcomes are only accepted for selections issued here, so a client cannot
    make up events. ``item_ids`` and ``new_item`` are what is needed to build
    the review event once the outcome is known.
    """

    __tablename__ = "issued_selections"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learners.id"), index=True)
    exercise_id: Mapped[str] = mapped_column(String(128))
    item_ids: Mapped[list[str]] = mapped_column(ARRAY(String(128)))
    new_item: Mapped[str | None] = mapped_column(String(128))
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReviewEventRecord(Base):
    """One exercise a learner completed. Rows are only ever added.

    ``sequence`` counts a learner's events from 1, so replaying them in
    sequence order is replaying them in the order they happened.
    ``selection_id`` is unique, so an outcome can only be recorded once.
    """

    __tablename__ = "review_events"
    __table_args__ = (
        UniqueConstraint("learner_id", "sequence"),
        CheckConstraint("sequence >= 1", name="sequence_positive"),
        CheckConstraint(
            "outcome IN ({})".format(", ".join(f"'{o}'" for o in OUTCOMES)),
            name="outcome_known",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("learners.id"))
    sequence: Mapped[int]
    selection_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("issued_selections.id"), unique=True
    )
    exercise_id: Mapped[str] = mapped_column(String(128))
    item_ids: Mapped[list[str]] = mapped_column(ARRAY(String(128)))
    new_item: Mapped[str | None] = mapped_column(String(128))
    outcome: Mapped[str] = mapped_column(String(16))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from persistence.database.models.base import Base

PROBLEM_REPORT_SOURCES = ("lesson", "summary", "course", "item", "general")
PROBLEM_REPORT_CATEGORIES = (
    "wrong_translation",
    "unnatural",
    "grammar",
    "mutation",
    "spelling_or_punctuation",
    "not_south_wales",
    "sounds_wrong",
    "audio_broken",
    "english_wording",
    "other",
)


class ProblemReport(Base):
    """A learner's report that something in the course is wrong.

    At most one of ``exercise_id`` and ``item_id`` is set. Neither means the
    problem is not about one sentence or word. ``release_hash`` says which
    version of the course the learner was looking at. ``resolved_at`` is for the
    developer's own triage: the learner never sees it.
    """

    __tablename__ = "problem_reports"
    __table_args__ = (
        CheckConstraint(
            "source IN ({})".format(
                ", ".join(f"'{source}'" for source in PROBLEM_REPORT_SOURCES)
            ),
            name="source_known",
        ),
        CheckConstraint(
            "category IN ({})".format(
                ", ".join(f"'{category}'" for category in PROBLEM_REPORT_CATEGORIES)
            ),
            name="category_known",
        ),
        CheckConstraint(
            "exercise_id IS NULL OR item_id IS NULL", name="one_subject_at_most"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    exercise_id: Mapped[str | None] = mapped_column(String(128))
    item_id: Mapped[str | None] = mapped_column(String(128))
    release_hash: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(16))
    category: Mapped[str] = mapped_column(String(32))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

import uuid

from sqlalchemy.orm import Session

from persistence.database import models
from persistence.database.mappings import to_learner_record
from persistence.database.commands import AddLearner
from persistence.database.records import LearnerRecord


class LearnerRepository:
    """Learners. Repositories never commit: the caller owns the transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, command: AddLearner) -> LearnerRecord:
        row = models.Learner(course_release=command.course_release)
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return to_learner_record(row)

    def get(self, learner_id: uuid.UUID) -> LearnerRecord | None:
        row = self._session.get(models.Learner, learner_id)
        return None if row is None else to_learner_record(row)

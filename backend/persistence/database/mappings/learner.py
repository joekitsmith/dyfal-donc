from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import LearnerRecord


def to_learner_record(row: models.Learner) -> LearnerRecord:
    return LearnerRecord(
        id=row.id,
        course_release=row.course_release,
        created_at=to_utc(row.created_at),
    )

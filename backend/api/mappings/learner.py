from api.course import CourseRelease
from api.schemas import LearnerResponse
from persistence.database import LearnerRecord, AddLearner


def to_add_learner(release: CourseRelease) -> AddLearner:
    return AddLearner(course_release=release.hash)


def to_learner_response(record: LearnerRecord) -> LearnerResponse:
    return LearnerResponse(
        id=record.id,
        course_release=record.course_release,
        created_at=record.created_at,
    )

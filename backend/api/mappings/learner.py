import uuid

from api.course import CourseRelease
from persistence.database import AddLearner


def to_add_learner(user_id: uuid.UUID, release: CourseRelease) -> AddLearner:
    return AddLearner(user_id=user_id, course_release=release.hash)

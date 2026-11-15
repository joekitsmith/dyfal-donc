from api.course import CourseRelease
from api.mappings import to_course_response
from api.schemas import CourseResponse


def describe_course(release: CourseRelease) -> CourseResponse:
    return to_course_response(release)

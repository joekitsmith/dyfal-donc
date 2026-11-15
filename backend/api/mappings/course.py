from api.course import CourseRelease
from api.schemas import CourseResponse, TopicResponse


def to_course_response(release: CourseRelease) -> CourseResponse:
    return CourseResponse(
        release=release.hash,
        item_count=len(release.curriculum.items),
        topics=tuple(
            TopicResponse(name=topic.name, requires=topic.requires)
            for topic in release.curriculum.topics
        ),
    )

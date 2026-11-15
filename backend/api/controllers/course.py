from api.course import CourseRelease
from api.schemas import CourseResponse, TopicResponse


def describe_course(release: CourseRelease) -> CourseResponse:
    return CourseResponse(
        release=release.hash,
        item_count=len(release.curriculum.items),
        topics=tuple(
            TopicResponse(name=topic.name, requires=topic.requires)
            for topic in release.curriculum.topics
        ),
    )

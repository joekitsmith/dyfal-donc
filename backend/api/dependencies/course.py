from typing import Annotated

from fastapi import Depends, Request

from api.course import CourseRelease


def get_course_release(request: Request) -> CourseRelease:
    release: CourseRelease = request.app.state.course_release
    return release


CourseReleaseDependency = Annotated[CourseRelease, Depends(get_course_release)]

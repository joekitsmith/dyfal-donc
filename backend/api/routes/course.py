from fastapi import APIRouter

from api.controllers import describe_course
from api.dependencies import CourseReleaseDependency
from api.schemas import CourseResponse

router = APIRouter()


@router.get("/course")
def course(release: CourseReleaseDependency) -> CourseResponse:
    return describe_course(release)

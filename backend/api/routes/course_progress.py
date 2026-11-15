from fastapi import APIRouter, Depends

from api.controllers import describe_course_progress, describe_item
from api.dependencies import (
    CourseReleaseDependency,
    LearnerIdDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import CourseProgressResponse, ItemDetailResponse

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("/course")
def get_course_progress(
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
) -> CourseProgressResponse:
    return describe_course_progress(unit_of_work, release, learner_id)


@router.get("/items/{item_id}")
def get_item(
    item_id: str,
    learner_id: LearnerIdDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
) -> ItemDetailResponse:
    return describe_item(unit_of_work, release, learner_id, item_id)

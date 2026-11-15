from fastapi import APIRouter, Depends

from api.controllers import change_user_settings, describe_user_settings
from api.dependencies import (
    AuthenticatedDependency,
    ClockDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import UserSettingsPatch, UserSettingsResponse

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("/settings")
def get_settings(
    authenticated: AuthenticatedDependency, unit_of_work: UnitOfWorkDependency
) -> UserSettingsResponse:
    return describe_user_settings(unit_of_work, authenticated.user.id)


@router.patch("/settings")
def patch_settings(
    patch: UserSettingsPatch,
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
) -> UserSettingsResponse:
    return change_user_settings(unit_of_work, authenticated.user.id, patch, clock())

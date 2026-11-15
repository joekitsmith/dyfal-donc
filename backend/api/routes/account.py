import uuid

from fastapi import APIRouter, Depends, Response, status

from api.controllers import delete_account, list_passkeys, remove_passkey
from api.dependencies import (
    AuthenticatedDependency,
    LoginSessionSettingsDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.mappings import to_user_response
from api.schemas import PasskeyResponse, UserResponse
from api.session_cookie import clear_session_cookie

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("")
def get_me(authenticated: AuthenticatedDependency) -> UserResponse:
    return to_user_response(authenticated.user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    response: Response,
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
    login_session: LoginSessionSettingsDependency,
) -> None:
    delete_account(unit_of_work, authenticated.user.id)
    clear_session_cookie(response, login_session)


@router.get("/passkeys")
def get_passkeys(
    authenticated: AuthenticatedDependency, unit_of_work: UnitOfWorkDependency
) -> tuple[PasskeyResponse, ...]:
    return list_passkeys(unit_of_work, authenticated.user.id)


@router.delete("/passkeys/{passkey_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_passkey(
    passkey_id: uuid.UUID,
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
) -> None:
    remove_passkey(unit_of_work, authenticated.user.id, passkey_id)

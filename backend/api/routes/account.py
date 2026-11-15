import uuid

from fastapi import APIRouter, Depends, Response, status

from api.controllers import (
    delete_account,
    describe_recovery_codes,
    list_passkeys,
    remove_passkey,
    replace_recovery_codes,
)
from api.dependencies import (
    AuthenticatedDependency,
    ClockDependency,
    ConfirmedDependency,
    LoginSessionSettingsDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.mappings import to_user_response
from api.schemas import (
    PasskeyResponse,
    RecoveryCodesResponse,
    RecoveryCodeStatusResponse,
    UserResponse,
)
from api.session_cookie import clear_session_cookie

router = APIRouter(prefix="/me", dependencies=[Depends(require_known_origin)])


@router.get("")
def get_me(authenticated: AuthenticatedDependency) -> UserResponse:
    return to_user_response(authenticated.user)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    response: Response,
    authenticated: ConfirmedDependency,
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
    authenticated: ConfirmedDependency,
    unit_of_work: UnitOfWorkDependency,
) -> None:
    remove_passkey(unit_of_work, authenticated.user.id, passkey_id)


@router.get("/recovery-codes")
def get_recovery_codes(
    authenticated: AuthenticatedDependency, unit_of_work: UnitOfWorkDependency
) -> RecoveryCodeStatusResponse:
    return describe_recovery_codes(unit_of_work, authenticated.user.id)


@router.post("/recovery-codes")
def post_recovery_codes(
    authenticated: ConfirmedDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
) -> RecoveryCodesResponse:
    """Replaces the user's codes with a new set, shown only in this response."""
    return replace_recovery_codes(unit_of_work, authenticated.user, clock())

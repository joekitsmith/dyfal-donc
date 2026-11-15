from fastapi import APIRouter, Depends, Response, status

from api.controllers import (
    begin_passkey_authentication,
    begin_passkey_registration,
    finish_passkey_authentication,
    finish_passkey_registration,
    sign_in_with_recovery_code,
    sign_out,
    start_guest,
)
from api.dependencies import (
    AuthenticatedDependency,
    ClockDependency,
    CourseReleaseDependency,
    LoginSessionSettingsDependency,
    PasskeySettingsDependency,
    SessionTokenDependency,
    UnitOfWorkDependency,
    require_known_origin,
)
from api.schemas import (
    AuthenticationVerifyRequest,
    PasskeyJson,
    RecoveryCodeSignInRequest,
    RegisteredPasskeyResponse,
    RegistrationVerifyRequest,
    UserResponse,
)
from api.session_cookie import clear_session_cookie, set_session_cookie

router = APIRouter(prefix="/auth", dependencies=[Depends(require_known_origin)])


@router.post("/guest")
def post_guest(
    response: Response,
    token: SessionTokenDependency,
    unit_of_work: UnitOfWorkDependency,
    release: CourseReleaseDependency,
    clock: ClockDependency,
    login_session: LoginSessionSettingsDependency,
) -> UserResponse:
    started = start_guest(unit_of_work, release, token, clock(), login_session)
    if started.token is not None:
        set_session_cookie(response, started.token, login_session, is_guest=True)

    return started.user


@router.post("/passkeys/registration/options")
def post_registration_options(
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    passkeys: PasskeySettingsDependency,
) -> PasskeyJson:
    return dict(
        begin_passkey_registration(unit_of_work, passkeys, authenticated.user, clock())
    )


@router.post("/passkeys/registration/verify", status_code=status.HTTP_201_CREATED)
def post_registration_verify(
    request: RegistrationVerifyRequest,
    response: Response,
    authenticated: AuthenticatedDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    passkeys: PasskeySettingsDependency,
    login_session: LoginSessionSettingsDependency,
) -> RegisteredPasskeyResponse:
    registered = finish_passkey_registration(
        unit_of_work,
        passkeys,
        authenticated,
        request,
        clock(),
        login_session,
    )
    if registered.token is not None:
        set_session_cookie(response, registered.token, login_session, is_guest=False)

    return RegisteredPasskeyResponse(
        passkey=registered.passkey,
        recovery_codes=None
        if registered.recovery_codes is None
        else list(registered.recovery_codes),
    )


@router.post("/passkeys/authentication/options")
def post_authentication_options(
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    passkeys: PasskeySettingsDependency,
) -> PasskeyJson:
    return dict(begin_passkey_authentication(unit_of_work, passkeys, clock()))


@router.post("/passkeys/authentication/verify")
def post_authentication_verify(
    request: AuthenticationVerifyRequest,
    response: Response,
    token: SessionTokenDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    passkeys: PasskeySettingsDependency,
    login_session: LoginSessionSettingsDependency,
) -> UserResponse:
    signed_in = finish_passkey_authentication(
        unit_of_work, passkeys, request, token, clock(), login_session
    )
    if signed_in.token is not None:
        set_session_cookie(response, signed_in.token, login_session, is_guest=False)

    return signed_in.user


@router.post("/recovery/verify")
def post_recovery_verify(
    request: RecoveryCodeSignInRequest,
    response: Response,
    token: SessionTokenDependency,
    unit_of_work: UnitOfWorkDependency,
    clock: ClockDependency,
    login_session: LoginSessionSettingsDependency,
) -> UserResponse:
    signed_in = sign_in_with_recovery_code(
        unit_of_work, request, token, clock(), login_session
    )
    if signed_in.token is not None:
        set_session_cookie(response, signed_in.token, login_session, is_guest=False)

    return signed_in.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def post_logout(
    response: Response,
    token: SessionTokenDependency,
    unit_of_work: UnitOfWorkDependency,
    login_session: LoginSessionSettingsDependency,
) -> None:
    sign_out(unit_of_work, token)
    clear_session_cookie(response, login_session)

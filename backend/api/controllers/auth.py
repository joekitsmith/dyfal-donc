import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta

from api.course import CourseRelease
from api.errors import InvalidPasskeyError, NotAuthenticatedError
from api.login_sessions import (
    expiry,
    is_expired,
    is_past_maximum_age,
    needs_extending,
)
from api.mappings import to_add_learner, to_passkey_response, to_user_response
from api.passkeys import (
    CHALLENGE_LIFETIME,
    begin_authentication,
    begin_registration,
    challenge_of,
    credential_id_of,
    finish_authentication,
    finish_registration,
)
from api.recovery_codes import (
    generate_recovery_codes,
    hash_recovery_code,
    hash_recovery_codes,
)
from api.schemas import (
    AuthenticationVerifyRequest,
    PasskeyResponse,
    RecoveryCodeSignInRequest,
    RegistrationVerifyRequest,
    UserResponse,
)
from api.settings import LoginSessionSettings, PasskeySettings
from api.tokens import hash_token, new_token
from persistence.database.errors import RecoveryCodeNotFoundError
from persistence.database import (
    AddChallenge,
    AddCredential,
    AddLoginSession,
    AddUser,
    ExtendLoginSession,
    LoginSessionRecord,
    RecordCredentialUse,
    ReplaceRecoveryCodes,
    UnitOfWork,
    UseRecoveryCode,
    UserRecord,
)

DEFAULT_PASSKEY_LABEL = "Passkey"
REGISTRATION = "registration"
AUTHENTICATION = "authentication"


@dataclass(frozen=True, slots=True, kw_only=True)
class Authenticated:
    """Who is making a request. ``extended`` says the session's expiry just moved."""

    user: UserRecord
    login_session: LoginSessionRecord
    extended: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class SignIn:
    """A user, and the token for the cookie when the browser needs a new one."""

    user: UserResponse
    token: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisteredPasskey:
    """A new passkey, its user's first recovery codes if they have none yet, and a cookie token if one is needed."""

    passkey: PasskeyResponse
    recovery_codes: tuple[str, ...] | None
    token: str | None


def authenticate(
    unit_of_work: UnitOfWork,
    token: str | None,
    now: datetime,
    login: LoginSessionSettings,
) -> Authenticated:
    """Find who the token belongs to, moving the session's expiry if it is due."""
    if token is None:
        raise NotAuthenticatedError("Not signed in")

    login_session = unit_of_work.login_sessions.by_token_hash(hash_token(token))
    if login_session is None or is_expired(login_session.expires_at, now):
        raise NotAuthenticatedError("Not signed in")

    user = unit_of_work.users.get(login_session.user_id)
    if user is None:
        raise NotAuthenticatedError("Not signed in")

    # A guest has no passkey to sign in again with, so only an account's session has a limit
    if not user.is_guest and is_past_maximum_age(
        login_session.created_at, now, login.max_age
    ):
        raise NotAuthenticatedError("Not signed in")

    extended = needs_extending(login_session.last_seen_at, now)
    if extended:
        unit_of_work.login_sessions.extend(
            ExtendLoginSession(
                login_session_id=login_session.id,
                seen_at=now,
                expires_at=expiry(now, login.lifetime_for(is_guest=user.is_guest)),
            )
        )
        unit_of_work.commit()

    return Authenticated(user=user, login_session=login_session, extended=extended)


def start_guest(
    unit_of_work: UnitOfWork,
    release: CourseRelease,
    token: str | None,
    now: datetime,
    login: LoginSessionSettings,
) -> SignIn:
    """Let someone start straight away, as a user with no passkeys.

    A browser that is already signed in gets its own user back.
    """
    try:
        current = authenticate(unit_of_work, token, now, login)
    except NotAuthenticatedError:
        pass
    else:
        return SignIn(user=to_user_response(current.user), token=None)

    user = unit_of_work.users.add(AddUser())
    unit_of_work.learners.add(to_add_learner(user.id, release))
    new_session_token = _open_session(
        unit_of_work, user.id, now, login.lifetime_for(is_guest=True)
    )
    unit_of_work.commit()
    return SignIn(user=to_user_response(user), token=new_session_token)


def begin_passkey_registration(
    unit_of_work: UnitOfWork,
    settings: PasskeySettings,
    user: UserRecord,
    now: datetime,
) -> Mapping[str, object]:
    existing = unit_of_work.credentials.for_user(user.id)
    begun = begin_registration(
        settings,
        user_id=user.id,
        user_name=user.display_name or f"learner-{user.id.hex[:8]}",
        existing_credential_ids=tuple(
            credential.credential_id for credential in existing
        ),
    )
    unit_of_work.challenges.delete_expired(now)
    unit_of_work.challenges.add(
        AddChallenge(
            challenge=begun.challenge,
            purpose=REGISTRATION,
            user_id=user.id,
            created_at=now,
            expires_at=now + CHALLENGE_LIFETIME,
        )
    )
    unit_of_work.commit()
    return begun.options


def finish_passkey_registration(
    unit_of_work: UnitOfWork,
    settings: PasskeySettings,
    authenticated: Authenticated,
    request: RegistrationVerifyRequest,
    now: datetime,
    login: LoginSessionSettings,
) -> RegisteredPasskey:
    """Store the passkey the browser made for the signed-in user.

    A guest who gets their first passkey is given a fresh token, so the one in
    their old cookie stops working.
    """
    user = authenticated.user
    challenge = challenge_of(request.credential)
    used = unit_of_work.challenges.consume(challenge, REGISTRATION, now)
    # Used up even if the passkey does not verify, so a bad answer cannot be retried
    unit_of_work.commit()
    if used.user_id != user.id:
        raise InvalidPasskeyError("Challenge was issued to someone else")

    new_passkey = finish_registration(settings, request.credential, challenge)
    stored = unit_of_work.credentials.add(
        AddCredential(
            user_id=user.id,
            credential_id=new_passkey.credential_id,
            public_key=new_passkey.public_key,
            sign_count=new_passkey.sign_count,
            transports=new_passkey.transports,
            label=request.label or DEFAULT_PASSKEY_LABEL,
            created_at=now,
        )
    )
    token = None
    recovery_codes = None
    if user.is_guest:
        unit_of_work.login_sessions.delete(authenticated.login_session.id)
        token = _open_session(
            unit_of_work, user.id, now, login.lifetime_for(is_guest=False)
        )
        recovery_codes = make_recovery_codes(unit_of_work, user.id, now)

    unit_of_work.commit()
    return RegisteredPasskey(
        passkey=to_passkey_response(stored),
        recovery_codes=recovery_codes,
        token=token,
    )


def begin_passkey_authentication(
    unit_of_work: UnitOfWork, settings: PasskeySettings, now: datetime
) -> Mapping[str, object]:
    begun = begin_authentication(settings)
    unit_of_work.challenges.delete_expired(now)
    unit_of_work.challenges.add(
        AddChallenge(
            challenge=begun.challenge,
            purpose=AUTHENTICATION,
            user_id=None,
            created_at=now,
            expires_at=now + CHALLENGE_LIFETIME,
        )
    )
    unit_of_work.commit()
    return begun.options


def finish_passkey_authentication(
    unit_of_work: UnitOfWork,
    settings: PasskeySettings,
    request: AuthenticationVerifyRequest,
    token: str | None,
    now: datetime,
    login: LoginSessionSettings,
) -> SignIn:
    """Sign in with a passkey, replacing whatever the browser was signed in as."""
    challenge = challenge_of(request.credential)
    unit_of_work.challenges.consume(challenge, AUTHENTICATION, now)
    # Used up even if the answer does not verify, so a bad answer cannot be retried
    unit_of_work.commit()
    stored = unit_of_work.credentials.by_credential_id(
        credential_id_of(request.credential)
    )
    if stored is None:
        raise InvalidPasskeyError("Passkey did not verify")

    signed_in = finish_authentication(
        settings,
        request.credential,
        challenge,
        public_key=stored.public_key,
        sign_count=stored.sign_count,
    )
    unit_of_work.credentials.record_use(
        RecordCredentialUse(
            credential_id=signed_in.credential_id,
            sign_count=signed_in.sign_count,
            used_at=now,
        )
    )
    _end_session(unit_of_work, token)
    new_session_token = _open_session(
        unit_of_work, stored.user_id, now, login.lifetime_for(is_guest=False)
    )
    user = unit_of_work.users.get(stored.user_id)
    if user is None:
        raise InvalidPasskeyError("Passkey did not verify")

    unit_of_work.commit()
    return SignIn(user=to_user_response(user), token=new_session_token)


def make_recovery_codes(
    unit_of_work: UnitOfWork, user_id: uuid.UUID, now: datetime
) -> tuple[str, ...]:
    """Replace the user's recovery codes with a new set, which is only ever shown this once."""
    codes = generate_recovery_codes()
    unit_of_work.recovery_codes.replace(
        ReplaceRecoveryCodes(
            user_id=user_id, code_hashes=hash_recovery_codes(codes), created_at=now
        )
    )
    return codes


def sign_in_with_recovery_code(
    unit_of_work: UnitOfWork,
    request: RecoveryCodeSignInRequest,
    token: str | None,
    now: datetime,
    login: LoginSessionSettings,
) -> SignIn:
    """Sign in with a recovery code, once, replacing whatever the browser was signed in as."""
    user_id = unit_of_work.recovery_codes.use(
        UseRecoveryCode(code_hash=hash_recovery_code(request.code), at=now)
    )
    user = unit_of_work.users.get(user_id)
    if user is None:
        raise RecoveryCodeNotFoundError("Recovery code belongs to no one")

    _end_session(unit_of_work, token)
    new_session_token = _open_session(
        unit_of_work, user_id, now, login.lifetime_for(is_guest=False)
    )
    unit_of_work.commit()
    return SignIn(user=to_user_response(user), token=new_session_token)


def sign_out(unit_of_work: UnitOfWork, token: str | None) -> None:
    """Forget the browser's login session. Signing out twice is fine."""
    _end_session(unit_of_work, token)
    unit_of_work.commit()


def _open_session(
    unit_of_work: UnitOfWork, user_id: uuid.UUID, now: datetime, lifetime: timedelta
) -> str:
    unit_of_work.login_sessions.delete_expired(now)
    token = new_token()
    unit_of_work.login_sessions.add(
        AddLoginSession(
            user_id=user_id,
            token_hash=hash_token(token),
            created_at=now,
            authenticated_at=now,
            expires_at=expiry(now, lifetime),
        )
    )
    return token


def _end_session(unit_of_work: UnitOfWork, token: str | None) -> None:
    if token is None:
        return

    login_session = unit_of_work.login_sessions.by_token_hash(hash_token(token))
    if login_session is not None:
        unit_of_work.login_sessions.delete(login_session.id)

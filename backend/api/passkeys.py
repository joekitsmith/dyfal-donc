import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import timedelta

from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers import (
    base64url_to_bytes,
    options_to_json_dict,
    parse_client_data_json,
    parse_registration_credential_json,
)
from webauthn.helpers.exceptions import WebAuthnException
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    PublicKeyCredentialDescriptor,
    ResidentKeyRequirement,
    UserVerificationRequirement,
)

from api.errors import InvalidPasskeyError
from api.settings import PasskeySettings

CHALLENGE_LIFETIME = timedelta(minutes=5)

type PasskeyResponse = Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class PasskeyOptions:
    """What to give the browser to start a passkey ceremony.

    ``options`` is the JSON the browser's WebAuthn API takes, and ``challenge``
    is what its answer must contain.
    """

    challenge: bytes
    options: Mapping[str, object]


@dataclass(frozen=True, slots=True, kw_only=True)
class NewPasskey:
    """A passkey the browser made, ready to store."""

    credential_id: bytes
    public_key: bytes
    sign_count: int
    transports: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class VerifiedSignIn:
    """A passkey that proved it is the one stored, and its new use count."""

    credential_id: bytes
    sign_count: int


def begin_registration(
    settings: PasskeySettings,
    *,
    user_id: uuid.UUID,
    user_name: str,
    existing_credential_ids: Sequence[bytes],
) -> PasskeyOptions:
    """Options for making a passkey for the user.

    Passkeys are discoverable, so signing in needs no username, and the ones the
    user already has are excluded so a device is not registered twice.
    """
    options = generate_registration_options(
        rp_id=settings.rp_id,
        rp_name=settings.rp_name,
        user_id=user_id.bytes,
        user_name=user_name,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
        exclude_credentials=[
            PublicKeyCredentialDescriptor(id=credential_id)
            for credential_id in existing_credential_ids
        ],
    )
    return PasskeyOptions(
        challenge=options.challenge, options=options_to_json_dict(options)
    )


def finish_registration(
    settings: PasskeySettings, response: PasskeyResponse, challenge: bytes
) -> NewPasskey:
    """Check the browser's new passkey, which must answer the challenge."""
    try:
        verified = verify_registration_response(
            credential=dict(response),
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=list(settings.origins),
        )
        transports = parse_registration_credential_json(
            dict(response)
        ).response.transports
    except (WebAuthnException, ValueError) as error:
        raise InvalidPasskeyError("Passkey did not verify") from error

    return NewPasskey(
        credential_id=verified.credential_id,
        public_key=verified.credential_public_key,
        sign_count=verified.sign_count,
        transports=tuple(transport.value for transport in transports or ()),
    )


def begin_authentication(settings: PasskeySettings) -> PasskeyOptions:
    """Options for signing in with any passkey the browser holds for this site."""
    options = generate_authentication_options(
        rp_id=settings.rp_id,
        user_verification=UserVerificationRequirement.PREFERRED,
    )
    return PasskeyOptions(
        challenge=options.challenge, options=options_to_json_dict(options)
    )


def finish_authentication(
    settings: PasskeySettings,
    response: PasskeyResponse,
    challenge: bytes,
    *,
    public_key: bytes,
    sign_count: int,
) -> VerifiedSignIn:
    """Check that the response is signed by the stored passkey, over the challenge."""
    try:
        verified = verify_authentication_response(
            credential=dict(response),
            expected_challenge=challenge,
            expected_rp_id=settings.rp_id,
            expected_origin=list(settings.origins),
            credential_public_key=public_key,
            credential_current_sign_count=sign_count,
        )
    except (WebAuthnException, ValueError) as error:
        raise InvalidPasskeyError("Passkey did not verify") from error

    return VerifiedSignIn(
        credential_id=verified.credential_id, sign_count=verified.new_sign_count
    )


def challenge_of(response: PasskeyResponse) -> bytes:
    """The challenge the browser signed, which says which ceremony this answers."""
    inner = response.get("response")
    client_data = inner.get("clientDataJSON") if isinstance(inner, Mapping) else None
    if not isinstance(client_data, str):
        raise InvalidPasskeyError("Passkey response has no client data")

    try:
        return parse_client_data_json(base64url_to_bytes(client_data)).challenge
    except (WebAuthnException, ValueError) as error:
        raise InvalidPasskeyError("Passkey client data is malformed") from error


def credential_id_of(response: PasskeyResponse) -> bytes:
    """The id of the passkey the browser used, to find its stored public key."""
    raw_id = response.get("rawId")
    if not isinstance(raw_id, str):
        raise InvalidPasskeyError("Passkey response has no credential id")

    try:
        return base64url_to_bytes(raw_id)
    except ValueError as error:
        raise InvalidPasskeyError("Passkey credential id is malformed") from error

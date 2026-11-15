import hashlib
import json
import secrets
import struct
from collections.abc import Mapping
from typing import cast

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from webauthn.helpers import base64url_to_bytes, bytes_to_base64url

USER_PRESENT = 0x01
USER_VERIFIED = 0x04
ATTESTED_CREDENTIAL = 0x40
COSE_ES256 = -7


class SoftwareAuthenticator:
    """A passkey made in software, answering ceremonies the way a device would.

    It makes `none`-attestation passkeys with an ES256 key, which is all the app
    asks for. Each call takes the options the server sent and returns the JSON
    the browser would send back.
    """

    def __init__(self) -> None:
        self.credential_id = secrets.token_bytes(16)
        self.sign_count = 0
        self._key = ec.generate_private_key(ec.SECP256R1())
        self._user_handle = b""

    def register(
        self,
        options: Mapping[str, object],
        origin: str,
        *,
        challenge: bytes | None = None,
    ) -> dict[str, object]:
        rp_id = _text(_mapping(options["rp"])["id"])
        used_challenge = challenge or base64url_to_bytes(_text(options["challenge"]))
        self._user_handle = base64url_to_bytes(_text(_mapping(options["user"])["id"]))
        client_data = _client_data("webauthn.create", used_challenge, origin)
        public_numbers = self._key.public_key().public_numbers()
        cose_key = cbor2.dumps(
            {
                1: 2,
                3: COSE_ES256,
                -1: 1,
                -2: public_numbers.x.to_bytes(32),
                -3: public_numbers.y.to_bytes(32),
            }
        )
        authenticator_data = (
            _rp_id_hash(rp_id)
            + bytes([USER_PRESENT | USER_VERIFIED | ATTESTED_CREDENTIAL])
            + struct.pack(">I", self.sign_count)
            + bytes(16)
            + struct.pack(">H", len(self.credential_id))
            + self.credential_id
            + cose_key
        )
        attestation = cbor2.dumps(
            {"fmt": "none", "attStmt": {}, "authData": authenticator_data}
        )
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data),
                "attestationObject": bytes_to_base64url(attestation),
                "transports": ["internal"],
            },
            "clientExtensionResults": {},
        }

    def sign_in(
        self,
        options: Mapping[str, object],
        origin: str,
        *,
        challenge: bytes | None = None,
    ) -> dict[str, object]:
        rp_id = _text(options["rpId"])
        used_challenge = challenge or base64url_to_bytes(_text(options["challenge"]))
        self.sign_count += 1
        client_data = _client_data("webauthn.get", used_challenge, origin)
        authenticator_data = (
            _rp_id_hash(rp_id)
            + bytes([USER_PRESENT | USER_VERIFIED])
            + struct.pack(">I", self.sign_count)
        )
        signature = self._key.sign(
            authenticator_data + hashlib.sha256(client_data).digest(),
            ec.ECDSA(hashes.SHA256()),
        )
        return {
            "id": bytes_to_base64url(self.credential_id),
            "rawId": bytes_to_base64url(self.credential_id),
            "type": "public-key",
            "response": {
                "clientDataJSON": bytes_to_base64url(client_data),
                "authenticatorData": bytes_to_base64url(authenticator_data),
                "signature": bytes_to_base64url(signature),
                "userHandle": bytes_to_base64url(self._user_handle),
            },
            "clientExtensionResults": {},
        }


def _client_data(kind: str, challenge: bytes, origin: str) -> bytes:
    return json.dumps(
        {
            "type": kind,
            "challenge": bytes_to_base64url(challenge),
            "origin": origin,
            "crossOrigin": False,
        }
    ).encode()


def _rp_id_hash(rp_id: str) -> bytes:
    return hashlib.sha256(rp_id.encode()).digest()


def _mapping(value: object) -> Mapping[str, object]:
    return cast("Mapping[str, object]", value)


def _text(value: object) -> str:
    return cast("str", value)

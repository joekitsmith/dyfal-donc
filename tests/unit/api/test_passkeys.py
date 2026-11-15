import uuid

import pytest

from api.errors import InvalidPasskeyError
from api.passkeys import (
    begin_authentication,
    begin_registration,
    challenge_of,
    credential_id_of,
    finish_authentication,
    finish_registration,
)
from api.settings import PasskeySettings
from tests.support.authenticator import SoftwareAuthenticator

ORIGIN = "http://localhost:8080"


@pytest.fixture
def settings() -> PasskeySettings:
    return PasskeySettings(_env_file=None)


@pytest.fixture
def authenticator() -> SoftwareAuthenticator:
    return SoftwareAuthenticator()


class TestRegistration:
    def test_a_passkey_made_for_the_challenge_verifies(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(),
        )
        response = authenticator.register(begun.options, ORIGIN)

        passkey = finish_registration(settings, response, begun.challenge)

        assert passkey.credential_id == authenticator.credential_id
        assert passkey.sign_count == 0
        assert passkey.transports == ("internal",)
        assert passkey.public_key

    def test_the_options_ask_for_a_discoverable_passkey(
        self, settings: PasskeySettings
    ) -> None:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(),
        )

        selection = begun.options["authenticatorSelection"]
        assert isinstance(selection, dict)
        assert selection["residentKey"] == "required"
        assert begun.options["attestation"] == "none"

    def test_existing_passkeys_are_excluded(self, settings: PasskeySettings) -> None:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(b"one", b"two"),
        )

        excluded = begun.options["excludeCredentials"]
        assert isinstance(excluded, list)
        assert len(excluded) == 2

    def test_a_response_to_another_challenge_does_not_verify(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(),
        )
        response = authenticator.register(begun.options, ORIGIN)

        with pytest.raises(InvalidPasskeyError):
            finish_registration(settings, response, b"another challenge")

    def test_a_response_from_another_origin_does_not_verify(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(),
        )
        response = authenticator.register(begun.options, "https://evil.example")

        with pytest.raises(InvalidPasskeyError):
            finish_registration(settings, response, begun.challenge)

    def test_garbage_does_not_verify(self, settings: PasskeySettings) -> None:
        with pytest.raises(InvalidPasskeyError):
            finish_registration(settings, {"nonsense": 1}, b"challenge")


class TestAuthentication:
    def registered(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> bytes:
        begun = begin_registration(
            settings,
            user_id=uuid.uuid4(),
            user_name="learner",
            existing_credential_ids=(),
        )
        passkey = finish_registration(
            settings, authenticator.register(begun.options, ORIGIN), begun.challenge
        )
        return passkey.public_key

    def test_a_signed_challenge_verifies_and_counts_the_use(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        public_key = self.registered(settings, authenticator)
        begun = begin_authentication(settings)
        response = authenticator.sign_in(begun.options, ORIGIN)

        signed_in = finish_authentication(
            settings, response, begun.challenge, public_key=public_key, sign_count=0
        )

        assert signed_in.credential_id == authenticator.credential_id
        assert signed_in.sign_count == 1

    def test_a_replayed_use_count_is_refused(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        public_key = self.registered(settings, authenticator)
        begun = begin_authentication(settings)
        response = authenticator.sign_in(begun.options, ORIGIN)

        with pytest.raises(InvalidPasskeyError):
            finish_authentication(
                settings, response, begun.challenge, public_key=public_key, sign_count=5
            )

    def test_another_passkeys_key_does_not_verify(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        self.registered(settings, authenticator)
        other_key = self.registered(settings, SoftwareAuthenticator())
        begun = begin_authentication(settings)
        response = authenticator.sign_in(begun.options, ORIGIN)

        with pytest.raises(InvalidPasskeyError):
            finish_authentication(
                settings, response, begun.challenge, public_key=other_key, sign_count=0
            )

    def test_a_response_to_another_challenge_does_not_verify(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        public_key = self.registered(settings, authenticator)
        begun = begin_authentication(settings)
        response = authenticator.sign_in(begun.options, ORIGIN)

        with pytest.raises(InvalidPasskeyError):
            finish_authentication(
                settings, response, b"another", public_key=public_key, sign_count=0
            )


class TestReadingAResponse:
    def test_the_challenge_and_credential_id_are_found(
        self, settings: PasskeySettings, authenticator: SoftwareAuthenticator
    ) -> None:
        begun = begin_authentication(settings)
        response = authenticator.sign_in(begun.options, ORIGIN)

        assert challenge_of(response) == begun.challenge
        assert credential_id_of(response) == authenticator.credential_id

    @pytest.mark.parametrize(
        "response",
        [
            {},
            {"response": "text"},
            {"response": {"clientDataJSON": 5}},
            {"response": {"clientDataJSON": "!!"}},
        ],
    )
    def test_a_response_without_usable_client_data_is_refused(
        self, response: dict[str, object]
    ) -> None:
        with pytest.raises(InvalidPasskeyError):
            challenge_of(response)

    @pytest.mark.parametrize("response", [{}, {"rawId": 5}])
    def test_a_response_without_a_credential_id_is_refused(
        self, response: dict[str, object]
    ) -> None:
        with pytest.raises(InvalidPasskeyError):
            credential_id_of(response)

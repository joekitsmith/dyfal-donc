from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from tests.integration.api.conftest import FakeClock
from tests.integration.api.helpers import (
    recovery_codes_after_saving,
    register_passkey,
    sign_in,
    start_guest,
)
from tests.support.authenticator import SoftwareAuthenticator

Browsers = Callable[[], TestClient]
OTHER_PASSKEY_ID = "00000000-0000-0000-0000-000000000000"
CHANGES = (
    ("POST", "/auth/passkeys/registration/options"),
    ("POST", "/me/recovery-codes"),
    ("DELETE", f"/me/passkeys/{OTHER_PASSKEY_ID}"),
    ("DELETE", "/me"),
)


def attempt(client: TestClient, method: str, path: str) -> int:
    return client.request(method, path).status_code


class TestChangingAnAccount:
    @pytest.mark.parametrize(("method", "path"), CHANGES)
    def test_needs_a_sign_in_within_the_last_ten_minutes(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
        method: str,
        path: str,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)

        clock.advance(minutes=11)

        assert attempt(client, method, path) == 403
        assert client.get("/me").status_code == 200

    def test_is_allowed_within_the_window(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)

        clock.advance(minutes=9)

        assert client.post("/me/recovery-codes").status_code == 200

    def test_using_the_session_does_not_count_as_signing_in(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)

        for _ in range(3):
            clock.advance(minutes=4)
            client.get("/me")

        assert client.post("/me/recovery-codes").status_code == 403

    def test_signing_in_with_a_passkey_confirms_it_again(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)
        clock.advance(minutes=11)
        assert client.post("/me/recovery-codes").status_code == 403

        sign_in(client, authenticator)

        assert client.post("/me/recovery-codes").status_code == 200

    def test_signing_in_with_a_recovery_code_confirms_it_so_a_new_passkey_can_be_added(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        codes = recovery_codes_after_saving(member, authenticator)
        browser.post("/auth/recovery/verify", json={"code": codes[0]})

        register_passkey(browser, SoftwareAuthenticator())

        assert len(browser.get("/me/passkeys").json()) == 2

    def test_another_browsers_confirmation_does_not_help(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        stale, fresh = make_client(), make_client()
        recovery_codes_after_saving(stale, authenticator)
        clock.advance(minutes=11)
        sign_in(fresh, authenticator)

        assert stale.post("/me/recovery-codes").status_code == 403
        assert fresh.post("/me/recovery-codes").status_code == 200


class TestAGuestIsNotAskedToConfirm:
    def test_a_guest_can_save_progress_and_delete_the_account_long_after_starting(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        saver, leaver = make_client(), make_client()
        start_guest(saver)
        start_guest(leaver)
        clock.advance(hours=3)

        register_passkey(saver, authenticator)

        assert saver.get("/me").json()["is_guest"] is False
        assert leaver.delete("/me").status_code == 204


class TestTheMaximumAgeOfAnAccountSession:
    def test_an_account_session_ends_after_thirty_days_however_much_it_is_used(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)

        for _ in range(29):
            clock.advance(hours=23)
            assert client.get("/me").status_code == 200

        clock.advance(days=2)
        assert client.get("/me").status_code == 401

    def test_signing_in_again_starts_a_new_session(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        recovery_codes_after_saving(client, authenticator)
        clock.advance(days=31)
        assert client.get("/me").status_code == 401

        sign_in(client, authenticator)

        assert client.get("/me").status_code == 200

    def test_a_guest_who_keeps_using_the_app_is_never_cut_off(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        for _ in range(8):
            clock.advance(days=20)
            assert client.get("/me").status_code == 200

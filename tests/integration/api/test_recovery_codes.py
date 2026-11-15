from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.integration.api.conftest import FakeClock
from tests.integration.api.helpers import (
    answer,
    offer,
    progress,
    recovery_codes_after_saving,
    register_passkey,
    register_passkey_response,
    sign_in,
    start_guest,
)
from tests.support.authenticator import SoftwareAuthenticator

Browsers = Callable[[], TestClient]


def use_code(client: TestClient, code: str) -> int:
    return client.post("/auth/recovery/verify", json={"code": code}).status_code


def remaining(client: TestClient) -> int:
    body = client.get("/me/recovery-codes").json()
    count: int = body["remaining"]
    return count


class TestMakingCodes:
    def test_the_first_passkey_brings_ten_codes(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        codes = recovery_codes_after_saving(client, authenticator)

        assert len(codes) == 10
        assert len(set(codes)) == 10
        assert remaining(client) == 10

    def test_a_second_passkey_brings_none(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        recovery_codes_after_saving(client, authenticator)

        second = register_passkey_response(client, SoftwareAuthenticator())

        assert second["recovery_codes"] is None
        assert remaining(client) == 10

    def test_the_codes_can_never_be_read_again(
        self, client: TestClient, authenticator: SoftwareAuthenticator, engine: Engine
    ) -> None:
        codes = recovery_codes_after_saving(client, authenticator)

        status = client.get("/me/recovery-codes").json()

        assert set(status) == {"remaining"}
        with engine.connect() as connection:
            stored = b"".join(
                bytes(row[0])
                for row in connection.execute(
                    text("SELECT code_hash FROM recovery_codes")
                )
            )
        assert all(code.replace("-", "").encode() not in stored for code in codes)

    def test_new_codes_replace_the_old_set(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        old = recovery_codes_after_saving(client, authenticator)

        response = client.post("/me/recovery-codes")
        new = response.json()["codes"]

        assert response.status_code == 200
        assert len(new) == 10
        assert set(new).isdisjoint(old)
        assert remaining(client) == 10
        assert use_code(client, old[0]) == 400
        assert use_code(client, new[0]) == 200

    def test_a_guest_has_none_to_make(self, client: TestClient) -> None:
        start_guest(client)

        assert remaining(client) == 0
        assert client.post("/me/recovery-codes").status_code == 409

    def test_they_need_someone_signed_in(self, client: TestClient) -> None:
        assert client.get("/me/recovery-codes").status_code == 401
        assert client.post("/me/recovery-codes").status_code == 401


class TestSigningInWithACode:
    def test_a_code_signs_in_as_its_user_on_another_browser(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        first, second = make_client(), make_client()
        codes = recovery_codes_after_saving(first, authenticator)
        answer(first, offer(first)["selection_id"])

        response = second.post("/auth/recovery/verify", json={"code": codes[0]})

        assert response.status_code == 200
        assert response.json() == first.get("/me").json()
        assert progress(second)["introduced"] == 1
        assert remaining(second) == 9

    def test_a_code_works_once(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        codes = recovery_codes_after_saving(make_client(), authenticator)

        assert use_code(make_client(), codes[0]) == 200
        assert use_code(make_client(), codes[0]) == 400

    def test_a_code_can_be_typed_loosely(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        codes = recovery_codes_after_saving(make_client(), authenticator)

        assert use_code(make_client(), codes[0].lower().replace("-", " ")) == 200

    def test_a_wrong_code_is_refused_the_same_way_as_a_used_one(
        self, client: TestClient
    ) -> None:
        response = client.post(
            "/auth/recovery/verify", json={"code": "ABCD-EFGH-JKMN-PQRS"}
        )

        assert response.status_code == 400
        assert client.get("/me").status_code == 401

    def test_an_empty_code_is_rejected(self, client: TestClient) -> None:
        assert (
            client.post("/auth/recovery/verify", json={"code": ""}).status_code == 422
        )

    def test_signing_in_gives_an_accounts_session_and_replaces_the_guest_one(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        member, browser = make_client(), make_client()
        codes = recovery_codes_after_saving(member, authenticator)
        guest = start_guest(browser)

        use_code(browser, codes[0])

        assert browser.get("/me").json()["id"] != guest["id"]
        clock.advance(days=1, seconds=1)
        assert browser.get("/me").status_code == 401

    def test_does_not_sign_out_the_accounts_other_sessions(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        codes = recovery_codes_after_saving(member, authenticator)

        use_code(browser, codes[0])

        assert member.get("/me").status_code == 200

    def test_a_new_passkey_can_be_added_after_recovering(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        codes = recovery_codes_after_saving(member, authenticator)
        use_code(browser, codes[0])

        replacement = SoftwareAuthenticator()
        register_passkey(browser, replacement)

        assert len(browser.get("/me/passkeys").json()) == 2
        assert sign_in(make_client(), replacement)["is_guest"] is False

    def test_a_request_from_another_origin_is_refused(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        codes = recovery_codes_after_saving(client, authenticator)

        response = client.post(
            "/auth/recovery/verify",
            json={"code": codes[0]},
            headers={"Origin": "https://evil.example"},
        )

        assert response.status_code == 403

    def test_a_deleted_accounts_codes_stop_working(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member = make_client()
        codes = recovery_codes_after_saving(member, authenticator)
        member.delete("/me")

        assert use_code(make_client(), codes[0]) == 400

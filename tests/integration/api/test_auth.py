from collections.abc import Callable
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, func, select, text

from persistence.database.models import Base
from tests.integration.api.conftest import ORIGIN, FakeClock
from tests.integration.api.helpers import (
    answer,
    offer,
    progress,
    register_passkey,
    sign_in,
    start_guest,
)
from tests.support.authenticator import SoftwareAuthenticator

Browsers = Callable[[], TestClient]


def stored_token_hashes(engine: Engine) -> list[bytes]:
    with engine.connect() as connection:
        return [
            bytes(row[0])
            for row in connection.execute(text("SELECT token_hash FROM login_sessions"))
        ]


def row_counts(engine: Engine) -> dict[str, int]:
    with engine.connect() as connection:
        return {
            name: connection.execute(
                select(func.count()).select_from(table)
            ).scalar_one()
            for name, table in Base.metadata.tables.items()
        }


class TestGuest:
    def test_starts_straight_away_as_a_guest(self, client: TestClient) -> None:
        user = start_guest(client)

        assert user["is_guest"] is True
        assert client.get("/me").json() == user

    def test_the_cookie_cannot_be_read_by_scripts_or_sent_cross_site(
        self, client: TestClient
    ) -> None:
        response = client.post("/auth/guest")

        cookie = response.headers["set-cookie"].lower()
        assert "httponly" in cookie
        assert "samesite=lax" in cookie
        assert "path=/" in cookie

    def test_only_a_hash_of_the_token_is_stored(
        self, client: TestClient, engine: Engine
    ) -> None:
        start_guest(client)

        token = client.cookies["session"]

        hashes = stored_token_hashes(engine)
        assert len(hashes) == 1
        assert token.encode() not in hashes[0]

    def test_asking_again_gives_back_the_same_user(self, client: TestClient) -> None:
        first = start_guest(client)

        second = client.post("/auth/guest")

        assert second.json() == first
        assert "set-cookie" not in second.headers

    def test_each_browser_gets_its_own_user(self, make_client: Browsers) -> None:
        first, second = make_client(), make_client()

        assert start_guest(first)["id"] != start_guest(second)["id"]

    def test_a_request_from_another_origin_creates_nothing(
        self, client: TestClient, engine: Engine
    ) -> None:
        response = client.post(
            "/auth/guest", headers={"Origin": "https://evil.example"}
        )

        assert response.status_code == 403
        assert row_counts(engine)["users"] == 0


class TestSavingProgress:
    def test_a_guest_keeps_their_progress_when_they_add_a_passkey(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        guest = start_guest(client)
        answer(client, offer(client)["selection_id"])

        passkey = register_passkey(client, authenticator, "My phone")

        me = client.get("/me").json()
        assert me["id"] == guest["id"]
        assert me["is_guest"] is False
        assert progress(client)["introduced"] == 1
        assert passkey["label"] == "My phone"
        assert client.get("/me/passkeys").json() == [passkey]

    def test_the_passkey_is_labelled_when_the_user_gives_no_name(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)

        assert register_passkey(client, authenticator)["label"] == "Passkey"

    def test_the_old_token_stops_working_when_a_guest_upgrades(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
    ) -> None:
        browser, thief = make_client(), make_client()
        start_guest(browser)
        thief.cookies.set("session", browser.cookies["session"])

        register_passkey(browser, authenticator)

        assert thief.get("/me").status_code == 401
        assert browser.get("/me").status_code == 200

    def test_a_second_passkey_does_not_change_the_token(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        register_passkey(client, authenticator)
        token = client.cookies["session"]

        register_passkey(client, SoftwareAuthenticator())

        assert client.cookies["session"] == token
        assert len(client.get("/me/passkeys").json()) == 2

    def test_the_same_passkey_cannot_be_added_twice(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        register_passkey(client, authenticator)
        options = client.post("/auth/passkeys/registration/options").json()

        response = client.post(
            "/auth/passkeys/registration/verify",
            json={"credential": authenticator.register(options, ORIGIN)},
        )

        assert response.status_code == 409

    def test_registering_needs_someone_signed_in(self, client: TestClient) -> None:
        assert client.post("/auth/passkeys/registration/options").status_code == 401


class TestSigningIn:
    def test_a_passkey_signs_in_on_another_browser_as_the_same_user(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        first, second = make_client(), make_client()
        guest = start_guest(first)
        answer(first, offer(first)["selection_id"])
        register_passkey(first, authenticator)

        signed_in = sign_in(second, authenticator)

        assert signed_in["id"] == guest["id"]
        assert signed_in["is_guest"] is False
        assert progress(second)["introduced"] == 1

    def test_signing_out_and_back_in(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        guest = start_guest(client)
        register_passkey(client, authenticator)
        client.post("/auth/logout")
        assert client.get("/me").status_code == 401

        signed_in = sign_in(client, authenticator)

        assert signed_in["id"] == guest["id"]
        assert client.get("/me").status_code == 200

    def test_signing_in_replaces_the_guest_the_browser_was(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        member_user = start_guest(member)
        register_passkey(member, authenticator)
        guest = start_guest(browser)

        sign_in(browser, authenticator)

        assert browser.get("/me").json()["id"] == member_user["id"]
        assert guest["id"] != member_user["id"]

    def test_signing_in_gives_a_new_token_and_records_the_use(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
        engine: Engine,
    ) -> None:
        first, second = make_client(), make_client()
        start_guest(first)
        register_passkey(first, authenticator)

        sign_in(second, authenticator)

        assert second.cookies["session"] != first.cookies["session"]
        passkey = second.get("/me/passkeys").json()[0]
        assert passkey["last_used_at"] is not None

    def test_a_passkey_nobody_registered_is_refused(self, client: TestClient) -> None:
        options = client.post("/auth/passkeys/authentication/options").json()

        response = client.post(
            "/auth/passkeys/authentication/verify",
            json={"credential": SoftwareAuthenticator().sign_in(options, ORIGIN)},
        )

        assert response.status_code == 400
        assert client.get("/me").status_code == 401

    def test_a_replayed_sign_in_is_refused(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        browser, attacker = make_client(), make_client()
        start_guest(browser)
        register_passkey(browser, authenticator)
        options = attacker.post("/auth/passkeys/authentication/options").json()
        credential = authenticator.sign_in(options, ORIGIN)
        body = {"credential": credential}
        assert (
            attacker.post("/auth/passkeys/authentication/verify", json=body).status_code
            == 200
        )

        replay = make_client().post("/auth/passkeys/authentication/verify", json=body)

        assert replay.status_code == 400


class TestWhatASignInFailureReveals:
    def test_an_unknown_passkey_and_a_bad_signature_look_the_same(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        start_guest(member)
        register_passkey(member, authenticator)

        def failure(device: SoftwareAuthenticator, origin: str) -> object:
            options = browser.post("/auth/passkeys/authentication/options").json()
            credential = device.sign_in(options, origin)
            response = browser.post(
                "/auth/passkeys/authentication/verify", json={"credential": credential}
            )
            assert response.status_code == 400
            return response.json()

        unknown = failure(SoftwareAuthenticator(), ORIGIN)
        bad_origin = failure(authenticator, "https://evil.example")

        assert unknown == bad_origin


class TestChallenges:
    def test_a_challenge_works_once(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        options = client.post("/auth/passkeys/registration/options").json()
        body = {"credential": authenticator.register(options, ORIGIN)}
        assert (
            client.post("/auth/passkeys/registration/verify", json=body).status_code
            == 201
        )

        again = client.post("/auth/passkeys/registration/verify", json=body)

        assert again.status_code == 400

    def test_a_challenge_expires(
        self, client: TestClient, authenticator: SoftwareAuthenticator, clock: FakeClock
    ) -> None:
        start_guest(client)
        options = client.post("/auth/passkeys/registration/options").json()
        body = {"credential": authenticator.register(options, ORIGIN)}

        clock.advance(minutes=6)
        response = client.post("/auth/passkeys/registration/verify", json=body)

        assert response.status_code == 400
        assert client.get("/me").json()["is_guest"] is True

    def test_a_challenge_for_signing_in_cannot_register_a_passkey(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        signing_in = client.post("/auth/passkeys/authentication/options").json()
        registration = client.post("/auth/passkeys/registration/options").json()
        registration["challenge"] = signing_in["challenge"]

        response = client.post(
            "/auth/passkeys/registration/verify",
            json={"credential": authenticator.register(registration, ORIGIN)},
        )

        assert response.status_code == 400

    def test_a_challenge_issued_to_someone_else_is_refused(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
    ) -> None:
        victim, attacker = make_client(), make_client()
        start_guest(victim)
        start_guest(attacker)
        options = victim.post("/auth/passkeys/registration/options").json()

        response = attacker.post(
            "/auth/passkeys/registration/verify",
            json={"credential": authenticator.register(options, ORIGIN)},
        )

        assert response.status_code == 400
        assert attacker.get("/me").json()["is_guest"] is True

    def test_a_passkey_made_for_another_site_is_refused(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        options = client.post("/auth/passkeys/registration/options").json()

        response = client.post(
            "/auth/passkeys/registration/verify",
            json={
                "credential": authenticator.register(options, "https://evil.example")
            },
        )

        assert response.status_code == 400

    def test_a_bad_answer_uses_the_challenge_up(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        options = client.post("/auth/passkeys/registration/options").json()
        bad = authenticator.register(options, "https://evil.example")
        good = authenticator.register(options, ORIGIN)
        assert (
            client.post(
                "/auth/passkeys/registration/verify", json={"credential": bad}
            ).status_code
            == 400
        )

        retry = client.post(
            "/auth/passkeys/registration/verify", json={"credential": good}
        )

        assert retry.status_code == 400

    def test_garbage_is_a_400_not_a_crash(self, client: TestClient) -> None:
        start_guest(client)

        for credential in ({}, {"response": {"clientDataJSON": "!!"}}):
            response = client.post(
                "/auth/passkeys/registration/verify", json={"credential": credential}
            )

            assert response.status_code == 400


class TestLoginSessions:
    def test_a_guests_session_ends_after_thirty_days(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        clock.advance(days=30, seconds=1)

        assert client.get("/me").status_code == 401

    def test_using_the_app_keeps_a_guests_session_alive(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        clock.advance(days=20)
        assert client.get("/me").status_code == 200
        clock.advance(days=20)

        assert client.get("/me").status_code == 200

    def test_an_accounts_session_ends_after_a_day(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        start_guest(client)
        register_passkey(client, authenticator)

        clock.advance(days=1, seconds=1)

        assert client.get("/me").status_code == 401

    def test_using_the_app_keeps_an_accounts_session_alive(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        start_guest(client)
        register_passkey(client, authenticator)

        clock.advance(hours=20)
        assert client.get("/me").status_code == 200
        clock.advance(hours=20)

        assert client.get("/me").status_code == 200

    def test_signing_in_with_a_passkey_gives_the_accounts_lifetime(
        self,
        make_client: Browsers,
        authenticator: SoftwareAuthenticator,
        clock: FakeClock,
    ) -> None:
        first, second = make_client(), make_client()
        start_guest(first)
        register_passkey(first, authenticator)
        sign_in(second, authenticator)

        clock.advance(days=1, seconds=1)

        assert second.get("/me").status_code == 401

    def test_adding_a_passkey_changes_the_cookie_to_the_accounts_lifetime(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        guest = client.post("/auth/guest")
        options = client.post("/auth/passkeys/registration/options").json()

        saved = client.post(
            "/auth/passkeys/registration/verify",
            json={"credential": authenticator.register(options, ORIGIN)},
        )

        assert "max-age=2592000" in guest.headers["set-cookie"].lower()
        assert "max-age=86400" in saved.headers["set-cookie"].lower()

    def test_the_cookie_is_sent_again_when_the_expiry_moves(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        quick = client.get("/me")
        clock.advance(hours=2)
        later = client.get("/me")

        assert "set-cookie" not in quick.headers
        assert "session=" in later.headers["set-cookie"]

    def test_a_session_used_again_within_the_hour_is_not_extended(
        self, client: TestClient, clock: FakeClock, engine: Engine
    ) -> None:
        start_guest(client)
        clock.advance(minutes=30)

        client.get("/me")

        with engine.connect() as connection:
            expires: datetime = connection.execute(
                text("SELECT expires_at FROM login_sessions")
            ).scalar_one()
        assert expires == clock.now - timedelta(minutes=30) + timedelta(days=30)

    def test_a_cookie_that_is_not_a_session_is_refused(
        self, client: TestClient
    ) -> None:
        client.cookies.set("session", "garbage")

        assert client.get("/me").status_code == 401

    def test_expired_sessions_are_removed_when_someone_signs_in(
        self, make_client: Browsers, clock: FakeClock, engine: Engine
    ) -> None:
        start_guest(make_client())
        clock.advance(days=31)

        start_guest(make_client())

        assert len(stored_token_hashes(engine)) == 1


class TestSignOut:
    def test_signing_out_ends_the_session_and_clears_the_cookie(
        self, client: TestClient
    ) -> None:
        start_guest(client)

        response = client.post("/auth/logout")

        assert response.status_code == 204
        assert "max-age=0" in response.headers["set-cookie"].lower()
        assert client.get("/me").status_code == 401

    def test_signing_out_twice_is_fine(self, client: TestClient) -> None:
        start_guest(client)
        client.post("/auth/logout")

        assert client.post("/auth/logout").status_code == 204

    def test_signing_out_does_not_sign_out_other_browsers(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        first, second = make_client(), make_client()
        start_guest(first)
        register_passkey(first, authenticator)
        sign_in(second, authenticator)

        first.post("/auth/logout")

        assert second.get("/me").status_code == 200


class TestPasskeys:
    def test_a_passkey_can_be_removed_while_another_remains(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        first = register_passkey(client, authenticator)
        register_passkey(client, SoftwareAuthenticator())

        response = client.delete(f"/me/passkeys/{first['id']}")

        assert response.status_code == 204
        assert len(client.get("/me/passkeys").json()) == 1

    def test_the_last_passkey_cannot_be_removed(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        only = register_passkey(client, authenticator)

        response = client.delete(f"/me/passkeys/{only['id']}")

        assert response.status_code == 409
        assert client.get("/me").json()["is_guest"] is False

    def test_another_users_passkey_cannot_be_removed(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        owner, other = make_client(), make_client()
        start_guest(owner)
        theirs = register_passkey(owner, authenticator)
        start_guest(other)
        register_passkey(other, SoftwareAuthenticator())

        response = other.delete(f"/me/passkeys/{theirs['id']}")

        assert response.status_code == 404
        assert len(owner.get("/me/passkeys").json()) == 1

    def test_a_guest_has_none(self, client: TestClient) -> None:
        start_guest(client)

        assert client.get("/me/passkeys").json() == []
        assert (
            client.delete(
                "/me/passkeys/00000000-0000-0000-0000-000000000000"
            ).status_code
            == 404
        )

    def test_the_key_material_is_not_exposed(
        self, client: TestClient, authenticator: SoftwareAuthenticator
    ) -> None:
        start_guest(client)
        register_passkey(client, authenticator)

        [passkey] = client.get("/me/passkeys").json()

        assert set(passkey) == {"id", "label", "created_at", "last_used_at"}


class TestDeleteAccount:
    def test_removes_everything_the_user_has(
        self,
        client: TestClient,
        authenticator: SoftwareAuthenticator,
        engine: Engine,
    ) -> None:
        start_guest(client)
        answer(client, offer(client)["selection_id"])
        offer(client)
        client.patch("/me/settings", json={"slow_welsh_enabled": False})
        register_passkey(client, authenticator)
        client.post("/auth/passkeys/registration/options")

        response = client.delete("/me")

        assert response.status_code == 204
        assert "max-age=0" in response.headers["set-cookie"].lower()
        assert row_counts(engine) == dict.fromkeys(Base.metadata.tables, 0)
        assert client.get("/me").status_code == 401

    def test_leaves_other_users_alone(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        leaving, staying = make_client(), make_client()
        start_guest(leaving)
        start_guest(staying)
        register_passkey(staying, authenticator)
        answer(staying, offer(staying)["selection_id"])

        leaving.delete("/me")

        assert staying.get("/me").status_code == 200
        assert progress(staying)["introduced"] == 1

    def test_a_deleted_passkey_no_longer_signs_in(
        self, make_client: Browsers, authenticator: SoftwareAuthenticator
    ) -> None:
        member, browser = make_client(), make_client()
        start_guest(member)
        register_passkey(member, authenticator)
        member.delete("/me")
        options = browser.post("/auth/passkeys/authentication/options").json()

        response = browser.post(
            "/auth/passkeys/authentication/verify",
            json={"credential": authenticator.sign_in(options, ORIGIN)},
        )

        assert response.status_code == 400


class TestSignedOutRoutes:
    @pytest.mark.parametrize(
        ("method", "path"),
        [
            ("GET", "/me"),
            ("DELETE", "/me"),
            ("GET", "/me/passkeys"),
            ("DELETE", "/me/passkeys/00000000-0000-0000-0000-000000000000"),
            ("POST", "/me/next"),
            ("POST", "/me/outcomes"),
            ("GET", "/me/progress"),
            ("POST", "/auth/passkeys/registration/options"),
            ("POST", "/auth/passkeys/registration/verify"),
        ],
    )
    def test_are_refused_without_a_session(
        self, client: TestClient, method: str, path: str
    ) -> None:
        response = client.request(method, path, json={})

        assert response.status_code == 401

    def test_the_public_routes_need_no_session(self, client: TestClient) -> None:
        assert client.get("/health").status_code == 200
        assert client.get("/course").status_code == 200

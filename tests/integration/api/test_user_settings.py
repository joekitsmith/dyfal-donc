from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from tests.integration.api.helpers import start_guest

Browsers = Callable[[], TestClient]

DEFAULTS = {
    "think_time_multiplier": 1.0,
    "slow_welsh_enabled": True,
    "learning_session_minutes": 20,
}


class TestDefaults:
    def test_a_new_user_has_the_defaults(self, client: TestClient) -> None:
        start_guest(client)

        response = client.get("/me/settings")

        assert response.status_code == 200
        assert response.json() == DEFAULTS


class TestChanging:
    def test_a_patch_changes_only_what_it_names(self, client: TestClient) -> None:
        start_guest(client)

        response = client.patch("/me/settings", json={"think_time_multiplier": 2.5})

        assert response.status_code == 200
        assert response.json() == {**DEFAULTS, "think_time_multiplier": 2.5}
        assert client.get("/me/settings").json() == {
            **DEFAULTS,
            "think_time_multiplier": 2.5,
        }

    def test_later_patches_keep_earlier_changes(self, client: TestClient) -> None:
        start_guest(client)
        client.patch("/me/settings", json={"slow_welsh_enabled": False})

        response = client.patch("/me/settings", json={"think_time_multiplier": 2})

        assert response.json() == {
            **DEFAULTS,
            "slow_welsh_enabled": False,
            "think_time_multiplier": 2,
        }

    def test_an_empty_patch_changes_nothing(self, client: TestClient) -> None:
        start_guest(client)

        assert client.patch("/me/settings", json={}).json() == DEFAULTS

    def test_null_minutes_means_no_limit_and_leaving_them_out_means_unchanged(
        self, client: TestClient
    ) -> None:
        start_guest(client)

        unlimited = client.patch(
            "/me/settings", json={"learning_session_minutes": None}
        )
        untouched = client.patch("/me/settings", json={"slow_welsh_enabled": False})

        assert unlimited.json()["learning_session_minutes"] is None
        assert untouched.json()["learning_session_minutes"] is None

    def test_settings_belong_to_one_user(self, make_client: Browsers) -> None:
        first, second = make_client(), make_client()
        start_guest(first)
        start_guest(second)

        first.patch("/me/settings", json={"think_time_multiplier": 3})

        assert second.get("/me/settings").json() == DEFAULTS


class TestValidation:
    @pytest.mark.parametrize(
        "change",
        [
            {"think_time_multiplier": 0.4},
            {"think_time_multiplier": 3.1},
            {"think_time_multiplier": None},
            {"slow_welsh_enabled": None},
            {"learning_session_minutes": 15},
            {"learning_session_minutes": 0},
        ],
    )
    def test_a_bad_value_is_refused_and_nothing_is_saved(
        self, client: TestClient, change: dict[str, object]
    ) -> None:
        start_guest(client)

        response = client.patch("/me/settings", json=change)

        assert response.status_code == 422
        assert client.get("/me/settings").json() == DEFAULTS

    def test_the_limits_themselves_are_allowed(self, client: TestClient) -> None:
        start_guest(client)

        low = client.patch("/me/settings", json={"think_time_multiplier": 0.5})
        high = client.patch("/me/settings", json={"think_time_multiplier": 3})

        assert (low.status_code, high.status_code) == (200, 200)


class TestWhoMayChangeThem:
    def test_signed_out_is_refused(self, client: TestClient) -> None:
        assert client.get("/me/settings").status_code == 401
        assert client.patch("/me/settings", json={}).status_code == 401

    def test_a_foreign_origin_is_refused(self, client: TestClient) -> None:
        start_guest(client)

        response = client.patch(
            "/me/settings",
            json={"slow_welsh_enabled": False},
            headers={"Origin": "https://evil.example"},
        )

        assert response.status_code == 403
        assert client.get("/me/settings").json() == DEFAULTS

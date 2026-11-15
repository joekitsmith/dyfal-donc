from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from tests.integration.api.helpers import start_guest

Browsers = Callable[[], TestClient]

DEFAULTS = {"think_time_multiplier": 1.0, "welsh_playback": "both"}


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
        client.patch("/me/settings", json={"welsh_playback": "slow"})

        response = client.patch("/me/settings", json={"think_time_multiplier": 2})

        assert response.json() == {"welsh_playback": "slow", "think_time_multiplier": 2}

    def test_an_empty_patch_changes_nothing(self, client: TestClient) -> None:
        start_guest(client)

        assert client.patch("/me/settings", json={}).json() == DEFAULTS

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
            {"welsh_playback": "never"},
            {"welsh_playback": 2},
            {"welsh_playback": None},
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
        fast = client.patch("/me/settings", json={"welsh_playback": "standard"})

        assert (low.status_code, high.status_code, fast.status_code) == (200, 200, 200)


class TestWhoMayChangeThem:
    def test_signed_out_is_refused(self, client: TestClient) -> None:
        assert client.get("/me/settings").status_code == 401
        assert client.patch("/me/settings", json={}).status_code == 401

    def test_a_foreign_origin_is_refused(self, client: TestClient) -> None:
        start_guest(client)

        response = client.patch(
            "/me/settings",
            json={"welsh_playback": "standard"},
            headers={"Origin": "https://evil.example"},
        )

        assert response.status_code == 403
        assert client.get("/me/settings").json() == DEFAULTS

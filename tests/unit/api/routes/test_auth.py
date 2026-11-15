import pytest
from fastapi.testclient import TestClient

ORIGIN = "http://localhost:8080"
CHANGING_PATHS = (
    "/auth/guest",
    "/auth/logout",
    "/auth/passkeys/registration/options",
    "/auth/passkeys/authentication/options",
    "/me/next",
    "/me/outcomes",
)


class TestOriginCheck:
    @pytest.mark.parametrize("path", CHANGING_PATHS)
    def test_a_request_that_changes_something_needs_the_apps_origin(
        self, client: TestClient, path: str
    ) -> None:
        missing = client.post(path)
        foreign = client.post(path, headers={"Origin": "https://evil.example"})

        assert missing.status_code == 403
        assert foreign.status_code == 403

    def test_deleting_the_account_needs_the_apps_origin(
        self, client: TestClient
    ) -> None:
        assert client.delete("/me").status_code == 403

    def test_a_known_origin_gets_past_the_check(self, client: TestClient) -> None:
        response = client.post("/me/next", headers={"Origin": ORIGIN})

        assert response.status_code == 401

    def test_the_development_server_is_a_known_origin(self, client: TestClient) -> None:
        response = client.post("/me/next", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 401

    def test_reading_needs_no_origin(self, client: TestClient) -> None:
        assert client.get("/me").status_code == 401


class TestSignedOut:
    @pytest.mark.parametrize("path", ("/me", "/me/progress", "/me/passkeys"))
    def test_account_and_progress_reads_are_401(
        self, client: TestClient, path: str
    ) -> None:
        response = client.get(path)

        assert response.status_code == 401
        assert response.json() == {"detail": "Not signed in"}


class TestRemovedRoutes:
    def test_the_learner_routes_are_gone(self, client: TestClient) -> None:
        assert client.post("/learners", headers={"Origin": ORIGIN}).status_code == 404

from fastapi.testclient import TestClient


class TestHealth:
    def test_reports_ok(self, client: TestClient) -> None:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

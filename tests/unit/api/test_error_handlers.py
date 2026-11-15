from collections.abc import Callable

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.error_handlers import STATUS_FOR_ERROR, register_error_handlers


def app_raising(error: Exception) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app)

    @app.get("/fail")
    def fail() -> None:
        raise error

    return app


class TestErrorHandlers:
    @pytest.mark.parametrize(
        ("error_type", "status_code"),
        STATUS_FOR_ERROR.items(),
        ids=lambda value: getattr(value, "__name__", str(value)),
    )
    def test_each_error_becomes_its_status(
        self, error_type: Callable[[str], Exception], status_code: int
    ) -> None:
        client = TestClient(app_raising(error_type("It went wrong")))

        response = client.get("/fail")

        assert response.status_code == status_code
        assert response.json() == {"detail": "It went wrong"}

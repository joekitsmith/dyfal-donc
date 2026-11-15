import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from persistence.database.models import PROBLEM_REPORT_CATEGORIES
from tests.integration.api.conftest import START
from tests.integration.api.helpers import start_guest

ITEM_ID = "lex:siarad"


def stored_reports(engine: Engine) -> list[dict[str, object]]:
    with engine.connect() as connection:
        rows = connection.execute(
            text("SELECT * FROM problem_reports ORDER BY id")
        ).mappings()
        return [dict(row) for row in rows]


def report(**changes: object) -> dict[str, object]:
    return {
        "source": "lesson",
        "category": "grammar",
        "description": "The verb is wrong",
        **changes,
    }


@pytest.fixture
def exercise_id(app: FastAPI) -> str:
    return next(iter(app.state.course_release.exercises))


class TestReporting:
    def test_a_report_about_a_sentence_is_stored(
        self, client: TestClient, app: FastAPI, engine: Engine, exercise_id: str
    ) -> None:
        start_guest(client)

        response = client.post(
            "/me/problem-reports", json=report(exercise_id=exercise_id)
        )

        assert response.status_code == 204
        assert response.content == b""
        [stored] = stored_reports(engine)
        assert stored["exercise_id"] == exercise_id
        assert stored["item_id"] is None
        assert stored["release_hash"] == app.state.course_release.hash
        assert stored["source"] == "lesson"
        assert stored["category"] == "grammar"
        assert stored["description"] == "The verb is wrong"
        assert stored["created_at"] == START
        assert stored["resolved_at"] is None

    def test_a_report_about_a_word_is_stored(
        self, client: TestClient, engine: Engine
    ) -> None:
        start_guest(client)

        response = client.post(
            "/me/problem-reports", json=report(item_id=ITEM_ID, source="item")
        )

        assert response.status_code == 204
        [stored] = stored_reports(engine)
        assert stored["item_id"] == ITEM_ID
        assert stored["exercise_id"] is None

    def test_something_else_needs_neither(
        self, client: TestClient, engine: Engine
    ) -> None:
        start_guest(client)

        response = client.post(
            "/me/problem-reports",
            json=report(source="general", category="other"),
        )

        assert response.status_code == 204
        [stored] = stored_reports(engine)
        assert stored["exercise_id"] is None
        assert stored["item_id"] is None

    def test_the_description_is_trimmed(
        self, client: TestClient, engine: Engine
    ) -> None:
        start_guest(client)

        client.post("/me/problem-reports", json=report(description="  Odd  \n"))

        assert stored_reports(engine)[0]["description"] == "Odd"

    @pytest.mark.parametrize("category", PROBLEM_REPORT_CATEGORIES)
    def test_every_category_is_accepted(
        self, client: TestClient, category: str
    ) -> None:
        start_guest(client)

        response = client.post("/me/problem-reports", json=report(category=category))

        assert response.status_code == 204


class TestRejecting:
    @pytest.mark.parametrize(
        "changes",
        [
            {"description": ""},
            {"description": "   "},
            {"description": "x" * 1001},
            {"source": "elsewhere"},
            {"category": "rude"},
            {"exercise_id": "a", "item_id": "b"},
        ],
    )
    def test_a_malformed_report_is_unprocessable(
        self, client: TestClient, engine: Engine, changes: dict[str, object]
    ) -> None:
        start_guest(client)

        response = client.post("/me/problem-reports", json=report(**changes))

        assert response.status_code == 422
        assert stored_reports(engine) == []

    @pytest.mark.parametrize(
        "changes", [{"exercise_id": "no-such-exercise"}, {"item_id": "lex:no-such"}]
    )
    def test_a_sentence_or_word_that_does_not_exist_is_unprocessable(
        self, client: TestClient, engine: Engine, changes: dict[str, object]
    ) -> None:
        start_guest(client)

        response = client.post("/me/problem-reports", json=report(**changes))

        assert response.status_code == 422
        assert stored_reports(engine) == []

    def test_the_longest_description_is_accepted(self, client: TestClient) -> None:
        start_guest(client)

        response = client.post(
            "/me/problem-reports", json=report(description="x" * 1000)
        )

        assert response.status_code == 204

    def test_needs_a_login_session(self, client: TestClient) -> None:
        response = client.post("/me/problem-reports", json=report())

        assert response.status_code == 401

    def test_needs_the_apps_own_origin(self, client: TestClient) -> None:
        start_guest(client)

        response = client.post(
            "/me/problem-reports",
            json=report(),
            headers={"Origin": "http://elsewhere.example"},
        )

        assert response.status_code == 403

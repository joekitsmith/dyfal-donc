import uuid
from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.integration.api.conftest import FakeClock
from tests.integration.api.helpers import (
    answer,
    offer,
    progress,
    start_guest,
)


class TestTheLearnLoop:
    def test_a_new_learner_is_offered_an_introduction(self, client: TestClient) -> None:
        start_guest(client)

        body = offer(client)

        assert body["kind"] == "exercise"
        assert body["purpose"] == "introduction"
        assert body["introduces"] is not None
        assert body["english"] and body["welsh"]
        uuid.UUID(str(body["selection_id"]))

    def test_answering_records_the_outcome_and_moves_the_learner_on(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        first = offer(client)

        recorded = answer(client, first["selection_id"])
        clock.advance(minutes=1)
        second = offer(client)

        assert recorded == {"sequence": 1, "recorded": True}
        assert second["selection_id"] != first["selection_id"]
        counts = progress(client)
        assert counts["introduced"] == 1
        assert counts["learning"] == 1

    def test_many_correct_answers_introduce_more_of_the_course(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        for _ in range(30):
            body = offer(client)
            assert body["kind"] == "exercise"
            answer(client, body["selection_id"])
            clock.advance(minutes=1)

        counts = progress(client)
        assert counts["introduced"] > 5
        assert counts["recent_error_rate"] == 0.0
        assert counts["introduced"] == counts["learning"] + counts["in_review"]

    def test_a_missed_exercise_shows_in_the_error_rate(
        self, client: TestClient
    ) -> None:
        start_guest(client)

        answer(client, offer(client)["selection_id"], "missed_it")

        assert progress(client)["recent_error_rate"] == 1.0

    def test_learners_progress_separately(
        self, make_client: Callable[[], TestClient]
    ) -> None:
        busy, idle = make_client(), make_client()
        start_guest(busy)
        start_guest(idle)

        answer(busy, offer(busy)["selection_id"])

        assert progress(busy)["introduced"] == 1
        assert progress(idle)["introduced"] == 0


class TestRepeatedAnswers:
    def test_the_same_outcome_again_returns_the_original_result(
        self, client: TestClient
    ) -> None:
        start_guest(client)
        selection_id = offer(client)["selection_id"]
        answer(client, selection_id)

        repeat = answer(client, selection_id)

        assert repeat == {"sequence": 1, "recorded": False}
        assert progress(client)["introduced"] == 1

    def test_a_different_outcome_for_an_answered_selection_is_a_conflict(
        self, client: TestClient
    ) -> None:
        start_guest(client)
        selection_id = offer(client)["selection_id"]
        answer(client, selection_id)

        response = client.post(
            "/me/outcomes",
            json={"selection_id": selection_id, "outcome": "missed_it"},
        )

        assert response.status_code == 409

    def test_an_expired_selection_cannot_be_answered(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        selection_id = offer(client)["selection_id"]

        clock.advance(hours=2)
        response = client.post(
            "/me/outcomes", json={"selection_id": selection_id, "outcome": "got_it"}
        )

        assert response.status_code == 410
        assert progress(client)["introduced"] == 0


class TestErrors:
    def test_an_unknown_selection_is_not_found(self, client: TestClient) -> None:
        start_guest(client)

        response = client.post(
            "/me/outcomes",
            json={"selection_id": str(uuid.uuid4()), "outcome": "got_it"},
        )

        assert response.status_code == 404

    def test_a_learner_cannot_answer_anothers_selection(
        self, make_client: Callable[[], TestClient]
    ) -> None:
        owner, other = make_client(), make_client()
        start_guest(owner)
        start_guest(other)
        selection_id = offer(owner)["selection_id"]

        response = other.post(
            "/me/outcomes", json={"selection_id": selection_id, "outcome": "got_it"}
        )

        assert response.status_code == 404

    def test_an_unknown_outcome_is_rejected(self, client: TestClient) -> None:
        start_guest(client)
        selection_id = offer(client)["selection_id"]

        response = client.post(
            "/me/outcomes", json={"selection_id": selection_id, "outcome": "maybe"}
        )

        assert response.status_code == 422


class TestNothingToOffer:
    def test_says_so_instead_of_failing(
        self, client_without_exercises: TestClient
    ) -> None:
        start_guest(client_without_exercises)

        response = client_without_exercises.post("/me/next")

        assert response.status_code == 200
        assert response.json() == {"kind": "nothing_eligible"}

    def test_nothing_is_recorded_as_issued(
        self, client_without_exercises: TestClient, engine: Engine
    ) -> None:
        start_guest(client_without_exercises)
        client_without_exercises.post("/me/next")

        with engine.connect() as connection:
            issued: int = connection.execute(
                text("SELECT count(*) FROM issued_selections")
            ).scalar_one()

        assert issued == 0

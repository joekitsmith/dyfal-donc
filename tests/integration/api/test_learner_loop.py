import uuid

from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from tests.integration.api.conftest import FakeClock


def create_learner(client: TestClient) -> str:
    response = client.post("/learners")
    assert response.status_code == 201
    return str(response.json()["id"])


def offer(client: TestClient, learner_id: str) -> dict[str, object]:
    response = client.get(f"/learners/{learner_id}/next")
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def answer(
    client: TestClient, learner_id: str, selection_id: object, outcome: str = "got_it"
) -> dict[str, object]:
    response = client.post(
        f"/learners/{learner_id}/outcomes",
        json={"selection_id": selection_id, "outcome": outcome},
    )
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


class TestCreateLearner:
    def test_starts_on_the_servers_course_release(self, client: TestClient) -> None:
        response = client.post("/learners")

        assert response.status_code == 201
        assert (
            response.json()["course_release"] == client.get("/course").json()["release"]
        )

    def test_every_learner_gets_their_own_id(self, client: TestClient) -> None:
        assert create_learner(client) != create_learner(client)


class TestTheLearnLoop:
    def test_a_new_learner_is_offered_an_introduction(self, client: TestClient) -> None:
        body = offer(client, create_learner(client))

        assert body["kind"] == "exercise"
        assert body["purpose"] == "introduction"
        assert body["introduces"] is not None
        assert body["english"] and body["welsh"]
        uuid.UUID(str(body["selection_id"]))

    def test_answering_records_the_outcome_and_moves_the_learner_on(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        learner_id = create_learner(client)
        first = offer(client, learner_id)

        recorded = answer(client, learner_id, first["selection_id"])
        clock.advance(minutes=1)
        second = offer(client, learner_id)

        assert recorded == {"sequence": 1, "recorded": True}
        assert second["selection_id"] != first["selection_id"]
        progress = client.get(f"/learners/{learner_id}/progress").json()
        assert progress["introduced"] == 1
        assert progress["learning"] == 1

    def test_many_correct_answers_introduce_more_of_the_course(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        learner_id = create_learner(client)

        for _ in range(30):
            body = offer(client, learner_id)
            assert body["kind"] == "exercise"
            answer(client, learner_id, body["selection_id"])
            clock.advance(minutes=1)

        progress = client.get(f"/learners/{learner_id}/progress").json()
        assert progress["introduced"] > 5
        assert progress["recent_error_rate"] == 0.0
        assert progress["introduced"] == progress["learning"] + progress["in_review"]

    def test_a_missed_exercise_shows_in_the_error_rate(
        self, client: TestClient
    ) -> None:
        learner_id = create_learner(client)
        body = offer(client, learner_id)

        answer(client, learner_id, body["selection_id"], "missed_it")

        progress = client.get(f"/learners/{learner_id}/progress").json()
        assert progress["recent_error_rate"] == 1.0

    def test_learners_progress_separately(self, client: TestClient) -> None:
        busy, idle = create_learner(client), create_learner(client)
        answer(client, busy, offer(client, busy)["selection_id"])

        assert client.get(f"/learners/{busy}/progress").json()["introduced"] == 1
        assert client.get(f"/learners/{idle}/progress").json()["introduced"] == 0


class TestRepeatedAnswers:
    def test_the_same_outcome_again_returns_the_original_result(
        self, client: TestClient
    ) -> None:
        learner_id = create_learner(client)
        selection_id = offer(client, learner_id)["selection_id"]
        answer(client, learner_id, selection_id)

        repeat = answer(client, learner_id, selection_id)

        assert repeat == {"sequence": 1, "recorded": False}
        progress = client.get(f"/learners/{learner_id}/progress").json()
        assert progress["introduced"] == 1

    def test_a_different_outcome_for_an_answered_selection_is_a_conflict(
        self, client: TestClient
    ) -> None:
        learner_id = create_learner(client)
        selection_id = offer(client, learner_id)["selection_id"]
        answer(client, learner_id, selection_id)

        response = client.post(
            f"/learners/{learner_id}/outcomes",
            json={"selection_id": selection_id, "outcome": "missed_it"},
        )

        assert response.status_code == 409

    def test_an_expired_selection_cannot_be_answered(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        learner_id = create_learner(client)
        selection_id = offer(client, learner_id)["selection_id"]

        clock.advance(hours=2)
        response = client.post(
            f"/learners/{learner_id}/outcomes",
            json={"selection_id": selection_id, "outcome": "got_it"},
        )

        assert response.status_code == 410
        progress = client.get(f"/learners/{learner_id}/progress").json()
        assert progress["introduced"] == 0


class TestErrors:
    def test_an_unknown_learner_is_not_found(self, client: TestClient) -> None:
        unknown = uuid.uuid4()

        assert client.get(f"/learners/{unknown}/next").status_code == 404
        assert client.get(f"/learners/{unknown}/progress").status_code == 404

    def test_an_unknown_selection_is_not_found(self, client: TestClient) -> None:
        learner_id = create_learner(client)

        response = client.post(
            f"/learners/{learner_id}/outcomes",
            json={"selection_id": str(uuid.uuid4()), "outcome": "got_it"},
        )

        assert response.status_code == 404

    def test_a_learner_cannot_answer_anothers_selection(
        self, client: TestClient
    ) -> None:
        owner, other = create_learner(client), create_learner(client)
        selection_id = offer(client, owner)["selection_id"]

        response = client.post(
            f"/learners/{other}/outcomes",
            json={"selection_id": selection_id, "outcome": "got_it"},
        )

        assert response.status_code == 404

    def test_an_unknown_outcome_is_rejected(self, client: TestClient) -> None:
        learner_id = create_learner(client)
        selection_id = offer(client, learner_id)["selection_id"]

        response = client.post(
            f"/learners/{learner_id}/outcomes",
            json={"selection_id": selection_id, "outcome": "maybe"},
        )

        assert response.status_code == 422

    def test_a_malformed_learner_id_is_rejected(self, client: TestClient) -> None:
        assert client.get("/learners/not-a-uuid/next").status_code == 422


class TestNothingToOffer:
    def test_says_why_instead_of_failing(
        self, client_without_exercises: TestClient
    ) -> None:
        learner_id = create_learner(client_without_exercises)

        response = client_without_exercises.get(f"/learners/{learner_id}/next")

        assert response.status_code == 200
        assert response.json() == {"kind": "nothing_eligible"}

    def test_nothing_is_recorded_as_issued(
        self, client_without_exercises: TestClient, engine: Engine
    ) -> None:
        learner_id = create_learner(client_without_exercises)
        client_without_exercises.get(f"/learners/{learner_id}/next")

        with engine.connect() as connection:
            issued: int = connection.execute(
                text("SELECT count(*) FROM issued_selections")
            ).scalar_one()

        assert issued == 0

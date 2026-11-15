from collections.abc import Callable

from fastapi.testclient import TestClient

from tests.integration.api.conftest import FakeClock
from tests.integration.api.helpers import answer, offer, start_guest

Browsers = Callable[[], TestClient]


def complete(
    client: TestClient,
    clock: FakeClock,
    *,
    minutes_later: float = 1,
    outcome: str = "got_it",
) -> dict[str, object]:
    """Waits, is given an exercise, and answers it straight away. Returns the exercise."""
    clock.advance(minutes=minutes_later)
    exercise = offer(client)
    answer(client, exercise["selection_id"], outcome)
    return exercise


def overview(client: TestClient) -> dict[str, object]:
    response = client.get("/me/overview")
    assert response.status_code == 200
    body: dict[str, object] = response.json()
    return body


def summary(client: TestClient, session_id: object) -> dict[str, object]:
    response = client.get(f"/me/learning-sessions/{session_id}/summary")
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


def latest(client: TestClient) -> dict[str, object]:
    session = overview(client)["latest_session"]
    assert isinstance(session, dict)
    return session


class TestOverviewOfANewLearner:
    def test_has_no_session_and_nothing_due(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)

        body = overview(client)

        assert body["latest_session"] is None
        assert body["introduced"] == 0
        assert (body["review_due"], body["learning_due"]) == (0, 0)
        assert body["new_words_ready"] is True
        assert isinstance(body["topic"], str)
        assert isinstance(body["course_items"], int)
        assert body["course_items"] > 0
        assert body["now"] == clock().isoformat().replace("+00:00", "Z")


class TestOverviewMidCourse:
    def test_describes_the_latest_session_and_the_course_position(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        for _ in range(3):
            complete(client, clock)

        body = overview(client)
        session = latest(client)

        assert body["introduced"] == len(session["items_introduced"])  # type: ignore[arg-type]
        assert body["introduced"] >= 1
        assert session["id"] == 1
        assert session["exercises_completed"] == 3
        assert session["duration_seconds"] == 120
        assert session["ongoing"] is True

    def test_names_the_words_introduced_in_both_languages(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        first = complete(client, clock)

        introduced = latest(client)["items_introduced"]

        assert isinstance(introduced, list)
        assert len(introduced) == 1
        assert introduced[0]["id"] == first["introduces"]
        assert introduced[0]["welsh"]
        assert introduced[0]["english"]

    def test_the_session_is_over_once_the_pause_is_longer_than_ten_minutes(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)

        clock.advance(minutes=10)
        assert latest(client)["ongoing"] is True

        clock.advance(seconds=1)
        assert latest(client)["ongoing"] is False

    def test_an_answer_after_a_long_pause_starts_a_new_session(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        complete(client, clock)
        complete(client, clock, minutes_later=60)

        session = latest(client)

        assert session["id"] == 3
        assert session["exercises_completed"] == 1
        assert session["duration_seconds"] == 0
        assert session["items_introduced"] == []

    def test_an_answer_within_ten_minutes_carries_the_session_on(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        complete(client, clock, minutes_later=10)

        session = latest(client)

        assert session["id"] == 1
        assert session["exercises_completed"] == 2
        assert session["duration_seconds"] == 600


class TestSummary:
    def test_an_earlier_session_can_still_be_read_after_a_later_one_begins(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        complete(client, clock)
        complete(client, clock, minutes_later=60)
        complete(client, clock)

        first = summary(client, 1)
        second = summary(client, 3)

        assert (first["exercises_completed"], first["ongoing"]) == (2, False)
        assert (second["exercises_completed"], second["ongoing"]) == (2, True)

        met_first = {item["id"] for item in first["items_introduced"]}  # type: ignore[attr-defined]
        met_second = {item["id"] for item in second["items_introduced"]}  # type: ignore[attr-defined]
        assert met_first
        assert not met_first & met_second

    def test_lists_a_missed_exercise_with_its_text_and_audio(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        missed = complete(client, clock, outcome="missed_it")
        complete(client, clock)

        body = summary(client, 1)

        assert body["missed_exercises"] == [
            {
                "id": body["missed_exercises"][0]["id"],  # type: ignore[index]
                "english": missed["english"],
                "welsh": missed["welsh"],
                "audio": missed["audio"],
            }
        ]
        assert body["missed_exercises"][0]["id"]  # type: ignore[index]

    def test_a_session_with_no_misses_lists_none(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)

        body = summary(client, 1)

        assert body["missed_exercises"] == []
        assert body["items_lapsed"] == []
        assert body["items_reviewed"] == 0

    def test_a_number_that_is_not_the_start_of_a_session_is_a_404(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        complete(client, clock)

        assert client.get("/me/learning-sessions/2/summary").status_code == 404
        assert client.get("/me/learning-sessions/99/summary").status_code == 404

    def test_a_session_of_someone_else_is_a_404(
        self, make_client: Browsers, clock: FakeClock
    ) -> None:
        first, second = make_client(), make_client()
        start_guest(first)
        start_guest(second)
        complete(first, clock)

        assert first.get("/me/learning-sessions/1/summary").status_code == 200
        assert second.get("/me/learning-sessions/1/summary").status_code == 404
        assert overview(second)["latest_session"] is None


class TestWhoMayAsk:
    def test_signed_out_is_refused(self, client: TestClient) -> None:
        assert client.get("/me/overview").status_code == 401
        assert client.get("/me/learning-sessions/1/summary").status_code == 401

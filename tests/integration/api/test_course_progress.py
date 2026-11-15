from collections.abc import Iterator
from pathlib import Path
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.integration.api.conftest import ORIGIN, FakeClock, build_app
from tests.integration.api.helpers import start_guest
from tests.integration.api.test_learning_sessions import complete, overview


@pytest.fixture
def small_course(tmp_path: Path) -> Path:
    """Two topics with a word each, and one exercise for each."""
    for directory in ("patterns", "lexemes", "order", "exercises"):
        (tmp_path / directory).mkdir()

    for directory in ("patterns", "order", "lexemes", "exercises"):
        for name in ("spine", "food"):
            (tmp_path / directory / f"{name}.yaml").write_text("[]\n", encoding="utf-8")

    words = (
        ("spine", "siarad", "to speak", "verb"),
        ("food", "coffi", "coffee", "noun"),
    )
    for topic, welsh, english, part_of_speech in words:
        (tmp_path / "lexemes" / f"{topic}.yaml").write_text(
            f"- id: lex:{welsh}\n  welsh: {welsh}\n  english: {english}\n"
            f"  part_of_speech: {part_of_speech}\n",
            encoding="utf-8",
        )
        (tmp_path / "order" / f"{topic}.yaml").write_text(
            f"- lex:{welsh}\n", encoding="utf-8"
        )
        (tmp_path / "exercises" / f"{topic}.yaml").write_text(
            f"- id: {welsh}\n  english: {english}\n  welsh: {welsh}\n"
            f"  items: [lex:{welsh}]\n  new_item: lex:{welsh}\n",
            encoding="utf-8",
        )

    (tmp_path / "topics.yaml").write_text(
        "- name: spine\n- name: food\n  requires: [spine]\n", encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def small_client(
    engine: Engine, clock: FakeClock, small_course: Path
) -> Iterator[TestClient]:
    with TestClient(
        build_app(engine, clock, small_course), headers={"Origin": ORIGIN}
    ) as test_client:
        yield test_client


def course(client: TestClient) -> list[dict[str, object]]:
    response = client.get("/me/course")
    assert response.status_code == 200, response.text
    topics: list[dict[str, object]] = response.json()["topics"]
    return topics


def item(client: TestClient, item_id: str) -> dict[str, object]:
    response = client.get(f"/me/items/{quote(item_id, safe='')}")
    assert response.status_code == 200, response.text
    body: dict[str, object] = response.json()
    return body


def met_ids(topics: list[dict[str, object]]) -> list[str]:
    return [
        str(entry["id"])
        for topic in topics
        for key in ("words", "phrases")
        for entry in topic[key]  # type: ignore[attr-defined]
    ]


class TestCourseOfANewLearner:
    def test_lists_every_topic_in_order_and_none_started(
        self, client: TestClient
    ) -> None:
        start_guest(client)

        topics = course(client)

        assert [topic["name"] for topic in topics][:2] == ["spine", "food"]
        assert [topic["started"] for topic in topics] == [False] * len(topics)
        assert [topic["is_current"] for topic in topics][0] is True
        assert sum(topic["is_current"] is True for topic in topics) == 1
        assert met_ids(topics) == []
        assert all(topic["sayable"] == [] for topic in topics)

    def test_needs_a_login_session(self, client: TestClient) -> None:
        assert client.get("/me/course").status_code == 401


class TestCourseMidWay:
    def test_shows_only_what_has_been_met_in_the_started_topic(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        for _ in range(8):
            complete(client, clock)

        topics = course(client)
        started = [topic for topic in topics if topic["started"]]

        assert [topic["name"] for topic in started] == ["spine"]
        assert started[0]["is_current"] is True
        assert started[0]["exercises_answered"] == 8
        assert len(met_ids(topics)) == overview(client)["introduced"]
        for unstarted in topics[1:]:
            assert unstarted["words"] == []
            assert unstarted["phrases"] == []
            assert unstarted["sayable"] == []

    def test_offers_sentences_the_learner_got_right_with_audio(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        completed = [complete(client, clock) for _ in range(4)]

        (spine, *_rest) = course(client)
        sayable = spine["sayable"]

        assert isinstance(sayable, list)
        assert 0 < len(sayable) <= 5
        for sentence in sayable:
            assert sentence["english"]
            assert sentence["welsh"]
            assert sentence["audio"]["welsh"]["slow"]
        assert {sentence["english"] for sentence in sayable} <= {
            str(exercise["english"]) for exercise in completed
        }

    def test_leaves_out_an_exercise_that_was_only_missed(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock, outcome="missed_it")

        (spine, *_rest) = course(client)

        assert spine["exercises_answered"] == 1
        assert spine["sayable"] == []


class TestItemDetail:
    def test_describes_an_item_the_learner_has_met(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        for _ in range(6):
            complete(client, clock)
        (spine, *_rest) = course(client)
        word = spine["words"][0]  # type: ignore[index]

        detail = item(client, word["id"])

        assert detail["kind"] == "word"
        assert (detail["welsh"], detail["english"]) == (word["welsh"], word["english"])
        assert detail["topic"] == "spine"
        assert detail["audio"] == f"/items/{quote(word['id'], safe='')}/audio"
        assert isinstance(detail["first_met_at"], str)
        assert isinstance(detail["examples"], list)
        assert len(detail["examples"]) <= 5

    def test_a_phrase_has_no_audio_link(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        for _ in range(6):
            complete(client, clock)
        topics = course(client)
        phrases = [entry for topic in topics for entry in topic["phrases"]]  # type: ignore[attr-defined]
        assert phrases

        detail = item(client, phrases[0]["id"])

        assert detail["kind"] == "phrase"
        assert detail["audio"] is None
        assert detail["forms"] == []

    def test_the_first_met_time_is_when_the_item_was_introduced(
        self, client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(client)
        complete(client, clock)
        introduced_at = clock().isoformat().replace("+00:00", "Z")
        complete(client, clock)
        (spine, *_rest) = course(client)

        detail = item(client, spine["words"][0]["id"])  # type: ignore[index]

        assert detail["first_met_at"] == introduced_at

    def test_examples_are_only_exercises_the_learner_got_right(
        self, small_client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(small_client)
        complete(small_client, clock, outcome="missed_it")

        assert item(small_client, "lex:siarad")["examples"] == []

        for _ in range(3):
            complete(small_client, clock)

        examples = item(small_client, "lex:siarad")["examples"]
        assert isinstance(examples, list)
        assert [example["welsh"] for example in examples] == ["siarad"]

    def test_an_item_not_met_is_not_found(self, client: TestClient) -> None:
        start_guest(client)

        response = client.get("/me/items/lex:cig")

        assert response.status_code == 404

    def test_an_item_that_does_not_exist_gets_the_same_answer_as_one_not_met(
        self, client: TestClient
    ) -> None:
        start_guest(client)

        unmet = client.get("/me/items/lex:cig")
        unknown = client.get("/me/items/lex:nonsense")

        assert unknown.status_code == unmet.status_code == 404
        assert unknown.json()["detail"].split()[0] == unmet.json()["detail"].split()[0]

    def test_needs_a_login_session(self, client: TestClient) -> None:
        assert client.get("/me/items/lex:cig").status_code == 401


class TestCourseOfAFinishedLearner:
    def test_has_started_every_topic_and_has_no_current_one(
        self, small_client: TestClient, clock: FakeClock
    ) -> None:
        start_guest(small_client)
        for _ in range(4):
            complete(small_client, clock)

        topics = course(small_client)

        assert overview(small_client)["new_words_ready"] is False
        assert [topic["name"] for topic in topics] == ["spine", "food"]
        assert all(topic["started"] for topic in topics)
        assert not any(topic["is_current"] for topic in topics)
        assert met_ids(topics) == ["lex:siarad", "lex:coffi"]

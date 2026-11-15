from datetime import UTC, datetime, timedelta

from api.mappings import (
    to_item_responses,
    to_missed_exercise_responses,
    to_overview_response,
    to_session_summary_response,
)
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech, Pattern
from engine.exercises import Exercise
from engine.learner import SessionSummary

MOMENT = datetime(2026, 1, 1, 12, tzinfo=UTC)
CURRICULUM = Curriculum(
    items=(
        Lexeme(
            id="lex:coffi",
            welsh="coffi",
            english="coffee",
            part_of_speech=PartOfSpeech.NOUN,
        ),
        Pattern(
            id="pat:dw-i",
            template="Dw i'n [VERB]",
            english="I am [VERB]-ing",
            slots={"VERB": PartOfSpeech.VERB},
        ),
    ),
    order=("lex:coffi", "pat:dw-i"),
)
EXERCISES = {
    "ex:1": Exercise(english="I can go", welsh="Galla i fynd", items=("lex:coffi",))
}


class TestToItemResponses:
    def test_a_word_gives_its_welsh_and_english(self) -> None:
        (response,) = to_item_responses(CURRICULUM, ("lex:coffi",))

        assert (response.id, response.welsh, response.english) == (
            "lex:coffi",
            "coffi",
            "coffee",
        )

    def test_a_pattern_gives_its_template(self) -> None:
        (response,) = to_item_responses(CURRICULUM, ("pat:dw-i",))

        assert response.welsh == "Dw i'n [VERB]"

    def test_keeps_the_order_asked_for(self) -> None:
        responses = to_item_responses(CURRICULUM, ("pat:dw-i", "lex:coffi"))

        assert [response.id for response in responses] == ["pat:dw-i", "lex:coffi"]

    def test_an_item_the_course_no_longer_has_is_left_out(self) -> None:
        assert to_item_responses(CURRICULUM, ("lex:gone",)) == ()


class TestToMissedExerciseResponses:
    def test_gives_the_text_and_the_audio_links(self) -> None:
        (response,) = to_missed_exercise_responses(EXERCISES, ("ex:1",))

        assert (response.english, response.welsh) == ("I can go", "Galla i fynd")
        assert response.audio.welsh.slow == "/exercises/ex%3A1/audio/welsh/slow"

    def test_an_exercise_the_course_no_longer_has_is_left_out(self) -> None:
        assert to_missed_exercise_responses(EXERCISES, ("ex:gone",)) == ()


class TestToSessionSummaryResponse:
    def test_counts_reviewed_items_and_names_the_rest(self) -> None:
        summary = SessionSummary(
            started_at=MOMENT,
            ended_at=MOMENT + timedelta(minutes=5, seconds=30),
            exercises_completed=4,
            items_introduced=("lex:coffi",),
            items_reviewed=("pat:dw-i", "lex:coffi"),
            items_lapsed=("pat:dw-i",),
            missed_exercises=("ex:1",),
        )

        response = to_session_summary_response(
            7, summary, ongoing=False, curriculum=CURRICULUM, exercises=EXERCISES
        )

        assert (response.id, response.duration_seconds, response.ongoing) == (
            7,
            330,
            False,
        )
        assert response.items_reviewed == 2
        assert [item.id for item in response.items_lapsed] == ["pat:dw-i"]
        assert [item.id for item in response.items_introduced] == ["lex:coffi"]
        assert [exercise.id for exercise in response.missed_exercises] == ["ex:1"]


class TestToOverviewResponse:
    def test_new_words_are_ready_while_the_course_has_a_next_topic(self) -> None:
        response = to_overview_response(
            now=MOMENT,
            review_due=2,
            learning_due=1,
            topic="greetings",
            introduced=3,
            course_items=10,
            latest_session=None,
        )

        assert response.new_words_ready is True

    def test_a_finished_course_has_no_topic_and_no_new_words(self) -> None:
        response = to_overview_response(
            now=MOMENT,
            review_due=0,
            learning_due=0,
            topic=None,
            introduced=10,
            course_items=10,
            latest_session=None,
        )

        assert (response.new_words_ready, response.topic) == (False, None)

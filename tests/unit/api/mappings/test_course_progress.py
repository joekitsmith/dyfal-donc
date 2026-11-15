from datetime import UTC, datetime

from api.mappings import (
    to_course_progress_response,
    to_item_detail_response,
    to_sentence_responses,
)
from api.schemas import ItemKind
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech, Pattern
from engine.exercises import Exercise
from engine.scheduler import TopicProgress

MOMENT = datetime(2026, 1, 1, 12, tzinfo=UTC)
COFFI = Lexeme(
    id="lex:coffi",
    welsh="coffi",
    english="coffee",
    part_of_speech=PartOfSpeech.NOUN,
    forms=("coffis",),
    notes="Borrowed from English",
)
DW_I = Pattern(
    id="pat:dw-i",
    template="Dw i'n [VERB]",
    english="I am [VERB]-ing",
    slots={"VERB": PartOfSpeech.VERB},
    notes="South Wales",
)
CURRICULUM = Curriculum(items=(COFFI, DW_I), order=(COFFI.id, DW_I.id))
EXERCISES = {"ex:1": Exercise(english="Coffee", welsh="Coffi", items=(COFFI.id,))}
(SENTENCE,) = to_sentence_responses(EXERCISES, ("ex:1",))


class TestToCourseProgressResponse:
    def test_gives_each_topic_with_its_items_and_sentences(self) -> None:
        progress = (
            TopicProgress(
                name="food",
                started=True,
                is_current=True,
                words=(COFFI.id,),
                phrases=(DW_I.id,),
                exercises_answered=3,
                sayable_exercise_ids=("ex:1",),
            ),
            TopicProgress(
                name="weather",
                started=False,
                is_current=False,
                words=(),
                phrases=(),
                exercises_answered=0,
                sayable_exercise_ids=(),
            ),
        )

        food, weather = to_course_progress_response(
            CURRICULUM, EXERCISES, progress
        ).topics

        assert (food.name, food.started, food.is_current) == ("food", True, True)
        assert food.exercises_answered == 3
        assert [item.id for item in food.words] == [COFFI.id]
        assert [item.welsh for item in food.phrases] == ["Dw i'n [VERB]"]
        assert [sentence.id for sentence in food.sayable] == ["ex:1"]
        assert (weather.started, weather.words, weather.phrases, weather.sayable) == (
            False,
            (),
            (),
            (),
        )


class TestToItemDetailResponse:
    def test_a_word_has_forms_notes_and_audio(self) -> None:
        response = to_item_detail_response(COFFI, MOMENT, (SENTENCE,))

        assert response.kind is ItemKind.WORD
        assert (response.welsh, response.english) == ("coffi", "coffee")
        assert response.forms == ("coffis",)
        assert response.notes == "Borrowed from English"
        assert response.audio == "/items/lex%3Acoffi/audio"
        assert response.first_met_at == MOMENT
        assert response.examples == (SENTENCE,)

    def test_a_phrase_has_its_template_and_no_audio(self) -> None:
        response = to_item_detail_response(DW_I, MOMENT, ())

        assert response.kind is ItemKind.PHRASE
        assert response.welsh == "Dw i'n [VERB]"
        assert response.forms == ()
        assert response.audio is None
        assert response.notes == "South Wales"

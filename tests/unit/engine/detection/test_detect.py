from collections.abc import Set as AbstractSet

from cymraeg import Mutation, Token
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech
from engine.detection import (
    CurriculumIndex,
    DetectedItem,
    Detection,
    SlotPartOfSpeechMismatch,
    UnknownToken,
    detect_items,
)
from tests.unit.engine.sample_curriculum import DW_IN, curriculum_of


def detect(
    text: str,
    *,
    preferred: AbstractSet[str] = frozenset(),
    curriculum: Curriculum | None = None,
) -> Detection:
    index = CurriculumIndex.from_curriculum(curriculum or curriculum_of())
    return detect_items(text, index, preferred)


class TestDetectPatterns:
    def test_pattern_and_its_filler_are_detected(self) -> None:
        detection = detect("Dw i'n moyn siarad")
        assert detection.items == (
            DetectedItem(item_id="pat:dw-in-moyn", start=0, end=18),
            DetectedItem(item_id="lex:siarad", start=12, end=18),
        )
        assert detection.problems == ()

    def test_longest_pattern_wins(self) -> None:
        assert detect("Dw i'n moyn dysgu").item_ids == ("pat:dw-in-moyn", "lex:dysgu")

    def test_shorter_pattern_matches_when_the_longer_does_not(self) -> None:
        assert detect("Dw i'n dysgu").item_ids == ("pat:dw-in", "lex:dysgu")

    def test_same_length_patterns_are_told_apart_by_their_slot(self) -> None:
        detection = detect("Dw i'n moyn coffi")
        assert detection.item_ids == ("pat:dw-in-moyn-noun", "lex:coffi")
        assert detection.problems == ()

    def test_tokens_after_a_pattern_are_matched_as_lexemes(self) -> None:
        detection = detect("Dw i'n moyn siarad Cymraeg")
        assert detection.item_ids == ("pat:dw-in-moyn", "lex:siarad", "lex:cymraeg")
        assert detection.problems == ()

    def test_matching_ignores_case(self) -> None:
        assert detect("DW I'N MOYN SIARAD").item_ids == ("pat:dw-in-moyn", "lex:siarad")

    def test_curly_apostrophes_are_accepted(self) -> None:
        assert detect("Dw i’n moyn siarad").item_ids == (
            "pat:dw-in-moyn",
            "lex:siarad",
        )


class TestDetectLexemes:
    def test_multi_word_lexeme_is_detected_as_one_item(self) -> None:
        detection = detect("Dw i'n dysgu fan hyn")
        assert DetectedItem(item_id="lex:fan-hyn", start=13, end=20) in detection.items
        assert detection.problems == ()

    def test_text_with_no_curriculum_items_has_no_items(self) -> None:
        assert detect("").items == ()


class TestDetectMutations:
    def test_soft_mutated_filler_is_recognised(self) -> None:
        detection = detect("Galla i fynd")
        mutated = DetectedItem(
            item_id="lex:mynd", start=8, end=12, mutation=Mutation.SOFT
        )
        assert mutated in detection.items
        assert detection.problems == ()

    def test_mutated_lexeme_in_context(self) -> None:
        detection = detect("Dw i'n dysgu Gymraeg")
        mutated = DetectedItem(
            item_id="lex:cymraeg", start=13, end=20, mutation=Mutation.SOFT
        )
        assert mutated in detection.items
        assert detection.problems == ()

    def test_mutation_on_the_first_word_of_a_phrase(self) -> None:
        assert detect("dŷ mawr").items == (
            DetectedItem(item_id="lex:ty-mawr", start=0, end=7, mutation=Mutation.SOFT),
        )

    def test_unmutated_reading_is_preferred(self) -> None:
        pen = Lexeme(
            id="lex:pen", welsh="pen", english="head", part_of_speech=PartOfSpeech.NOUN
        )
        ben = Lexeme(
            id="lex:ben",
            welsh="ben",
            english="female",
            part_of_speech=PartOfSpeech.NOUN,
        )
        detection = detect("ben", curriculum=curriculum_of((pen, ben)))
        assert detection.items == (DetectedItem(item_id="lex:ben", start=0, end=3),)

    def test_preferred_items_break_a_tie_between_mutated_readings(self) -> None:
        glas = Lexeme(
            id="lex:glas",
            welsh="glas",
            english="blue",
            part_of_speech=PartOfSpeech.ADJECTIVE,
        )
        llas = Lexeme(
            id="lex:llas",
            welsh="llas",
            english="killed",
            part_of_speech=PartOfSpeech.VERB,
        )
        curriculum = curriculum_of((glas, llas))
        assert detect("las", curriculum=curriculum).item_ids == ("lex:glas",)
        preferring_llas = detect(
            "las", curriculum=curriculum, preferred=frozenset({"lex:llas"})
        )
        assert preferring_llas.item_ids == ("lex:llas",)


class TestDetectUnknownTokens:
    def test_unknown_word_is_reported_with_offsets(self) -> None:
        detection = detect("Dw i'n moyn siarad Almaeneg")
        assert detection.problems == (
            UnknownToken(token=Token(text="Almaeneg", start=19, end=27)),
        )

    def test_unknown_filler_still_detects_the_pattern(self) -> None:
        detection = detect("Dw i'n moyn blah")
        assert detection.item_ids == ("pat:dw-in-moyn",)
        assert detection.problems == (
            UnknownToken(token=Token(text="blah", start=12, end=16)),
        )

    def test_every_unknown_token_is_reported_in_text_order(self) -> None:
        assert detect("un dau").problems == (
            UnknownToken(token=Token(text="un", start=0, end=2)),
            UnknownToken(token=Token(text="dau", start=3, end=6)),
        )


class TestDetectSlots:
    def test_filler_of_the_wrong_part_of_speech_is_reported(self) -> None:
        assert detect("Dw i'n coffi").problems == (
            SlotPartOfSpeechMismatch(
                pattern_id="pat:dw-in",
                slot="VERB",
                expected=PartOfSpeech.VERB,
                actual=PartOfSpeech.NOUN,
                item_id="lex:coffi",
                token=Token(text="coffi", start=7, end=12),
            ),
        )

    def test_right_part_of_speech_is_chosen_among_homographs(self) -> None:
        verb = Lexeme(
            id="lex:cwrw-verb",
            welsh="cwrw",
            english="to brew",
            part_of_speech=PartOfSpeech.VERB,
        )
        noun = Lexeme(
            id="lex:cwrw-noun",
            welsh="cwrw",
            english="beer",
            part_of_speech=PartOfSpeech.NOUN,
        )
        detection = detect("Dw i'n cwrw", curriculum=curriculum_of((DW_IN, verb, noun)))
        assert detection.item_ids == ("pat:dw-in", "lex:cwrw-verb")
        assert detection.problems == ()

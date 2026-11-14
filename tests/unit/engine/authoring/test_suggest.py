from cymraeg import Mutation, Token
from engine.authoring import suggest_forms
from engine.detection import CurriculumIndex
from tests.fake_lemmatisers import FixedLemmatiser
from tests.unit.engine.sample_curriculum import (
    DW_IN,
    FAN_HYN,
    GALLA_I,
    GWELD,
    MYND,
    STANDARD_ITEMS,
    curriculum_of,
)

INDEX = CurriculumIndex.from_curriculum(curriculum_of((*STANDARD_ITEMS, GWELD)))


class TestSuggestForms:
    def test_unknown_token_whose_lemma_is_a_lexeme_is_suggested(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld",)})

        (suggestion,) = suggest_forms("Gwelais i", INDEX, lemmatiser)

        assert suggestion.token == Token(text="Gwelais", start=0, end=7)
        assert suggestion.form == "gwelais"
        assert suggestion.item_id == "lex:gweld"
        assert suggestion.english == "to see"
        assert suggestion.lemma == "gweld"
        assert suggestion.mutation is None

    def test_lemmatiser_sees_the_whole_sentence(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld",)})

        suggest_forms("Gwelais i e", INDEX, lemmatiser)

        assert lemmatiser.calls[0] == ("Gwelais", "i", "e")

    def test_unknown_token_with_an_unrelated_lemma_is_not_suggested(self) -> None:
        lemmatiser = FixedLemmatiser({"siop": ("siop",)})

        assert suggest_forms("siop", INDEX, lemmatiser) == ()

    def test_unknown_token_with_no_lemma_is_not_suggested(self) -> None:
        assert suggest_forms("siop", INDEX, FixedLemmatiser({})) == ()

    def test_recognised_tokens_are_not_suggested(self) -> None:
        lemmatiser = FixedLemmatiser({"dysgu": ("dysgu",), "Cymraeg": ("Cymraeg",)})

        assert suggest_forms("Dw i'n dysgu Cymraeg", INDEX, lemmatiser) == ()

    def test_mutated_lexemes_are_not_suggested(self) -> None:
        lemmatiser = FixedLemmatiser({"fynd": ("mynd",)})

        assert suggest_forms("Galla i fynd", INDEX, lemmatiser) == ()

    def test_words_inside_a_pattern_are_not_suggested(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((GALLA_I, MYND, DW_IN)))
        lemmatiser = FixedLemmatiser({"Galla": ("gallu",)})

        assert suggest_forms("Galla i fynd", index, lemmatiser) == ()

    def test_the_same_form_is_suggested_once(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld", "gweld")})

        assert len(suggest_forms("Gwelais Gwelais", INDEX, lemmatiser)) == 1

    def test_several_lemmas_can_suggest_several_lexemes(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld", "mynd")})

        suggestions = suggest_forms("Gwelais", INDEX, lemmatiser)

        assert {suggestion.item_id for suggestion in suggestions} == {
            "lex:gweld",
            "lex:mynd",
        }

    def test_multi_word_lexemes_are_not_suggested(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((FAN_HYN,)))
        lemmatiser = FixedLemmatiser({"hwn": ("fan hyn",)})

        assert suggest_forms("hwn", index, lemmatiser) == ()


class TestSuggestFormsForMutatedWords:
    def test_unmutated_reading_is_tried_first_and_wins(self) -> None:
        lemmatiser = FixedLemmatiser(
            {"Wela": ("gweld",), "Gwela": ("gweld",)},
        )

        (suggestion,) = suggest_forms("Wela", INDEX, lemmatiser)

        assert suggestion.form == "wela"
        assert suggestion.mutation is None

    def test_radical_is_suggested_when_the_word_as_written_suggests_nothing(
        self,
    ) -> None:
        lemmatiser = FixedLemmatiser({"Gwela": ("gweld",)})

        (suggestion,) = suggest_forms("Wela i", INDEX, lemmatiser)

        assert suggestion.form == "gwela"
        assert suggestion.mutation == Mutation.SOFT
        assert suggestion.item_id == "lex:gweld"
        assert suggestion.token == Token(text="Wela", start=0, end=4)

    def test_radical_is_lemmatised_in_the_context_of_the_sentence(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwela": ("gweld",)})

        suggest_forms("Wela i di", INDEX, lemmatiser)

        assert ("Gwela", "i", "di") in lemmatiser.calls

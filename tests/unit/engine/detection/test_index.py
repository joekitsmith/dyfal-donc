from cymraeg import Mutation
from engine.curriculum import Lexeme, PartOfSpeech
from engine.detection import CurriculumIndex
from engine.detection.index import Slot
from tests.unit.engine.sample_curriculum import STANDARD_ITEMS, curriculum_of


def build_index() -> CurriculumIndex:
    return CurriculumIndex.from_curriculum(curriculum_of())


class TestCurriculumIndexFromCurriculum:
    def test_item_ids_cover_every_item(self) -> None:
        assert build_index().item_ids == {item.id for item in STANDARD_ITEMS}

    def test_patterns_become_fixed_tokens_and_slots(self) -> None:
        shapes = {shape.pattern.id: shape for shape in build_index().shapes}
        assert shapes["pat:dw-in-moyn"].elements == (
            "dw",
            "i",
            "'n",
            "moyn",
            Slot(name="VERB", part_of_speech=PartOfSpeech.VERB),
        )

    def test_patterns_are_ordered_longest_first_then_by_id(self) -> None:
        ids = [shape.pattern.id for shape in build_index().shapes]
        assert ids == [
            "pat:dw-in-moyn",
            "pat:dw-in-moyn-noun",
            "pat:dw-in",
            "pat:galla-i",
        ]

    def test_multi_word_lexemes_are_phrases(self) -> None:
        phrases = {phrase.lexeme.id: phrase.words for phrase in build_index().phrases}
        assert phrases == {
            "lex:fan-hyn": ("fan", "hyn"),
            "lex:ty-mawr": ("tŷ", "mawr"),
        }

    def test_single_word_lexemes_are_keyed_by_casefolded_word(self) -> None:
        words = build_index().words
        assert [lexeme.id for lexeme in words["cymraeg"]] == ["lex:cymraeg"]
        assert "fan" not in words


class TestCurriculumIndexCandidates:
    def test_unmutated_word_is_a_candidate_with_no_mutation(self) -> None:
        (candidate,) = build_index().candidates("siarad")
        assert candidate.lexeme.id == "lex:siarad"
        assert candidate.mutation is None

    def test_mutated_word_is_a_candidate_with_its_mutation(self) -> None:
        (candidate,) = build_index().candidates("Gymraeg")
        assert candidate.lexeme.id == "lex:cymraeg"
        assert candidate.mutation == Mutation.SOFT

    def test_unknown_word_has_no_candidates(self) -> None:
        assert build_index().candidates("blah") == ()


class TestCurriculumIndexForms:
    LLYFR = Lexeme(
        id="lex:llyfr",
        welsh="llyfr",
        english="book",
        part_of_speech=PartOfSpeech.NOUN,
        forms=("llyfrau",),
    )

    def test_every_form_is_a_word_key(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))
        assert set(index.words) == {"llyfr", "llyfrau"}

    def test_candidate_records_the_form_that_matched(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))
        assert [c.form for c in index.candidates("llyfrau")] == ["llyfrau"]
        assert [c.form for c in index.candidates("Llyfr")] == ["llyfr"]

    def test_each_form_of_a_multi_word_lexeme_is_a_phrase(self) -> None:
        phrase = Lexeme(
            id="lex:fan-hyn",
            welsh="fan hyn",
            english="here",
            part_of_speech=PartOfSpeech.ADVERB,
            forms=("fan 'ma",),
        )
        index = CurriculumIndex.from_curriculum(curriculum_of((phrase,)))
        assert sorted(entry.form for entry in index.phrases) == ["fan 'ma", "fan hyn"]


class TestCurriculumIndexLexemesFor:
    LLYFR = Lexeme(
        id="lex:llyfr",
        welsh="llyfr",
        english="book",
        part_of_speech=PartOfSpeech.NOUN,
        forms=("llyfrau",),
    )

    def test_finds_lexemes_by_base_form_or_declared_form(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))

        assert index.lexemes_for(["llyfrau"]) == (self.LLYFR,)
        assert index.lexemes_for(["LLYFR"]) == (self.LLYFR,)

    def test_each_lexeme_is_returned_once(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))

        assert index.lexemes_for(["llyfr", "llyfrau"]) == (self.LLYFR,)

    def test_does_not_undo_mutations(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))

        assert index.lexemes_for(["lyfr"]) == ()

    def test_unknown_forms_and_no_forms_find_nothing(self) -> None:
        index = CurriculumIndex.from_curriculum(curriculum_of((self.LLYFR,)))

        assert index.lexemes_for(["nothing"]) == ()
        assert index.lexemes_for([]) == ()

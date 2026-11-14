import pytest

from engine.detection import CurriculumIndex
from evals.benchmark import BenchmarkError
from evals.benchmark.models import SentenceCandidates
from evals.benchmark.authoring import score_authoring
from evals.gold import GoldSentence, GoldToken, Tag
from tests.unit.engine.sample_curriculum import FAN_HYN, curriculum_of
from tests.unit.evals.benchmark.sample_gold_sentences import (
    CURRICULUM,
    PERFECT_LEMMAS,
    SENTENCES,
)

INDEX = CurriculumIndex.from_curriculum(CURRICULUM)


def candidates_for(
    lemmas: dict[str, tuple[str, ...]],
) -> tuple[SentenceCandidates, ...]:
    return tuple(
        tuple(lemmas.get(token.text, ()) for token in sentence.tokens)
        for sentence in SENTENCES
    )


class TestScoreAuthoring:
    def test_undeclared_form_is_surfaced_by_the_right_lemma(self) -> None:
        result = score_authoring(SENTENCES, INDEX, candidates_for(dict(PERFECT_LEMMAS)))

        assert result.undeclared == 1
        assert result.surfaced == 1
        assert result.recall == 1.0
        assert result.missed == ()

    def test_declared_forms_are_not_counted_as_undeclared_or_suggested(self) -> None:
        result = score_authoring(SENTENCES, INDEX, candidates_for(dict(PERFECT_LEMMAS)))

        assert result.suggestions == 1
        assert result.correct_suggestions == 1
        assert result.precision == 1.0

    def test_missed_form_is_listed_with_its_item(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "Gwelais": ()}

        result = score_authoring(SENTENCES, INDEX, candidates_for(lemmas))

        assert result.surfaced == 0
        assert result.missed == ("Gwelais (lex:gweld)",)
        assert result.suggestions == 0
        assert result.precision == 0.0

    def test_wrong_suggestion_is_listed_and_costs_precision(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "i": ("gweld",)}

        result = score_authoring(SENTENCES, INDEX, candidates_for(lemmas))

        assert result.suggestions == 3
        assert result.correct_suggestions == 1
        assert result.precision == pytest.approx(1 / 3)
        assert result.wrong == ("i (lex:gweld)", "i (lex:gweld)")

    def test_multi_word_lexemes_are_not_counted(self) -> None:
        sentence = GoldSentence(
            id="here",
            welsh="fan hyn",
            english="here",
            tags=(Tag.PLAIN,),
            tokens=(
                GoldToken(text="fan", lemma="fan", item="lex:fan-hyn"),
                GoldToken(text="hyn", lemma="hyn", item="lex:fan-hyn"),
            ),
        )
        index = CurriculumIndex.from_curriculum(curriculum_of((FAN_HYN,)))

        result = score_authoring((sentence,), index, (((), ()),))

        assert result.undeclared == 0

    def test_wrong_number_of_sentences_is_rejected(self) -> None:
        with pytest.raises(BenchmarkError, match="candidates for 2 sentences, got 0"):
            score_authoring(SENTENCES, INDEX, ())

    def test_wrong_number_of_tokens_is_rejected(self) -> None:
        with pytest.raises(
            BenchmarkError, match="learning-welsh: Expected candidates for 5 tokens"
        ):
            score_authoring(SENTENCES, INDEX, (((),), ((), ())))

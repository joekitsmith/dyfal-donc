import pytest

from evals.benchmark import BenchmarkError
from evals.benchmark.models import SentenceCandidates
from evals.benchmark.lemma_level import score_lemmas
from evals.gold import Tag
from tests.unit.evals.benchmark.sample_gold_sentences import (
    LEARNING_WELSH,
    PERFECT_LEMMAS,
    SAW_ME,
    SENTENCES,
)


def candidates_for(
    lemmas: dict[str, tuple[str, ...]],
) -> tuple[SentenceCandidates, ...]:
    return tuple(
        tuple(lemmas.get(token.text, ()) for token in sentence.tokens)
        for sentence in SENTENCES
    )


class TestScoreLemmas:
    def test_perfect_candidates_score_full_accuracy(self) -> None:
        result = score_lemmas(SENTENCES, candidates_for(dict(PERFECT_LEMMAS)))

        assert result.overall.correct == result.overall.tokens == 7
        assert result.overall.accuracy == 1.0

    def test_missing_candidates_lower_the_accuracy(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "Gwelais": ()}

        result = score_lemmas(SENTENCES, candidates_for(lemmas))

        assert result.overall.correct == 6
        assert result.overall.accuracy == pytest.approx(6 / 7)

    def test_lemmas_match_ignoring_case(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "Cymraeg": ("cymraeg",)}

        assert score_lemmas(SENTENCES, candidates_for(lemmas)).overall.accuracy == 1.0

    def test_the_gold_lemma_only_has_to_be_among_the_candidates(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "dysgu": ("dysgu", "tysgu", "dysgi")}

        result = score_lemmas(SENTENCES, candidates_for(lemmas))

        assert result.overall.accuracy == 1.0
        assert result.overall.average_candidates == pytest.approx(9 / 7)

    def test_each_tag_covers_the_tokens_of_its_sentences(self) -> None:
        lemmas = {**PERFECT_LEMMAS, "Gwelais": ()}

        result = score_lemmas(SENTENCES, candidates_for(lemmas))

        assert result.by_tag[Tag.CLITIC].tokens == len(LEARNING_WELSH.tokens)
        assert result.by_tag[Tag.CLITIC].accuracy == 1.0
        assert result.by_tag[Tag.INFLECTION].tokens == len(SAW_ME.tokens)
        assert result.by_tag[Tag.INFLECTION].correct == 1
        assert result.by_tag[Tag.MUTATION].tokens == 0
        assert result.by_tag[Tag.MUTATION].accuracy == 0.0

    def test_wrong_number_of_sentences_is_rejected(self) -> None:
        with pytest.raises(BenchmarkError, match="candidates for 2 sentences, got 0"):
            score_lemmas(SENTENCES, ())

    def test_wrong_number_of_tokens_is_rejected(self) -> None:
        candidates = (((),), ((), ()))

        with pytest.raises(
            BenchmarkError, match="learning-welsh: Expected candidates for 5 tokens"
        ):
            score_lemmas(SENTENCES, candidates)

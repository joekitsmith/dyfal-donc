import pytest

from engine.detection import CurriculumIndex
from evals.benchmark import BenchmarkError
from evals.benchmark.models import SentenceCandidates
from evals.benchmark.item_level import augment_index, score_items
from evals.gold import Tag
from tests.unit.evals.benchmark.sample_gold_sentences import (
    CURRICULUM,
    GWELD,
    PERFECT_LEMMAS,
    SENTENCES,
)

INDEX = CurriculumIndex.from_curriculum(CURRICULUM)


def perfect_candidates() -> tuple[SentenceCandidates, ...]:
    return tuple(
        tuple(PERFECT_LEMMAS.get(token.text, ()) for token in sentence.tokens)
        for sentence in SENTENCES
    )


class TestScoreItems:
    def test_declared_forms_only_misses_an_undeclared_form(self) -> None:
        result = score_items(SENTENCES, INDEX)

        assert result.overall.true_positives == 3
        assert result.overall.predicted == 3
        assert result.overall.expected == 4
        assert result.overall.precision == 1.0
        assert result.overall.recall == 0.75

    def test_lemma_candidates_recover_the_undeclared_form(self) -> None:
        result = score_items(SENTENCES, INDEX, perfect_candidates())

        assert result.overall.recall == 1.0
        assert result.overall.precision == 1.0
        assert result.overall.f1 == 1.0

    def test_a_wrong_lemma_costs_precision(self) -> None:
        candidates = (
            perfect_candidates()[0],
            (("gweld",), ("gweld",)),
        )

        result = score_items(SENTENCES, INDEX, candidates)

        assert result.overall.predicted == 4
        assert result.overall.true_positives == 4
        assert result.overall.expected == 4
        wrong = (
            perfect_candidates()[0],
            (("gweld",), ("dysgu",)),
        )
        assert score_items(SENTENCES, INDEX, wrong).overall.predicted == 5

    def test_each_tag_covers_the_sentences_carrying_it(self) -> None:
        result = score_items(SENTENCES, INDEX)

        assert result.by_tag[Tag.INFLECTION].expected == 1
        assert result.by_tag[Tag.INFLECTION].recall == 0.0
        assert result.by_tag[Tag.CLITIC].recall == 1.0
        assert result.by_tag[Tag.MUTATION].expected == 0

    def test_wrong_number_of_sentences_is_rejected(self) -> None:
        with pytest.raises(BenchmarkError, match="candidates for 2 sentences, got 1"):
            score_items(SENTENCES, INDEX, ((),))

    def test_wrong_number_of_tokens_is_rejected(self) -> None:
        with pytest.raises(
            BenchmarkError, match="learning-welsh: Expected candidates for 5 tokens"
        ):
            score_items(SENTENCES, INDEX, (((),), ((), ())))


class TestAugmentIndex:
    def test_token_matches_the_lexeme_its_lemma_points_to(self) -> None:
        index = augment_index(INDEX, ["Gwelais"], (("gweld",),))

        assert [c.lexeme for c in index.candidates("Gwelais")] == [GWELD]

    def test_original_index_is_not_changed(self) -> None:
        augment_index(INDEX, ["Gwelais"], (("gweld",),))

        assert INDEX.candidates("Gwelais") == ()

    def test_lemmas_that_match_no_lexeme_change_nothing(self) -> None:
        index = augment_index(INDEX, ["Gwelais"], (("nothing",),))

        assert index.words == INDEX.words

    def test_a_lexeme_already_matched_is_not_added_twice(self) -> None:
        index = augment_index(INDEX, ["dysgu"], (("dysgu",),))

        assert index.words["dysgu"] == INDEX.words["dysgu"]

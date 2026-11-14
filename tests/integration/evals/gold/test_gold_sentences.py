import pytest

from cymraeg import demutate, tokenise
from engine.curriculum import load_curriculum
from evals.gold import GoldSentence, Tag, load_gold_sentences
from tests.integration.engine.exercises.exercise_fixtures import CURRICULUM_DIRECTORY

SENTENCES = load_gold_sentences()
CURRICULUM = load_curriculum(CURRICULUM_DIRECTORY)
ITEM_IDS = frozenset(item.id for item in CURRICULUM.items)
MINIMUM_SENTENCES_PER_TAG = 5


class TestGoldSentences:
    def test_set_has_about_sixty_sentences(self) -> None:
        assert 55 <= len(SENTENCES) <= 70

    @pytest.mark.parametrize("sentence", SENTENCES, ids=lambda sentence: sentence.id)
    def test_every_item_and_pattern_exists_in_the_curriculum(
        self, sentence: GoldSentence
    ) -> None:
        assert sentence.item_ids <= ITEM_IDS

    @pytest.mark.parametrize("sentence", SENTENCES, ids=lambda sentence: sentence.id)
    def test_tokens_line_up_with_tokenise(self, sentence: GoldSentence) -> None:
        assert tuple(token.text for token in tokenise(sentence.welsh)) == tuple(
            token.text for token in sentence.tokens
        )

    @pytest.mark.parametrize("sentence", SENTENCES, ids=lambda sentence: sentence.id)
    def test_annotated_mutations_are_readings_of_the_token(
        self, sentence: GoldSentence
    ) -> None:
        for token in sentence.tokens:
            if token.mutation is None:
                continue

            readings = {
                (demutation.radical.casefold(), demutation.mutation)
                for demutation in demutate(token.text)
            }
            if Tag.INFLECTION in sentence.tags:
                # An inflected, mutated verb has its inflected form as radical, not the lemma
                assert token.mutation in {mutation for _, mutation in readings}
            else:
                assert (token.lemma.casefold(), token.mutation) in readings

    @pytest.mark.parametrize("sentence", SENTENCES, ids=lambda sentence: sentence.id)
    def test_tags_match_the_annotations(self, sentence: GoldSentence) -> None:
        tags = set(sentence.tags)
        assert (Tag.MUTATION in tags) == any(
            token.mutation for token in sentence.tokens
        )
        assert (Tag.CLITIC in tags) == any(
            token.text.startswith("'") for token in sentence.tokens
        )
        assert (Tag.ARTICLE in tags) == any(
            token.lemma == "y" for token in sentence.tokens
        )
        assert (Tag.PLAIN in tags) == (tags <= {Tag.PLAIN})

    def test_ids_are_unique(self) -> None:
        assert len({sentence.id for sentence in SENTENCES}) == len(SENTENCES)

    @pytest.mark.parametrize("tag", list(Tag))
    def test_every_tag_is_well_covered(self, tag: Tag) -> None:
        assert (
            sum(tag in sentence.tags for sentence in SENTENCES)
            >= MINIMUM_SENTENCES_PER_TAG
        )

    def test_mutation_kinds_are_all_represented(self) -> None:
        kinds = {token.mutation for sentence in SENTENCES for token in sentence.tokens}
        assert {"soft", "nasal", "aspirate", "h_prothesis"} <= {
            kind.value for kind in kinds if kind is not None
        }

import pytest

from cymraeg import Mutation
from evals.gold import GoldSentence, GoldSetError, GoldToken, Tag


def sentence(
    *,
    tokens: tuple[GoldToken, ...] = (GoldToken(text="Bore", lemma="bore"),),
    tags: tuple[Tag, ...] = (Tag.PLAIN,),
    patterns: tuple[str, ...] = (),
    english: str = "Morning",
) -> GoldSentence:
    return GoldSentence(
        id="morning",
        welsh="Bore",
        english=english,
        tags=tags,
        patterns=patterns,
        tokens=tokens,
    )


class TestGoldToken:
    def test_blank_text_is_rejected(self) -> None:
        with pytest.raises(GoldSetError, match="Token text must not be blank"):
            GoldToken(text=" ", lemma="bore")

    def test_blank_lemma_is_rejected(self) -> None:
        with pytest.raises(GoldSetError, match="'bore': Lemma must not be blank"):
            GoldToken(text="bore", lemma="")

    def test_item_and_mutation_default_to_none(self) -> None:
        token = GoldToken(text="bore", lemma="bore")
        assert token.item is None
        assert token.mutation is None


class TestGoldSentence:
    def test_blank_english_is_rejected(self) -> None:
        with pytest.raises(GoldSetError, match="morning: English must not be blank"):
            sentence(english="")

    def test_tags_are_required(self) -> None:
        with pytest.raises(GoldSetError, match="At least one tag is required"):
            sentence(tags=())

    def test_tokens_are_required(self) -> None:
        with pytest.raises(GoldSetError, match="At least one token is required"):
            sentence(tokens=())

    def test_item_ids_combine_patterns_and_token_items(self) -> None:
        tokens = (
            GoldToken(text="Dw", lemma="bod"),
            GoldToken(
                text="Gymraeg",
                lemma="Cymraeg",
                item="lex:cymraeg",
                mutation=Mutation.SOFT,
            ),
            GoldToken(text="Cymraeg", lemma="Cymraeg", item="lex:cymraeg"),
        )
        gold = sentence(tokens=tokens, patterns=("pat:dw-in",))
        assert gold.item_ids == {"pat:dw-in", "lex:cymraeg"}

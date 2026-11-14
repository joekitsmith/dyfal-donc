from dataclasses import dataclass
from enum import StrEnum

from cymraeg import Mutation
from evals.gold.errors import GoldSetError


class Tag(StrEnum):
    """What a sentence is there to test."""

    MUTATION = "mutation"
    INFLECTION = "inflection"
    CLITIC = "clitic"
    ARTICLE = "article"
    PLAIN = "plain"


@dataclass(frozen=True, slots=True, kw_only=True)
class GoldToken:
    """One token as ``tokenise`` splits it, with what it should be recognised as.

    ``lemma`` is the dictionary form. ``item`` is the lexeme id it should be
    detected as, or ``None`` for words that are not lexemes (words outside the
    curriculum, and the fixed words of a pattern). ``mutation`` is the mutation
    on the token, if any.
    """

    text: str
    lemma: str
    item: str | None = None
    mutation: Mutation | None = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise GoldSetError("Token text must not be blank")

        if not self.lemma.strip():
            raise GoldSetError(f"{self.text!r}: Lemma must not be blank")


@dataclass(frozen=True, slots=True, kw_only=True)
class GoldSentence:
    """A hand-annotated sentence.

    ``patterns`` are the pattern ids the sentence is an instance of.
    """

    id: str
    welsh: str
    english: str
    tags: tuple[Tag, ...]
    patterns: tuple[str, ...] = ()
    tokens: tuple[GoldToken, ...]

    @property
    def item_ids(self) -> frozenset[str]:
        """Every item the sentence should be detected as: its patterns and lexemes."""
        return frozenset(self.patterns) | {
            token.item for token in self.tokens if token.item is not None
        }

    def __post_init__(self) -> None:
        for name, value in (
            ("id", self.id),
            ("welsh", self.welsh),
            ("english", self.english),
        ):
            if not value.strip():
                raise GoldSetError(f"{self.id}: {name.capitalize()} must not be blank")

        if not self.tags:
            raise GoldSetError(f"{self.id}: At least one tag is required")

        if not self.tokens:
            raise GoldSetError(f"{self.id}: At least one token is required")

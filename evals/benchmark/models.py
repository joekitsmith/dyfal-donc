from collections.abc import Mapping
from dataclasses import dataclass

from evals.gold import Tag

type SentenceCandidates = tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class LemmaScore:
    """How often the gold lemma was among a lemmatiser's candidates."""

    correct: int
    tokens: int
    candidates: int

    @property
    def accuracy(self) -> float:
        return _ratio(self.correct, self.tokens)

    @property
    def average_candidates(self) -> float:
        return _ratio(self.candidates, self.tokens)


@dataclass(frozen=True, slots=True, kw_only=True)
class LemmaResult:
    overall: LemmaScore
    by_tag: Mapping[Tag, LemmaScore]


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemScore:
    """Detected items compared with the expected ones, summed over sentences."""

    true_positives: int
    predicted: int
    expected: int

    @property
    def precision(self) -> float:
        return _ratio(self.true_positives, self.predicted)

    @property
    def recall(self) -> float:
        return _ratio(self.true_positives, self.expected)

    @property
    def f1(self) -> float:
        return _ratio(2 * self.precision * self.recall, self.precision + self.recall)


@dataclass(frozen=True, slots=True, kw_only=True)
class ItemResult:
    overall: ItemScore
    by_tag: Mapping[Tag, ItemScore]


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthoringResult:
    """How well a lemmatiser suggests undeclared forms of curriculum words.

    ``undeclared`` counts gold tokens that are a form of a single-word lexeme
    but that the curriculum doesn't recognise yet. ``surfaced`` is how many of
    those the lemmatiser maps to the right lexeme (``missed`` lists the rest).
    ``suggestions`` counts every new token-to-lexeme suggestion it makes, and
    ``correct_suggestions`` those that match the gold item (``wrong`` lists the rest).
    """

    undeclared: int
    surfaced: int
    suggestions: int
    correct_suggestions: int
    missed: tuple[str, ...]
    wrong: tuple[str, ...]

    @property
    def recall(self) -> float:
        return _ratio(self.surfaced, self.undeclared)

    @property
    def precision(self) -> float:
        return _ratio(self.correct_suggestions, self.suggestions)


@dataclass(frozen=True, slots=True, kw_only=True)
class LemmatiserResult:
    name: str
    lemmas: LemmaResult
    items: ItemResult
    authoring: AuthoringResult
    milliseconds_per_sentence: float


@dataclass(frozen=True, slots=True, kw_only=True)
class BenchmarkResult:
    sentences: int
    tokens: int
    declared_forms_only: ItemResult
    lemmatisers: tuple[LemmatiserResult, ...]


def _ratio(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0

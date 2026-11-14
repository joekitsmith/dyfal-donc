from collections.abc import Mapping
from dataclasses import dataclass

from cymraeg import Mutation, demutate, tokenise
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech, Pattern

type Element = str | Slot


@dataclass(frozen=True, slots=True, kw_only=True)
class CurriculumIndex:
    """A curriculum prepared for finding its items in Welsh text.

    Patterns and phrases are ordered longest first, then by id.
    """

    item_ids: frozenset[str]
    shapes: tuple[PatternShape, ...]
    phrases: tuple[Phrase, ...]
    words: Mapping[str, tuple[Lexeme, ...]]

    @classmethod
    def from_curriculum(cls, curriculum: Curriculum) -> CurriculumIndex:
        shapes: list[PatternShape] = []
        phrases: list[Phrase] = []
        words: dict[str, list[Lexeme]] = {}
        for item in curriculum.items:
            if isinstance(item, Pattern):
                shapes.append(
                    PatternShape(pattern=item, elements=_pattern_elements(item))
                )
                continue
            lexeme_words = tuple(
                token.text.casefold() for token in tokenise(item.welsh)
            )
            if len(lexeme_words) == 1:
                words.setdefault(lexeme_words[0], []).append(item)
            elif lexeme_words:
                phrases.append(Phrase(lexeme=item, words=lexeme_words))
        shapes.sort(key=lambda shape: (-len(shape.elements), shape.pattern.id))
        phrases.sort(key=lambda phrase: (-len(phrase.words), phrase.lexeme.id))
        return cls(
            item_ids=frozenset(item.id for item in curriculum.items),
            shapes=tuple(shapes),
            phrases=tuple(phrases),
            words={word: tuple(lexemes) for word, lexemes in words.items()},
        )

    def candidates(self, token_text: str) -> tuple[Candidate, ...]:
        """Every single-word lexeme the token could be, undoing mutations if needed.

        Ordered by the position of the reading in ``demutate``, so an unmutated
        reading comes first.
        """
        return tuple(
            Candidate(lexeme=lexeme, mutation=demutation.mutation, order=order)
            for order, demutation in enumerate(demutate(token_text))
            for lexeme in self.words.get(demutation.radical.casefold(), ())
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class Candidate:
    lexeme: Lexeme
    mutation: Mutation | None
    order: int


@dataclass(frozen=True, slots=True, kw_only=True)
class PatternShape:
    """A pattern as a token sequence: casefolded fixed tokens and slots."""

    pattern: Pattern
    elements: tuple[Element, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Phrase:
    """A multi-word lexeme as its casefolded words."""

    lexeme: Lexeme
    words: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class Slot:
    name: str
    part_of_speech: PartOfSpeech


def _pattern_elements(pattern: Pattern) -> tuple[Element, ...]:
    template = pattern.template
    elements: list[Element] = []
    for token in tokenise(template):
        is_slot = (
            token.text in pattern.slots
            and template[token.start - 1 : token.start] == "["
            and template[token.end : token.end + 1] == "]"
        )
        if is_slot:
            elements.append(
                Slot(name=token.text, part_of_speech=pattern.slots[token.text])
            )
        else:
            elements.append(token.text.casefold())
    return tuple(elements)

from collections.abc import Iterable

from engine.curriculum import Lexeme
from engine.detection import CurriculumIndex


def lexemes_for_lemmas(
    index: CurriculumIndex, lemmas: Iterable[str]
) -> tuple[Lexeme, ...]:
    """The single-word lexemes with a form matching any of the lemmas (ignoring case)."""
    found = {
        lexeme.id: lexeme
        for lemma in lemmas
        for lexeme in index.words.get(lemma.casefold(), ())
    }

    return tuple(found.values())

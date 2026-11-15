from collections.abc import Sequence

from cymraeg import Lemmatiser, Token


class AgreeingLemmatiser:
    """Keeps only the lemmas every lemmatiser agrees on, ignoring case.

    The candidates are the first lemmatiser's, in its order, that all the
    others also give for the same token.
    """

    def __init__(self, first: Lemmatiser, *others: Lemmatiser) -> None:
        self._first = first
        self._others = others

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        first = self._first.lemmatise(tokens)
        others = [other.lemmatise(tokens) for other in self._others]

        return tuple(
            tuple(
                lemma
                for lemma in lemmas
                if all(
                    lemma.casefold()
                    in {option.casefold() for option in other[position]}
                    for other in others
                )
            )
            for position, lemmas in enumerate(first)
        )


class EitherLemmatiser:
    """Gathers the lemmas any of the lemmatisers gives, without repeats.

    Candidates keep the order of the lemmatisers, and the first spelling of
    a lemma wins when they differ only in case.
    """

    def __init__(self, first: Lemmatiser, *others: Lemmatiser) -> None:
        self._lemmatisers = (first, *others)

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        results = [lemmatiser.lemmatise(tokens) for lemmatiser in self._lemmatisers]

        merged: list[tuple[str, ...]] = []
        for per_lemmatiser in zip(*results, strict=True):
            by_lemma: dict[str, str] = {}
            for options in per_lemmatiser:
                for lemma in options:
                    by_lemma.setdefault(lemma.casefold(), lemma)

            merged.append(tuple(by_lemma.values()))

        return tuple(merged)

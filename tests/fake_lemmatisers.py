from collections.abc import Mapping, Sequence

from cymraeg import Token


class FixedLemmatiser:
    """A lemmatiser that looks each token up in a fixed dictionary and records its calls."""

    def __init__(self, lemmas: Mapping[str, tuple[str, ...]]) -> None:
        self._lemmas = lemmas
        self.calls: list[tuple[str, ...]] = []

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        self.calls.append(tuple(token.text for token in tokens))

        return tuple(self._lemmas.get(token.text, ()) for token in tokens)

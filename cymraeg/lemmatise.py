from collections.abc import Sequence
from dataclasses import replace
from typing import Protocol

from cymraeg.mutation import demutate
from cymraeg.tokenise import Token


class Lemmatiser(Protocol):
    """Finds the possible dictionary forms (lemmas) of the tokens of one sentence."""

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        """The candidate lemmas of each token, in the same order as ``tokens``.

        ``tokens`` are one sentence, so an implementation may use the context.
        A token with no known lemma has no candidates.
        """
        ...


class RuleLemmatiser:
    """Undoes mutations and nothing else: the radicals ``demutate`` finds."""

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        return tuple(
            tuple(dict.fromkeys(reading.radical for reading in demutate(token.text)))
            for token in tokens
        )


class DemutatingLemmatiser:
    """Adds mutation handling to another lemmatiser.

    Each token is also lemmatised as every radical it could be a mutation of,
    with the rest of the sentence unchanged. The inner lemmatiser's own
    candidates for the token as written come first.
    """

    def __init__(self, inner: Lemmatiser) -> None:
        self._inner = inner

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        candidates = [list(lemmas) for lemmas in self._inner.lemmatise(tokens)]
        for position, token in enumerate(tokens):
            for radical in self._other_radicals(token):
                alternative = (
                    *tokens[:position],
                    replace(token, text=radical),
                    *tokens[position + 1 :],
                )
                candidates[position].extend(
                    self._inner.lemmatise(alternative)[position]
                )

        return tuple(tuple(dict.fromkeys(lemmas)) for lemmas in candidates)

    def _other_radicals(self, token: Token) -> tuple[str, ...]:
        radicals = dict.fromkeys(reading.radical for reading in demutate(token.text))

        return tuple(radical for radical in radicals if radical != token.text)

from collections.abc import Sequence
from types import ModuleType

from cymraeg.errors import CymraegError
from cymraeg.tokenise import Token

LANGUAGE = "cy"


class SimplemmaLemmatiser:
    """Lemmatises with Simplemma, which looks each word up on its own.

    Needs the optional ``lemmatisers`` dependency group.
    """

    def __init__(self) -> None:
        self._simplemma = _load_simplemma()

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        return tuple(
            (str(self._simplemma.lemmatize(token.text, lang=LANGUAGE)),)
            for token in tokens
        )


def _load_simplemma() -> ModuleType:
    try:
        import simplemma
    except ImportError as exc:
        raise CymraegError(
            "Simplemma is not installed: run 'poetry install --with lemmatisers'"
        ) from exc

    return simplemma

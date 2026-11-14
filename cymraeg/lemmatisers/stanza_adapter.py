from collections.abc import Sequence
from pathlib import Path

from cymraeg.errors import CymraegError
from cymraeg.tokenise import Token

LANGUAGE = "cy"
PROCESSORS = "tokenize,pos,lemma"


class StanzaLemmatiser:
    """Lemmatises with Stanza's Welsh model, using the whole sentence as context.

    Needs the optional ``lemmatisers`` dependency group. With ``download``, the
    Welsh model (about 200 MB) is fetched on first use; without it, a missing
    model raises ``CymraegError``. The tokens are passed in as given, so
    Stanza does no tokenising of its own.
    """

    def __init__(
        self, *, model_directory: Path | None = None, download: bool = True
    ) -> None:
        try:
            import stanza
            from stanza.resources.common import DEFAULT_MODEL_DIR
        except ImportError as exc:
            raise CymraegError(
                "Stanza is not installed: run 'poetry install --with lemmatisers'"
            ) from exc

        method = (
            stanza.DownloadMethod.REUSE_RESOURCES
            if download
            else stanza.DownloadMethod.NONE
        )
        try:
            self._pipeline = stanza.Pipeline(
                LANGUAGE,
                dir=str(model_directory or DEFAULT_MODEL_DIR),
                processors=PROCESSORS,
                tokenize_pretokenized=True,
                download_method=method,
                verbose=False,
            )
        except Exception as exc:
            raise CymraegError(f"Could not load the Stanza Welsh model: {exc}") from exc

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        if not tokens:
            return ()

        document = self._pipeline([[token.text for token in tokens]])
        words = document.sentences[0].words
        if len(words) != len(tokens):
            raise CymraegError(
                f"Stanza returned {len(words)} words for {len(tokens)} tokens"
            )

        return tuple((word.lemma,) if word.lemma else () for word in words)

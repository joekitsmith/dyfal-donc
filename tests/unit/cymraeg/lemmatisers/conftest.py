import pytest

from cymraeg import CymraegError, SimplemmaLemmatiser, StanzaLemmatiser


@pytest.fixture(scope="session")
def simplemma_lemmatiser() -> SimplemmaLemmatiser:
    pytest.importorskip("simplemma")

    return SimplemmaLemmatiser()


@pytest.fixture(scope="session")
def stanza_lemmatiser() -> StanzaLemmatiser:
    pytest.importorskip("stanza")
    try:
        return StanzaLemmatiser(download=False)
    except CymraegError:
        pytest.skip(
            "Stanza Welsh model not downloaded: run 'poe download-stanza-model'"
        )

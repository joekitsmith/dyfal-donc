import sys

import pytest

from cymraeg import CymraegError, SimplemmaLemmatiser, tokenise


class TestSimplemmaLemmatiserMissingDependency:
    def test_reports_how_to_install_it(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "simplemma", None)

        with pytest.raises(CymraegError, match="poetry install --with lemmatisers"):
            SimplemmaLemmatiser()


class TestSimplemmaLemmatiser:
    @pytest.mark.parametrize(
        ("text", "lemma"),
        [
            ("gwelais", "gweld"),
            ("llyfrau", "llyfr"),
            ("gallwn", "gallu"),
            ("Gymraeg", "Cymraeg"),
        ],
    )
    def test_finds_the_lemma_of_a_single_word(
        self, simplemma_lemmatiser: SimplemmaLemmatiser, text: str, lemma: str
    ) -> None:
        assert simplemma_lemmatiser.lemmatise(tokenise(text)) == ((lemma,),)

    def test_gives_one_candidate_per_token(
        self, simplemma_lemmatiser: SimplemmaLemmatiser
    ) -> None:
        tokens = tokenise("Dw i'n hoffi'r llyfrau")

        candidates = simplemma_lemmatiser.lemmatise(tokens)

        assert len(candidates) == len(tokens)
        assert all(len(options) == 1 for options in candidates)

    def test_no_tokens_gives_no_candidates(
        self, simplemma_lemmatiser: SimplemmaLemmatiser
    ) -> None:
        assert simplemma_lemmatiser.lemmatise(()) == ()

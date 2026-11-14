import sys

import pytest

from cymraeg import CymraegError, StanzaLemmatiser, tokenise


class TestStanzaLemmatiserMissingDependency:
    def test_reports_how_to_install_it(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "stanza", None)

        with pytest.raises(CymraegError, match="poetry install --with lemmatisers"):
            StanzaLemmatiser()


class TestStanzaLemmatiser:
    def test_uses_the_sentence_as_context_for_each_token(
        self, stanza_lemmatiser: StanzaLemmatiser
    ) -> None:
        tokens = tokenise("Gwelais i e neithiwr")

        candidates = stanza_lemmatiser.lemmatise(tokens)

        assert candidates[0] == ("gweld",)

    def test_gives_one_candidate_per_token_including_clitics(
        self, stanza_lemmatiser: StanzaLemmatiser
    ) -> None:
        tokens = tokenise("Dw i'n hoffi'r Gymraeg")

        candidates = stanza_lemmatiser.lemmatise(tokens)

        assert len(candidates) == len(tokens) == 6
        assert candidates[2] == ("yn",)
        assert candidates[5] == ("Cymraeg",)

    def test_no_tokens_gives_no_candidates(
        self, stanza_lemmatiser: StanzaLemmatiser
    ) -> None:
        assert stanza_lemmatiser.lemmatise(()) == ()

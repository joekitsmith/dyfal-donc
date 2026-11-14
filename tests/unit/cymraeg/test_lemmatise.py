from collections.abc import Mapping, Sequence

from cymraeg import DemutatingLemmatiser, Lemmatiser, RuleLemmatiser, Token, tokenise


class DictionaryLemmatiser:
    """A test double that looks each token up in a dictionary and records its calls."""

    def __init__(self, lemmas: Mapping[str, tuple[str, ...]]) -> None:
        self.lemmas = lemmas
        self.calls: list[tuple[str, ...]] = []

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        self.calls.append(tuple(token.text for token in tokens))

        return tuple(self.lemmas.get(token.text, ()) for token in tokens)


class TestRuleLemmatiser:
    def test_gives_one_tuple_of_candidates_per_token(self) -> None:
        tokens = tokenise("Dw i'n moyn")

        assert len(RuleLemmatiser().lemmatise(tokens)) == len(tokens)

    def test_unmutated_reading_comes_first(self) -> None:
        (candidates,) = RuleLemmatiser().lemmatise(tokenise("cath"))

        assert candidates[0] == "cath"

    def test_mutated_word_gives_its_radical(self) -> None:
        (candidates,) = RuleLemmatiser().lemmatise(tokenise("Gymraeg"))

        assert "Cymraeg" in candidates

    def test_candidates_are_unique(self) -> None:
        for candidates in RuleLemmatiser().lemmatise(tokenise("ddod ardd hen")):
            assert len(candidates) == len(set(candidates))

    def test_does_not_handle_inflection(self) -> None:
        (candidates,) = RuleLemmatiser().lemmatise(tokenise("gwelais"))

        assert "gweld" not in candidates

    def test_no_tokens_gives_no_candidates(self) -> None:
        assert RuleLemmatiser().lemmatise(()) == ()

    def test_satisfies_the_protocol(self) -> None:
        lemmatiser: Lemmatiser = RuleLemmatiser()

        assert lemmatiser.lemmatise(()) == ()


class TestDemutatingLemmatiser:
    def test_inner_candidates_for_the_token_as_written_come_first(self) -> None:
        inner = DictionaryLemmatiser({"ddod": ("ddod",), "dod": ("dod",)})

        (candidates,) = DemutatingLemmatiser(inner).lemmatise(tokenise("ddod"))

        assert candidates[0] == "ddod"
        assert "dod" in candidates

    def test_radical_is_lemmatised_in_the_context_of_the_sentence(self) -> None:
        inner = DictionaryLemmatiser({"dod": ("dod",)})

        DemutatingLemmatiser(inner).lemmatise(tokenise("Galla i ddod"))

        assert ("Galla", "i", "dod") in inner.calls

    def test_other_tokens_are_not_changed_when_one_is_replaced(self) -> None:
        inner = DictionaryLemmatiser({})
        tokens = tokenise("Galla i ddod")

        DemutatingLemmatiser(inner).lemmatise(tokens)

        assert all(
            call[:2] == ("Galla", "i") or call[2] == "ddod" for call in inner.calls
        )

    def test_replaced_tokens_keep_their_offsets(self) -> None:
        seen: list[Token] = []

        class Recording:
            def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
                seen.extend(tokens)

                return tuple(() for _ in tokens)

        DemutatingLemmatiser(Recording()).lemmatise(tokenise("ddod"))

        assert {(token.start, token.end) for token in seen} == {(0, 4)}

    def test_candidates_are_unique(self) -> None:
        inner = DictionaryLemmatiser({"dod": ("dod",), "ddod": ("dod",)})

        (candidates,) = DemutatingLemmatiser(inner).lemmatise(tokenise("ddod"))

        assert candidates.count("dod") == 1

    def test_word_with_no_mutation_readings_is_lemmatised_once(self) -> None:
        inner = DictionaryLemmatiser({"mynd": ("mynd",)})

        DemutatingLemmatiser(inner).lemmatise(tokenise("mynd"))

        assert ("mynd",) in inner.calls
        assert all(call == ("mynd",) or call[0] != "mynd" for call in inner.calls)

    def test_empty_input(self) -> None:
        assert DemutatingLemmatiser(DictionaryLemmatiser({})).lemmatise(()) == ()

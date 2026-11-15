from cymraeg import tokenise
from evals.benchmark.combinations import AgreeingLemmatiser, EitherLemmatiser
from tests.fake_lemmatisers import FixedLemmatiser as DictionaryLemmatiser


class TestAgreeingLemmatiser:
    def test_keeps_only_lemmas_every_lemmatiser_gives(self) -> None:
        first = DictionaryLemmatiser({"ei": ("ef", "mynd")})
        second = DictionaryLemmatiser({"ei": ("ef",)})

        assert AgreeingLemmatiser(first, second).lemmatise(tokenise("ei")) == (("ef",),)

    def test_agreement_ignores_case(self) -> None:
        first = DictionaryLemmatiser({"Cymraeg": ("Cymraeg",)})
        second = DictionaryLemmatiser({"Cymraeg": ("cymraeg",)})

        assert AgreeingLemmatiser(first, second).lemmatise(tokenise("Cymraeg")) == (
            ("Cymraeg",),
        )

    def test_keeps_the_first_lemmatisers_order_and_spelling(self) -> None:
        first = DictionaryLemmatiser({"x": ("b", "A")})
        second = DictionaryLemmatiser({"x": ("a", "b")})

        assert AgreeingLemmatiser(first, second).lemmatise(tokenise("x")) == (
            ("b", "A"),
        )

    def test_no_agreement_gives_no_candidates(self) -> None:
        first = DictionaryLemmatiser({"x": ("a",)})
        second = DictionaryLemmatiser({"x": ("b",)})

        assert AgreeingLemmatiser(first, second).lemmatise(tokenise("x")) == ((),)

    def test_a_token_one_lemmatiser_does_not_know_gets_no_candidates(self) -> None:
        first = DictionaryLemmatiser({"x": ("a",)})
        second = DictionaryLemmatiser({})

        assert AgreeingLemmatiser(first, second).lemmatise(tokenise("x")) == ((),)

    def test_agreement_among_three(self) -> None:
        lemmatisers = [
            DictionaryLemmatiser({"x": ("a", "b")}),
            DictionaryLemmatiser({"x": ("a", "b")}),
            DictionaryLemmatiser({"x": ("b",)}),
        ]

        assert AgreeingLemmatiser(*lemmatisers).lemmatise(tokenise("x")) == (("b",),)

    def test_a_single_lemmatiser_agrees_with_itself(self) -> None:
        only = DictionaryLemmatiser({"x": ("a",)})

        assert AgreeingLemmatiser(only).lemmatise(tokenise("x")) == (("a",),)

    def test_empty_input(self) -> None:
        both = DictionaryLemmatiser({})

        assert AgreeingLemmatiser(both, both).lemmatise(()) == ()


class TestEitherLemmatiser:
    def test_gathers_lemmas_from_every_lemmatiser(self) -> None:
        first = DictionaryLemmatiser({"x": ("a",)})
        second = DictionaryLemmatiser({"x": ("b",)})

        assert EitherLemmatiser(first, second).lemmatise(tokenise("x")) == (("a", "b"),)

    def test_repeats_are_removed_ignoring_case_and_the_first_spelling_wins(
        self,
    ) -> None:
        first = DictionaryLemmatiser({"x": ("Cymraeg",)})
        second = DictionaryLemmatiser({"x": ("cymraeg", "other")})

        assert EitherLemmatiser(first, second).lemmatise(tokenise("x")) == (
            ("Cymraeg", "other"),
        )

    def test_a_token_only_one_lemmatiser_knows_keeps_its_lemmas(self) -> None:
        first = DictionaryLemmatiser({})
        second = DictionaryLemmatiser({"x": ("a",)})

        assert EitherLemmatiser(first, second).lemmatise(tokenise("x")) == (("a",),)

    def test_one_tuple_per_token(self) -> None:
        both = DictionaryLemmatiser({})
        tokens = tokenise("Dw i'n moyn")

        assert len(EitherLemmatiser(both, both).lemmatise(tokens)) == len(tokens)

    def test_empty_input(self) -> None:
        both = DictionaryLemmatiser({})

        assert EitherLemmatiser(both, both).lemmatise(()) == ()

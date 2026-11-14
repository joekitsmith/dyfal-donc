import pytest

from cymraeg.tokenise import CLITICS, Token, tokenise


def texts(text: str) -> tuple[str, ...]:
    return tuple(token.text for token in tokenise(text))


class TestTokeniseClitics:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("Dw i'n moyn", ("Dw", "i", "'n", "moyn")),
            ("o'r tŷ", ("o", "'r", "tŷ")),
            ("i'r siop", ("i", "'r", "siop")),
            ("a'r bachgen", ("a", "'r", "bachgen")),
            ("mae e'n dysgu", ("mae", "e", "'n", "dysgu")),
            ("dw i'm yn gwybod", ("dw", "i", "'m", "yn", "gwybod")),
            ("dw i'w weld e", ("dw", "i", "'w", "weld", "e")),
            ("fan 'ma", ("fan", "'ma")),
            ("fan'na", ("fan", "'na")),
            ("dw i'ch gweld chi", ("dw", "i", "'ch", "gweld", "chi")),
            ("dw i'th weld di", ("dw", "i", "'th", "weld", "di")),
            ("dw i'u gweld nhw", ("dw", "i", "'u", "gweld", "nhw")),
            ("fe'i gwelais i", ("fe", "'i", "gwelais", "i")),
        ],
    )
    def test_clitics_become_their_own_tokens(
        self, text: str, expected: tuple[str, ...]
    ) -> None:
        assert texts(text) == expected

    def test_every_clitic_is_covered_above(self) -> None:
        assert CLITICS == {
            "'n",
            "'r",
            "'w",
            "'ma",
            "'na",
            "'m",
            "'i",
            "'u",
            "'ch",
            "'th",
        }

    def test_leading_clitic_keeps_its_apostrophe(self) -> None:
        assert texts("'n") == ("'n",)

    def test_case_is_preserved_and_clitics_match_case_insensitively(self) -> None:
        assert texts("DW I'N MOYN") == ("DW", "I", "'N", "MOYN")

    def test_quotation_marks_are_not_clitics(self) -> None:
        assert texts("'Helo' medde fe") == ("Helo", "medde", "fe")

    def test_non_clitic_apostrophe_stays_inside_the_word(self) -> None:
        assert texts("ma'e fe") == ("ma'e", "fe")

    def test_curly_apostrophes_are_normalised(self) -> None:
        assert texts("Dw i’n moyn") == texts("Dw i'n moyn")
        assert texts("Dw i‘n moyn") == texts("Dw i'n moyn")


class TestTokeniseWords:
    def test_hyphenated_words_stay_whole(self) -> None:
        assert texts("Mae e'n ail-law") == ("Mae", "e", "'n", "ail-law")

    def test_punctuation_is_dropped(self) -> None:
        assert texts("Helo, shwmae? Dw i'n iawn!") == (
            "Helo",
            "shwmae",
            "Dw",
            "i",
            "'n",
            "iawn",
        )

    def test_welsh_circumflex_letters_are_word_characters(self) -> None:
        assert texts("tŷ ŵy") == ("tŷ", "ŵy")

    def test_empty_and_punctuation_only_text_has_no_tokens(self) -> None:
        assert tokenise("") == ()
        assert tokenise("?! ...") == ()


class TestTokeniseOffsets:
    def test_offsets_index_into_the_original_text(self) -> None:
        text = "Dw i'n moyn."
        tokens = tokenise(text)
        assert tokens == (
            Token(text="Dw", start=0, end=2),
            Token(text="i", start=3, end=4),
            Token(text="'n", start=4, end=6),
            Token(text="moyn", start=7, end=11),
        )
        assert all(text[token.start : token.end] == token.text for token in tokens)

    def test_offsets_with_curly_apostrophes_and_merged_pieces(self) -> None:
        text = "Ma'e fe, dw i’n moyn"
        for token in tokenise(text):
            assert text[token.start : token.end].replace("’", "'") == token.text

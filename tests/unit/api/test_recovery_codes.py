import re

import pytest

from api.recovery_codes import (
    ALPHABET,
    CODE_COUNT,
    generate_recovery_codes,
    hash_recovery_code,
    normalise_recovery_code,
)

CODE_PATTERN = re.compile(rf"^([{ALPHABET}]{{4}}-){{3}}[{ALPHABET}]{{4}}$")


class TestGenerateRecoveryCodes:
    def test_makes_ten_distinct_codes_in_groups_of_four(self) -> None:
        codes = generate_recovery_codes()

        assert len(codes) == CODE_COUNT
        assert len(set(codes)) == CODE_COUNT
        assert all(CODE_PATTERN.match(code) for code in codes)

    def test_never_uses_characters_that_look_alike(self) -> None:
        text = "".join(generate_recovery_codes())

        assert not set(text) & set("ILOU")

    def test_sets_differ(self) -> None:
        assert set(generate_recovery_codes()).isdisjoint(generate_recovery_codes())


class TestNormaliseRecoveryCode:
    @pytest.mark.parametrize(
        "typed",
        [
            "ABCD-EFGH-JKMN-PQRS",
            "abcd efgh jkmn pqrs",
            "  abcdefghjkmnpqrs ",
            "ABCD–EFGH-JKMN-PQRS",
        ],
    )
    def test_any_way_of_writing_a_code_gives_the_same_text(self, typed: str) -> None:
        assert normalise_recovery_code(typed) == "ABCDEFGHJKMNPQRS"

    def test_look_alikes_are_mapped(self) -> None:
        assert normalise_recovery_code("oOiIlL") == "001111"


class TestHashRecoveryCode:
    def test_a_code_hashes_the_same_however_it_is_written(self) -> None:
        assert hash_recovery_code("ABCD-EFGH-JKMN-PQRS") == hash_recovery_code(
            "abcdefghjkmnpqrs"
        )

    def test_different_codes_hash_differently(self) -> None:
        assert hash_recovery_code("ABCD-EFGH-JKMN-PQRS") != hash_recovery_code(
            "ABCD-EFGH-JKMN-PQRT"
        )

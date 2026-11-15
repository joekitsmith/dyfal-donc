import secrets
import string
from collections.abc import Sequence

from api.tokens import hash_token

# Crockford's base32: digits and capitals without I, L, O and U, so a code read aloud or off paper is not ambiguous
LEFT_OUT = "ILOU"
ALPHABET = "".join(
    character
    for character in string.digits + string.ascii_uppercase
    if character not in LEFT_OUT
)
CODE_LENGTH = 16
GROUP_LENGTH = 4
CODE_COUNT = 10
LOOK_ALIKES = str.maketrans({"I": "1", "L": "1", "O": "0"})


def generate_recovery_codes() -> tuple[str, ...]:
    """A new set of codes to show the user once, as `ABCD-EFGH-JKMN-PQRS`."""
    codes: set[str] = set()
    while len(codes) < CODE_COUNT:
        codes.add("".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH)))

    return tuple(_grouped(code) for code in sorted(codes))


def normalise_recovery_code(text: str) -> str:
    """What was typed, without the dashes and spaces, in capitals, with look-alikes mapped."""
    return "".join(
        character for character in text.upper() if character.isalnum()
    ).translate(LOOK_ALIKES)


def hash_recovery_code(text: str) -> bytes:
    """The hash that stands for the code in the database. Any way of writing it gives the same hash."""
    return hash_token(normalise_recovery_code(text))


def hash_recovery_codes(codes: Sequence[str]) -> tuple[bytes, ...]:
    return tuple(hash_recovery_code(code) for code in codes)


def _grouped(code: str) -> str:
    return "-".join(
        code[start : start + GROUP_LENGTH]
        for start in range(0, len(code), GROUP_LENGTH)
    )

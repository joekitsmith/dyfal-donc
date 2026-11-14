import re
from dataclasses import dataclass

CLITICS = frozenset({"'n", "'r", "'w", "'ma", "'na", "'m", "'i", "'u", "'ch", "'th"})

_CURLY_APOSTROPHES = str.maketrans({"’": "'", "‘": "'"})
_CHUNK = re.compile(r"'?[^\W_]+(?:['-][^\W_]+)*")
_BEFORE_APOSTROPHE = re.compile(r"(?=')")


@dataclass(frozen=True, slots=True, kw_only=True)
class Token:
    text: str
    start: int
    end: int


def tokenise(text: str) -> tuple[Token, ...]:
    normalised = text.translate(_CURLY_APOSTROPHES)
    tokens: list[Token] = []
    for match in _CHUNK.finditer(normalised):
        tokens.extend(_split_chunk(match.group(), match.start()))
    return tuple(tokens)


def _split_chunk(chunk: str, offset: int) -> tuple[Token, ...]:
    tokens: list[Token] = []
    position = offset
    for piece in _BEFORE_APOSTROPHE.split(chunk):
        if not piece:
            continue
        piece_start = position
        position += len(piece)
        if piece.startswith("'") and piece.casefold() not in CLITICS:
            if not tokens:
                piece = piece[1:]
                piece_start += 1
            else:
                previous = tokens.pop()
                piece = previous.text + piece
                piece_start = previous.start
        tokens.append(Token(text=piece, start=piece_start, end=position))
    return tuple(tokens)

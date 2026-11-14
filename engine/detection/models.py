from dataclasses import dataclass

from cymraeg import Mutation, Token
from engine.curriculum import PartOfSpeech

type Problem = UnknownToken | SlotPartOfSpeechMismatch


@dataclass(frozen=True, slots=True, kw_only=True)
class Detection:
    """The curriculum items found in some Welsh text, and what could not be explained.

    ``problems`` are in text order.
    """

    items: tuple[DetectedItem, ...]
    problems: tuple[Problem, ...]

    @property
    def item_ids(self) -> tuple[str, ...]:
        """Unique detected item ids, in order of first appearance."""
        return tuple(dict.fromkeys(item.item_id for item in self.items))


@dataclass(frozen=True, slots=True, kw_only=True)
class DetectedItem:
    """An item found in the text, with the span it covers.

    ``mutation`` is the mutation that had to be undone to recognise a lexeme,
    or ``None`` if it appeared as written.
    """

    item_id: str
    start: int
    end: int
    mutation: Mutation | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UnknownToken:
    """A token that matches no pattern or lexeme."""

    token: Token


@dataclass(frozen=True, slots=True, kw_only=True)
class SlotPartOfSpeechMismatch:
    """A pattern slot was filled by a word of the wrong part of speech."""

    pattern_id: str
    slot: str
    expected: PartOfSpeech
    actual: PartOfSpeech
    item_id: str
    token: Token

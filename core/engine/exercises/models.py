from dataclasses import dataclass

from engine.detection import DetectedItem, Problem

type Issue = (
    Problem
    | UnknownDeclaredItem
    | UndeclaredItem
    | DeclaredItemNotFound
    | MissingNewItem
    | MultipleNewItems
    | WrongNewItem
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Exercise:
    """One English prompt and its Welsh answer, tagged with the items it practises.

    ``items`` are the declared item ids. ``new_item``, if set, is the item the
    exercise introduces, and counts as declared even if it is not in ``items``.
    """

    english: str
    welsh: str
    items: tuple[str, ...]
    new_item: str | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class UnknownDeclaredItem:
    """A declared item id that is not in the curriculum."""

    item_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class UndeclaredItem:
    """An item used in the Welsh that the exercise does not declare."""

    item_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class DeclaredItemNotFound:
    """A declared item that does not appear in the Welsh."""

    item_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MissingNewItem:
    """The Welsh introduces an item the learner has not met, but no ``new_item`` is set."""

    item_id: str


@dataclass(frozen=True, slots=True, kw_only=True)
class MultipleNewItems:
    """The Welsh introduces more than one item the learner has not met."""

    item_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class WrongNewItem:
    """``new_item`` is not the one new item in the Welsh (``detected`` is ``None`` if there is none)."""

    declared: str
    detected: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidationResult:
    detected: tuple[DetectedItem, ...]
    issues: tuple[Issue, ...]

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def detected_item_ids(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(detected.item_id for detected in self.detected))

"""Curriculum domain models: lexemes, patterns, and the curriculum graph.

Plain frozen dataclasses with no parsing logic. Each validates its own invariants
on construction and raises ``CurriculumError``; turning YAML into these types is
the loader's job.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from engine.curriculum import graph
from engine.curriculum.errors import CurriculumError

type Item = Lexeme | Pattern

_SLOT_PATTERN = re.compile(r"\[([A-Z]+)\]")
_LEXEME_ID_PATTERN = re.compile(r"^lex:[a-z0-9-]+$")
_PATTERN_ID_PATTERN = re.compile(r"^pat:[a-z0-9-]+$")


class PartOfSpeech(StrEnum):
    """Part of speech."""

    NOUN = "noun"
    VERB = "verb"
    ADJECTIVE = "adj"
    ADVERB = "adv"
    PREPOSITION = "prep"
    PRONOUN = "pron"
    CONJUNCTION = "conj"
    PARTICLE = "particle"
    NUMERAL = "num"
    PHRASE = "phrase"


class Gender(StrEnum):
    """Grammatical gender of a Welsh noun."""

    MASCULINE = "m"
    FEMININE = "f"


@dataclass(frozen=True, slots=True, kw_only=True)
class Lexeme:
    """A single vocabulary item, e.g. ``siarad``."""

    id: str
    welsh: str
    english: str
    part_of_speech: PartOfSpeech
    gender: Gender | None = None
    notes: str = ""
    prerequisites: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check_id(self.id, _LEXEME_ID_PATTERN, "lex:")
        _check_not_blank(self.id, welsh=self.welsh, english=self.english)
        if self.gender is not None and self.part_of_speech != PartOfSpeech.NOUN:
            raise CurriculumError(
                f"{self.id}: gender is only valid for nouns, "
                f"not {self.part_of_speech.value!r}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class Pattern:
    """A grammar pattern with slots, e.g. ``Dw i'n [VERB]``."""

    id: str
    template: str
    english: str
    slots: Mapping[str, PartOfSpeech] = field(default_factory=dict)
    notes: str = ""
    prerequisites: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _check_id(self.id, _PATTERN_ID_PATTERN, "pat:")
        _check_not_blank(self.id, template=self.template, english=self.english)
        in_template = set(_SLOT_PATTERN.findall(self.template))
        declared = set(self.slots)
        if in_template != declared:
            raise CurriculumError(
                f"{self.id}: template slots {sorted(in_template)} "
                f"do not match declared slot constraints {sorted(declared)}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class Curriculum:
    """A validated prerequisite graph of items plus the intended learning order."""

    items: tuple[Item, ...]
    order: tuple[str, ...]

    def __post_init__(self) -> None:
        ids = [item.id for item in self.items]

        duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        if duplicates:
            raise CurriculumError(f"duplicate item ids: {', '.join(duplicates)}")

        known = set(ids)
        missing = [
            f"{item.id} requires unknown item {dependency}"
            for item in self.items
            for dependency in item.prerequisites
            if dependency not in known
        ]
        if missing:
            raise CurriculumError("unknown prerequisites:\n  " + "\n  ".join(missing))

        if (cycle := graph.find_cycle(self._prerequisite_map())) is not None:
            raise CurriculumError("prerequisite cycle: " + " -> ".join(cycle))

        self._validate_order(known)

    def get(self, item_id: str) -> Item:
        for item in self.items:
            if item.id == item_id:
                return item
        raise KeyError(item_id)

    def topological_order(self) -> tuple[str, ...]:
        """A valid ordering derived from the graph alone (ignores ``order``)."""
        return graph.topological_order(self._prerequisite_map())

    def _prerequisite_map(self) -> dict[str, tuple[str, ...]]:
        return {item.id: item.prerequisites for item in self.items}

    def _validate_order(self, known: set[str]) -> None:
        seen: set[str] = set()
        problems: list[str] = []
        for position, item_id in enumerate(self.order):
            if item_id not in known:
                problems.append(f"order[{position}] is unknown item {item_id}")
            elif item_id in seen:
                problems.append(f"order[{position}] repeats {item_id}")
            seen.add(item_id)
        problems.extend(
            f"{item_id} is missing from order" for item_id in sorted(known - seen)
        )
        if problems:
            raise CurriculumError("invalid order:\n  " + "\n  ".join(problems))

        prerequisites = self._prerequisite_map()
        placed: set[str] = set()
        violations: list[str] = []
        for item_id in self.order:
            late = [
                missing
                for missing in sorted(prerequisites[item_id])
                if missing not in placed
            ]
            if late:
                violations.append(
                    f"{item_id} comes before its prerequisite(s): {', '.join(late)}"
                )
            placed.add(item_id)
        if violations:
            raise CurriculumError(
                "order violates prerequisites:\n  " + "\n  ".join(violations)
            )


def _check_id(item_id: str, pattern: re.Pattern[str], prefix: str) -> None:
    if not pattern.match(item_id):
        raise CurriculumError(
            f"invalid id {item_id!r}: expected {prefix!r} followed by "
            "lowercase letters, digits or hyphens"
        )


def _check_not_blank(item_id: str, **fields: str) -> None:
    for name, value in fields.items():
        if not value.strip():
            raise CurriculumError(f"{item_id}: {name} must not be blank")

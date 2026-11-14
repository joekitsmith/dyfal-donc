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
    DETERMINER = "det"
    NUMERAL = "num"
    PHRASE = "phrase"


class Gender(StrEnum):
    """Grammatical gender of a Welsh noun."""

    MASCULINE = "m"
    FEMININE = "f"


@dataclass(frozen=True, slots=True, kw_only=True)
class Lexeme:
    """A single vocabulary item, e.g. ``siarad``.

    ``forms`` are other surface forms a learner is taught for it (plurals,
    inflections, variants). Every form is unique across the curriculum unless
    the lexemes involved list each other in ``homographs``.
    """

    id: str
    welsh: str
    english: str
    part_of_speech: PartOfSpeech
    gender: Gender | None = None
    forms: tuple[str, ...] = ()
    homographs: tuple[str, ...] = ()
    notes: str = ""
    prerequisites: tuple[str, ...] = ()

    @property
    def surface_forms(self) -> tuple[str, ...]:
        """The base form followed by the other forms."""
        return (self.welsh, *self.forms)

    def __post_init__(self) -> None:
        _check_id(self.id, _LEXEME_ID_PATTERN, "lex:")
        _check_not_blank(self.id, welsh=self.welsh, english=self.english)
        _check_forms(self)
        if self.gender is not None and self.part_of_speech != PartOfSpeech.NOUN:
            raise CurriculumError(
                f"{self.id}: Gender is only valid for nouns, "
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
                f"{self.id}: Template slots {sorted(in_template)} "
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
            raise CurriculumError(f"Duplicate item ids: {', '.join(duplicates)}")

        _check_surface_forms(
            tuple(item for item in self.items if isinstance(item, Lexeme))
        )

        known = set(ids)
        missing = [
            f"{item.id} requires unknown item {dependency}"
            for item in self.items
            for dependency in item.prerequisites
            if dependency not in known
        ]
        if missing:
            raise CurriculumError("Unknown prerequisites:\n  " + "\n  ".join(missing))

        if (cycle := graph.find_cycle(self._prerequisite_map())) is not None:
            raise CurriculumError("Prerequisite cycle: " + " -> ".join(cycle))

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
            raise CurriculumError("Invalid order:\n  " + "\n  ".join(problems))

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
                "Order violates prerequisites:\n  " + "\n  ".join(violations)
            )


def _check_id(item_id: str, pattern: re.Pattern[str], prefix: str) -> None:
    if not pattern.match(item_id):
        raise CurriculumError(
            f"Invalid id {item_id!r}: expected {prefix!r} followed by "
            "lowercase letters, digits or hyphens"
        )


def _check_not_blank(item_id: str, **fields: str) -> None:
    for name, value in fields.items():
        if not value.strip():
            raise CurriculumError(f"{item_id}: {name.capitalize()} must not be blank")


def _check_forms(lexeme: Lexeme) -> None:
    _check_not_blank(lexeme.id, **{f"form {n}": f for n, f in enumerate(lexeme.forms)})
    seen: set[str] = set()
    for form in lexeme.surface_forms:
        key = form.casefold()
        if key in seen:
            raise CurriculumError(f"{lexeme.id}: Duplicate form {form!r}")

        seen.add(key)

    if lexeme.id in lexeme.homographs:
        raise CurriculumError(f"{lexeme.id}: A lexeme cannot be its own homograph")


def _check_surface_forms(lexemes: tuple[Lexeme, ...]) -> None:
    by_id = {lexeme.id: lexeme for lexeme in lexemes}
    problems = [
        f"{lexeme.id} lists unknown homograph {other}"
        for lexeme in lexemes
        for other in lexeme.homographs
        if other not in by_id
    ]
    owners: dict[str, list[Lexeme]] = {}
    for lexeme in lexemes:
        for form in lexeme.surface_forms:
            owners.setdefault(form.casefold(), []).append(lexeme)

    for form, sharing in sorted(owners.items()):
        if len(sharing) > 1 and not _are_homographs(sharing):
            ids = ", ".join(lexeme.id for lexeme in sharing)
            problems.append(f"{form!r} is shared by {ids}")

    if problems:
        raise CurriculumError(
            "Invalid forms (lexemes sharing a form must list each other in homographs):\n  "
            + "\n  ".join(problems)
        )


def _are_homographs(lexemes: list[Lexeme]) -> bool:
    return all(
        other.id in lexeme.homographs
        for lexeme in lexemes
        for other in lexemes
        if other is not lexeme
    )

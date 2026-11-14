from dataclasses import dataclass
from enum import StrEnum

_VOWELS = frozenset("aeiouwyâêîôûŵŷäëïöüáéíóúàèìòù")

# Each table is ordered longest prefix first, and only the first match applies.
# Forward entries that map a prefix to itself stop a shorter prefix matching
# inside a digraph, e.g. the "p" of "ph" does not soften.
_SOFT_FORWARD = (
    ("ll", "l"),
    ("rh", "r"),
    ("dd", "dd"),
    ("ph", "ph"),
    ("th", "th"),
    ("ch", "ch"),
    ("p", "b"),
    ("t", "d"),
    ("c", "g"),
    ("b", "f"),
    ("d", "dd"),
    ("g", ""),
    ("m", "f"),
)
_NASAL_FORWARD = (
    ("dd", "dd"),
    ("ph", "ph"),
    ("th", "th"),
    ("ch", "ch"),
    ("p", "mh"),
    ("t", "nh"),
    ("c", "ngh"),
    ("b", "m"),
    ("d", "n"),
    ("g", "ng"),
)
_ASPIRATE_FORWARD = (
    ("ph", "ph"),
    ("th", "th"),
    ("ch", "ch"),
    ("p", "ph"),
    ("t", "th"),
    ("c", "ch"),
)

# Reverse entries map a mutated prefix to every radical prefix it could come
# from. An empty tuple means the prefix is a digraph that no mutation produces.
_SOFT_REVERSE = (
    ("dd", ("d",)),
    ("ll", ()),
    ("rh", ()),
    ("ff", ()),
    ("b", ("p",)),
    ("d", ("t",)),
    ("g", ("c",)),
    ("f", ("b", "m")),
    ("l", ("ll",)),
    ("r", ("rh",)),
)
_NASAL_REVERSE = (
    ("ngh", ("c",)),
    ("ng", ("g",)),
    ("mh", ("p",)),
    ("nh", ("t",)),
    ("m", ("b",)),
    ("n", ("d",)),
)
_ASPIRATE_REVERSE = (
    ("ph", ("p",)),
    ("th", ("t",)),
    ("ch", ("c",)),
)


class Mutation(StrEnum):
    SOFT = "soft"
    NASAL = "nasal"
    ASPIRATE = "aspirate"
    H_PROTHESIS = "h_prothesis"


@dataclass(frozen=True, slots=True, kw_only=True)
class Demutation:
    radical: str
    mutation: Mutation | None


def mutate(word: str, mutation: Mutation) -> str:
    match mutation:
        case Mutation.SOFT:
            return _apply_forward(word, _SOFT_FORWARD)
        case Mutation.NASAL:
            return _apply_forward(word, _NASAL_FORWARD)
        case Mutation.ASPIRATE:
            return _apply_forward(word, _ASPIRATE_FORWARD)
        case Mutation.H_PROTHESIS:
            return _prefix_h(word)


def demutate(token: str) -> tuple[Demutation, ...]:
    demutations = [Demutation(radical=token, mutation=None)]
    for mutation in Mutation:
        for radical in sorted(set(_radicals(token, mutation))):
            demutations.append(Demutation(radical=radical, mutation=mutation))

    return tuple(demutations)


def find_demutation(token: str, radical: str) -> Demutation | None:
    """How ``token`` reads as ``radical`` (ignoring case), preferring no mutation."""
    for demutation in demutate(token):
        if demutation.radical.casefold() == radical.casefold():
            return demutation

    return None


def _apply_forward(word: str, table: tuple[tuple[str, str], ...]) -> str:
    lowered = word.lower()
    for prefix, replacement in table:
        if lowered.startswith(prefix):
            return _replace_prefix(word, len(prefix), replacement)

    return word


def _prefix_h(word: str) -> str:
    if word[:1].lower() not in _VOWELS:
        return word

    return _replace_prefix(word, 1, "h" + word[0].lower())


def _radicals(token: str, mutation: Mutation) -> tuple[str, ...]:
    match mutation:
        case Mutation.SOFT:
            return _apply_reverse(token, _SOFT_REVERSE) + _restore_deleted_g(token)
        case Mutation.NASAL:
            return _apply_reverse(token, _NASAL_REVERSE)
        case Mutation.ASPIRATE:
            return _apply_reverse(token, _ASPIRATE_REVERSE)
        case Mutation.H_PROTHESIS:
            return _remove_h(token)


def _apply_reverse(
    token: str, table: tuple[tuple[str, tuple[str, ...]], ...]
) -> tuple[str, ...]:
    lowered = token.lower()
    for prefix, radical_prefixes in table:
        if lowered.startswith(prefix):
            return tuple(
                _replace_prefix(token, len(prefix), radical_prefix)
                for radical_prefix in radical_prefixes
            )

    return ()


def _restore_deleted_g(token: str) -> tuple[str, ...]:
    lowered = token.lower()
    if lowered[:2] in ("ll", "rh"):
        return ()

    if lowered[:1] in _VOWELS or lowered[:1] in ("l", "r"):
        return (_replace_prefix(token, 0, "g"),)

    return ()


def _remove_h(token: str) -> tuple[str, ...]:
    lowered = token.lower()
    if lowered[:1] == "h" and lowered[1:2] in _VOWELS:
        return (_replace_prefix(token, 1, ""),)

    return ()


def _replace_prefix(word: str, prefix_length: int, replacement: str) -> str:
    remainder = word[prefix_length:]
    if prefix_length == 0 and word[:1].isupper() and not _is_all_capitals(word):
        remainder = remainder[:1].lower() + remainder[1:]

    result = replacement + remainder
    if word[:1].isupper():
        return result[:1].upper() + result[1:]

    return result


def _is_all_capitals(word: str) -> bool:
    return len(word) > 1 and word.isupper()

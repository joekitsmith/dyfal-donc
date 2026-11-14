from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

from cymraeg import Token, find_demutation, tokenise
from engine.curriculum import Pattern
from engine.detection.index import Candidate, CurriculumIndex, PatternShape, Slot
from engine.detection.models import (
    DetectedItem,
    Detection,
    Problem,
    SlotPartOfSpeechMismatch,
    UnknownToken,
)


def detect_items(
    text: str, index: CurriculumIndex, preferred: AbstractSet[str] = frozenset()
) -> Detection:
    """Find the curriculum items in Welsh ``text``.

    At each token it tries patterns, then multi-word lexemes, then single words.
    When a mutated or ambiguous word could be several lexemes, it prefers an
    unmutated reading, then items in ``preferred``, then the order of
    ``demutate``. Tokens matching nothing are reported as ``UnknownToken``.
    """
    tokens = tokenise(text)
    items: list[DetectedItem] = []
    problems: list[Problem] = []
    position = 0
    while position < len(tokens):
        match = _match_at(tokens, position, index, preferred)
        if match is None:
            problems.append(UnknownToken(token=tokens[position]))
            position += 1
        else:
            items.extend(match.items)
            problems.extend(match.problems)
            position += match.length
    return Detection(items=tuple(items), problems=tuple(problems))


@dataclass(frozen=True, slots=True, kw_only=True)
class _Match:
    items: tuple[DetectedItem, ...]
    problems: tuple[Problem, ...]
    length: int


def _match_at(
    tokens: Sequence[Token],
    position: int,
    index: CurriculumIndex,
    preferred: AbstractSet[str],
) -> _Match | None:
    pattern_match = _match_pattern(tokens, position, index, preferred)
    if pattern_match is not None:
        return pattern_match
    phrase_match = _match_phrase(tokens, position, index)
    if phrase_match is not None:
        return phrase_match
    return _match_word(tokens[position], index, preferred)


def _match_pattern(
    tokens: Sequence[Token],
    position: int,
    index: CurriculumIndex,
    preferred: AbstractSet[str],
) -> _Match | None:
    # Shapes are ordered longest first, so min() keeps that order on ties
    matches = tuple(
        match
        for shape in index.shapes
        if (match := _try_pattern(shape, tokens, position, index, preferred))
        is not None
    )
    if not matches:
        return None
    return min(matches, key=lambda match: (bool(match.problems), -match.length))


def _try_pattern(
    shape: PatternShape,
    tokens: Sequence[Token],
    position: int,
    index: CurriculumIndex,
    preferred: AbstractSet[str],
) -> _Match | None:
    if position + len(shape.elements) > len(tokens):
        return None
    first, last = tokens[position], tokens[position + len(shape.elements) - 1]
    items = [DetectedItem(item_id=shape.pattern.id, start=first.start, end=last.end)]
    problems: list[Problem] = []
    for offset, element in enumerate(shape.elements):
        token = tokens[position + offset]
        if isinstance(element, str):
            if token.text.casefold() != element:
                return None
            continue
        slot_items, slot_problems = _fill_slot(
            shape.pattern, element, token, index, preferred
        )
        items.extend(slot_items)
        problems.extend(slot_problems)
    return _Match(
        items=tuple(items), problems=tuple(problems), length=len(shape.elements)
    )


def _fill_slot(
    pattern: Pattern,
    slot: Slot,
    token: Token,
    index: CurriculumIndex,
    preferred: AbstractSet[str],
) -> tuple[tuple[DetectedItem, ...], tuple[Problem, ...]]:
    candidates = index.candidates(token.text)
    if not candidates:
        return (), (UnknownToken(token=token),)
    right_part = tuple(
        candidate
        for candidate in candidates
        if candidate.lexeme.part_of_speech == slot.part_of_speech
    )
    if right_part:
        return (_detect(_best(right_part, preferred), token),), ()
    best = _best(candidates, preferred)
    mismatch = SlotPartOfSpeechMismatch(
        pattern_id=pattern.id,
        slot=slot.name,
        expected=slot.part_of_speech,
        actual=best.lexeme.part_of_speech,
        item_id=best.lexeme.id,
        token=token,
    )
    return (_detect(best, token),), (mismatch,)


def _match_phrase(
    tokens: Sequence[Token], position: int, index: CurriculumIndex
) -> _Match | None:
    for phrase in index.phrases:
        end = position + len(phrase.words)
        if end > len(tokens):
            continue
        rest_matches = all(
            tokens[position + offset].text.casefold() == word
            for offset, word in enumerate(phrase.words)
            if offset > 0
        )
        if not rest_matches:
            continue
        first = find_demutation(tokens[position].text, phrase.words[0])
        if first is None:
            continue
        item = DetectedItem(
            item_id=phrase.lexeme.id,
            start=tokens[position].start,
            end=tokens[end - 1].end,
            form=phrase.form,
            mutation=first.mutation,
        )
        return _Match(items=(item,), problems=(), length=len(phrase.words))
    return None


def _match_word(
    token: Token, index: CurriculumIndex, preferred: AbstractSet[str]
) -> _Match | None:
    candidates = index.candidates(token.text)
    if not candidates:
        return None
    return _Match(
        items=(_detect(_best(candidates, preferred), token),), problems=(), length=1
    )


def _best(candidates: Sequence[Candidate], preferred: AbstractSet[str]) -> Candidate:
    return min(
        candidates,
        key=lambda candidate: (
            candidate.mutation is not None,
            candidate.lexeme.id not in preferred,
            candidate.order,
            candidate.lexeme.id,
        ),
    )


def _detect(candidate: Candidate, token: Token) -> DetectedItem:
    return DetectedItem(
        item_id=candidate.lexeme.id,
        start=token.start,
        end=token.end,
        form=candidate.form,
        mutation=candidate.mutation,
    )

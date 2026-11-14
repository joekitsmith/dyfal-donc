from collections.abc import Iterable, Sequence
from dataclasses import replace

from engine.detection import CurriculumIndex, detect_items
from evals.benchmark.errors import BenchmarkError
from evals.benchmark.lexemes import lexemes_for_lemmas
from evals.benchmark.models import ItemResult, ItemScore, SentenceCandidates
from evals.gold import GoldSentence, Tag


def score_items(
    sentences: Sequence[GoldSentence],
    index: CurriculumIndex,
    candidates: Sequence[SentenceCandidates] | None = None,
) -> ItemResult:
    """Precision and recall of ``detect_items`` against the gold items.

    Without ``candidates`` it uses the declared forms only. With them, each
    token also matches the lexemes its candidate lemmas point to. Patterns and
    lexemes are scored together, and each tag covers the sentences carrying it.
    """
    if candidates is not None and len(candidates) != len(sentences):
        raise BenchmarkError(
            f"Expected candidates for {len(sentences)} sentences, got {len(candidates)}"
        )

    scored = tuple(
        (
            sentence,
            _score_sentence(
                sentence, index, None if candidates is None else candidates[position]
            ),
        )
        for position, sentence in enumerate(sentences)
    )

    return ItemResult(
        overall=_total(score for _, score in scored),
        by_tag={
            tag: _total(score for sentence, score in scored if tag in sentence.tags)
            for tag in Tag
        },
    )


def augment_index(
    index: CurriculumIndex, texts: Sequence[str], candidates: SentenceCandidates
) -> CurriculumIndex:
    """A copy of the index where each token also matches the lexemes its lemmas point to."""
    words = {word: tuple(lexemes) for word, lexemes in index.words.items()}
    for text, options in zip(texts, candidates, strict=True):
        key = text.casefold()
        known = {lexeme.id for lexeme in words.get(key, ())}
        extra = tuple(
            lexeme
            for lexeme in lexemes_for_lemmas(index, options)
            if lexeme.id not in known
        )
        if extra:
            words[key] = (*words.get(key, ()), *extra)

    return replace(index, words=words)


def _score_sentence(
    sentence: GoldSentence,
    index: CurriculumIndex,
    candidates: SentenceCandidates | None,
) -> ItemScore:
    if candidates is not None:
        if len(candidates) != len(sentence.tokens):
            raise BenchmarkError(
                f"{sentence.id}: Expected candidates for {len(sentence.tokens)} tokens, "
                f"got {len(candidates)}"
            )

        index = augment_index(
            index, [token.text for token in sentence.tokens], candidates
        )

    predicted = frozenset(detect_items(sentence.welsh, index).item_ids)
    expected = sentence.item_ids

    return ItemScore(
        true_positives=len(predicted & expected),
        predicted=len(predicted),
        expected=len(expected),
    )


def _total(scores: Iterable[ItemScore]) -> ItemScore:
    scores = tuple(scores)

    return ItemScore(
        true_positives=sum(score.true_positives for score in scores),
        predicted=sum(score.predicted for score in scores),
        expected=sum(score.expected for score in scores),
    )

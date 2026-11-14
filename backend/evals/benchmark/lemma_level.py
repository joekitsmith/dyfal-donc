from collections.abc import Iterable, Sequence

from evals.benchmark.errors import BenchmarkError
from evals.benchmark.models import LemmaResult, LemmaScore, SentenceCandidates
from evals.gold import GoldSentence, Tag


def score_lemmas(
    sentences: Sequence[GoldSentence], candidates: Sequence[SentenceCandidates]
) -> LemmaResult:
    """Score a lemmatiser's candidates for every token against the gold lemmas.

    A token is correct when its gold lemma is among the candidates, ignoring
    case. Each tag covers the tokens of the sentences carrying it.
    """
    if len(sentences) != len(candidates):
        raise BenchmarkError(
            f"Expected candidates for {len(sentences)} sentences, got {len(candidates)}"
        )

    scored = tuple(
        (sentence, _score_sentence(sentence, sentence_candidates))
        for sentence, sentence_candidates in zip(sentences, candidates, strict=True)
    )

    return LemmaResult(
        overall=_total(score for _, score in scored),
        by_tag={
            tag: _total(score for sentence, score in scored if tag in sentence.tags)
            for tag in Tag
        },
    )


def _score_sentence(
    sentence: GoldSentence, candidates: SentenceCandidates
) -> LemmaScore:
    if len(sentence.tokens) != len(candidates):
        raise BenchmarkError(
            f"{sentence.id}: Expected candidates for {len(sentence.tokens)} tokens, "
            f"got {len(candidates)}"
        )

    correct = sum(
        token.lemma.casefold() in {option.casefold() for option in options}
        for token, options in zip(sentence.tokens, candidates, strict=True)
    )

    return LemmaScore(
        correct=correct,
        tokens=len(sentence.tokens),
        candidates=sum(len(options) for options in candidates),
    )


def _total(scores: Iterable[LemmaScore]) -> LemmaScore:
    scores = tuple(scores)

    return LemmaScore(
        correct=sum(score.correct for score in scores),
        tokens=sum(score.tokens for score in scores),
        candidates=sum(score.candidates for score in scores),
    )

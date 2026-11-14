from collections.abc import Sequence

from engine.detection import CurriculumIndex
from evals.benchmark.errors import BenchmarkError
from evals.benchmark.models import AuthoringResult, SentenceCandidates
from evals.gold import GoldSentence


def score_authoring(
    sentences: Sequence[GoldSentence],
    index: CurriculumIndex,
    candidates: Sequence[SentenceCandidates],
) -> AuthoringResult:
    """Score a lemmatiser as a way to find forms the curriculum should declare.

    A suggestion is a token that the curriculum doesn't recognise as a lexeme
    (even through mutation) but whose lemmas point to one. It is correct when
    that lexeme is the token's gold item. Multi-word lexemes are not covered.
    """
    if len(sentences) != len(candidates):
        raise BenchmarkError(
            f"Expected candidates for {len(sentences)} sentences, got {len(candidates)}"
        )

    phrase_ids = {phrase.lexeme.id for phrase in index.phrases}
    undeclared = surfaced = suggestions = correct_suggestions = 0
    missed: list[str] = []
    wrong: list[str] = []
    for sentence, sentence_candidates in zip(sentences, candidates, strict=True):
        if len(sentence.tokens) != len(sentence_candidates):
            raise BenchmarkError(
                f"{sentence.id}: Expected candidates for {len(sentence.tokens)} tokens, "
                f"got {len(sentence_candidates)}"
            )

        for token, options in zip(sentence.tokens, sentence_candidates, strict=True):
            recognised = {
                candidate.lexeme.id for candidate in index.candidates(token.text)
            }
            suggested = {
                lexeme.id for lexeme in index.lexemes_for(options)
            } - recognised
            suggestions += len(suggested)
            correct_suggestions += token.item in suggested
            wrong.extend(
                f"{token.text} ({lexeme_id})"
                for lexeme_id in sorted(suggested)
                if lexeme_id != token.item
            )

            is_undeclared = (
                token.item is not None
                and token.item not in phrase_ids
                and token.item not in recognised
            )
            if not is_undeclared:
                continue

            undeclared += 1
            if token.item in suggested:
                surfaced += 1
            else:
                missed.append(f"{token.text} ({token.item})")

    return AuthoringResult(
        undeclared=undeclared,
        surfaced=surfaced,
        suggestions=suggestions,
        correct_suggestions=correct_suggestions,
        missed=tuple(missed),
        wrong=tuple(wrong),
    )

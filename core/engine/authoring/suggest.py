from dataclasses import replace

from cymraeg import Demutation, Lemmatiser, Token, demutate, tokenise
from engine.authoring.models import FormSuggestion
from engine.detection import CurriculumIndex, UnknownToken, detect_items


def suggest_forms(
    text: str, index: CurriculumIndex, lemmatiser: Lemmatiser
) -> tuple[FormSuggestion, ...]:
    """Forms the curriculum could declare so that unknown tokens in ``text`` are recognised.

    Only tokens that ``detect_items`` reports as unknown are considered, and
    the lemmatiser sees the whole sentence. Suggestions are only proposals: a
    lemmatiser can be wrong, so a person should approve each one before it is
    declared as a form.

    A token is first read as written. Only if that suggests nothing is it read
    as a mutation of each radical it could be, so that an inflected, mutated
    word is declared by its radical form.
    """
    tokens = tokenise(text)
    unknown = tuple(
        problem.token
        for problem in detect_items(text, index).problems
        if isinstance(problem, UnknownToken)
    )

    suggestions: dict[tuple[str, str], FormSuggestion] = {}
    for token in unknown:
        for suggestion in _suggest_for_token(token, tokens, index, lemmatiser):
            suggestions.setdefault((suggestion.form, suggestion.item_id), suggestion)

    return tuple(suggestions.values())


def _suggest_for_token(
    token: Token,
    tokens: tuple[Token, ...],
    index: CurriculumIndex,
    lemmatiser: Lemmatiser,
) -> tuple[FormSuggestion, ...]:
    position = tokens.index(token)
    as_written = _suggest_for_reading(
        Demutation(radical=token.text, mutation=None),
        token,
        position,
        tokens,
        index,
        lemmatiser,
    )
    if as_written:
        return as_written

    return tuple(
        suggestion
        for reading in demutate(token.text)
        if reading.mutation is not None
        for suggestion in _suggest_for_reading(
            reading, token, position, tokens, index, lemmatiser
        )
    )


def _suggest_for_reading(
    reading: Demutation,
    token: Token,
    position: int,
    tokens: tuple[Token, ...],
    index: CurriculumIndex,
    lemmatiser: Lemmatiser,
) -> tuple[FormSuggestion, ...]:
    sentence = (
        *tokens[:position],
        replace(token, text=reading.radical),
        *tokens[position + 1 :],
    )
    lemmas = lemmatiser.lemmatise(sentence)[position]

    return tuple(
        FormSuggestion(
            token=token,
            form=reading.radical.casefold(),
            item_id=lexeme.id,
            english=lexeme.english,
            lemma=lemma,
            mutation=reading.mutation,
        )
        for lemma in lemmas
        for lexeme in index.lexemes_for([lemma])
    )

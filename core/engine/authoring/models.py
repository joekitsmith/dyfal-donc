from dataclasses import dataclass

from cymraeg import Mutation, Token


@dataclass(frozen=True, slots=True, kw_only=True)
class FormSuggestion:
    """A token the curriculum doesn't recognise that may be a form of a lexeme.

    ``form`` is the casefolded form to declare. It is the token as written, or,
    when ``mutation`` is set, the radical it would be a mutation of.
    ``lemma`` is the lemma the lemmatiser gave that led to the lexeme.
    """

    token: Token
    form: str
    item_id: str
    english: str
    lemma: str
    mutation: Mutation | None = None

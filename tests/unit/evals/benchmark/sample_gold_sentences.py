from collections.abc import Mapping, Sequence

from cymraeg import Token
from engine.curriculum import Curriculum, Lexeme, PartOfSpeech
from evals.gold import GoldSentence, GoldToken, Tag
from tests.unit.engine.sample_curriculum import STANDARD_ITEMS, curriculum_of

GWELD = Lexeme(
    id="lex:gweld", welsh="gweld", english="to see", part_of_speech=PartOfSpeech.VERB
)
CURRICULUM: Curriculum = curriculum_of((*STANDARD_ITEMS, GWELD))

LEARNING_WELSH = GoldSentence(
    id="learning-welsh",
    welsh="Dw i'n dysgu Cymraeg",
    english="I'm learning Welsh",
    tags=(Tag.CLITIC,),
    patterns=("pat:dw-in",),
    tokens=(
        GoldToken(text="Dw", lemma="bod"),
        GoldToken(text="i", lemma="i"),
        GoldToken(text="'n", lemma="yn"),
        GoldToken(text="dysgu", lemma="dysgu", item="lex:dysgu"),
        GoldToken(text="Cymraeg", lemma="Cymraeg", item="lex:cymraeg"),
    ),
)
SAW_ME = GoldSentence(
    id="saw-me",
    welsh="Gwelais i",
    english="I saw",
    tags=(Tag.INFLECTION,),
    tokens=(
        GoldToken(text="Gwelais", lemma="gweld", item="lex:gweld"),
        GoldToken(text="i", lemma="i"),
    ),
)
SENTENCES = (LEARNING_WELSH, SAW_ME)

PERFECT_LEMMAS: Mapping[str, tuple[str, ...]] = {
    "Dw": ("bod",),
    "i": ("i",),
    "'n": ("yn",),
    "dysgu": ("dysgu",),
    "Cymraeg": ("Cymraeg",),
    "Gwelais": ("gweld",),
}


class FixedLemmatiser:
    """A lemmatiser that looks each token up in a fixed dictionary."""

    def __init__(self, lemmas: Mapping[str, tuple[str, ...]]) -> None:
        self._lemmas = lemmas

    def lemmatise(self, tokens: Sequence[Token]) -> tuple[tuple[str, ...], ...]:
        return tuple(self._lemmas.get(token.text, ()) for token in tokens)

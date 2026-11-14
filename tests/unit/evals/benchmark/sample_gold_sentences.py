from collections.abc import Mapping

from engine.curriculum import Curriculum
from evals.gold import GoldSentence, GoldToken, Tag
from tests.unit.engine.sample_curriculum import GWELD, STANDARD_ITEMS, curriculum_of

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

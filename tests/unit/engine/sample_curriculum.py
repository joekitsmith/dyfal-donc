from engine.curriculum import Curriculum, Item, Lexeme, PartOfSpeech, Pattern

DW_IN_MOYN = Pattern(
    id="pat:dw-in-moyn",
    template="Dw i'n moyn [VERB]",
    english="I want to [VERB]",
    slots={"VERB": PartOfSpeech.VERB},
)
DW_IN_MOYN_NOUN = Pattern(
    id="pat:dw-in-moyn-noun",
    template="Dw i'n moyn [NOUN]",
    english="I want [NOUN]",
    slots={"NOUN": PartOfSpeech.NOUN},
)
DW_IN = Pattern(
    id="pat:dw-in",
    template="Dw i'n [VERB]",
    english="I'm [VERB]ing",
    slots={"VERB": PartOfSpeech.VERB},
)
GALLA_I = Pattern(
    id="pat:galla-i",
    template="Galla i [VERB]",
    english="I can [VERB]",
    slots={"VERB": PartOfSpeech.VERB},
)
SIARAD = Lexeme(
    id="lex:siarad",
    welsh="siarad",
    english="to speak",
    part_of_speech=PartOfSpeech.VERB,
)
DYSGU = Lexeme(
    id="lex:dysgu", welsh="dysgu", english="to learn", part_of_speech=PartOfSpeech.VERB
)
MYND = Lexeme(
    id="lex:mynd", welsh="mynd", english="to go", part_of_speech=PartOfSpeech.VERB
)
CYMRAEG = Lexeme(
    id="lex:cymraeg", welsh="Cymraeg", english="Welsh", part_of_speech=PartOfSpeech.NOUN
)
COFFI = Lexeme(
    id="lex:coffi", welsh="coffi", english="coffee", part_of_speech=PartOfSpeech.NOUN
)
FAN_HYN = Lexeme(
    id="lex:fan-hyn",
    welsh="fan hyn",
    english="here",
    part_of_speech=PartOfSpeech.ADVERB,
)
TY_MAWR = Lexeme(
    id="lex:ty-mawr",
    welsh="tŷ mawr",
    english="big house",
    part_of_speech=PartOfSpeech.PHRASE,
)
GWELD = Lexeme(
    id="lex:gweld", welsh="gweld", english="to see", part_of_speech=PartOfSpeech.VERB
)
STANDARD_ITEMS = (
    DW_IN_MOYN,
    DW_IN_MOYN_NOUN,
    DW_IN,
    GALLA_I,
    SIARAD,
    DYSGU,
    MYND,
    CYMRAEG,
    COFFI,
    FAN_HYN,
    TY_MAWR,
)


def curriculum_of(items: tuple[Item, ...] = STANDARD_ITEMS) -> Curriculum:
    return Curriculum(items=items, order=tuple(item.id for item in items))

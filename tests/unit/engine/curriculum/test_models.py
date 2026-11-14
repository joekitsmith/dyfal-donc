import pytest

from engine.curriculum import (
    Curriculum,
    CurriculumError,
    Gender,
    Lexeme,
    PartOfSpeech,
    Pattern,
)


def build(items: list[Lexeme], order: list[str]) -> Curriculum:
    return Curriculum(items=tuple(items), order=tuple(order))


def L(id_: str, *prerequisites: str) -> Lexeme:
    return Lexeme(
        id=f"lex:{id_}",
        welsh=id_,
        english=id_,
        part_of_speech=PartOfSpeech.VERB,
        prerequisites=prerequisites,
    )


class TestModels:
    def test_gender_requires_noun(self) -> None:
        with pytest.raises(CurriculumError, match="gender is only valid for nouns"):
            Lexeme(
                id="lex:x",
                welsh="x",
                english="x",
                part_of_speech=PartOfSpeech.VERB,
                gender=Gender.MASCULINE,
            )

    def test_noun_with_gender(self) -> None:
        assert (
            Lexeme(
                id="lex:x",
                welsh="x",
                english="x",
                part_of_speech=PartOfSpeech.NOUN,
                gender=Gender.FEMININE,
            ).gender
            == Gender.FEMININE
        )

    def test_id_prefix_enforced(self) -> None:
        with pytest.raises(CurriculumError, match="invalid id 'pat:x'"):
            Lexeme(id="pat:x", welsh="x", english="x", part_of_speech=PartOfSpeech.NOUN)

    def test_pattern_slots_must_match_template(self) -> None:
        with pytest.raises(CurriculumError, match="do not match declared slot"):
            Pattern(
                id="pat:x", template="Dw i'n [VERB]", english="I am [VERB]ing", slots={}
            )

    def test_pattern_ok(self) -> None:
        p = Pattern(
            id="pat:x",
            template="Dw i'n [VERB]",
            english="I'm [VERB]ing",
            slots={"VERB": PartOfSpeech.VERB},
        )
        assert p.slots == {"VERB": PartOfSpeech.VERB}

    def test_blank_fields_rejected(self) -> None:
        with pytest.raises(CurriculumError, match="welsh must not be blank"):
            Lexeme(id="lex:x", welsh=" ", english="x", part_of_speech=PartOfSpeech.NOUN)


class TestValidation:
    def test_valid(self) -> None:
        c = build([L("a"), L("b", "lex:a")], ["lex:a", "lex:b"])
        assert c.topological_order() == ("lex:a", "lex:b")
        assert c.get("lex:b").id == "lex:b"

    def test_duplicate_ids(self) -> None:
        with pytest.raises(CurriculumError, match="duplicate item ids: lex:a"):
            build([L("a"), L("a")], ["lex:a"])

    def test_unknown_prerequisite(self) -> None:
        with pytest.raises(
            CurriculumError, match="lex:a requires unknown item lex:zzz"
        ):
            build([L("a", "lex:zzz")], ["lex:a"])

    def test_cycle_reports_path(self) -> None:
        items = [L("a", "lex:c"), L("b", "lex:a"), L("c", "lex:b")]
        with pytest.raises(CurriculumError, match=r"lex:a -> lex:c -> lex:b -> lex:a"):
            build(items, ["lex:a", "lex:b", "lex:c"])

    def test_self_prerequisite_is_a_cycle(self) -> None:
        with pytest.raises(CurriculumError, match=r"lex:a -> lex:a"):
            build([L("a", "lex:a")], ["lex:a"])

    def test_order_violating_prerequisites(self) -> None:
        with pytest.raises(
            CurriculumError, match="lex:a comes before its prerequisite.*lex:b"
        ):
            build([L("a", "lex:b"), L("b")], ["lex:a", "lex:b"])

    def test_order_missing_item(self) -> None:
        with pytest.raises(CurriculumError, match="lex:b is missing from order"):
            build([L("a"), L("b")], ["lex:a"])

    def test_order_unknown_item(self) -> None:
        with pytest.raises(
            CurriculumError, match="order\\[1\\] is unknown item lex:nope"
        ):
            build([L("a")], ["lex:a", "lex:nope"])

    def test_order_repeated_item(self) -> None:
        with pytest.raises(CurriculumError, match="order\\[1\\] repeats lex:a"):
            build([L("a")], ["lex:a", "lex:a"])

from engine.curriculum import Curriculum
from engine.exercises import (
    DeclaredItemNotFound,
    Exercise,
    MissingNewItem,
    MultipleNewItems,
    UndeclaredItem,
    UnknownDeclaredItem,
    ValidationResult,
    WrongNewItem,
    validate_exercise,
)
from engine.detection import UnknownToken
from tests.unit.engine.sample_curriculum import curriculum_of


def validate(
    welsh: str,
    items: tuple[str, ...] = (),
    *,
    new_item: str | None = None,
    known: frozenset[str] | None = None,
    curriculum: Curriculum | None = None,
) -> ValidationResult:
    curriculum = curriculum or curriculum_of()
    if known is None:
        known = frozenset(item.id for item in curriculum.items)

    exercise = Exercise(english="", welsh=welsh, items=items, new_item=new_item)
    return validate_exercise(exercise, curriculum, known)


class TestValidateExercise:
    def test_clean_exercise_is_valid(self) -> None:
        result = validate("Dw i'n moyn siarad", ("pat:dw-in-moyn", "lex:siarad"))
        assert result.is_valid
        assert result.detected_item_ids == ("pat:dw-in-moyn", "lex:siarad")

    def test_detection_problems_are_issues(self) -> None:
        result = validate(
            "Dw i'n moyn siarad Almaeneg", ("pat:dw-in-moyn", "lex:siarad")
        )
        assert [type(issue) for issue in result.issues] == [UnknownToken]

    def test_unknown_filler_does_not_hide_the_pattern(self) -> None:
        result = validate("Dw i'n moyn blah", ("pat:dw-in-moyn",))
        assert [type(issue) for issue in result.issues] == [UnknownToken]


class TestDeclaredItems:
    def test_item_used_but_not_declared(self) -> None:
        result = validate("Dw i'n moyn siarad", ("pat:dw-in-moyn",))
        assert result.issues == (UndeclaredItem(item_id="lex:siarad"),)

    def test_item_declared_but_not_used(self) -> None:
        result = validate(
            "Dw i'n moyn siarad", ("pat:dw-in-moyn", "lex:siarad", "lex:coffi")
        )
        assert result.issues == (DeclaredItemNotFound(item_id="lex:coffi"),)

    def test_declared_item_that_is_not_in_the_curriculum(self) -> None:
        result = validate(
            "Dw i'n moyn siarad", ("pat:dw-in-moyn", "lex:siarad", "lex:nope")
        )
        assert result.issues == (UnknownDeclaredItem(item_id="lex:nope"),)

    def test_new_item_counts_as_declared(self) -> None:
        known = frozenset({"pat:dw-in-moyn"})
        result = validate(
            "Dw i'n moyn siarad",
            ("pat:dw-in-moyn",),
            new_item="lex:siarad",
            known=known,
        )
        assert result.is_valid

    def test_token_issues_come_before_declaration_issues(self) -> None:
        result = validate("Dw i'n moyn siarad blah", ("pat:dw-in-moyn",))
        assert [type(issue) for issue in result.issues] == [
            UnknownToken,
            UndeclaredItem,
        ]


class TestNewItems:
    ITEMS = ("pat:dw-in-moyn", "lex:dysgu")
    KNOWN = frozenset({"pat:dw-in-moyn", "lex:siarad", "lex:coffi"})

    def test_exactly_one_new_item_that_is_declared_is_valid(self) -> None:
        result = validate(
            "Dw i'n moyn dysgu", self.ITEMS, new_item="lex:dysgu", known=self.KNOWN
        )
        assert result.is_valid

    def test_review_exercise_with_no_new_item_is_valid(self) -> None:
        result = validate(
            "Dw i'n moyn siarad", ("pat:dw-in-moyn", "lex:siarad"), known=self.KNOWN
        )
        assert result.is_valid

    def test_new_item_missing_from_the_exercise(self) -> None:
        result = validate("Dw i'n moyn dysgu", self.ITEMS, known=self.KNOWN)
        assert result.issues == (MissingNewItem(item_id="lex:dysgu"),)

    def test_more_than_one_new_item(self) -> None:
        known = frozenset({"pat:dw-in-moyn"})
        result = validate(
            "Dw i'n moyn dysgu Cymraeg",
            ("pat:dw-in-moyn", "lex:dysgu", "lex:cymraeg"),
            new_item="lex:dysgu",
            known=known,
        )
        assert result.issues == (
            MultipleNewItems(item_ids=("lex:dysgu", "lex:cymraeg")),
        )

    def test_declared_new_item_is_not_the_new_one(self) -> None:
        result = validate(
            "Dw i'n moyn dysgu",
            ("pat:dw-in-moyn", "lex:dysgu", "lex:siarad"),
            new_item="lex:siarad",
            known=self.KNOWN,
        )
        assert (
            WrongNewItem(declared="lex:siarad", detected="lex:dysgu") in result.issues
        )

    def test_declared_new_item_when_nothing_is_new(self) -> None:
        result = validate(
            "Dw i'n moyn siarad",
            ("pat:dw-in-moyn", "lex:siarad"),
            new_item="lex:siarad",
            known=self.KNOWN,
        )
        assert result.issues == (WrongNewItem(declared="lex:siarad", detected=None),)

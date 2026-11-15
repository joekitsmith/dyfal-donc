from cymraeg import Token
from engine.detection import DetectedItem, UnknownToken
from engine.exercises import Exercise, ValidationResult


class TestExercise:
    def test_new_item_defaults_to_none(self) -> None:
        exercise = Exercise(
            english="I want to speak", welsh="Dw i'n moyn siarad", items=()
        )
        assert exercise.new_item is None


class TestValidationResult:
    def test_is_valid_when_there_are_no_issues(self) -> None:
        assert ValidationResult(detected=(), issues=()).is_valid

    def test_is_not_valid_with_any_issue(self) -> None:
        issue = UnknownToken(token=Token(text="blah", start=0, end=4))
        assert not ValidationResult(detected=(), issues=(issue,)).is_valid

    def test_detected_item_ids_are_unique_and_in_order_of_appearance(self) -> None:
        detected = tuple(
            DetectedItem(item_id=item_id, start=position, end=position + 1)
            for position, item_id in enumerate(["lex:b", "lex:a", "lex:b"])
        )
        result = ValidationResult(detected=detected, issues=())
        assert result.detected_item_ids == ("lex:b", "lex:a")


class TestDeclaredItems:
    def test_is_the_items_when_there_is_no_new_item(self) -> None:
        exercise = Exercise(english="", welsh="", items=("lex:a", "lex:b"))

        assert exercise.declared_items == ("lex:a", "lex:b")

    def test_adds_a_new_item_that_is_not_in_items(self) -> None:
        exercise = Exercise(english="", welsh="", items=("lex:a",), new_item="lex:b")

        assert exercise.declared_items == ("lex:a", "lex:b")

    def test_does_not_repeat_a_new_item_that_is_in_items(self) -> None:
        exercise = Exercise(
            english="", welsh="", items=("lex:a", "lex:b"), new_item="lex:a"
        )

        assert exercise.declared_items == ("lex:a", "lex:b")

    def test_drops_repeated_items(self) -> None:
        exercise = Exercise(english="", welsh="", items=("lex:a", "lex:a"))

        assert exercise.declared_items == ("lex:a",)

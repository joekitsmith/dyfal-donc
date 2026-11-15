import uuid
from datetime import UTC, datetime, timedelta

import pytest

from api.mappings import (
    to_exercise_purpose,
    to_exercise_response,
    to_issue_selection,
    to_nothing_eligible_response,
)
from api.schemas import ExercisePurpose
from engine.exercises import Exercise
from engine.scheduler import Purpose, Selection
from persistence.database import IssuedSelectionRecord

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)


def selection(
    *, items: tuple[str, ...] = ("lex:a",), introduces: str | None = "lex:b"
) -> Selection:
    return Selection(
        exercise_id="ex:1",
        exercise=Exercise(
            english="To speak", welsh="Siarad", items=items, new_item=introduces
        ),
        purpose=Purpose.INTRODUCTION,
        introduces=introduces,
    )


class TestToIssueSelection:
    def test_keeps_what_is_needed_to_record_the_outcome(self) -> None:
        learner_id = uuid.uuid4()

        new = to_issue_selection(learner_id, selection(), NOW, timedelta(minutes=30))

        assert new.learner_id == learner_id
        assert new.exercise_id == "ex:1"
        assert new.item_ids == ("lex:a", "lex:b")
        assert new.new_item == "lex:b"
        assert new.issued_at == NOW
        assert new.expires_at == NOW + timedelta(minutes=30)

    def test_an_exercise_that_introduces_nothing_has_no_new_item(self) -> None:
        new = to_issue_selection(
            uuid.uuid4(), selection(introduces=None), NOW, timedelta(hours=1)
        )

        assert new.new_item is None
        assert new.item_ids == ("lex:a",)


class TestToExerciseResponse:
    def test_shows_the_exercise_under_the_issued_selections_id(self) -> None:
        issued = IssuedSelectionRecord(
            id=uuid.uuid4(),
            learner_id=uuid.uuid4(),
            exercise_id="ex:1",
            item_ids=("lex:a", "lex:b"),
            new_item="lex:b",
            issued_at=NOW,
            expires_at=NOW + timedelta(hours=1),
            consumed_at=None,
        )

        response = to_exercise_response(selection(), issued)

        assert response.selection_id == issued.id
        assert response.exercise_id == "ex:1"
        assert (response.english, response.welsh) == ("To speak", "Siarad")
        assert response.audio.welsh.standard == "/exercises/ex%3A1/audio/welsh/standard"
        assert response.item_ids == ("lex:a", "lex:b")
        assert response.introduces == "lex:b"
        assert response.purpose is ExercisePurpose.INTRODUCTION


class TestToNothingEligibleResponse:
    def test_says_there_is_nothing_to_give(self) -> None:
        assert to_nothing_eligible_response().kind == "nothing_eligible"


class TestEnumsStayInStep:
    """If the engine gains a value, these fail until the API's enum and mapping do too."""

    @pytest.mark.parametrize("purpose", Purpose)
    def test_every_engine_purpose_has_an_api_purpose(self, purpose: Purpose) -> None:
        assert to_exercise_purpose(purpose).value == purpose.value

    def test_the_api_has_no_purpose_the_engine_lacks(self) -> None:
        assert {p.value for p in ExercisePurpose} == {p.value for p in Purpose}

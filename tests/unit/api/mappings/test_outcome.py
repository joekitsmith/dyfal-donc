import uuid
from datetime import UTC, datetime, timedelta

import pytest

from api.mappings import (
    to_append_event,
    to_consume_selection,
    to_outcome,
    to_outcome_response,
    to_review_event,
    to_review_events,
)
from api.schemas import OutcomeRequest, ReportedOutcome
from engine.learner import Outcome
from persistence.database import EventRecord, IssuedSelectionRecord
from persistence.database.models import OUTCOMES

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)


def issued() -> IssuedSelectionRecord:
    return IssuedSelectionRecord(
        id=uuid.uuid4(),
        learner_id=uuid.uuid4(),
        exercise_id="ex:1",
        item_ids=("lex:a", "lex:b"),
        new_item="lex:b",
        issued_at=NOW,
        expires_at=NOW + timedelta(hours=1),
        consumed_at=None,
    )


def event_record(*, outcome: str = "got_it", sequence: int = 1) -> EventRecord:
    return EventRecord(
        sequence=sequence,
        selection_id=uuid.uuid4(),
        exercise_id="ex:1",
        item_ids=("lex:a", "lex:b"),
        new_item="lex:b",
        outcome=outcome,
        reviewed_at=NOW,
    )


class TestToAppendEvent:
    def test_carries_the_selection_and_the_outcome(self) -> None:
        selection = issued()

        new = to_append_event(selection, Outcome.MISSED_IT, NOW)

        assert new.learner_id == selection.learner_id
        assert new.selection_id == selection.id
        assert new.exercise_id == "ex:1"
        assert new.item_ids == ("lex:a", "lex:b")
        assert new.new_item == "lex:b"
        assert new.outcome == "missed_it"
        assert new.reviewed_at == NOW


class TestToConsumeSelection:
    def test_carries_the_learner_the_selection_and_the_time(self) -> None:
        learner_id, selection_id = uuid.uuid4(), uuid.uuid4()
        request = OutcomeRequest(
            selection_id=selection_id, outcome=ReportedOutcome.GOT_IT
        )

        command = to_consume_selection(learner_id, request, NOW)

        assert command.learner_id == learner_id
        assert command.selection_id == selection_id
        assert command.at == NOW


class TestToReviewEvent:
    def test_maps_every_field(self) -> None:
        event = to_review_event(event_record(outcome="missed_it"))

        assert event.exercise_id == "ex:1"
        assert event.item_ids == ("lex:a", "lex:b")
        assert event.new_item == "lex:b"
        assert event.outcome is Outcome.MISSED_IT
        assert event.reviewed_at == NOW

    def test_keeps_the_order_of_the_records(self) -> None:
        records = (event_record(sequence=1), event_record(sequence=2))

        assert len(to_review_events(records)) == 2


class TestOutcomes:
    def test_a_reported_outcome_becomes_the_engines(self) -> None:
        assert to_outcome(ReportedOutcome.GOT_IT) is Outcome.GOT_IT

    @pytest.mark.parametrize("outcome", Outcome)
    def test_every_engine_outcome_can_be_reported(self, outcome: Outcome) -> None:
        assert to_outcome(ReportedOutcome(outcome.value)) is outcome

    def test_the_api_reports_no_outcome_the_engine_lacks(self) -> None:
        assert {o.value for o in ReportedOutcome} == {o.value for o in Outcome}

    def test_the_database_stores_exactly_the_engines_outcomes(self) -> None:
        assert set(OUTCOMES) == {outcome.value for outcome in Outcome}


class TestToOutcomeResponse:
    def test_says_whether_it_was_newly_recorded(self) -> None:
        response = to_outcome_response(4, recorded=False)

        assert (response.sequence, response.recorded) == (4, False)

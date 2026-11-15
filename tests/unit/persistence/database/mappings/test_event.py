from datetime import timedelta

from engine.learner import Outcome
from persistence.database import models
from persistence.database.mappings import to_review_event
from tests.unit.persistence.database.mappings.conftest import MOMENT, TOKYO


class TestToReviewEvent:
    def test_maps_every_field(self) -> None:
        row = models.ReviewEvent(
            exercise_id="ex:1",
            item_ids=["lex:a", "lex:b"],
            new_item="lex:b",
            outcome="missed_it",
            reviewed_at=MOMENT,
        )

        event = to_review_event(row)

        assert event.exercise_id == "ex:1"
        assert event.item_ids == ("lex:a", "lex:b")
        assert event.new_item == "lex:b"
        assert event.outcome is Outcome.MISSED_IT
        assert event.reviewed_at == MOMENT

    def test_converts_the_time_to_utc(self) -> None:
        row = models.ReviewEvent(
            exercise_id="ex:1",
            item_ids=["lex:a"],
            new_item=None,
            outcome="got_it",
            reviewed_at=MOMENT.astimezone(TOKYO),
        )

        event = to_review_event(row)

        assert event.reviewed_at == MOMENT
        assert event.reviewed_at.utcoffset() == timedelta(0)

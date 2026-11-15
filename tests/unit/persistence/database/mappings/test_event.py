import uuid
from datetime import timedelta

from persistence.database import models
from persistence.database.mappings import to_event_record
from tests.unit.persistence.database.mappings.conftest import MOMENT, TOKYO


class TestToEventRecord:
    def test_maps_every_field(self) -> None:
        row = models.ReviewEvent(
            sequence=3,
            selection_id=uuid.uuid4(),
            exercise_id="ex:1",
            item_ids=["lex:a", "lex:b"],
            new_item="lex:b",
            outcome="missed_it",
            reviewed_at=MOMENT,
        )

        record = to_event_record(row)

        assert record.sequence == 3
        assert record.selection_id == row.selection_id
        assert record.exercise_id == "ex:1"
        assert record.item_ids == ("lex:a", "lex:b")
        assert record.new_item == "lex:b"
        assert record.outcome == "missed_it"
        assert record.reviewed_at == MOMENT

    def test_converts_the_time_to_utc(self) -> None:
        row = models.ReviewEvent(
            sequence=1,
            selection_id=uuid.uuid4(),
            exercise_id="ex:1",
            item_ids=["lex:a"],
            new_item=None,
            outcome="got_it",
            reviewed_at=MOMENT.astimezone(TOKYO),
        )

        record = to_event_record(row)

        assert record.reviewed_at == MOMENT
        assert record.reviewed_at.utcoffset() == timedelta(0)

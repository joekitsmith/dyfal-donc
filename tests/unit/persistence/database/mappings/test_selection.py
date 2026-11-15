import uuid
from datetime import datetime, timedelta

from persistence.database import models
from persistence.database.mappings import to_issued_selection_record
from tests.unit.persistence.database.mappings.conftest import MOMENT, TOKYO


def selection_row(*, consumed_at: datetime | None = None) -> models.IssuedSelection:
    return models.IssuedSelection(
        id=uuid.uuid4(),
        learner_id=uuid.uuid4(),
        exercise_id="ex:1",
        item_ids=["lex:a", "lex:b"],
        new_item="lex:b",
        issued_at=MOMENT,
        expires_at=MOMENT + timedelta(hours=1),
        consumed_at=consumed_at,
    )


class TestToIssuedSelectionRecord:
    def test_maps_every_field(self) -> None:
        row = selection_row()

        record = to_issued_selection_record(row)

        assert record.id == row.id
        assert record.learner_id == row.learner_id
        assert record.item_ids == ("lex:a", "lex:b")
        assert record.new_item == "lex:b"
        assert record.expires_at == MOMENT + timedelta(hours=1)
        assert record.consumed_at is None

    def test_converts_times_to_utc(self) -> None:
        row = selection_row(consumed_at=MOMENT.astimezone(TOKYO))

        record = to_issued_selection_record(row)

        assert record.consumed_at == MOMENT
        assert record.consumed_at is not None
        assert record.consumed_at.utcoffset() == timedelta(0)

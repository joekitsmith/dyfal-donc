from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import EventRecord


def to_event_record(row: models.ReviewEvent) -> EventRecord:
    return EventRecord(
        sequence=row.sequence,
        selection_id=row.selection_id,
        exercise_id=row.exercise_id,
        item_ids=tuple(row.item_ids),
        new_item=row.new_item,
        outcome=row.outcome,
        reviewed_at=to_utc(row.reviewed_at),
    )

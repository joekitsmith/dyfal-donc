from persistence.database import models
from persistence.database.mappings.utc import to_utc
from persistence.database.records import IssuedSelectionRecord


def to_issued_selection_record(row: models.IssuedSelection) -> IssuedSelectionRecord:
    return IssuedSelectionRecord(
        id=row.id,
        learner_id=row.learner_id,
        exercise_id=row.exercise_id,
        item_ids=tuple(row.item_ids),
        new_item=row.new_item,
        issued_at=to_utc(row.issued_at),
        expires_at=to_utc(row.expires_at),
        consumed_at=None if row.consumed_at is None else to_utc(row.consumed_at),
    )

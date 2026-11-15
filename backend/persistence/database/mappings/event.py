from engine.learner import Outcome, ReviewEvent
from persistence.database import models
from persistence.database.mappings.utc import to_utc


def to_review_event(row: models.ReviewEvent) -> ReviewEvent:
    return ReviewEvent(
        exercise_id=row.exercise_id,
        item_ids=tuple(row.item_ids),
        new_item=row.new_item,
        outcome=Outcome(row.outcome),
        reviewed_at=to_utc(row.reviewed_at),
    )

from datetime import timedelta

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import Outcome, ReviewEvent
from tests.unit.engine.learner.helpers import START
from tests.unit.engine.sample_curriculum import (
    COFFI,
    DYSGU,
    MYND,
    SIARAD,
    curriculum_of,
)

SIARAD_ID = SIARAD.id
DYSGU_ID = DYSGU.id
MYND_ID = MYND.id
COFFI_ID = COFFI.id


def course() -> Curriculum:
    """Four words, taught in this order: siarad, dysgu, mynd, coffi."""
    return curriculum_of((SIARAD, DYSGU, MYND, COFFI))


def exercise(*items: str, new_item: str | None = None) -> Exercise:
    return Exercise(english="", welsh="", items=items, new_item=new_item)


def event(
    exercise_id: str,
    *item_ids: str,
    outcome: Outcome = Outcome.GOT_IT,
    minutes: int = 0,
) -> ReviewEvent:
    return ReviewEvent(
        exercise_id=exercise_id,
        item_ids=item_ids,
        outcome=outcome,
        reviewed_at=START + timedelta(minutes=minutes),
    )

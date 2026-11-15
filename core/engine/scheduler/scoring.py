from collections.abc import Set as AbstractSet

from engine.learner import ReviewEvent
from engine.scheduler.eligibility import Candidate
from engine.scheduler.models import SchedulerSettings


def score(
    candidate: Candidate,
    due_items: AbstractSet[str],
    previous: ReviewEvent | None,
    settings: SchedulerSettings,
) -> int:
    """How good a choice the exercise is: due items, build-up, and no repeats."""
    items = set(candidate.exercise.declared_items)
    total = settings.due_item_weight * len(items & due_items)
    if previous is None:
        return total

    total += settings.overlap_weight * len(items & set(previous.item_ids))
    if previous.exercise_id == candidate.exercise_id:
        total -= settings.repeat_penalty

    return total

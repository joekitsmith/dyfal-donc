from collections.abc import Sequence
from datetime import datetime

from engine.learner.errors import LearnerError
from engine.learner.models import LearnerState, Learning, Review, ReviewEvent
from engine.learner.outcome import Outcome
from engine.learner.settings import DEFAULT_SETTINGS, LearnerSettings
from engine.learner.utc import require_utc


def introduced_items(state: LearnerState) -> frozenset[str]:
    """Every item the learner has been introduced to."""
    return frozenset(state.memories)


def learning_items_due(state: LearnerState) -> tuple[str, ...]:
    """The ``Learning`` items whose countdown is over, by id."""
    return tuple(
        sorted(
            item_id
            for item_id, memory in state.memories.items()
            if isinstance(memory, Learning) and memory.exercises_until_due == 0
        )
    )


def review_items_due(
    state: LearnerState,
    now: datetime,
    settings: LearnerSettings = DEFAULT_SETTINGS,
) -> tuple[str, ...]:
    """The ``Review`` items due at ``now``, longest overdue first."""
    require_utc(now, "now")
    due = sorted(
        (settings.memory_model.due_at(memory.memory), item_id)
        for item_id, memory in state.memories.items()
        if isinstance(memory, Review)
    )
    return tuple(item_id for due_at, item_id in due if due_at <= now)


def recent_error_rate(events: Sequence[ReviewEvent], window: int) -> float:
    """The share of the last ``window`` events that were missed, 0.0 if there are none.

    Events are in chronological order. Missed introductions count as misses.
    """
    if window < 1:
        raise LearnerError(f"Window must be at least 1, not {window}")

    recent = events[-window:]
    if not recent:
        return 0.0

    return sum(event.outcome is Outcome.MISSED_IT for event in recent) / len(recent)

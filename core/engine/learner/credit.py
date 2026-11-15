from dataclasses import dataclass
from datetime import datetime

from engine.learner.memory import MemoryModel, ReviewMemory
from engine.learner.models import LearnerState, Learning, Review, ReviewEvent
from engine.learner.outcome import Outcome


@dataclass(frozen=True, slots=True, kw_only=True)
class Credit:
    """The items that take the event's outcome. Items not listed are left alone."""

    learning: tuple[str, ...] = ()
    review: tuple[str, ...] = ()


def assign_credit(
    state: LearnerState,
    event: ReviewEvent,
    memory_model: MemoryModel,
    review_credit_fraction: float = 1.0,
) -> Credit:
    """Decide which items an exercise's outcome counts for (the weakest link).

    A success counts only for items that are due: a ``Learning`` item whose
    countdown is over, or a ``Review`` item once ``review_credit_fraction`` of
    its interval has passed (all of it, by default, which is its due date).
    Practising an item early would otherwise inflate its stability.

    A miss counts for the newest material. If the exercise introduces an item
    or practises a ``Learning`` item, every ``Learning`` item takes the miss and
    ``Review`` items are spared. Otherwise the ``Review`` item least likely to
    be recalled takes it, the lowest id breaking a tie.
    """
    if event.outcome is Outcome.GOT_IT:
        return _credit_for_success(state, event, memory_model, review_credit_fraction)

    return _credit_for_miss(state, event, memory_model)


def _credit_for_success(
    state: LearnerState,
    event: ReviewEvent,
    memory_model: MemoryModel,
    review_credit_fraction: float,
) -> Credit:
    return Credit(
        learning=tuple(
            item_id
            for item_id in event.item_ids
            if isinstance(memory := state.memories.get(item_id), Learning)
            and memory.exercises_until_due == 0
        ),
        review=tuple(
            item_id
            for item_id in event.item_ids
            if isinstance(memory := state.memories.get(item_id), Review)
            and _credit_from(memory.memory, memory_model, review_credit_fraction)
            <= event.reviewed_at
        ),
    )


def _credit_for_miss(
    state: LearnerState, event: ReviewEvent, memory_model: MemoryModel
) -> Credit:
    learning = tuple(
        item_id
        for item_id in event.item_ids
        if isinstance(state.memories.get(item_id), Learning)
    )
    if learning or event.new_item is not None:
        return Credit(learning=learning)

    weakest = min(
        (
            (memory_model.retrievability(memory.memory, event.reviewed_at), item_id)
            for item_id in event.item_ids
            if isinstance(memory := state.memories.get(item_id), Review)
        ),
        default=None,
    )
    if weakest is None:
        return Credit()

    return Credit(review=(weakest[1],))


def _credit_from(
    memory: ReviewMemory, memory_model: MemoryModel, review_credit_fraction: float
) -> datetime:
    interval = memory_model.due_at(memory) - memory.last_reviewed_at
    return memory.last_reviewed_at + interval * review_credit_fraction

from collections.abc import Sequence

from engine.learner.credit import assign_credit
from engine.learner.errors import LearnerError
from engine.learner.memory import ReviewMemory
from engine.learner.models import (
    ItemMemory,
    LearnerState,
    Learning,
    Review,
    ReviewEvent,
)
from engine.learner.outcome import Outcome
from engine.learner.settings import DEFAULT_SETTINGS, LearnerSettings


def replay(
    events: Sequence[ReviewEvent], settings: LearnerSettings = DEFAULT_SETTINGS
) -> LearnerState:
    """The learner's state after the events, which must be in chronological order."""
    state = LearnerState()
    for event in events:
        state = apply_event(state, event, settings)

    return state


def apply_event(
    state: LearnerState,
    event: ReviewEvent,
    settings: LearnerSettings = DEFAULT_SETTINGS,
) -> LearnerState:
    """The state after one more event.

    Every ``Learning`` item counts down by one. The items the outcome is
    credited to then move on, and a new item enters at the first learning step.
    """
    _check_applicable(state, event)
    credit = assign_credit(state, event, settings.memory_model)
    memories: dict[str, ItemMemory] = {
        item_id: _counted_down(memory) if isinstance(memory, Learning) else memory
        for item_id, memory in state.memories.items()
    }
    for item_id in credit.learning:
        memories[item_id] = _after_learning_exercise(
            _learning_memory(state, item_id), event, settings
        )

    for item_id in credit.review:
        memories[item_id] = Review(
            memory=settings.memory_model.review(
                _review_memory(state, item_id), event.outcome, event.reviewed_at
            )
        )

    if event.new_item is not None:
        memories[event.new_item] = _first_step(settings)

    return LearnerState(memories=memories, last_reviewed_at=event.reviewed_at)


def _check_applicable(state: LearnerState, event: ReviewEvent) -> None:
    if (
        state.last_reviewed_at is not None
        and event.reviewed_at < state.last_reviewed_at
    ):
        raise LearnerError(
            f"{event.exercise_id}: Events must be in chronological order"
        )

    if event.new_item is not None and event.new_item in state.memories:
        raise LearnerError(
            f"{event.exercise_id}: {event.new_item} has already been introduced"
        )

    for item_id in event.item_ids:
        if item_id != event.new_item and item_id not in state.memories:
            raise LearnerError(
                f"{event.exercise_id}: {item_id} has not been introduced"
            )


def _counted_down(memory: Learning) -> Learning:
    return Learning(
        step_index=memory.step_index,
        exercises_until_due=max(0, memory.exercises_until_due - 1),
    )


def _first_step(settings: LearnerSettings) -> Learning:
    return Learning(step_index=0, exercises_until_due=settings.learning_steps[0])


def _after_learning_exercise(
    memory: Learning, event: ReviewEvent, settings: LearnerSettings
) -> ItemMemory:
    if event.outcome is Outcome.MISSED_IT:
        return _first_step(settings)

    next_index = memory.step_index + 1
    if next_index < len(settings.learning_steps):
        return Learning(
            step_index=next_index,
            exercises_until_due=settings.learning_steps[next_index],
        )

    return Review(memory=settings.memory_model.initial(event.reviewed_at))


def _learning_memory(state: LearnerState, item_id: str) -> Learning:
    memory = state.memories.get(item_id)
    if not isinstance(memory, Learning):
        raise LearnerError(f"{item_id} is not being learned")

    return memory


def _review_memory(state: LearnerState, item_id: str) -> ReviewMemory:
    memory = state.memories.get(item_id)
    if not isinstance(memory, Review):
        raise LearnerError(f"{item_id} is not in review")

    return memory.memory

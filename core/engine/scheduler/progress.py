from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from engine.curriculum import Curriculum, Item, Lexeme
from engine.exercises import Exercise
from engine.learner import LearnerState, Outcome, ReviewEvent, introduced_items
from engine.scheduler.eligibility import frontier_topic

MAX_SAYABLE_EXERCISES = 5


@dataclass(frozen=True, slots=True, kw_only=True)
class TopicProgress:
    """What a learner has met in one topic.

    ``words`` and ``phrases`` are the items they have met, in teaching order.
    ``exercises_answered`` counts every answer to an exercise of the topic, repeats
    included. ``sayable_exercise_ids`` are a few exercises of the topic they got
    right at least once. A topic they have not started has none of these.
    """

    name: str
    started: bool
    is_current: bool
    words: tuple[str, ...]
    phrases: tuple[str, ...]
    exercises_answered: int
    sayable_exercise_ids: tuple[str, ...]


def course_progress(
    curriculum: Curriculum,
    exercises: Mapping[str, Exercise],
    exercise_topics: Mapping[str, str],
    state: LearnerState,
    events: Sequence[ReviewEvent],
) -> tuple[TopicProgress, ...]:
    """Every topic in teaching order, with what the learner has met in it.

    An exercise belongs to the one topic it is registered under in
    ``exercise_topics``, whichever topics its items come from.
    """
    items = {item.id: item for item in curriculum.items}
    topics = tuple(dict.fromkeys(items[item_id].topic for item_id in curriculum.order))
    current = frontier_topic(curriculum, introduced_items(state))
    answered = Counter(
        exercise_topics[event.exercise_id]
        for event in events
        if event.exercise_id in exercise_topics
    )
    successes = _last_successes(events)

    return tuple(
        _topic_progress(
            topic,
            items=items,
            order=curriculum.order,
            state=state,
            is_current=topic == current,
            exercises_answered=answered[topic],
            sayable_exercise_ids=_sayable(exercises, exercise_topics, successes, topic),
        )
        for topic in topics
    )


def example_exercise_ids(
    exercises: Mapping[str, Exercise],
    events: Sequence[ReviewEvent],
    item_id: str,
    limit: int,
) -> tuple[str, ...]:
    """Up to ``limit`` exercises with the item that the learner got right, most recent first."""
    successes = _last_successes(events)
    found = sorted(
        (
            exercise_id
            for exercise_id in successes
            if (exercise := exercises.get(exercise_id)) is not None
            and item_id in exercise.declared_items
        ),
        key=lambda exercise_id: -successes[exercise_id],
    )

    return tuple(found[:limit])


def first_met_at(events: Sequence[ReviewEvent], item_id: str) -> datetime | None:
    """When the learner first practised the item, which is when they met it."""
    return next(
        (event.reviewed_at for event in events if item_id in event.item_ids), None
    )


def _topic_progress(
    topic: str,
    *,
    items: Mapping[str, Item],
    order: Sequence[str],
    state: LearnerState,
    is_current: bool,
    exercises_answered: int,
    sayable_exercise_ids: tuple[str, ...],
) -> TopicProgress:
    met = tuple(
        item_id
        for item_id in order
        if item_id in state.memories and items[item_id].topic == topic
    )

    return TopicProgress(
        name=topic,
        started=bool(met),
        is_current=is_current,
        words=tuple(item_id for item_id in met if isinstance(items[item_id], Lexeme)),
        phrases=tuple(
            item_id for item_id in met if not isinstance(items[item_id], Lexeme)
        ),
        exercises_answered=exercises_answered,
        sayable_exercise_ids=sayable_exercise_ids,
    )


def _sayable(
    exercises: Mapping[str, Exercise],
    exercise_topics: Mapping[str, str],
    successes: Mapping[str, int],
    topic: str,
) -> tuple[str, ...]:
    """The exercises of the topic with the most items, then the most recently got right."""
    candidates = sorted(
        (
            exercise_id
            for exercise_id in successes
            if exercise_id in exercises and exercise_topics.get(exercise_id) == topic
        ),
        key=lambda exercise_id: (
            -len(exercises[exercise_id].declared_items),
            -successes[exercise_id],
        ),
    )

    return tuple(candidates[:MAX_SAYABLE_EXERCISES])


def _last_successes(events: Sequence[ReviewEvent]) -> Mapping[str, int]:
    """Where in the log each exercise was last got right."""
    return {
        event.exercise_id: position
        for position, event in enumerate(events)
        if event.outcome is Outcome.GOT_IT
    }

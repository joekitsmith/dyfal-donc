import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from engine.learner import Outcome
from simulation.profile import LearnerProfile

SECONDS_PER_DAY = 86400


@dataclass(frozen=True, slots=True, kw_only=True)
class TrueMemory:
    """What the learner really remembers of one item."""

    stability_days: float
    last_seen: datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class Attempt:
    """The result of one exercise: the learner's new memories and what they would say."""

    memories: Mapping[str, TrueMemory]
    truly_correct: bool
    reported: Outcome


def item_ease(seed: int, item_id: str, spread: float) -> float:
    """How much a success helps for this item: log-normal with mean 1.

    Derived from the seed and the item, so it is the same whatever order items
    are introduced in.
    """
    return random.Random(f"{seed}:{item_id}").lognormvariate(-(spread**2) / 2, spread)


def recall_probability(
    memory: TrueMemory, now: datetime, profile: LearnerProfile
) -> float:
    elapsed_days = (now - memory.last_seen).total_seconds() / SECONDS_PER_DAY
    return profile.memory.recall_probability(memory.stability_days, elapsed_days)


def attempt_exercise(
    memories: Mapping[str, TrueMemory],
    item_ids: Sequence[str],
    introduces: str | None,
    now: datetime,
    profile: LearnerProfile,
    seed: int,
    rng: random.Random,
) -> Attempt:
    """The learner does an exercise.

    They are truly right only if they recall every item, each tried independently.
    Every item's memory then updates on its own result, whatever the engine's
    credit assignment does. An item being introduced is seen, not recalled.
    """
    updated = dict(memories)
    truly_correct = True
    for item_id in item_ids:
        ease = item_ease(seed, item_id, profile.difficulty_spread)
        if item_id == introduces:
            updated[item_id] = TrueMemory(
                stability_days=profile.memory.initial_stability_days
                * profile.learning_rate
                * ease,
                last_seen=now,
            )
            continue

        memory = memories[item_id]
        probability = recall_probability(memory, now, profile)
        gain_scale = profile.learning_rate * ease
        if rng.random() < probability:
            stability = profile.memory.after_success(
                memory.stability_days, probability, gain_scale
            )
        else:
            truly_correct = False
            stability = profile.memory.after_failure(memory.stability_days)

        updated[item_id] = TrueMemory(stability_days=stability, last_seen=now)

    return Attempt(
        memories=updated,
        truly_correct=truly_correct,
        reported=_reported(truly_correct, profile, rng),
    )


def _reported(
    truly_correct: bool, profile: LearnerProfile, rng: random.Random
) -> Outcome:
    if truly_correct:
        return Outcome.GOT_IT

    if rng.random() < profile.under_report_rate:
        return Outcome.GOT_IT

    return Outcome.MISSED_IT

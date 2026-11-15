import random
from collections.abc import Mapping
from datetime import datetime, timedelta

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import (
    DEFAULT_SETTINGS,
    LearnerSettings,
    LearnerState,
    ReviewEvent,
    apply_event,
)
from engine.scheduler import (
    DEFAULT_SCHEDULER_SETTINGS,
    NothingEligible,
    SchedulerSettings,
    next_exercise,
)
from simulation.outcome import TrueMemory, attempt_exercise, recall_probability
from simulation.profile import LearnerProfile
from simulation.session import DEFAULT_SESSION_SETTINGS, SessionSettings
from simulation.trace import (
    DaySnapshot,
    ItemTruth,
    SimulatedStep,
    SimulationTrace,
    Stall,
)


def simulate(
    pool: Mapping[str, Exercise],
    curriculum: Curriculum,
    profile: LearnerProfile,
    *,
    seed: int,
    session: SessionSettings = DEFAULT_SESSION_SETTINGS,
    scheduler_settings: SchedulerSettings = DEFAULT_SCHEDULER_SETTINGS,
    learner_settings: LearnerSettings = DEFAULT_SETTINGS,
) -> SimulationTrace:
    """Run a simulated learner through the course, one session a day.

    Each exercise is chosen by the real scheduler and recorded as the real
    learner model would see it, while the simulated learner forgets by their
    own ground-truth memory. The same seed and settings give the same trace.
    """
    rng = random.Random(seed)
    state = LearnerState()
    events: list[ReviewEvent] = []
    steps: list[SimulatedStep] = []
    stalls: list[Stall] = []
    snapshots: list[DaySnapshot] = []
    memories: Mapping[str, TrueMemory] = {}

    for day in range(session.days):
        skipped = rng.random() < session.skip_day_probability
        now = session.day_start(day)
        session_end = now + timedelta(minutes=session.session_minutes)
        while not skipped and now < session_end:
            selection = next_exercise(
                pool,
                curriculum,
                state,
                events,
                now,
                scheduler_settings,
                learner_settings,
            )
            if isinstance(selection, NothingEligible):
                stalls.append(Stall(day=day, at=now, reason=selection.reason))
                break

            attempt = attempt_exercise(
                memories,
                selection.exercise.declared_items,
                selection.introduces,
                now,
                profile,
                seed,
                rng,
            )
            event = selection.as_event(attempt.reported, now)
            state = apply_event(state, event, learner_settings)
            events.append(event)
            memories = attempt.memories
            steps.append(
                SimulatedStep(
                    event=event,
                    purpose=selection.purpose,
                    truly_correct=attempt.truly_correct,
                )
            )
            now += _duration(session, rng)

        snapshots.append(
            _snapshot(day, memories, session.day_start(day + 1), profile, skipped)
        )

    return SimulationTrace(
        seed=seed,
        steps=tuple(steps),
        snapshots=tuple(snapshots),
        stalls=tuple(stalls),
    )


def _duration(session: SessionSettings, rng: random.Random) -> timedelta:
    jitter = 1 + rng.uniform(-session.exercise_jitter, session.exercise_jitter)
    return timedelta(seconds=session.exercise_seconds * jitter)


def _snapshot(
    day: int,
    memories: Mapping[str, TrueMemory],
    measured_at: datetime,
    profile: LearnerProfile,
    skipped: bool,
) -> DaySnapshot:
    return DaySnapshot(
        day=day,
        measured_at=measured_at,
        skipped=skipped,
        items=tuple(
            ItemTruth(
                item_id=item_id,
                stability_days=memory.stability_days,
                recall_probability=recall_probability(memory, measured_at, profile),
            )
            for item_id, memory in sorted(memories.items())
        ),
    )

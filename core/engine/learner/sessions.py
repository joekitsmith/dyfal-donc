from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from engine.learner.credit import assign_credit
from engine.learner.errors import LearnerError
from engine.learner.models import ReviewEvent
from engine.learner.outcome import Outcome
from engine.learner.replay import apply_event, replay
from engine.learner.settings import DEFAULT_SETTINGS, LearnerSettings
from engine.learner.utc import require_utc

SESSION_GAP = timedelta(minutes=10)


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionRun:
    """A stretch of a learner's events with no long gap: where it starts, and where it ends (not included)."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if not 0 <= self.start < self.end:
            raise LearnerError(
                f"A session run must hold at least one event, not {self.start} to {self.end}"
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionSummary:
    """What a learner did in one session.

    ``items_introduced`` are the items they met for the first time. ``items_reviewed``
    are items they already knew that the exercises counted for, and ``items_lapsed``
    are those among them that were in long-term review and were missed.
    ``missed_exercises`` are the exercises they marked as missed, each once.
    """

    started_at: datetime
    ended_at: datetime
    exercises_completed: int
    items_introduced: tuple[str, ...]
    items_reviewed: tuple[str, ...]
    items_lapsed: tuple[str, ...]
    missed_exercises: tuple[str, ...]

    @property
    def duration(self) -> timedelta:
        return self.ended_at - self.started_at


def split_sessions(
    events: Sequence[ReviewEvent], gap: timedelta = SESSION_GAP
) -> tuple[SessionRun, ...]:
    """Cut the events, which are in chronological order, into sessions.

    A session goes on as long as each answer comes within ``gap`` of the one
    before it. A pause of exactly ``gap`` does not end it.
    """
    if gap <= timedelta(0):
        raise LearnerError(f"The gap between sessions must be positive, not {gap}")

    runs: list[SessionRun] = []
    start = 0
    for position in range(1, len(events)):
        if events[position].reviewed_at - events[position - 1].reviewed_at > gap:
            runs.append(SessionRun(start=start, end=position))
            start = position

    if events:
        runs.append(SessionRun(start=start, end=len(events)))

    return tuple(runs)


def is_ongoing(
    last_answered_at: datetime, now: datetime, gap: timedelta = SESSION_GAP
) -> bool:
    """Whether a session whose last answer was at ``last_answered_at`` is still going at ``now``."""
    require_utc(last_answered_at, "last_answered_at")
    require_utc(now, "now")
    return now - last_answered_at <= gap


def summarise_session(
    before: Sequence[ReviewEvent],
    during: Sequence[ReviewEvent],
    settings: LearnerSettings = DEFAULT_SETTINGS,
) -> SessionSummary:
    """Sum up the session's events, given everything the learner did before it.

    Review items never return to the learning phase, so a lapse cannot be seen
    by comparing phases. It is a miss that the engine counted against an item
    that was in long-term review.
    """
    if not during:
        raise LearnerError("A session needs at least one event")

    state = replay(before, settings)
    known_before = frozenset(state.memories)
    reviewed: dict[str, None] = {}
    lapsed: dict[str, None] = {}
    for event in during:
        credit = assign_credit(
            state, event, settings.memory_model, settings.review_credit_fraction
        )
        for item_id in (*credit.learning, *credit.review):
            if item_id in known_before:
                reviewed[item_id] = None

        if event.outcome is Outcome.MISSED_IT:
            for item_id in credit.review:
                if item_id in known_before:
                    lapsed[item_id] = None

        state = apply_event(state, event, settings)

    return SessionSummary(
        started_at=during[0].reviewed_at,
        ended_at=during[-1].reviewed_at,
        exercises_completed=len(during),
        items_introduced=tuple(
            event.new_item for event in during if event.new_item is not None
        ),
        items_reviewed=tuple(reviewed),
        items_lapsed=tuple(lapsed),
        missed_exercises=tuple(
            dict.fromkeys(
                event.exercise_id
                for event in during
                if event.outcome is Outcome.MISSED_IT
            )
        ),
    )

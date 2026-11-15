from datetime import datetime

from fsrs import Card, Rating, Scheduler, State

from engine.learner.errors import LearnerError
from engine.learner.memory import ReviewMemory
from engine.learner.outcome import Outcome
from engine.learner.utc import as_utc

_RATINGS = {Outcome.GOT_IT: Rating.Good, Outcome.MISSED_IT: Rating.Again}
_CARD_ID = 0
DEFAULT_MAXIMUM_INTERVAL_DAYS = 180


class FsrsMemoryModel:
    """Long-term memory by FSRS, using the ``fsrs`` package.

    The package's own learning steps and fuzzing are off: this engine owns the
    short-term steps and must be deterministic. This is the only module that
    imports ``fsrs``, so none of its types reach the public API.

    Intervals are capped (180 days by default) so that a well-known item still
    comes back now and then, and is never retired for good.
    """

    def __init__(
        self,
        *,
        desired_retention: float = 0.9,
        maximum_interval_days: int = DEFAULT_MAXIMUM_INTERVAL_DAYS,
    ) -> None:
        if not 0 < desired_retention < 1:
            raise LearnerError(
                f"Desired retention must be between 0 and 1, not {desired_retention}"
            )

        if maximum_interval_days < 1:
            raise LearnerError(
                f"Maximum interval must be at least one day, not {maximum_interval_days}"
            )

        self._scheduler = Scheduler(
            desired_retention=desired_retention,
            learning_steps=(),
            relearning_steps=(),
            maximum_interval=maximum_interval_days,
            enable_fuzzing=False,
        )

    def initial(self, now: datetime) -> ReviewMemory:
        now = as_utc(now, "now")
        card = Card(card_id=_CARD_ID, due=now)
        return self._reviewed(card, Rating.Good, now)

    def review(
        self, memory: ReviewMemory, outcome: Outcome, now: datetime
    ) -> ReviewMemory:
        now = as_utc(now, "now")
        self._require_not_before_last_review(memory, now)
        return self._reviewed(_card_of(memory), _RATINGS[outcome], now)

    def retrievability(self, memory: ReviewMemory, now: datetime) -> float:
        now = as_utc(now, "now")
        self._require_not_before_last_review(memory, now)
        return float(self._scheduler.get_card_retrievability(_card_of(memory), now))

    def due_at(self, memory: ReviewMemory) -> datetime:
        return memory.due_at

    def _reviewed(self, card: Card, rating: Rating, now: datetime) -> ReviewMemory:
        reviewed, _ = self._scheduler.review_card(card, rating, now)
        if reviewed.stability is None or reviewed.difficulty is None:
            raise LearnerError("FSRS returned a card without memory state")

        return ReviewMemory(
            stability=reviewed.stability,
            difficulty=reviewed.difficulty,
            last_reviewed_at=now,
            due_at=reviewed.due,
        )

    @staticmethod
    def _require_not_before_last_review(memory: ReviewMemory, now: datetime) -> None:
        if now < memory.last_reviewed_at:
            raise LearnerError("A review cannot be earlier than the previous one")


def _card_of(memory: ReviewMemory) -> Card:
    return Card(
        card_id=_CARD_ID,
        state=State.Review,
        step=None,
        stability=memory.stability,
        difficulty=memory.difficulty,
        due=memory.due_at,
        last_review=memory.last_reviewed_at,
    )

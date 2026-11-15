from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

from hypothesis import strategies as st

from engine.learner import (
    ItemMemory,
    LearnerSettings,
    LearnerState,
    Outcome,
    Review,
    ReviewEvent,
    apply_event,
)

START = datetime(2026, 1, 1, 12, tzinfo=UTC)
FILLER = "lex:filler"
ITEM_IDS = tuple(f"lex:item-{number}" for number in range(6))


class Session:
    """Applies events to a learner's state, one minute apart.

    ``FILLER`` is always in review and not due for two days, so practising it
    is a way to pass exercises without touching anything else.
    """

    def __init__(
        self,
        settings: LearnerSettings,
        memories: Mapping[str, ItemMemory] | None = None,
    ) -> None:
        self.settings = settings
        self.now = START
        self.events: list[ReviewEvent] = []
        self.state = LearnerState(
            memories={
                FILLER: Review(memory=settings.memory_model.initial(START)),
                **(memories or {}),
            },
            last_reviewed_at=START,
        )

    def give(
        self,
        *item_ids: str,
        outcome: Outcome = Outcome.GOT_IT,
        new_item: str | None = None,
    ) -> LearnerState:
        self.now += timedelta(minutes=1)
        event = ReviewEvent(
            exercise_id=f"ex:{len(self.events)}",
            item_ids=item_ids,
            new_item=new_item,
            outcome=outcome,
            reviewed_at=self.now,
        )
        self.events.append(event)
        self.state = apply_event(self.state, event, self.settings)
        return self.state

    def introduce(
        self, item_id: str, outcome: Outcome = Outcome.GOT_IT
    ) -> LearnerState:
        return self.give(item_id, new_item=item_id, outcome=outcome)

    def fillers(self, count: int) -> LearnerState:
        for _ in range(count):
            self.give(FILLER)

        return self.state

    def wait(self, **duration: float) -> None:
        self.now += timedelta(**duration)


@st.composite
def event_sequences(
    draw: st.DrawFn, *, max_events: int = 40
) -> tuple[ReviewEvent, ...]:
    """Valid chronological events: only introduced items, and one new item at a time."""
    introduced: list[str] = []
    moment = START
    events: list[ReviewEvent] = []
    for number in range(draw(st.integers(min_value=0, max_value=max_events))):
        moment += timedelta(
            minutes=draw(st.integers(min_value=0, max_value=3 * 24 * 60))
        )
        can_introduce = len(introduced) < len(ITEM_IDS)
        introduces = can_introduce and (not introduced or draw(st.booleans()))
        new_item = ITEM_IDS[len(introduced)] if introduces else None
        practised = (
            draw(
                st.lists(
                    st.sampled_from(introduced),
                    unique=True,
                    min_size=0 if introduces else 1,
                    max_size=3,
                )
            )
            if introduced
            else []
        )
        events.append(
            ReviewEvent(
                exercise_id=f"ex:{number}",
                item_ids=(*practised, *((new_item,) if new_item else ())),
                new_item=new_item,
                outcome=draw(st.sampled_from(Outcome)),
                reviewed_at=moment,
            )
        )
        if new_item:
            introduced.append(new_item)

    return tuple(events)

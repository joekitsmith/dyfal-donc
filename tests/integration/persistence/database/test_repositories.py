import threading
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from engine.exercises import Exercise
from engine.learner import Outcome, ReviewEvent, replay
from engine.scheduler import Selection
from engine.scheduler.models import Purpose
from persistence.database import (
    EventRepository,
    IssuedSelectionRecord,
    LearnerRepository,
    SelectionRepository,
)
from persistence.database.errors import (
    EventOutOfOrderError,
    LearnerNotFoundError,
    SelectionAlreadyAnsweredError,
    SelectionExpiredError,
    SelectionNotFoundError,
)

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)
LIFETIME = timedelta(hours=1)


def selection(item: str = "lex:a", exercise_id: str = "ex:1") -> Selection:
    return Selection(
        exercise_id=exercise_id,
        exercise=Exercise(english="", welsh="", items=(item,), new_item=item),
        purpose=Purpose.INTRODUCTION,
        introduces=item,
    )


def answer(
    session: Session,
    learner_id: uuid.UUID,
    chosen: Selection,
    at: datetime,
    outcome: Outcome = Outcome.GOT_IT,
) -> tuple[IssuedSelectionRecord, int]:
    """Issue a selection and record the learner's answer, as the API will."""
    issued = SelectionRepository(session).issue(learner_id, chosen, at, LIFETIME)
    SelectionRepository(session).consume(learner_id, issued.id, at)
    sequence = EventRepository(session).append(
        learner_id, issued.id, issued.as_event(outcome, at)
    )
    return issued, sequence


class TestLearnerRepository:
    def test_a_learner_can_be_added_and_found(self, session: Session) -> None:
        repository = LearnerRepository(session)

        added = repository.add("release-1")

        found = repository.get(added.id)
        assert found == added
        assert found is not None
        assert found.course_release == "release-1"
        assert found.created_at.utcoffset() == timedelta(0)

    def test_an_unknown_learner_is_not_found(self, session: Session) -> None:
        assert LearnerRepository(session).get(uuid.uuid4()) is None


class TestSelectionRepository:
    def test_an_issued_selection_keeps_what_the_event_needs(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add("release-1")

        issued = SelectionRepository(session).issue(
            learner.id, selection("lex:b"), NOW, LIFETIME
        )

        assert issued.exercise_id == "ex:1"
        assert issued.item_ids == ("lex:b",)
        assert issued.new_item == "lex:b"
        assert issued.expires_at == NOW + LIFETIME
        assert issued.consumed_at is None

    def test_consuming_marks_the_time_it_was_answered(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")
        issued = SelectionRepository(session).issue(
            learner.id, selection(), NOW, LIFETIME
        )

        consumed = SelectionRepository(session).consume(
            learner.id, issued.id, NOW + timedelta(minutes=5)
        )

        assert consumed.consumed_at == NOW + timedelta(minutes=5)

    def test_a_selection_cannot_be_answered_twice(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")
        repository = SelectionRepository(session)
        issued = repository.issue(learner.id, selection(), NOW, LIFETIME)
        repository.consume(learner.id, issued.id, NOW)

        with pytest.raises(SelectionAlreadyAnsweredError):
            repository.consume(learner.id, issued.id, NOW)

    def test_an_expired_selection_cannot_be_answered(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")
        repository = SelectionRepository(session)
        issued = repository.issue(learner.id, selection(), NOW, LIFETIME)

        with pytest.raises(SelectionExpiredError):
            repository.consume(learner.id, issued.id, NOW + LIFETIME)

    def test_a_selection_can_be_answered_just_before_it_expires(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add("release-1")
        repository = SelectionRepository(session)
        issued = repository.issue(learner.id, selection(), NOW, LIFETIME)

        repository.consume(learner.id, issued.id, NOW + LIFETIME - timedelta(seconds=1))

    def test_an_unknown_selection_is_not_found(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")

        with pytest.raises(SelectionNotFoundError):
            SelectionRepository(session).consume(learner.id, uuid.uuid4(), NOW)

    def test_a_learner_cannot_answer_another_learners_selection(
        self, session: Session
    ) -> None:
        learners = LearnerRepository(session)
        owner, other = learners.add("release-1"), learners.add("release-1")
        repository = SelectionRepository(session)
        issued = repository.issue(owner.id, selection(), NOW, LIFETIME)

        with pytest.raises(SelectionNotFoundError):
            repository.consume(other.id, issued.id, NOW)


class TestEventRepository:
    def test_sequence_numbers_count_up_from_one(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")

        sequences = [
            answer(
                session,
                learner.id,
                selection(f"lex:{n}", f"ex:{n}"),
                NOW + timedelta(minutes=n),
            )[1]
            for n in range(3)
        ]

        assert sequences == [1, 2, 3]

    def test_each_learner_has_their_own_sequence(self, session: Session) -> None:
        learners = LearnerRepository(session)

        sequences = [
            answer(session, learners.add("release-1").id, selection(), NOW)[1]
            for _ in range(2)
        ]

        assert sequences == [1, 1]

    def test_events_come_back_in_the_order_they_happened(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add("release-1")
        for n in range(3):
            answer(
                session,
                learner.id,
                selection(f"lex:{n}", f"ex:{n}"),
                NOW + timedelta(minutes=n),
            )

        events = EventRepository(session).events(learner.id)

        assert [event.exercise_id for event in events] == ["ex:0", "ex:1", "ex:2"]

    def test_an_event_earlier_than_the_last_is_rejected(self, session: Session) -> None:
        learner = LearnerRepository(session).add("release-1")
        answer(session, learner.id, selection("lex:a", "ex:1"), NOW)
        late = SelectionRepository(session).issue(
            learner.id, selection("lex:b", "ex:2"), NOW, LIFETIME
        )

        with pytest.raises(EventOutOfOrderError):
            EventRepository(session).append(
                learner.id, late.id, late.as_event(Outcome.GOT_IT, NOW - timedelta(1))
            )

    def test_an_unknown_learner_is_rejected(self, session: Session) -> None:
        event = ReviewEvent(
            exercise_id="ex:1",
            item_ids=("lex:a",),
            outcome=Outcome.GOT_IT,
            reviewed_at=NOW,
        )

        with pytest.raises(LearnerNotFoundError):
            EventRepository(session).append(uuid.uuid4(), uuid.uuid4(), event)

    def test_times_come_back_in_utc_whatever_the_session_time_zone(
        self, session: Session
    ) -> None:
        session.execute(text("SET TIME ZONE 'Asia/Tokyo'"))
        learner = LearnerRepository(session).add("release-1")
        answer(session, learner.id, selection(), NOW)

        (event,) = EventRepository(session).events(learner.id)

        assert event.reviewed_at == NOW
        assert event.reviewed_at.utcoffset() == timedelta(0)


class TestReplayRoundTrip:
    def test_replaying_the_stored_events_gives_the_learners_state(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add("release-1")
        answer(session, learner.id, selection("lex:a", "ex:1"), NOW)
        answer(
            session,
            learner.id,
            selection("lex:b", "ex:2"),
            NOW + timedelta(minutes=1),
            Outcome.MISSED_IT,
        )

        stored = replay(EventRepository(session).events(learner.id))

        assert set(stored.memories) == {"lex:a", "lex:b"}
        assert stored.last_reviewed_at == NOW + timedelta(minutes=1)


class TestConcurrentAppends:
    def test_simultaneous_appends_for_one_learner_get_distinct_sequences(
        self, session_factory: sessionmaker[Session]
    ) -> None:
        with session_factory() as setup:
            learner = LearnerRepository(setup).add("release-1")
            issued = tuple(
                SelectionRepository(setup).issue(
                    learner.id, selection(f"lex:{n}", f"ex:{n}"), NOW, LIFETIME
                )
                for n in range(8)
            )
            setup.commit()

        errors: list[BaseException] = []
        sequences: list[int] = []

        def append(stored: IssuedSelectionRecord) -> None:
            try:
                with session_factory() as worker:
                    sequence = EventRepository(worker).append(
                        learner.id, stored.id, stored.as_event(Outcome.GOT_IT, NOW)
                    )
                    worker.commit()
                    sequences.append(sequence)
            except BaseException as error:  # noqa: BLE001
                errors.append(error)

        threads = [threading.Thread(target=append, args=(s,)) for s in issued]
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        assert errors == []
        assert sorted(sequences) == list(range(1, 9))

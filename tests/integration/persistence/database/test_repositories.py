import threading
import uuid
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from persistence.database import (
    AddLearner,
    AppendEvent,
    ConsumeSelection,
    EventRepository,
    IssueSelection,
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


def new_selection(
    learner_id: uuid.UUID,
    item: str = "lex:a",
    exercise_id: str = "ex:1",
    issued_at: datetime = NOW,
) -> IssueSelection:
    return IssueSelection(
        learner_id=learner_id,
        exercise_id=exercise_id,
        item_ids=(item,),
        new_item=item,
        issued_at=issued_at,
        expires_at=issued_at + LIFETIME,
    )


def new_event(
    issued: IssuedSelectionRecord, at: datetime, outcome: str = "got_it"
) -> AppendEvent:
    return AppendEvent(
        learner_id=issued.learner_id,
        selection_id=issued.id,
        exercise_id=issued.exercise_id,
        item_ids=issued.item_ids,
        new_item=issued.new_item,
        outcome=outcome,
        reviewed_at=at,
    )


def consuming(
    learner_id: uuid.UUID, selection_id: uuid.UUID, at: datetime
) -> ConsumeSelection:
    return ConsumeSelection(learner_id=learner_id, selection_id=selection_id, at=at)


def answer(
    session: Session,
    learner_id: uuid.UUID,
    at: datetime,
    item: str = "lex:a",
    exercise_id: str = "ex:1",
    outcome: str = "got_it",
) -> tuple[IssuedSelectionRecord, int]:
    """Issue a selection and record the learner's answer, as the API will."""
    issued = SelectionRepository(session).issue(
        new_selection(learner_id, item, exercise_id, at)
    )
    SelectionRepository(session).consume(consuming(learner_id, issued.id, at))
    sequence = EventRepository(session).append(new_event(issued, at, outcome))
    return issued, sequence


class TestLearnerRepository:
    def test_a_learner_can_be_added_and_found(self, session: Session) -> None:
        repository = LearnerRepository(session)

        added = repository.add(AddLearner(course_release="release-1"))

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
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))

        issued = SelectionRepository(session).issue(new_selection(learner.id, "lex:b"))

        assert issued.exercise_id == "ex:1"
        assert issued.item_ids == ("lex:b",)
        assert issued.new_item == "lex:b"
        assert issued.expires_at == NOW + LIFETIME
        assert issued.consumed_at is None

    def test_consuming_marks_the_time_it_was_answered(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        issued = SelectionRepository(session).issue(new_selection(learner.id))

        consumed = SelectionRepository(session).consume(
            consuming(learner.id, issued.id, NOW + timedelta(minutes=5))
        )

        assert consumed.consumed_at == NOW + timedelta(minutes=5)

    def test_a_selection_cannot_be_answered_twice(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        repository = SelectionRepository(session)
        issued = repository.issue(new_selection(learner.id))
        repository.consume(consuming(learner.id, issued.id, NOW))

        with pytest.raises(SelectionAlreadyAnsweredError):
            repository.consume(consuming(learner.id, issued.id, NOW))

    def test_an_expired_selection_cannot_be_answered(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        repository = SelectionRepository(session)
        issued = repository.issue(new_selection(learner.id))

        with pytest.raises(SelectionExpiredError):
            repository.consume(consuming(learner.id, issued.id, NOW + LIFETIME))

    def test_a_selection_can_be_answered_just_before_it_expires(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        repository = SelectionRepository(session)
        issued = repository.issue(new_selection(learner.id))

        repository.consume(
            consuming(learner.id, issued.id, NOW + LIFETIME - timedelta(seconds=1))
        )

    def test_an_unknown_selection_is_not_found(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))

        with pytest.raises(SelectionNotFoundError):
            SelectionRepository(session).consume(
                consuming(learner.id, uuid.uuid4(), NOW)
            )

    def test_a_learner_cannot_answer_another_learners_selection(
        self, session: Session
    ) -> None:
        learners = LearnerRepository(session)
        owner = learners.add(AddLearner(course_release="r"))
        other = learners.add(AddLearner(course_release="r"))
        repository = SelectionRepository(session)
        issued = repository.issue(new_selection(owner.id))

        with pytest.raises(SelectionNotFoundError):
            repository.consume(consuming(other.id, issued.id, NOW))


class TestEventRepository:
    def test_sequence_numbers_count_up_from_one(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))

        sequences = [
            answer(
                session,
                learner.id,
                NOW + timedelta(minutes=n),
                f"lex:{n}",
                f"ex:{n}",
            )[1]
            for n in range(3)
        ]

        assert sequences == [1, 2, 3]

    def test_each_learner_has_their_own_sequence(self, session: Session) -> None:
        learners = LearnerRepository(session)

        sequences = [
            answer(session, learners.add(AddLearner(course_release="r")).id, NOW)[1]
            for _ in range(2)
        ]

        assert sequences == [1, 1]

    def test_events_come_back_in_the_order_they_happened(
        self, session: Session
    ) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        for n in range(3):
            answer(
                session, learner.id, NOW + timedelta(minutes=n), f"lex:{n}", f"ex:{n}"
            )

        events = EventRepository(session).events(learner.id)

        assert [event.exercise_id for event in events] == ["ex:0", "ex:1", "ex:2"]
        assert [event.sequence for event in events] == [1, 2, 3]

    def test_an_event_keeps_everything_it_was_given(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        issued, _ = answer(session, learner.id, NOW, outcome="missed_it")

        (event,) = EventRepository(session).events(learner.id)

        assert event.selection_id == issued.id
        assert event.item_ids == ("lex:a",)
        assert event.new_item == "lex:a"
        assert event.outcome == "missed_it"
        assert event.reviewed_at == NOW

    def test_an_event_can_be_found_by_its_selection(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        issued, _ = answer(session, learner.id, NOW)
        repository = EventRepository(session)

        found = repository.for_selection(learner.id, issued.id)

        assert found is not None
        assert found.sequence == 1
        assert repository.for_selection(learner.id, uuid.uuid4()) is None

    def test_an_event_earlier_than_the_last_is_rejected(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        answer(session, learner.id, NOW)
        late = SelectionRepository(session).issue(
            new_selection(learner.id, "lex:b", "ex:2")
        )

        with pytest.raises(EventOutOfOrderError):
            EventRepository(session).append(new_event(late, NOW - timedelta(1)))

    def test_an_unknown_learner_is_rejected(self, session: Session) -> None:
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        issued = SelectionRepository(session).issue(new_selection(learner.id))

        with pytest.raises(LearnerNotFoundError):
            EventRepository(session).append(
                replace(new_event(issued, NOW), learner_id=uuid.uuid4())
            )

    def test_times_come_back_in_utc_whatever_the_session_time_zone(
        self, session: Session
    ) -> None:
        session.execute(text("SET TIME ZONE 'Asia/Tokyo'"))
        learner = LearnerRepository(session).add(AddLearner(course_release="r"))
        answer(session, learner.id, NOW)

        (event,) = EventRepository(session).events(learner.id)

        assert event.reviewed_at == NOW
        assert event.reviewed_at.utcoffset() == timedelta(0)


class TestConcurrentAppends:
    def test_simultaneous_appends_for_one_learner_get_distinct_sequences(
        self, session_factory: sessionmaker[Session]
    ) -> None:
        with session_factory() as setup:
            learner = LearnerRepository(setup).add(AddLearner(course_release="r"))
            issued = tuple(
                SelectionRepository(setup).issue(
                    new_selection(learner.id, f"lex:{n}", f"ex:{n}")
                )
                for n in range(8)
            )
            setup.commit()

        errors: list[BaseException] = []
        sequences: list[int] = []

        def append(stored: IssuedSelectionRecord) -> None:
            try:
                with session_factory() as worker:
                    sequence = EventRepository(worker).append(new_event(stored, NOW))
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

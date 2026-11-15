import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from persistence.database import create_session_factory
from persistence.database.models import IssuedSelection, Learner, ReviewEvent

NOW = datetime(2026, 1, 1, 9, tzinfo=UTC)


def add_learner(session: Session) -> Learner:
    learner = Learner(course_release="hash")
    session.add(learner)
    session.flush()
    return learner


def add_selection(session: Session, learner: Learner) -> IssuedSelection:
    selection = IssuedSelection(
        learner_id=learner.id,
        exercise_id="ex:1",
        item_ids=["lex:siarad"],
        new_item="lex:siarad",
        issued_at=NOW,
        expires_at=NOW + timedelta(hours=1),
    )
    session.add(selection)
    session.flush()
    return selection


def event(
    learner: Learner,
    selection: IssuedSelection,
    *,
    sequence: int = 1,
    outcome: str = "got_it",
) -> ReviewEvent:
    return ReviewEvent(
        learner_id=learner.id,
        sequence=sequence,
        selection_id=selection.id,
        exercise_id=selection.exercise_id,
        item_ids=selection.item_ids,
        new_item=selection.new_item,
        outcome=outcome,
        reviewed_at=NOW,
    )


class TestRoundTrip:
    def test_a_learner_is_stored_with_a_creation_time(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            session.commit()

            session.refresh(learner)

            assert learner.created_at.tzinfo is not None
            assert isinstance(learner.id, uuid.UUID)

    def test_item_ids_and_times_survive_storage(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            selection = add_selection(session, add_learner(session))
            session.commit()

            session.expire_all()

            assert selection.item_ids == ["lex:siarad"]
            assert selection.issued_at == NOW
            assert selection.consumed_at is None


class TestConstraints:
    def test_a_learner_cannot_have_two_events_with_one_sequence(
        self, engine: Engine
    ) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            first = add_selection(session, learner)
            second = add_selection(session, learner)
            session.add(event(learner, first))
            session.flush()

            session.add(event(learner, second))

            with pytest.raises(IntegrityError):
                session.flush()

    def test_different_learners_can_share_a_sequence(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            for _ in range(2):
                learner = add_learner(session)
                session.add(event(learner, add_selection(session, learner)))

            session.flush()

    def test_a_selection_can_only_be_answered_once(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            selection = add_selection(session, learner)
            session.add(event(learner, selection, sequence=1))
            session.flush()

            session.add(event(learner, selection, sequence=2))

            with pytest.raises(IntegrityError):
                session.flush()

    def test_sequences_start_at_one(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            session.add(event(learner, add_selection(session, learner), sequence=0))

            with pytest.raises(IntegrityError):
                session.flush()

    def test_an_unknown_outcome_is_rejected(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            session.add(
                event(learner, add_selection(session, learner), outcome="maybe")
            )

            with pytest.raises(IntegrityError):
                session.flush()

    def test_an_event_needs_a_real_learner(self, engine: Engine) -> None:
        with create_session_factory(engine)() as session:
            learner = add_learner(session)
            selection = add_selection(session, learner)
            record = event(learner, selection)
            record.learner_id = uuid.uuid4()
            session.add(record)

            with pytest.raises(IntegrityError):
                session.flush()

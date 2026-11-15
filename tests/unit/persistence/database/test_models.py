from sqlalchemy import UniqueConstraint

from persistence.database import Base
from persistence.database.models import OUTCOMES
from engine.learner import Outcome


class TestModels:
    def test_defines_the_three_tables(self) -> None:
        assert set(Base.metadata.tables) == {
            "learners",
            "issued_selections",
            "review_events",
        }

    def test_outcomes_match_the_engine(self) -> None:
        assert set(OUTCOMES) == {outcome.value for outcome in Outcome}

    def test_review_events_are_unique_per_learner_and_sequence(self) -> None:
        constraints = {
            tuple(column.name for column in constraint.columns)
            for constraint in Base.metadata.tables["review_events"].constraints
            if isinstance(constraint, UniqueConstraint)
        }

        assert ("learner_id", "sequence") in constraints
        assert ("selection_id",) in constraints

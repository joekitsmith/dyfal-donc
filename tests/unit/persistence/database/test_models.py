from sqlalchemy import UniqueConstraint

from persistence.database.models import Base


class TestModels:
    def test_defines_the_tables(self) -> None:
        assert set(Base.metadata.tables) == {
            "issued_selections",
            "learners",
            "login_sessions",
            "review_events",
            "users",
            "webauthn_challenges",
            "webauthn_credentials",
        }

    def test_review_events_are_unique_per_learner_and_sequence(self) -> None:
        constraints = {
            tuple(column.name for column in constraint.columns)
            for constraint in Base.metadata.tables["review_events"].constraints
            if isinstance(constraint, UniqueConstraint)
        }

        assert ("learner_id", "sequence") in constraints
        assert ("selection_id",) in constraints

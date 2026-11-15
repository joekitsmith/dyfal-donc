from datetime import UTC, datetime

from api.mappings import to_progress_response
from engine.learner import (
    DEFAULT_SETTINGS,
    LearnerState,
    Learning,
    Review,
    ReviewMemory,
)


def state() -> LearnerState:
    return LearnerState(
        memories={
            "lex:a": Learning(step_index=0, exercises_until_due=0),
            "lex:b": Learning(step_index=1, exercises_until_due=2),
            "lex:c": Review(memory=_review_memory()),
        },
        last_reviewed_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _review_memory() -> ReviewMemory:
    return DEFAULT_SETTINGS.memory_model.initial(datetime(2026, 1, 1, tzinfo=UTC))


class TestToProgressResponse:
    def test_counts_where_each_item_is(self) -> None:
        response = to_progress_response(
            state=state(),
            learning_due=("lex:a",),
            review_due=(),
            recent_error_rate=0.25,
            course_items=234,
        )

        assert response.introduced == 3
        assert response.learning == 2
        assert response.in_review == 1
        assert response.learning_due == 1
        assert response.review_due == 0
        assert response.recent_error_rate == 0.25
        assert response.course_items == 234

    def test_a_new_learner_has_nothing_yet(self) -> None:
        response = to_progress_response(
            state=LearnerState(),
            learning_due=(),
            review_due=(),
            recent_error_rate=0.0,
            course_items=10,
        )

        assert (response.introduced, response.learning, response.in_review) == (0, 0, 0)

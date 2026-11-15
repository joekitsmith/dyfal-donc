from collections.abc import Sequence

from api.schemas import ProgressResponse
from engine.learner import LearnerState, Learning


def to_progress_response(
    *,
    state: LearnerState,
    learning_due: Sequence[str],
    review_due: Sequence[str],
    recent_error_rate: float,
    course_items: int,
) -> ProgressResponse:
    learning = sum(isinstance(memory, Learning) for memory in state.memories.values())
    return ProgressResponse(
        introduced=len(state.memories),
        learning=learning,
        in_review=len(state.memories) - learning,
        learning_due=len(learning_due),
        review_due=len(review_due),
        recent_error_rate=recent_error_rate,
        course_items=course_items,
    )

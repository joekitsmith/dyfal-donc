from pydantic import BaseModel


class ProgressResponse(BaseModel):
    """Where the learner is, as of the server's clock."""

    introduced: int
    learning: int
    in_review: int
    learning_due: int
    review_due: int
    recent_error_rate: float
    course_items: int

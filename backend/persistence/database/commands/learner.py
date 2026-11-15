from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AddLearner:
    """Add a learner who starts on the given course release."""

    course_release: str

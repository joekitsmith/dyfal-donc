from dataclasses import dataclass, field

from engine.learner.errors import LearnerError
from engine.learner.fsrs_model import FsrsMemoryModel
from engine.learner.memory import MemoryModel

DEFAULT_LEARNING_STEPS = (1, 3, 8)


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerSettings:
    """How a learner's memory is modelled.

    ``learning_steps`` count exercises, not time. An item just introduced is
    due again after ``learning_steps[0]`` other exercises, and so on. Passing
    the last step graduates it to ``memory_model``.
    """

    learning_steps: tuple[int, ...] = DEFAULT_LEARNING_STEPS
    memory_model: MemoryModel = field(default_factory=FsrsMemoryModel)

    def __post_init__(self) -> None:
        if not self.learning_steps:
            raise LearnerError("Learning steps cannot be empty")

        if any(step < 1 for step in self.learning_steps):
            raise LearnerError(
                f"Learning steps must each be at least 1, not {self.learning_steps}"
            )


DEFAULT_SETTINGS = LearnerSettings()

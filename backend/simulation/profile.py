from dataclasses import dataclass, replace

from simulation.errors import SimulationError
from simulation.memory import ExponentialMemory, TrueMemoryModel


@dataclass(frozen=True, slots=True, kw_only=True)
class LearnerProfile:
    """Who the simulated learner is.

    ``difficulty_spread`` is the spread of how hard each item is for them (the
    standard deviation of a log-normal multiplier on how much a success helps).
    ``learning_rate`` scales every gain. ``under_report_rate`` is the chance a
    true miss is reported as a success, as a learner who says nothing would.
    """

    name: str
    memory: TrueMemoryModel = ExponentialMemory()
    difficulty_spread: float = 0.4
    learning_rate: float = 1.0
    under_report_rate: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise SimulationError("Profile name must not be blank")

        if self.difficulty_spread < 0:
            raise SimulationError("Difficulty spread must not be negative")

        if self.learning_rate <= 0:
            raise SimulationError("Learning rate must be positive")

        if not 0 <= self.under_report_rate <= 1:
            raise SimulationError("Under-report rate must be between 0 and 1")

    def with_memory(self, memory: TrueMemoryModel) -> LearnerProfile:
        return replace(self, memory=memory)


STRONG = LearnerProfile(
    name="strong", difficulty_spread=0.2, learning_rate=1.5, under_report_rate=0.1
)
AVERAGE = LearnerProfile(
    name="average", difficulty_spread=0.4, learning_rate=1.0, under_report_rate=0.2
)
WEAK = LearnerProfile(
    name="weak", difficulty_spread=0.7, learning_rate=0.45, under_report_rate=0.3
)

PROFILES = (STRONG, AVERAGE, WEAK)

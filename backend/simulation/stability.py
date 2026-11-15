import math
from dataclasses import dataclass

from simulation.errors import SimulationError


@dataclass(frozen=True, slots=True, kw_only=True)
class StabilityUpdate:
    """How a recall attempt changes stability, shared by the forgetting curves.

    A success multiplies stability by ``1 + gain`` where ``gain`` is
    ``gain_scale * (exp(gain_steepness * (1 - recall)) - 1) * stability **
    -gain_decay``, capped at ``max_gain``. It is zero when the item was fully
    remembered, so repeating an item within a minute adds almost nothing (the
    spacing effect), grows as more was forgotten, and shrinks as the memory
    gets stronger. A failure keeps ``failure_keeps`` of the stability, never
    below ``initial_days``, since seeing the answer again is a fresh exposure.
    An item starts at ``initial_days``, about what a learner retains after a
    first exposure. These are assumptions, set so an average learner looks
    plausible, not fitted to real data.
    """

    initial_days: float = 0.15
    gain_scale: float = 3.0
    gain_steepness: float = 3.0
    gain_decay: float = 0.15
    max_gain: float = 8.0
    failure_keeps: float = 0.3

    def __post_init__(self) -> None:
        if self.initial_days <= 0:
            raise SimulationError("Initial stability must be positive")

        if min(self.gain_scale, self.gain_steepness, self.gain_decay) < 0:
            raise SimulationError("Stability gain settings must not be negative")

        if self.max_gain < 0:
            raise SimulationError("Maximum gain must not be negative")

        if not 0 < self.failure_keeps < 1:
            raise SimulationError("Failure keeps must be between 0 and 1")

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        raw = (
            self.gain_scale
            * (math.exp(self.gain_steepness * (1 - recall_probability)) - 1)
            * stability_days**-self.gain_decay
        )
        return stability_days * (1 + min(self.max_gain, gain_scale * raw))

    def after_failure(self, stability_days: float) -> float:
        return max(self.initial_days, stability_days * self.failure_keeps)


DEFAULT_STABILITY_UPDATE = StabilityUpdate()

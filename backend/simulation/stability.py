from dataclasses import dataclass

from simulation.errors import SimulationError


@dataclass(frozen=True, slots=True, kw_only=True)
class StabilityUpdate:
    """How a recall attempt changes stability, shared by the forgetting curves.

    A success multiplies stability by ``1 + gain_scale * (gain_base + gain_hard *
    (1 - recall))``, so a hard recall gains more than an easy one (the spacing
    effect). A failure keeps ``failure_keeps`` of it, never below the starting
    stability. These are assumptions, set so an average learner looks plausible,
    not fitted to real data.
    """

    initial_days: float = 0.01
    gain_base: float = 1.5
    gain_hard: float = 5.0
    failure_keeps: float = 0.3

    def __post_init__(self) -> None:
        if self.initial_days <= 0:
            raise SimulationError("Initial stability must be positive")

        if self.gain_base < 0 or self.gain_hard < 0:
            raise SimulationError("Stability gains must not be negative")

        if not 0 < self.failure_keeps < 1:
            raise SimulationError("Failure keeps must be between 0 and 1")

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        gain = gain_scale * (self.gain_base + self.gain_hard * (1 - recall_probability))
        return stability_days * (1 + gain)

    def after_failure(self, stability_days: float) -> float:
        return max(self.initial_days, stability_days * self.failure_keeps)


DEFAULT_STABILITY_UPDATE = StabilityUpdate()

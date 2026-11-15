from dataclasses import dataclass
from typing import Protocol

from simulation.stability import DEFAULT_STABILITY_UPDATE, StabilityUpdate

REFERENCE_RECALL = 0.9
"""Stability is the time for recall to fall to this, as in FSRS, so models are comparable."""

POWER_LAW_OFFSET = 9
"""Makes the power-law curve pass through ``REFERENCE_RECALL`` at one unit of stability."""


class TrueMemoryModel(Protocol):
    """How the simulated learner really forgets, independent of the engine's FSRS.

    Stability is in days: the time for recall to fall to 90%.
    """

    @property
    def initial_stability_days(self) -> float: ...

    def recall_probability(
        self, stability_days: float, elapsed_days: float
    ) -> float: ...

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        """The stability after a successful recall. ``recall_probability`` is what it was at review."""
        ...

    def after_failure(self, stability_days: float) -> float: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ExponentialMemory:
    """Recall decays at a constant rate: ``0.9 ** (t / S)``."""

    update: StabilityUpdate = DEFAULT_STABILITY_UPDATE

    @property
    def initial_stability_days(self) -> float:
        return self.update.initial_days

    def recall_probability(self, stability_days: float, elapsed_days: float) -> float:
        return REFERENCE_RECALL ** (max(0.0, elapsed_days) / stability_days)

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        return self.update.after_success(stability_days, recall_probability, gain_scale)

    def after_failure(self, stability_days: float) -> float:
        return self.update.after_failure(stability_days)


@dataclass(frozen=True, slots=True, kw_only=True)
class PowerLawMemory:
    """Recall decays quickly then slowly: ``1 / (1 + t / (9 S))``. Closest to FSRS's own curve."""

    update: StabilityUpdate = DEFAULT_STABILITY_UPDATE

    @property
    def initial_stability_days(self) -> float:
        return self.update.initial_days

    def recall_probability(self, stability_days: float, elapsed_days: float) -> float:
        return 1 / (1 + max(0.0, elapsed_days) / (POWER_LAW_OFFSET * stability_days))

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        return self.update.after_success(stability_days, recall_probability, gain_scale)

    def after_failure(self, stability_days: float) -> float:
        return self.update.after_failure(stability_days)

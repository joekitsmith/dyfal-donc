from dataclasses import dataclass

from simulation.profile import LearnerProfile
from simulation.session import SessionSettings


@dataclass(frozen=True, slots=True, kw_only=True)
class PerfectMemory:
    """Never forgets."""

    initial_stability_days: float = 1.0

    def recall_probability(self, stability_days: float, elapsed_days: float) -> float:
        return 1.0

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        return stability_days

    def after_failure(self, stability_days: float) -> float:
        return stability_days


@dataclass(frozen=True, slots=True, kw_only=True)
class NoMemory:
    """Forgets everything the moment it is seen."""

    initial_stability_days: float = 1.0

    def recall_probability(self, stability_days: float, elapsed_days: float) -> float:
        return 0.0

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        return stability_days

    def after_failure(self, stability_days: float) -> float:
        return stability_days


@dataclass(frozen=True, slots=True, kw_only=True)
class ShakyMemory:
    """Remembers items with a stability of at least half a day, and forgets the rest."""

    initial_stability_days: float = 1.0

    def recall_probability(self, stability_days: float, elapsed_days: float) -> float:
        return 1.0 if stability_days >= 0.5 else 0.0

    def after_success(
        self, stability_days: float, recall_probability: float, gain_scale: float
    ) -> float:
        return stability_days

    def after_failure(self, stability_days: float) -> float:
        return stability_days


PERFECT = LearnerProfile(name="perfect", memory=PerfectMemory())
FORGETFUL = LearnerProfile(name="forgetful", memory=NoMemory())

SHORT_RUN = SessionSettings(days=10, skip_day_probability=0.0)

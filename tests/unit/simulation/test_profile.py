from collections.abc import Callable

import pytest

from simulation.errors import SimulationError
from simulation.memory import PowerLawMemory
from simulation.profile import AVERAGE, PROFILES, LearnerProfile


class TestLearnerProfile:
    def test_with_memory_changes_only_the_memory(self) -> None:
        changed = AVERAGE.with_memory(PowerLawMemory())

        assert changed.memory == PowerLawMemory()
        assert changed.name == AVERAGE.name
        assert changed.under_report_rate == AVERAGE.under_report_rate

    @pytest.mark.parametrize(
        "make",
        (
            lambda: LearnerProfile(name=" "),
            lambda: LearnerProfile(name="x", difficulty_spread=-0.1),
            lambda: LearnerProfile(name="x", learning_rate=0),
            lambda: LearnerProfile(name="x", under_report_rate=1.1),
            lambda: LearnerProfile(name="x", under_report_rate=-0.1),
        ),
    )
    def test_invalid_values_are_rejected(
        self, make: Callable[[], LearnerProfile]
    ) -> None:
        with pytest.raises(SimulationError):
            make()

    def test_presets_are_ordered_from_strong_to_weak(self) -> None:
        rates = tuple(profile.learning_rate for profile in PROFILES)

        assert rates == tuple(sorted(rates, reverse=True))
        assert len({profile.name for profile in PROFILES}) == len(PROFILES)

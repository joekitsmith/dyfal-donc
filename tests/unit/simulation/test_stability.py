import pytest

from simulation.errors import SimulationError
from simulation.stability import StabilityUpdate


class TestStabilityUpdate:
    @pytest.mark.parametrize(
        "update",
        (
            {"initial_days": 0},
            {"gain_base": -1},
            {"gain_hard": -1},
            {"failure_keeps": 0},
            {"failure_keeps": 1},
        ),
    )
    def test_invalid_values_are_rejected(self, update: dict[str, float]) -> None:
        with pytest.raises(SimulationError):
            StabilityUpdate(**update)

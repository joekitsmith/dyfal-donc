from pathlib import Path

import pytest

from engine.curriculum import load_curriculum
from simulation.memory import ExponentialMemory, PowerLawMemory
from simulation.pool import build_pool, coverage
from simulation.profile import AVERAGE
from simulation.runner import simulate
from simulation.session import SessionSettings

CURRICULUM = load_curriculum(Path(__file__).parents[3] / "curriculum")
POOL = build_pool(CURRICULUM)
SESSION = SessionSettings(days=60)


class TestRealPool:
    def test_every_item_can_be_introduced(self) -> None:
        assert coverage(POOL, CURRICULUM).without_introduction == ()


@pytest.mark.parametrize(
    "memory", (ExponentialMemory(), PowerLawMemory()), ids=lambda m: type(m).__name__
)
class TestRealRun:
    def test_an_average_learner_gets_through_the_course(
        self, memory: ExponentialMemory | PowerLawMemory
    ) -> None:
        trace = simulate(
            POOL,
            CURRICULUM,
            AVERAGE.with_memory(memory),
            seed=1,
            session=SESSION,
        )

        introduced = {
            step.event.new_item for step in trace.steps if step.event.new_item
        }
        assert introduced == set(CURRICULUM.order)

    def test_a_run_is_reproducible(
        self, memory: ExponentialMemory | PowerLawMemory
    ) -> None:
        profile = AVERAGE.with_memory(memory)

        first = simulate(POOL, CURRICULUM, profile, seed=5, session=SESSION)
        second = simulate(POOL, CURRICULUM, profile, seed=5, session=SESSION)

        assert first == second

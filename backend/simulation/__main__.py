import argparse
from collections.abc import Sequence
from pathlib import Path

from engine.curriculum import load_curriculum
from simulation.memory import ExponentialMemory, PowerLawMemory, TrueMemoryModel
from simulation.pool import build_pool, coverage
from simulation.profile import PROFILES
from simulation.runner import simulate
from simulation.session import SessionSettings
from simulation.summary import RunSummary, render_coverage

CURRICULUM_DIRECTORY = Path(__file__).parents[2] / "curriculum"
MEMORY_MODELS: dict[str, TrueMemoryModel] = {
    "exponential": ExponentialMemory(),
    "power-law": PowerLawMemory(),
}


def main(arguments: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="simulate", description="Run a simulated learner through the course"
    )
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument(
        "--profile",
        choices=tuple(profile.name for profile in PROFILES),
        default="average",
    )
    parser.add_argument("--memory", choices=tuple(MEMORY_MODELS), default="exponential")
    options = parser.parse_args(arguments)

    curriculum = load_curriculum(CURRICULUM_DIRECTORY)
    pool = build_pool(curriculum)
    print(render_coverage(coverage(pool, curriculum)))

    profile = next(
        profile for profile in PROFILES if profile.name == options.profile
    ).with_memory(MEMORY_MODELS[options.memory])
    trace = simulate(
        pool,
        curriculum,
        profile,
        seed=options.seed,
        session=SessionSettings(days=options.days),
    )
    print()
    print(
        f"{options.profile} learner, {options.memory} memory, "
        f"seed {options.seed}, {options.days} days"
    )
    print(RunSummary.from_trace(trace).render())


if __name__ == "__main__":
    main()

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from simulation.pool import PoolCoverage
from simulation.trace import SimulationTrace


@dataclass(frozen=True, slots=True, kw_only=True)
class RunSummary:
    """The headline numbers of one run."""

    exercises: int
    introduced: int
    true_retention: float
    reported_error_rate: float
    true_error_rate: float
    stalls: tuple[tuple[str, int], ...]

    @classmethod
    def from_trace(cls, trace: SimulationTrace) -> RunSummary:
        steps = trace.steps
        final = trace.snapshots[-1].items if trace.snapshots else ()
        return cls(
            exercises=len(steps),
            introduced=sum(step.event.new_item is not None for step in steps),
            true_retention=_mean(item.recall_probability for item in final),
            reported_error_rate=_mean(
                step.event.outcome.value == "missed_it" for step in steps
            ),
            true_error_rate=_mean(not step.truly_correct for step in steps),
            stalls=tuple(
                sorted(Counter(stall.reason.value for stall in trace.stalls).items())
            ),
        )

    def render(self) -> str:
        stalls = ", ".join(f"{reason}: {count}" for reason, count in self.stalls)
        return "\n".join(
            (
                f"Exercises given: {self.exercises}",
                f"Items introduced: {self.introduced}",
                f"True retention at the end: {self.true_retention:.0%}",
                f"Error rate, as reported: {self.reported_error_rate:.0%}",
                f"Error rate, in truth: {self.true_error_rate:.0%}",
                f"Sessions cut short: {stalls or 'none'}",
            )
        )


def render_coverage(coverage: PoolCoverage, rejected: int) -> str:
    gaps = ", ".join(coverage.without_introduction) or "none"
    blocking = coverage.blocking or "none"
    thinnest = min(coverage.introducing.values(), default=0)
    return "\n".join(
        (
            f"Pool: {sum(coverage.introducing.values())} exercises introduce "
            f"{len(coverage.introducing) - len(coverage.without_introduction)} "
            f"of {len(coverage.introducing)} items "
            f"({rejected} gold sentences rejected)",
            f"Items with no introducing exercise: {gaps}",
            f"First item blocking the course: {blocking}",
            f"Fewest introducing exercises for one item: {thinnest}",
        )
    )


def _mean(values: Iterable[float | bool]) -> float:
    numbers = tuple(float(value) for value in values)
    return sum(numbers) / len(numbers) if numbers else 0.0

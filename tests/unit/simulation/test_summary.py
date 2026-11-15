from collections.abc import Mapping

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from simulation.pool import coverage
from simulation.profile import AVERAGE
from simulation.runner import simulate
from simulation.summary import RunSummary, render_coverage
from tests.unit.simulation.helpers import PERFECT, SHORT_RUN


class TestRunSummary:
    def test_summarises_a_perfect_run(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, PERFECT, seed=1, session=SHORT_RUN)

        summary = RunSummary.from_trace(trace)

        assert summary.introduced == 4
        assert summary.true_error_rate == 0
        assert summary.true_retention == 1
        assert summary.stalls == ()

    def test_render_mentions_each_headline_number(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, AVERAGE, seed=1, session=SHORT_RUN)

        text = RunSummary.from_trace(trace).render()

        for label in ("Exercises given", "Items introduced", "True retention"):
            assert label in text

    def test_an_empty_trace_summarises_to_zeros(self, curriculum: Curriculum) -> None:
        trace = simulate({}, curriculum, AVERAGE, seed=1, session=SHORT_RUN)

        summary = RunSummary.from_trace(trace)

        assert summary.exercises == 0
        assert summary.true_error_rate == 0


class TestRenderCoverage:
    def test_names_the_blocking_item(self, curriculum: Curriculum) -> None:
        text = render_coverage(coverage({}, curriculum))

        assert "First item blocking the course: lex:siarad" in text

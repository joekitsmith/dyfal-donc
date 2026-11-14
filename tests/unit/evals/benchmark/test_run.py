from evals.benchmark import render_report, run_benchmark
from tests.unit.evals.benchmark.sample_gold_sentences import (
    CURRICULUM,
    PERFECT_LEMMAS,
    SENTENCES,
)
from tests.fake_lemmatisers import FixedLemmatiser


class TestRunBenchmark:
    def test_scores_every_lemmatiser_in_order(self) -> None:
        lemmatisers = {
            "Perfect": FixedLemmatiser(PERFECT_LEMMAS),
            "Empty": FixedLemmatiser({}),
        }

        result = run_benchmark(lemmatisers, SENTENCES, CURRICULUM)

        assert [row.name for row in result.lemmatisers] == ["Perfect", "Empty"]
        assert result.sentences == 2
        assert result.tokens == 7

    def test_a_better_lemmatiser_scores_higher(self) -> None:
        lemmatisers = {
            "Perfect": FixedLemmatiser(PERFECT_LEMMAS),
            "Empty": FixedLemmatiser({}),
        }

        perfect, empty = run_benchmark(lemmatisers, SENTENCES, CURRICULUM).lemmatisers

        assert perfect.lemmas.overall.accuracy == 1.0
        assert empty.lemmas.overall.accuracy == 0.0
        assert perfect.items.overall.recall > empty.items.overall.recall
        assert perfect.authoring.surfaced == 1

    def test_declared_forms_only_matches_a_lemmatiser_with_no_candidates(self) -> None:
        result = run_benchmark({"Empty": FixedLemmatiser({})}, SENTENCES, CURRICULUM)

        assert result.lemmatisers[0].items == result.declared_forms_only

    def test_runtime_is_measured(self) -> None:
        result = run_benchmark(
            {"Perfect": FixedLemmatiser(PERFECT_LEMMAS)}, SENTENCES, CURRICULUM
        )

        assert result.lemmatisers[0].milliseconds_per_sentence >= 0.0


class TestRenderReport:
    def test_report_has_every_section_and_lemmatiser(self) -> None:
        result = run_benchmark(
            {"Perfect": FixedLemmatiser(PERFECT_LEMMAS)}, SENTENCES, CURRICULUM
        )

        report = render_report(
            result, recommendation="Use it.", environment={"simplemma": "1.2.3"}
        )

        for heading in (
            "# Lemmatiser benchmark",
            "## Summary",
            "## Lemma level",
            "## Item level",
            "## Authoring aid",
            "## Runtime",
            "## Recommendation",
            "## Notes",
        ):
            assert heading in report
        assert "| Perfect |" in report
        assert "Declared forms only" in report
        assert "Use it." in report
        assert "simplemma 1.2.3" in report

    def test_report_ends_with_a_single_newline(self) -> None:
        result = run_benchmark({"Empty": FixedLemmatiser({})}, SENTENCES, CURRICULUM)

        report = render_report(result, recommendation="x\n", environment={})

        assert report.endswith("\n")
        assert not report.endswith("\n\n")

import pytest

from cymraeg import DemutatingLemmatiser, Lemmatiser, RuleLemmatiser
from engine.curriculum import load_curriculum
from evals.benchmark import render_report, run_benchmark
from evals.benchmark.run import CURRICULUM_DIRECTORY, RECOMMENDATION_PATH
from evals.gold import load_gold_sentences

SENTENCES = load_gold_sentences()
CURRICULUM = load_curriculum(CURRICULUM_DIRECTORY)


class TestBenchmarkOnTheGoldSet:
    def test_rule_lemmatiser_adds_nothing_to_declared_forms(self) -> None:
        result = run_benchmark({"Rule": RuleLemmatiser()}, SENTENCES, CURRICULUM)

        assert result.lemmatisers[0].items == result.declared_forms_only

    def test_declared_forms_miss_some_gold_items(self) -> None:
        result = run_benchmark({"Rule": RuleLemmatiser()}, SENTENCES, CURRICULUM)

        assert 0.0 < result.declared_forms_only.overall.recall < 1.0
        assert result.lemmatisers[0].authoring.undeclared > 0

    def test_rule_lemmatiser_cannot_surface_inflected_forms(self) -> None:
        result = run_benchmark({"Rule": RuleLemmatiser()}, SENTENCES, CURRICULUM)

        assert result.lemmatisers[0].authoring.surfaced == 0

    def test_report_renders_with_the_written_recommendation(self) -> None:
        result = run_benchmark(
            {"Rule (demutate)": RuleLemmatiser()}, SENTENCES, CURRICULUM
        )

        report = render_report(
            result,
            recommendation=RECOMMENDATION_PATH.read_text(encoding="utf-8"),
            environment={},
        )

        assert "## Recommendation\n\nUse a lemmatiser as an **authoring aid**" in report


class TestBenchmarkWithSimplemma:
    def test_simplemma_surfaces_undeclared_forms_the_rule_lemmatiser_misses(
        self,
    ) -> None:
        pytest.importorskip("simplemma")
        from cymraeg import SimplemmaLemmatiser

        lemmatisers: dict[str, Lemmatiser] = {
            "Rule": RuleLemmatiser(),
            "Simplemma": SimplemmaLemmatiser(),
            "Simplemma + demutate": DemutatingLemmatiser(SimplemmaLemmatiser()),
        }

        rule, simplemma, demutating = run_benchmark(
            lemmatisers, SENTENCES, CURRICULUM
        ).lemmatisers

        assert simplemma.authoring.surfaced > rule.authoring.surfaced
        assert simplemma.lemmas.overall.accuracy > rule.lemmas.overall.accuracy
        assert (
            demutating.lemmas.overall.average_candidates
            >= simplemma.lemmas.overall.average_candidates
        )

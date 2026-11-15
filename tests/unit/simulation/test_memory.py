import pytest
from hypothesis import given
from hypothesis import strategies as st

from simulation.memory import (
    DEFAULT_STABILITY_UPDATE,
    ExponentialMemory,
    PowerLawMemory,
    TrueMemoryModel,
)

MODELS = (ExponentialMemory(), PowerLawMemory())
STABILITIES = st.floats(min_value=0.001, max_value=1000)
ELAPSED = st.floats(min_value=0, max_value=10_000)


@pytest.mark.parametrize("model", MODELS, ids=lambda model: type(model).__name__)
class TestTrueMemoryModels:
    @given(stability=STABILITIES)
    def test_recall_is_certain_at_once(
        self, model: TrueMemoryModel, stability: float
    ) -> None:
        assert model.recall_probability(stability, 0) == 1

    @given(stability=STABILITIES, elapsed=ELAPSED, later=ELAPSED)
    def test_recall_never_rises_with_time(
        self, model: TrueMemoryModel, stability: float, elapsed: float, later: float
    ) -> None:
        sooner, after = sorted((elapsed, later))

        assert model.recall_probability(stability, after) <= model.recall_probability(
            stability, sooner
        )

    @given(stability=STABILITIES)
    def test_stability_is_the_time_to_ninety_percent(
        self, model: TrueMemoryModel, stability: float
    ) -> None:
        assert model.recall_probability(stability, stability) == pytest.approx(0.9)

    @given(stability=STABILITIES, elapsed=ELAPSED)
    def test_recall_is_a_probability(
        self, model: TrueMemoryModel, stability: float, elapsed: float
    ) -> None:
        assert 0 <= model.recall_probability(stability, elapsed) <= 1

    @given(stability=STABILITIES, recall=st.floats(min_value=0, max_value=0.99))
    def test_a_success_raises_stability_when_something_was_forgotten(
        self, model: TrueMemoryModel, stability: float, recall: float
    ) -> None:
        assert model.after_success(stability, recall, 1.0) > stability

    @given(stability=STABILITIES)
    def test_a_success_at_full_recall_adds_nothing(
        self, model: TrueMemoryModel, stability: float
    ) -> None:
        assert model.after_success(stability, 1.0, 1.0) == stability

    @given(stability=STABILITIES, recall=st.floats(min_value=0, max_value=1))
    def test_a_success_never_gains_more_than_the_cap(
        self, model: TrueMemoryModel, stability: float, recall: float
    ) -> None:
        assert model.after_success(stability, recall, 1.0) <= stability * (
            1 + DEFAULT_STABILITY_UPDATE.max_gain
        )

    @given(stability=st.floats(min_value=0.1, max_value=1000))
    def test_repeating_an_item_within_a_minute_gains_almost_nothing(
        self, model: TrueMemoryModel, stability: float
    ) -> None:
        recall = model.recall_probability(stability, 1 / (24 * 60))

        assert model.after_success(stability, recall, 1.0) < stability * 1.05

    @given(stability=STABILITIES)
    def test_a_failure_lowers_stability_but_not_below_the_start(
        self, model: TrueMemoryModel, stability: float
    ) -> None:
        after = model.after_failure(stability)

        assert after <= max(stability, model.initial_stability_days)
        assert after >= model.initial_stability_days

    def test_a_hard_recall_gains_more_than_an_easy_one(
        self, model: TrueMemoryModel
    ) -> None:
        assert model.after_success(1.0, 0.5, 1.0) > model.after_success(1.0, 0.95, 1.0)

    def test_a_larger_gain_scale_gains_more(self, model: TrueMemoryModel) -> None:
        assert model.after_success(1.0, 0.9, 2.0) > model.after_success(1.0, 0.9, 1.0)


class TestForgettingCurves:
    def test_the_power_law_remembers_more_after_a_long_gap(self) -> None:
        assert PowerLawMemory().recall_probability(
            1.0, 30
        ) > ExponentialMemory().recall_probability(1.0, 30)

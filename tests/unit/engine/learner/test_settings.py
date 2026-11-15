import pytest

from engine.learner import (
    DEFAULT_SETTINGS,
    FsrsMemoryModel,
    LearnerError,
    LearnerSettings,
)


class TestLearnerSettings:
    def test_default_steps_count_exercises(self) -> None:
        assert DEFAULT_SETTINGS.learning_steps == (1, 3, 8)

    def test_default_memory_model_is_fsrs(self) -> None:
        assert isinstance(DEFAULT_SETTINGS.memory_model, FsrsMemoryModel)

    def test_custom_steps(self) -> None:
        assert LearnerSettings(learning_steps=(2,)).learning_steps == (2,)

    def test_rejects_empty_steps(self) -> None:
        with pytest.raises(LearnerError, match="cannot be empty"):
            LearnerSettings(learning_steps=())

    @pytest.mark.parametrize("steps", [(0,), (1, 0, 3), (-1,)])
    def test_rejects_steps_below_one(self, steps: tuple[int, ...]) -> None:
        with pytest.raises(LearnerError, match="at least 1"):
            LearnerSettings(learning_steps=steps)


class TestReviewCreditFraction:
    def test_defaults_to_crediting_only_due_items(self) -> None:
        assert DEFAULT_SETTINGS.review_credit_fraction == 1.0

    def test_accepts_a_fraction(self) -> None:
        assert LearnerSettings(review_credit_fraction=0.5).review_credit_fraction == 0.5

    @pytest.mark.parametrize("fraction", [0.0, -0.5, 1.01])
    def test_rejects_a_fraction_outside_zero_to_one(self, fraction: float) -> None:
        with pytest.raises(LearnerError, match="above 0 and at most 1"):
            LearnerSettings(review_credit_fraction=fraction)

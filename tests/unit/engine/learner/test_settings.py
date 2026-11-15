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

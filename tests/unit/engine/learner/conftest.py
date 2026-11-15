import pytest

from engine.learner import FsrsMemoryModel, LearnerSettings
from tests.unit.engine.learner.helpers import Session


@pytest.fixture
def memory_model() -> FsrsMemoryModel:
    return FsrsMemoryModel()


@pytest.fixture
def learner_settings(memory_model: FsrsMemoryModel) -> LearnerSettings:
    return LearnerSettings(memory_model=memory_model)


@pytest.fixture
def session(learner_settings: LearnerSettings) -> Session:
    return Session(learner_settings)

import pytest

from engine.learner import FsrsMemoryModel


@pytest.fixture
def memory_model() -> FsrsMemoryModel:
    return FsrsMemoryModel()

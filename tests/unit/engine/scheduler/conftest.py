import pytest

from engine.curriculum import Curriculum
from tests.unit.engine.scheduler.helpers import course


@pytest.fixture
def curriculum() -> Curriculum:
    return course()

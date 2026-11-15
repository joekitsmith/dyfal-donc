from collections.abc import Mapping

import pytest

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    MYND_ID,
    SIARAD_ID,
    course,
    exercise,
)


@pytest.fixture
def curriculum() -> Curriculum:
    return course()


@pytest.fixture
def pool() -> Mapping[str, Exercise]:
    return {
        "ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID),
        "ex:2": exercise(SIARAD_ID, DYSGU_ID, new_item=DYSGU_ID),
        "ex:3": exercise(DYSGU_ID),
        "ex:4": exercise(MYND_ID, SIARAD_ID, new_item=MYND_ID),
        "ex:5": exercise(COFFI_ID, MYND_ID, new_item=COFFI_ID),
        "ex:6": exercise(SIARAD_ID, DYSGU_ID, MYND_ID, COFFI_ID),
    }

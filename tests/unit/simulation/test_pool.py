from collections.abc import Mapping
from pathlib import Path

import pytest

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from simulation.errors import SimulationError
from simulation.pool import build_pool, coverage
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    MYND_ID,
    SIARAD_ID,
    exercise,
)


class TestCoverage:
    def test_counts_introducing_and_practising_exercises(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        result = coverage(pool, curriculum)

        assert result.introducing[SIARAD_ID] == 1
        assert result.introducing[DYSGU_ID] == 1
        assert result.practising[SIARAD_ID] == 4
        assert result.without_introduction == ()
        assert result.blocking is None

    def test_reports_the_first_item_nothing_can_introduce(
        self, curriculum: Curriculum
    ) -> None:
        pool = {
            "ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID),
            "ex:2": exercise(COFFI_ID, MYND_ID, new_item=COFFI_ID),
        }

        result = coverage(pool, curriculum)

        assert result.without_introduction == (DYSGU_ID, MYND_ID)
        assert result.blocking == DYSGU_ID

    def test_an_empty_pool_blocks_at_the_first_item(
        self, curriculum: Curriculum
    ) -> None:
        assert coverage({}, curriculum).blocking == SIARAD_ID


class TestBuildPool:
    def test_an_extra_exercise_that_does_not_validate_is_an_error(
        self, curriculum: Curriculum, tmp_path: Path
    ) -> None:
        extras = tmp_path / "extras.yaml"
        extras.write_text(
            "- id: bad\n  english: Nothing\n  welsh: Nonsense\n"
            f"  items: [{SIARAD_ID}]\n  new_item: {SIARAD_ID}\n",
            encoding="utf-8",
        )

        with pytest.raises(SimulationError, match="bad"):
            build_pool(curriculum, extras)

    def test_a_missing_extras_file_is_an_error(
        self, curriculum: Curriculum, tmp_path: Path
    ) -> None:
        with pytest.raises(SimulationError):
            build_pool(curriculum, tmp_path / "missing.yaml")

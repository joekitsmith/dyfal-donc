from engine.learner import Outcome
from engine.scheduler import SchedulerSettings
from engine.scheduler.eligibility import Candidate
from engine.scheduler.scoring import score
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    SIARAD_ID,
    event,
    exercise,
)

SETTINGS = SchedulerSettings(due_item_weight=10, overlap_weight=2, repeat_penalty=100)


def candidate(exercise_id: str, *items: str) -> Candidate:
    return Candidate(exercise_id=exercise_id, exercise=exercise(*items))


class TestScore:
    def test_nothing_due_and_no_previous_exercise_scores_zero(self) -> None:
        assert score(candidate("ex:1", SIARAD_ID), frozenset(), None, SETTINGS) == 0

    def test_each_due_item_adds_weight(self) -> None:
        both = candidate("ex:1", SIARAD_ID, DYSGU_ID)

        assert score(both, {SIARAD_ID, DYSGU_ID}, None, SETTINGS) == 20
        assert score(both, {SIARAD_ID}, None, SETTINGS) == 10

    def test_due_items_outside_the_exercise_do_not_count(self) -> None:
        assert score(candidate("ex:1", SIARAD_ID), {COFFI_ID}, None, SETTINGS) == 0

    def test_each_item_shared_with_the_previous_exercise_adds_weight(self) -> None:
        previous = event("ex:0", SIARAD_ID, DYSGU_ID)

        assert (
            score(
                candidate("ex:1", SIARAD_ID, DYSGU_ID, COFFI_ID),
                frozenset(),
                previous,
                SETTINGS,
            )
            == 4
        )

    def test_repeating_the_previous_exercise_is_penalised(self) -> None:
        previous = event("ex:1", SIARAD_ID)

        assert (
            score(candidate("ex:1", SIARAD_ID), frozenset(), previous, SETTINGS)
            == 2 - 100
        )

    def test_the_previous_outcome_does_not_matter(self) -> None:
        missed = event("ex:0", SIARAD_ID, outcome=Outcome.MISSED_IT)
        got = event("ex:0", SIARAD_ID)
        option = candidate("ex:1", SIARAD_ID)

        assert score(option, frozenset(), missed, SETTINGS) == score(
            option, frozenset(), got, SETTINGS
        )

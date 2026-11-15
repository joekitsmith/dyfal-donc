from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.scheduler.eligibility import Candidate, candidates, frontier
from tests.unit.engine.scheduler.helpers import (
    COFFI_ID,
    DYSGU_ID,
    MYND_ID,
    SIARAD_ID,
    exercise,
)


class TestFrontier:
    def test_is_the_first_item_when_nothing_is_introduced(
        self, curriculum: Curriculum
    ) -> None:
        assert frontier(curriculum, frozenset()) == SIARAD_ID

    def test_is_the_first_item_in_order_that_is_not_introduced(
        self, curriculum: Curriculum
    ) -> None:
        assert frontier(curriculum, {SIARAD_ID, DYSGU_ID}) == MYND_ID

    def test_there_is_none_when_everything_is_introduced(
        self, curriculum: Curriculum
    ) -> None:
        assert frontier(curriculum, set(curriculum.order)) is None


class TestCandidates:
    def ids(
        self, pool: dict[str, Exercise], introduced: set[str], frontier_item: str | None
    ) -> tuple[str, ...]:
        return tuple(c.exercise_id for c in candidates(pool, introduced, frontier_item))

    def test_an_exercise_of_introduced_items_is_practice(self) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, DYSGU_ID)}

        found = candidates(pool, {SIARAD_ID, DYSGU_ID}, MYND_ID)

        assert found == (Candidate(exercise_id="ex:1", exercise=pool["ex:1"]),)

    def test_the_exercise_introducing_the_frontier_item_qualifies(self) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, DYSGU_ID, new_item=DYSGU_ID)}

        found = candidates(pool, {SIARAD_ID}, DYSGU_ID)

        assert found[0].introduces == DYSGU_ID

    def test_the_introducing_exercise_needs_only_to_name_the_new_item(self) -> None:
        pool = {"ex:1": exercise(new_item=SIARAD_ID)}

        assert candidates(pool, set(), SIARAD_ID)[0].introduces == SIARAD_ID

    def test_an_exercise_with_an_unmet_item_that_is_not_the_frontier_is_out(
        self,
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, COFFI_ID, new_item=COFFI_ID)}

        assert self.ids(pool, {SIARAD_ID}, DYSGU_ID) == ()

    def test_an_exercise_with_two_unmet_items_is_out(self) -> None:
        pool = {"ex:1": exercise(DYSGU_ID, MYND_ID, new_item=DYSGU_ID)}

        assert self.ids(pool, {SIARAD_ID}, DYSGU_ID) == ()

    def test_an_unmet_frontier_item_that_the_exercise_does_not_introduce_is_out(
        self,
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, DYSGU_ID)}

        assert self.ids(pool, {SIARAD_ID}, DYSGU_ID) == ()

    def test_an_exercise_introducing_a_different_item_is_out(self) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, DYSGU_ID, new_item=SIARAD_ID)}

        assert self.ids(pool, {SIARAD_ID}, DYSGU_ID) == ()

    def test_an_exercise_that_introduced_an_item_the_learner_now_knows_is_practice(
        self,
    ) -> None:
        pool = {"ex:1": exercise(SIARAD_ID, new_item=SIARAD_ID)}

        found = candidates(pool, {SIARAD_ID}, DYSGU_ID)

        assert [c.introduces for c in found] == [None]

    def test_an_exercise_with_no_items_is_out(self) -> None:
        assert self.ids({"ex:1": exercise()}, set(), SIARAD_ID) == ()

    def test_candidates_come_in_id_order(self) -> None:
        pool = {
            "ex:b": exercise(SIARAD_ID),
            "ex:c": exercise(SIARAD_ID),
            "ex:a": exercise(SIARAD_ID),
        }

        assert self.ids(pool, {SIARAD_ID}, None) == ("ex:a", "ex:b", "ex:c")

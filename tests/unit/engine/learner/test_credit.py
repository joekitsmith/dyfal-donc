from datetime import timedelta

from engine.learner import (
    Credit,
    FsrsMemoryModel,
    ItemMemory,
    LearnerState,
    Learning,
    Outcome,
    Review,
    ReviewEvent,
    assign_credit,
)
from tests.unit.engine.learner.helpers import START

DAY = timedelta(days=1)


def credit_for(
    memories: dict[str, ItemMemory],
    item_ids: tuple[str, ...],
    outcome: Outcome,
    memory_model: FsrsMemoryModel,
    *,
    new_item: str | None = None,
    review_credit_fraction: float = 1.0,
) -> Credit:
    event = ReviewEvent(
        exercise_id="ex:1",
        item_ids=item_ids,
        new_item=new_item,
        outcome=outcome,
        reviewed_at=START,
    )
    return assign_credit(
        LearnerState(memories=memories), event, memory_model, review_credit_fraction
    )


def reviewed_ago(memory_model: FsrsMemoryModel, ago: timedelta) -> Review:
    return Review(memory=memory_model.initial(START - ago))


class TestCreditForSuccess:
    def test_credits_only_items_that_are_due(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:learning-due": Learning(step_index=0, exercises_until_due=0),
            "lex:learning-waiting": Learning(step_index=0, exercises_until_due=2),
            "lex:review-due": reviewed_ago(memory_model, 3 * DAY),
            "lex:review-not-due": reviewed_ago(memory_model, timedelta(0)),
        }

        credit = credit_for(memories, tuple(memories), Outcome.GOT_IT, memory_model)

        assert credit == Credit(
            learning=("lex:learning-due",), review=("lex:review-due",)
        )

    def test_credits_nothing_when_nothing_is_due(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:a": reviewed_ago(memory_model, timedelta(0)),
        }

        assert (
            credit_for(memories, ("lex:a",), Outcome.GOT_IT, memory_model) == Credit()
        )

    def test_an_item_due_exactly_now_is_credited(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {"lex:a": reviewed_ago(memory_model, 2 * DAY)}

        credit = credit_for(memories, ("lex:a",), Outcome.GOT_IT, memory_model)

        assert credit.review == ("lex:a",)

    def test_does_not_credit_the_new_item(self, memory_model: FsrsMemoryModel) -> None:
        credit = credit_for(
            {}, ("lex:new",), Outcome.GOT_IT, memory_model, new_item="lex:new"
        )

        assert credit == Credit()

    def test_follows_the_order_of_the_event(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:b": Learning(step_index=0, exercises_until_due=0),
            "lex:a": Learning(step_index=0, exercises_until_due=0),
        }

        credit = credit_for(memories, ("lex:b", "lex:a"), Outcome.GOT_IT, memory_model)

        assert credit.learning == ("lex:b", "lex:a")


class TestCreditForSuccessBeforeDue:
    """``review_credit_fraction`` lets a success count part-way through an interval."""

    def test_an_item_part_way_through_its_interval_is_credited(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {"lex:a": reviewed_ago(memory_model, DAY)}

        credit = credit_for(
            memories,
            ("lex:a",),
            Outcome.GOT_IT,
            memory_model,
            review_credit_fraction=0.5,
        )

        assert credit == Credit(review=("lex:a",))

    def test_an_item_earlier_than_that_is_not(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:a": reviewed_ago(memory_model, DAY // 2)
        }

        credit = credit_for(
            memories,
            ("lex:a",),
            Outcome.GOT_IT,
            memory_model,
            review_credit_fraction=0.5,
        )

        assert credit == Credit()

    def test_a_whole_interval_is_the_default(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {"lex:a": reviewed_ago(memory_model, DAY)}

        assert (
            credit_for(memories, ("lex:a",), Outcome.GOT_IT, memory_model) == Credit()
        )

    def test_learning_items_are_unaffected(self, memory_model: FsrsMemoryModel) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:a": Learning(step_index=0, exercises_until_due=2)
        }

        credit = credit_for(
            memories,
            ("lex:a",),
            Outcome.GOT_IT,
            memory_model,
            review_credit_fraction=0.1,
        )

        assert credit == Credit()


class TestCreditForMiss:
    def test_blames_every_learning_item_even_if_not_due(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:waiting": Learning(step_index=1, exercises_until_due=2),
            "lex:due": Learning(step_index=0, exercises_until_due=0),
        }

        credit = credit_for(
            memories, ("lex:waiting", "lex:due"), Outcome.MISSED_IT, memory_model
        )

        assert credit == Credit(learning=("lex:waiting", "lex:due"))

    def test_spares_review_items_when_a_learning_item_is_present(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:learning": Learning(step_index=0, exercises_until_due=1),
            "lex:review": reviewed_ago(memory_model, 5 * DAY),
        }

        credit = credit_for(
            memories, ("lex:learning", "lex:review"), Outcome.MISSED_IT, memory_model
        )

        assert credit == Credit(learning=("lex:learning",))

    def test_credits_nothing_when_only_a_new_item_is_to_blame(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:review": reviewed_ago(memory_model, 5 * DAY)
        }

        credit = credit_for(
            memories,
            ("lex:review", "lex:new"),
            Outcome.MISSED_IT,
            memory_model,
            new_item="lex:new",
        )

        assert credit == Credit()

    def test_blames_the_review_item_least_likely_to_be_recalled(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:recent": reviewed_ago(memory_model, DAY),
            "lex:old": reviewed_ago(memory_model, 6 * DAY),
            "lex:middle": reviewed_ago(memory_model, 3 * DAY),
        }

        credit = credit_for(
            memories,
            ("lex:recent", "lex:old", "lex:middle"),
            Outcome.MISSED_IT,
            memory_model,
        )

        assert credit == Credit(review=("lex:old",))

    def test_blames_a_review_item_that_is_not_yet_due(
        self, memory_model: FsrsMemoryModel
    ) -> None:
        memories: dict[str, ItemMemory] = {"lex:a": reviewed_ago(memory_model, DAY)}

        credit = credit_for(memories, ("lex:a",), Outcome.MISSED_IT, memory_model)

        assert credit == Credit(review=("lex:a",))

    def test_a_tie_goes_to_the_lowest_id(self, memory_model: FsrsMemoryModel) -> None:
        memories: dict[str, ItemMemory] = {
            "lex:b": reviewed_ago(memory_model, 3 * DAY),
            "lex:a": reviewed_ago(memory_model, 3 * DAY),
        }

        credit = credit_for(
            memories, ("lex:b", "lex:a"), Outcome.MISSED_IT, memory_model
        )

        assert credit == Credit(review=("lex:a",))

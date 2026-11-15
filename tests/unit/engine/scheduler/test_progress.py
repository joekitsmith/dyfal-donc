from collections.abc import Mapping
from datetime import timedelta

from engine.curriculum import Curriculum, Lexeme, PartOfSpeech, Pattern, Topic
from engine.exercises import Exercise
from engine.learner import Outcome, ReviewEvent, replay
from engine.scheduler import (
    MAX_SAYABLE_EXERCISES,
    TopicProgress,
    course_progress,
    example_exercise_ids,
    first_met_at,
)
from tests.unit.engine.learner.helpers import START

CAKE = "lex:cake"
CHEESE = "lex:cheese"
RAIN = "lex:rain"
WANT = "pat:want"
SUN = "lex:sun"

COURSE = Curriculum(
    items=(
        Pattern(
            id=WANT,
            template="Dw i'n moyn [NOUN]",
            english="I want [NOUN]",
            slots={"NOUN": PartOfSpeech.NOUN},
            topic="food",
        ),
        Lexeme(
            id=CAKE,
            welsh="teisen",
            english="cake",
            part_of_speech=PartOfSpeech.NOUN,
            topic="food",
        ),
        Lexeme(
            id=CHEESE,
            welsh="caws",
            english="cheese",
            part_of_speech=PartOfSpeech.NOUN,
            topic="food",
        ),
        Lexeme(
            id=RAIN,
            welsh="glaw",
            english="rain",
            part_of_speech=PartOfSpeech.NOUN,
            topic="weather",
        ),
        Lexeme(
            id=SUN,
            welsh="haul",
            english="sun",
            part_of_speech=PartOfSpeech.NOUN,
            topic="weather",
        ),
    ),
    order=(WANT, CAKE, CHEESE, RAIN, SUN),
    topics=(Topic(name="food"), Topic(name="weather")),
)
EXERCISES = {
    "intro-want": Exercise(english="", welsh="", items=(WANT,), new_item=WANT),
    "want-cake": Exercise(english="", welsh="", items=(WANT, CAKE), new_item=CAKE),
    "want-cheese": Exercise(english="", welsh="", items=(WANT, CHEESE)),
    "cake-and-cheese": Exercise(english="", welsh="", items=(WANT, CAKE, CHEESE)),
    "rain": Exercise(english="", welsh="", items=(RAIN,), new_item=RAIN),
    "rain-on-cake": Exercise(english="", welsh="", items=(RAIN, CAKE)),
}
TOPICS = {
    "intro-want": "food",
    "want-cake": "food",
    "want-cheese": "food",
    "cake-and-cheese": "food",
    "rain": "weather",
    "rain-on-cake": "weather",
}


def event(
    exercise_id: str,
    *item_ids: str,
    minutes: int = 0,
    new_item: str | None = None,
    outcome: Outcome = Outcome.GOT_IT,
) -> ReviewEvent:
    return ReviewEvent(
        exercise_id=exercise_id,
        item_ids=item_ids,
        new_item=new_item,
        outcome=outcome,
        reviewed_at=START + timedelta(minutes=minutes),
    )


def progress_of(
    events: tuple[ReviewEvent, ...],
    *,
    exercises: Mapping[str, Exercise] = EXERCISES,
    topics: Mapping[str, str] = TOPICS,
) -> tuple[TopicProgress, ...]:
    return course_progress(COURSE, exercises, topics, replay(events), events)


INTRODUCE_WANT = event("intro-want", WANT, new_item=WANT, minutes=0)
INTRODUCE_RAIN = event("rain", RAIN, new_item=RAIN, minutes=3)
FOOD_STARTED = (
    INTRODUCE_WANT,
    event("want-cake", WANT, CAKE, new_item=CAKE, minutes=1),
    event("want-cheese", WANT, CHEESE, new_item=CHEESE, minutes=2),
)


class TestCourseProgress:
    def test_lists_every_topic_in_teaching_order(self) -> None:
        assert [topic.name for topic in progress_of(())] == ["food", "weather"]

    def test_a_new_learner_has_started_nothing_and_is_at_the_first_topic(self) -> None:
        topics = progress_of(())

        assert [topic.started for topic in topics] == [False, False]
        assert [topic.is_current for topic in topics] == [True, False]
        assert all(
            (topic.words, topic.phrases, topic.sayable_exercise_ids) == ((), (), ())
            for topic in topics
        )

    def test_a_met_item_makes_its_topic_started_and_sorts_into_words_and_phrases(
        self,
    ) -> None:
        food = progress_of(FOOD_STARTED)[0]

        assert food.started is True
        assert food.words == (CAKE, CHEESE)
        assert food.phrases == (WANT,)

    def test_an_item_nobody_has_met_is_not_listed(self) -> None:
        food = progress_of(FOOD_STARTED[:2])[0]

        assert food.words == (CAKE,)

    def test_the_current_topic_is_the_one_holding_the_next_new_item(self) -> None:
        topics = progress_of((*FOOD_STARTED, INTRODUCE_RAIN))

        assert [topic.is_current for topic in topics] == [False, True]
        assert topics[1].started is True

    def test_no_topic_is_current_once_everything_is_met(self) -> None:
        events = (
            *FOOD_STARTED,
            INTRODUCE_RAIN,
            event("sun", SUN, new_item=SUN, minutes=4),
        )

        topics = progress_of(events)

        assert not any(topic.is_current for topic in topics)
        assert all(topic.started for topic in topics)

    def test_counts_every_answer_to_an_exercise_of_the_topic_repeats_included(
        self,
    ) -> None:
        events = (
            *FOOD_STARTED,
            event("want-cake", WANT, CAKE, minutes=3),
            event("want-cake", WANT, CAKE, minutes=4, outcome=Outcome.MISSED_IT),
        )

        assert progress_of(events)[0].exercises_answered == 5

    def test_an_exercise_counts_for_its_registered_topic_not_for_its_items(
        self,
    ) -> None:
        events = (
            *FOOD_STARTED,
            INTRODUCE_RAIN,
            event("rain-on-cake", RAIN, CAKE, minutes=4),
        )

        topics = progress_of(events)

        assert [topic.exercises_answered for topic in topics] == [3, 2]

    def test_ignores_an_answer_to_an_exercise_the_course_no_longer_has(self) -> None:
        events = (*FOOD_STARTED, event("retired", CAKE, minutes=3))

        assert progress_of(events)[0].exercises_answered == 3


class TestSayableExercises:
    def ids(self, events: tuple[ReviewEvent, ...], topic: int = 0) -> tuple[str, ...]:
        return progress_of(events)[topic].sayable_exercise_ids

    def test_an_exercise_that_was_only_missed_is_left_out(self) -> None:
        events = (event("intro-want", WANT, new_item=WANT, outcome=Outcome.MISSED_IT),)

        assert self.ids(events) == ()

    def test_an_exercise_missed_and_then_got_is_included(self) -> None:
        events = (
            event("intro-want", WANT, new_item=WANT, outcome=Outcome.MISSED_IT),
            event("intro-want", WANT, minutes=1),
        )

        assert self.ids(events) == ("intro-want",)

    def test_prefers_more_items_then_the_more_recently_got_right(self) -> None:
        events = (
            *FOOD_STARTED,
            event("cake-and-cheese", WANT, CAKE, CHEESE, minutes=3),
        )

        assert self.ids(events) == (
            "cake-and-cheese",
            "want-cheese",
            "want-cake",
            "intro-want",
        )

    def test_an_exercise_is_listed_under_its_registered_topic_only(self) -> None:
        events = (
            *FOOD_STARTED,
            INTRODUCE_RAIN,
            event("rain-on-cake", RAIN, CAKE, minutes=4),
        )

        assert self.ids(events, 0) == ("want-cheese", "want-cake", "intro-want")
        assert self.ids(events, 1) == ("rain-on-cake", "rain")

    def test_keeps_only_a_few(self) -> None:
        exercises = {
            f"ex-{number}": Exercise(english="", welsh="", items=(CAKE,))
            for number in range(MAX_SAYABLE_EXERCISES + 3)
        }
        events = (
            event("intro-cake", CAKE, new_item=CAKE),
            *(
                event(exercise_id, CAKE, minutes=minutes)
                for minutes, exercise_id in enumerate(exercises, start=1)
            ),
        )

        topics = progress_of(
            events, exercises=exercises, topics=dict.fromkeys(exercises, "food")
        )

        assert len(topics[0].sayable_exercise_ids) == MAX_SAYABLE_EXERCISES


class TestExampleExerciseIds:
    def test_lists_exercises_with_the_item_that_were_got_right_most_recent_first(
        self,
    ) -> None:
        events = (
            *FOOD_STARTED,
            event("cake-and-cheese", WANT, CAKE, CHEESE, minutes=3),
            event("rain-on-cake", RAIN, CAKE, minutes=4),
        )

        assert example_exercise_ids(EXERCISES, events, CAKE, 5) == (
            "rain-on-cake",
            "cake-and-cheese",
            "want-cake",
        )

    def test_leaves_out_an_exercise_that_was_never_got_right(self) -> None:
        events = (event("want-cake", WANT, CAKE, outcome=Outcome.MISSED_IT),)

        assert example_exercise_ids(EXERCISES, events, CAKE, 5) == ()

    def test_stops_at_the_limit(self) -> None:
        events = (
            *FOOD_STARTED,
            event("cake-and-cheese", WANT, CAKE, CHEESE, minutes=3),
        )

        assert example_exercise_ids(EXERCISES, events, CAKE, 2) == (
            "cake-and-cheese",
            "want-cake",
        )

    def test_a_limit_of_zero_gives_none(self) -> None:
        assert example_exercise_ids(EXERCISES, FOOD_STARTED, CAKE, 0) == ()

    def test_leaves_out_an_exercise_the_course_no_longer_has(self) -> None:
        events = (event("retired", CAKE),)

        assert example_exercise_ids(EXERCISES, events, CAKE, 5) == ()


class TestFirstMetAt:
    def test_is_when_the_item_was_first_practised(self) -> None:
        events = (*FOOD_STARTED, event("want-cake", WANT, CAKE, minutes=9))

        assert first_met_at(events, CAKE) == START + timedelta(minutes=1)
        assert first_met_at(events, CHEESE) == START + timedelta(minutes=2)

    def test_is_none_for_an_item_not_met(self) -> None:
        assert first_met_at(FOOD_STARTED, RAIN) is None

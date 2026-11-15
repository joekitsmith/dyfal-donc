from collections.abc import Mapping
from dataclasses import replace
from datetime import timedelta

from engine.curriculum import Curriculum
from engine.exercises import Exercise
from engine.learner import Outcome, replay
from engine.scheduler import NoExerciseReason
from simulation.profile import AVERAGE
from simulation.runner import simulate
from simulation.session import SessionSettings
from tests.unit.simulation.helpers import FORGETFUL, PERFECT, SHORT_RUN


class TestDeterminism:
    def test_the_same_seed_gives_the_same_trace(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        first = simulate(pool, curriculum, AVERAGE, seed=7, session=SHORT_RUN)
        second = simulate(pool, curriculum, AVERAGE, seed=7, session=SHORT_RUN)

        assert first == second

    def test_different_seeds_give_different_traces(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        first = simulate(pool, curriculum, AVERAGE, seed=1, session=SHORT_RUN)
        second = simulate(pool, curriculum, AVERAGE, seed=2, session=SHORT_RUN)

        assert first != second


class TestSessions:
    def test_events_are_chronological_and_replay_without_error(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, AVERAGE, seed=3, session=SHORT_RUN)
        times = [event.reviewed_at for event in trace.events]

        assert times == sorted(times)
        assert replay(trace.events).memories

    def test_there_is_one_snapshot_per_day(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, AVERAGE, seed=3, session=SHORT_RUN)

        assert [snapshot.day for snapshot in trace.snapshots] == list(range(10))

    def test_a_session_does_not_run_past_its_length(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        session = SessionSettings(days=3, session_minutes=2, skip_day_probability=0.0)

        trace = simulate(pool, curriculum, PERFECT, seed=1, session=session)

        for step in trace.steps:
            day_start = session.day_start((step.event.reviewed_at - session.start).days)
            assert step.event.reviewed_at - day_start < timedelta(minutes=2)

    def test_skipped_days_have_no_exercises(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        session = SessionSettings(days=5, skip_day_probability=1.0)

        trace = simulate(pool, curriculum, PERFECT, seed=1, session=session)

        assert trace.steps == ()
        assert all(snapshot.skipped for snapshot in trace.snapshots)

    def test_a_session_with_nothing_to_give_is_cut_short_and_recorded(
        self, curriculum: Curriculum
    ) -> None:
        trace = simulate({}, curriculum, PERFECT, seed=1, session=SHORT_RUN)

        assert trace.steps == ()
        assert len(trace.stalls) == 10
        assert {stall.reason for stall in trace.stalls} == {
            NoExerciseReason.NO_EXERCISE_INTRODUCES_FRONTIER
        }


class TestExtremeLearners:
    def test_a_perfect_memory_never_truly_misses_and_finishes_the_course(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, PERFECT, seed=1, session=SHORT_RUN)

        assert all(step.truly_correct for step in trace.steps)
        assert {item for step in trace.steps for item in step.event.item_ids} == set(
            curriculum.order
        )

    def test_a_learner_who_forgets_everything_stalls_at_the_error_gate(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        trace = simulate(pool, curriculum, FORGETFUL, seed=1, session=SHORT_RUN)

        introduced = sum(step.event.new_item is not None for step in trace.steps)
        assert introduced < len(curriculum.order)
        assert any(not step.truly_correct for step in trace.steps)

    def test_a_learner_who_never_reports_a_miss_hides_every_miss(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        silent = replace(FORGETFUL, under_report_rate=1.0)

        trace = simulate(pool, curriculum, silent, seed=1, session=SHORT_RUN)

        assert any(not step.truly_correct for step in trace.steps)
        assert all(step.event.outcome is Outcome.GOT_IT for step in trace.steps)

    def test_hiding_misses_lets_the_course_move_faster(
        self, pool: Mapping[str, Exercise], curriculum: Curriculum
    ) -> None:
        honest = simulate(pool, curriculum, FORGETFUL, seed=1, session=SHORT_RUN)
        silent = simulate(
            pool,
            curriculum,
            replace(FORGETFUL, under_report_rate=1.0),
            seed=1,
            session=SHORT_RUN,
        )

        assert sum(s.event.new_item is not None for s in silent.steps) > sum(
            s.event.new_item is not None for s in honest.steps
        )

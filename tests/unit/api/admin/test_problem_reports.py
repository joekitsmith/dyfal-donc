import uuid
from datetime import UTC, datetime

from api.course import CourseRelease
from engine.exercises import Exercise
from persistence.database import ProblemReportRecord
from tests.unit.engine.sample_curriculum import SIARAD, curriculum_of
from api.admin.problem_reports import (
    COURSE_CHANGED,
    REMOVED_FROM_COURSE,
    render_reports,
)

HASH = "a" * 64
RELEASE = CourseRelease(
    hash=HASH,
    curriculum=curriculum_of(),
    exercises={"ex:1": Exercise(english="I speak", welsh="Dw i'n siarad", items=())},
    exercise_topics={"ex:1": "spine"},
)
MOMENT = datetime(2026, 1, 1, 9, 30, tzinfo=UTC)


def make_report(**changes: object) -> ProblemReportRecord:
    values: dict[str, object] = {
        "id": 1,
        "user_id": uuid.uuid4(),
        "exercise_id": None,
        "item_id": None,
        "release_hash": HASH,
        "source": "lesson",
        "category": "grammar",
        "description": "Wrong verb",
        "created_at": MOMENT,
        "resolved_at": None,
    }
    return ProblemReportRecord(**{**values, **changes})  # type: ignore[arg-type]


class TestRenderReports:
    def test_says_when_there_are_none(self) -> None:
        assert render_reports((), RELEASE) == "No problem reports"

    def test_shows_a_sentence_with_its_text(self) -> None:
        text = render_reports((make_report(exercise_id="ex:1"),), RELEASE)

        assert "#1  2026-01-01 09:30  lesson  grammar  (open)" in text
        assert "English: I speak" in text
        assert "Welsh:   Dw i'n siarad" in text
        assert "Report:  Wrong verb" in text

    def test_shows_a_word_with_its_text(self) -> None:
        text = render_reports((make_report(item_id=SIARAD.id),), RELEASE)

        assert f"English: {SIARAD.english}" in text
        assert f"Welsh:   {SIARAD.welsh}" in text

    def test_says_when_the_sentence_is_no_longer_in_the_course(self) -> None:
        text = render_reports((make_report(exercise_id="ex:gone"),), RELEASE)

        assert "Exercise ex:gone" in text
        assert REMOVED_FROM_COURSE in text

    def test_says_when_the_course_has_changed(self) -> None:
        text = render_reports((make_report(release_hash="b" * 64),), RELEASE)

        assert COURSE_CHANGED in text

    def test_does_not_say_the_course_changed_when_it_has_not(self) -> None:
        assert COURSE_CHANGED not in render_reports((make_report(),), RELEASE)

    def test_shows_a_resolved_report_as_resolved(self) -> None:
        text = render_reports((make_report(resolved_at=MOMENT),), RELEASE)

        assert "(resolved)" in text

    def test_counts_the_reports_in_each_category(self) -> None:
        reports = (
            make_report(id=1),
            make_report(id=2),
            make_report(id=3, category="mutation"),
        )

        text = render_reports(reports, RELEASE)

        assert text.endswith("By category:\n    2  grammar\n    1  mutation")

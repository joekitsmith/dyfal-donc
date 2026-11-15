import argparse
from collections import Counter
from collections.abc import Callable, Sequence
from datetime import UTC, datetime

from api.course import CourseRelease, load_course_release
from api.settings import DEFAULT_CURRICULUM_DIRECTORY
from engine.curriculum import Lexeme
from persistence.database import (
    DatabaseSettings,
    ProblemReportRecord,
    UnitOfWork,
    create_database_engine,
    create_session_factory,
)
from persistence.database.errors import ProblemReportNotFoundError

REMOVED_FROM_COURSE = "  (No longer in the course: it was removed or renamed)"
COURSE_CHANGED = "  (The course has changed since this was reported)"


def render_reports(
    reports: Sequence[ProblemReportRecord], release: CourseRelease
) -> str:
    """Each report as a block, then how many there are of each category."""
    if not reports:
        return "No problem reports"

    blocks = (_render_report(report, release) for report in reports)
    return "\n\n".join((*blocks, _render_counts(reports)))


def main(
    argv: Sequence[str] | None = None,
    clock: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> None:
    arguments = _build_parser().parse_args(argv)
    if arguments.resolve is not None and arguments.all:
        raise SystemExit("--all and --resolve cannot be used together")

    engine = create_database_engine(DatabaseSettings().url)
    try:
        with create_session_factory(engine)() as session:
            unit_of_work = UnitOfWork(session)
            if arguments.resolve is not None:
                print(_resolve(unit_of_work, arguments.resolve, clock()))
                return

            release = load_course_release(DEFAULT_CURRICULUM_DIRECTORY)
            reports = unit_of_work.problem_reports.list(include_resolved=arguments.all)
            print(render_reports(reports, release))
    finally:
        engine.dispose()


def _resolve(unit_of_work: UnitOfWork, report_id: int, now: datetime) -> str:
    try:
        changed = unit_of_work.problem_reports.resolve(report_id, now)
    except ProblemReportNotFoundError as error:
        raise SystemExit(str(error)) from error

    unit_of_work.commit()
    if not changed:
        return f"Problem report {report_id} was already resolved"

    return f"Resolved problem report {report_id}"


def _render_report(report: ProblemReportRecord, release: CourseRelease) -> str:
    status = "open" if report.resolved_at is None else "resolved"
    lines = [
        f"#{report.id}  {report.created_at:%Y-%m-%d %H:%M}  {report.source}  "
        f"{report.category}  ({status})",
        *_render_subject(report, release),
    ]
    if report.release_hash != release.hash:
        lines.append(COURSE_CHANGED)

    lines.append(f"  Report:  {report.description}")

    return "\n".join(lines)


def _render_subject(
    report: ProblemReportRecord, release: CourseRelease
) -> tuple[str, ...]:
    if report.exercise_id is not None:
        exercise = release.exercises.get(report.exercise_id)
        if exercise is None:
            return (f"  Exercise {report.exercise_id}", REMOVED_FROM_COURSE)

        return (f"  English: {exercise.english}", f"  Welsh:   {exercise.welsh}")

    if report.item_id is not None:
        item = next(
            (item for item in release.curriculum.items if item.id == report.item_id),
            None,
        )
        if item is None:
            return (f"  Item {report.item_id}", REMOVED_FROM_COURSE)

        welsh = item.welsh if isinstance(item, Lexeme) else item.template
        return (f"  English: {item.english}", f"  Welsh:   {welsh}")

    return ()


def _render_counts(reports: Sequence[ProblemReportRecord]) -> str:
    counts = Counter(report.category for report in reports)
    lines = (f"  {count:>3}  {category}" for category, count in counts.most_common())

    return "\n".join(("By category:", *lines))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="problem-reports",
        description="List the problems learners have reported, oldest first.",
    )
    parser.add_argument(
        "--all", action="store_true", help="include reports that are resolved"
    )
    parser.add_argument(
        "--resolve", type=int, metavar="ID", help="mark a report resolved"
    )

    return parser


if __name__ == "__main__":
    main()

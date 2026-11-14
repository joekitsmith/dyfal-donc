import pytest

from tests.integration.engine.exercises.exercise_fixtures import (
    ExerciseFixture,
    curriculum_with_fixture_only_patterns,
    load_fixtures,
    validate_fixture,
)

FIXTURES = load_fixtures()


class TestExerciseFixtures:
    @pytest.mark.parametrize("fixture", FIXTURES, ids=lambda fixture: fixture.id)
    def test_validation_reports_exactly_the_expected_issues(
        self, fixture: ExerciseFixture
    ) -> None:
        result = validate_fixture(fixture, curriculum_with_fixture_only_patterns())

        assert tuple(type(issue).__name__ for issue in result.issues) == fixture.expect

    @pytest.mark.parametrize(
        "fixture",
        [fixture for fixture in FIXTURES if fixture.mutations],
        ids=lambda fixture: fixture.id,
    )
    def test_mutated_items_are_recognised_with_their_mutation(
        self, fixture: ExerciseFixture
    ) -> None:
        result = validate_fixture(fixture, curriculum_with_fixture_only_patterns())

        detected = {item.item_id: item.mutation for item in result.detected}
        assert {
            item_id: detected.get(item_id) for item_id in fixture.mutations
        } == dict(fixture.mutations)

    def test_fixtures_cover_valid_and_invalid_exercises(self) -> None:
        assert any(not fixture.expect for fixture in FIXTURES)
        assert any(fixture.expect for fixture in FIXTURES)
        assert len({fixture.id for fixture in FIXTURES}) == len(FIXTURES)

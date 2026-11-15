import uuid
from datetime import UTC, datetime
from pathlib import Path

from api.course import load_course_release
from api.mappings import to_learner_response, to_add_learner
from persistence.database import LearnerRecord


class TestToAddLearner:
    def test_starts_the_learner_on_the_release_hash(
        self, curriculum_directory: Path
    ) -> None:
        release = load_course_release(curriculum_directory)

        assert to_add_learner(release).course_release == release.hash


class TestToLearnerResponse:
    def test_maps_every_field(self) -> None:
        record = LearnerRecord(
            id=uuid.uuid4(),
            course_release="hash",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
        )

        response = to_learner_response(record)

        assert response.id == record.id
        assert response.course_release == "hash"
        assert response.created_at == record.created_at

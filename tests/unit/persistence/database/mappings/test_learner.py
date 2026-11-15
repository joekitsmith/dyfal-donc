import uuid

from persistence.database import models
from persistence.database.mappings import to_learner_record
from tests.unit.persistence.database.mappings.conftest import MOMENT


class TestToLearnerRecord:
    def test_maps_every_field(self) -> None:
        row = models.Learner(id=uuid.uuid4(), course_release="hash", created_at=MOMENT)

        record = to_learner_record(row)

        assert record.id == row.id
        assert record.course_release == "hash"
        assert record.created_at == MOMENT

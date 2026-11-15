import uuid
from pathlib import Path

from api.course import load_course_release
from api.mappings import to_add_learner


class TestToAddLearner:
    def test_starts_the_users_learner_on_the_release_hash(
        self, curriculum_directory: Path
    ) -> None:
        release = load_course_release(curriculum_directory)
        user_id = uuid.uuid4()

        command = to_add_learner(user_id, release)

        assert command.user_id == user_id
        assert command.course_release == release.hash

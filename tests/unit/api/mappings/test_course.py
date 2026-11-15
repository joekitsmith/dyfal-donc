from pathlib import Path

from api.course import load_course_release
from api.mappings import to_course_response


class TestToCourseResponse:
    def test_reports_the_release_the_size_and_the_topics(
        self, curriculum_directory: Path
    ) -> None:
        release = load_course_release(curriculum_directory)

        response = to_course_response(release)

        assert response.release == release.hash
        assert response.item_count == len(release.curriculum.items)
        assert response.topics[0].name == "spine"
        assert {topic.name: topic.requires for topic in response.topics}["time"] == (
            "spine",
            "places",
        )

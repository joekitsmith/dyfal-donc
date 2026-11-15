from pathlib import Path

from api.controllers import describe_course
from api.course import load_course_release


class TestDescribeCourse:
    def test_reports_the_release_and_the_size_of_the_course(
        self, curriculum_directory: Path
    ) -> None:
        release = load_course_release(curriculum_directory)

        response = describe_course(release)

        assert response.release == release.hash
        assert response.item_count == len(release.curriculum.items)

    def test_lists_the_topics_with_what_they_require(
        self, curriculum_directory: Path
    ) -> None:
        response = describe_course(load_course_release(curriculum_directory))

        by_name = {topic.name: topic.requires for topic in response.topics}

        assert response.topics[0].name == "spine"
        assert by_name["time"] == ("spine", "places")

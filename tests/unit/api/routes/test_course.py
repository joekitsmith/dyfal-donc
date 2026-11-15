from pathlib import Path

from fastapi.testclient import TestClient

from api.course import content_hash


class TestCourse:
    def test_describes_the_course_release(
        self, client: TestClient, curriculum_directory: Path
    ) -> None:
        body = client.get("/course").json()

        assert body["release"] == content_hash(curriculum_directory)
        assert body["item_count"] > 0

    def test_lists_the_topics_in_teaching_order(self, client: TestClient) -> None:
        topics = client.get("/course").json()["topics"]

        assert topics[0] == {"name": "spine", "requires": []}
        assert {"name": "time", "requires": ["spine", "places"]} in topics

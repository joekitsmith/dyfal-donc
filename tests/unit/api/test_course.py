from pathlib import Path

from api.course import content_hash, load_course_release


class TestContentHash:
    def test_is_the_same_for_the_same_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.yaml").write_text("one")

        assert content_hash(tmp_path) == content_hash(tmp_path)

    def test_changes_when_a_file_changes(self, tmp_path: Path) -> None:
        (tmp_path / "a.yaml").write_text("one")
        before = content_hash(tmp_path)

        (tmp_path / "a.yaml").write_text("two")

        assert content_hash(tmp_path) != before

    def test_changes_when_a_file_is_renamed(self, tmp_path: Path) -> None:
        (tmp_path / "a.yaml").write_text("one")
        before = content_hash(tmp_path)

        (tmp_path / "a.yaml").rename(tmp_path / "b.yaml")

        assert content_hash(tmp_path) != before

    def test_includes_files_in_subdirectories(self, tmp_path: Path) -> None:
        (tmp_path / "nested").mkdir()
        before = content_hash(tmp_path)

        (tmp_path / "nested" / "a.yaml").write_text("one")

        assert content_hash(tmp_path) != before

    def test_does_not_confuse_where_a_name_ends_and_content_starts(
        self, tmp_path: Path
    ) -> None:
        (tmp_path / "ab").write_text("c")
        first = content_hash(tmp_path)
        (tmp_path / "ab").unlink()

        (tmp_path / "a").write_text("bc")

        assert content_hash(tmp_path) != first


class TestLoadCourseRelease:
    def test_loads_the_course_and_hashes_it(self, curriculum_directory: Path) -> None:
        release = load_course_release(curriculum_directory)

        assert release.hash == content_hash(curriculum_directory)
        assert release.curriculum.topics[0].name == "spine"

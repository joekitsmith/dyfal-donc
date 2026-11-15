from collections.abc import Callable
from pathlib import Path

import pytest

from engine.exercises import (
    Exercise,
    ExerciseError,
    exercise_pool,
    load_exercises,
)

VALID = """\
- id: want-coffee
  english: I want coffee
  welsh: Dw i'n moyn coffi
  items: [pat:dw-in-moyn-noun, lex:coffi]
  new_item: lex:coffi

- id: speak
  english: To speak
  welsh: Siarad
  items: [lex:siarad]
"""

Writer = Callable[[str, str], Path]


@pytest.fixture
def write_pack(tmp_path: Path) -> Writer:
    def write(name: str, content: str) -> Path:
        (tmp_path / name).write_text(content, encoding="utf-8")
        return tmp_path

    return write


class TestLoadExercises:
    def test_loads_exercises_with_their_pack(self, write_pack: Writer) -> None:
        directory = write_pack("spine.yaml", VALID)

        first, second = load_exercises(directory)

        assert first.id == "want-coffee"
        assert first.pack == "spine"
        assert first.exercise == Exercise(
            english="I want coffee",
            welsh="Dw i'n moyn coffi",
            items=("pat:dw-in-moyn-noun", "lex:coffi"),
            new_item="lex:coffi",
        )
        assert second.exercise.new_item is None

    def test_reads_every_pack_in_file_name_order(self, write_pack: Writer) -> None:
        write_pack("weather.yaml", VALID.split("\n\n")[1].replace("speak", "rain"))
        directory = write_pack("spine.yaml", VALID.split("\n\n")[0])

        entries = load_exercises(directory)

        assert [(entry.pack, entry.id) for entry in entries] == [
            ("spine", "want-coffee"),
            ("weather", "rain"),
        ]

    def test_ignores_files_that_are_not_yaml(self, write_pack: Writer) -> None:
        write_pack("notes.md", "Not exercises")
        directory = write_pack("spine.yaml", VALID)

        assert len(load_exercises(directory)) == 2

    def test_a_missing_directory_is_an_error(self, tmp_path: Path) -> None:
        with pytest.raises(ExerciseError, match="Missing directory"):
            load_exercises(tmp_path / "nothing")

    def test_the_top_level_must_be_a_list(self, write_pack: Writer) -> None:
        with pytest.raises(ExerciseError, match="Expected a YAML list"):
            load_exercises(write_pack("spine.yaml", "id: x\n"))

    def test_invalid_yaml_is_an_error(self, write_pack: Writer) -> None:
        with pytest.raises(ExerciseError, match="Invalid YAML"):
            load_exercises(write_pack("spine.yaml", "- [unclosed\n"))

    def test_an_entry_must_be_a_mapping(self, write_pack: Writer) -> None:
        with pytest.raises(
            ExerciseError, match=r"spine\.yaml\[0\]: Expected a mapping"
        ):
            load_exercises(write_pack("spine.yaml", "- just text\n"))

    def test_an_unknown_field_names_the_exercise(self, write_pack: Writer) -> None:
        content = VALID.replace("  new_item: lex:coffi\n", "  typo: 1\n")

        with pytest.raises(
            ExerciseError,
            match=r"spine\.yaml \(want-coffee\): Unknown field\(s\): typo",
        ):
            load_exercises(write_pack("spine.yaml", content))

    def test_a_missing_field_names_the_exercise(self, write_pack: Writer) -> None:
        content = "- id: broken\n  english: Hello\n"

        with pytest.raises(ExerciseError, match=r"\(broken\): welsh"):
            load_exercises(write_pack("spine.yaml", content))

    @pytest.mark.parametrize("bad_id", ("Upper", "has space", "-leading", ""))
    def test_an_invalid_id_is_an_error(self, write_pack: Writer, bad_id: str) -> None:
        content = VALID.replace("want-coffee", f'"{bad_id}"')

        with pytest.raises(ExerciseError, match="Invalid id"):
            load_exercises(write_pack("spine.yaml", content))

    def test_blank_welsh_is_an_error(self, write_pack: Writer) -> None:
        content = VALID.replace("Dw i'n moyn coffi", '" "')

        with pytest.raises(ExerciseError, match="Welsh must not be blank"):
            load_exercises(write_pack("spine.yaml", content))

    def test_an_exercise_with_no_items_is_an_error(self, write_pack: Writer) -> None:
        content = "- id: empty\n  english: Hello\n  welsh: Helo\n"

        with pytest.raises(ExerciseError, match="At least one item is required"):
            load_exercises(write_pack("spine.yaml", content))

    def test_a_new_item_alone_counts_as_an_item(self, write_pack: Writer) -> None:
        content = (
            "- id: only-new\n  english: Hello\n  welsh: Helo\n  new_item: lex:helo\n"
        )

        (entry,) = load_exercises(write_pack("spine.yaml", content))

        assert entry.exercise.declared_items == ("lex:helo",)

    def test_duplicate_ids_across_packs_are_an_error(self, write_pack: Writer) -> None:
        write_pack("spine.yaml", VALID)

        with pytest.raises(ExerciseError, match="Duplicate exercise ids: speak"):
            load_exercises(write_pack("weather.yaml", VALID.split("\n\n")[1]))


class TestExercisePool:
    def test_maps_each_id_to_its_exercise(self, write_pack: Writer) -> None:
        entries = load_exercises(write_pack("spine.yaml", VALID))

        pool = exercise_pool(entries)

        assert tuple(pool) == ("want-coffee", "speak")
        assert pool["speak"] == entries[1].exercise

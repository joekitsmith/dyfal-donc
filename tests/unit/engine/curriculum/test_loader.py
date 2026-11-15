from pathlib import Path

import pytest

from engine.curriculum import (
    CurriculumError,
    Topic,
    PartOfSpeech,
    Lexeme,
    Pattern,
    load_curriculum,
)
from tests.unit.engine.curriculum.conftest import YAML_LEXEMES, CurriculumWriter


class TestLoader:
    def test_loads(self, write_curriculum: CurriculumWriter) -> None:
        c = load_curriculum(write_curriculum())
        assert c.order == ("lex:siarad", "pat:dw-in")
        assert isinstance(c.get("pat:dw-in"), Pattern)

    def test_an_empty_directory_has_no_topics_file(self, tmp_path: Path) -> None:
        with pytest.raises(CurriculumError, match="Missing file"):
            load_curriculum(tmp_path)

    def test_missing_lexemes_directory(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum()
        (directory / "lexemes" / "spine.yaml").unlink()
        (directory / "lexemes").rmdir()

        with pytest.raises(CurriculumError, match="Missing directory"):
            load_curriculum(directory)

    def test_missing_topics_file(self, write_curriculum: CurriculumWriter) -> None:
        directory = write_curriculum()
        (directory / "topics.yaml").unlink()

        with pytest.raises(CurriculumError, match="Missing file"):
            load_curriculum(directory)

    def test_missing_order_directory(self, write_curriculum: CurriculumWriter) -> None:
        directory = write_curriculum()
        (directory / "order" / "spine.yaml").unlink()
        (directory / "order").rmdir()

        with pytest.raises(CurriculumError, match="Missing directory"):
            load_curriculum(directory)

    def test_bad_item_names_file_and_id(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        bad = "- id: lex:siarad\n  welsh: siarad\n  english: x\n  part_of_speech: nonsense\n"
        with pytest.raises(
            CurriculumError, match=r"spine\.yaml \(lex:siarad\): part_of_speech"
        ):
            load_curriculum(write_curriculum(lexemes=bad))

    def test_unknown_field_rejected(self, write_curriculum: CurriculumWriter) -> None:
        typo = (
            "- id: lex:siarad\n  welsh: siarad\n  english: x\n"
            "  part_of_speech: verb\n  typo: 1\n"
        )
        with pytest.raises(
            CurriculumError, match=r"lex:siarad\): Unknown field\(s\): typo"
        ):
            load_curriculum(write_curriculum(lexemes=typo))

    def test_domain_error_names_file_and_id(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        bad = (
            "- id: lex:siarad\n  welsh: siarad\n  english: x\n"
            "  part_of_speech: verb\n  gender: m\n"
        )
        with pytest.raises(
            CurriculumError,
            match=r"spine\.yaml \(lex:siarad\).*Gender is only valid for nouns",
        ):
            load_curriculum(write_curriculum(lexemes=bad))

    def test_slots_parse_to_part_of_speech(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        pattern = load_curriculum(write_curriculum()).get("pat:dw-in")
        assert isinstance(pattern, Pattern)
        assert pattern.slots == {"VERB": PartOfSpeech.VERB}

    def test_top_level_must_be_list(self, write_curriculum: CurriculumWriter) -> None:
        with pytest.raises(CurriculumError, match="Expected a YAML list"):
            load_curriculum(write_curriculum(order="a: b\n"))

    def test_order_entries_must_be_strings(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        with pytest.raises(CurriculumError, match="Every entry must be an item id"):
            load_curriculum(write_curriculum(order="- 1\n"))

    def test_cross_file_validation(self, write_curriculum: CurriculumWriter) -> None:
        with pytest.raises(CurriculumError, match="comes before its prerequisite"):
            load_curriculum(write_curriculum(order="- pat:dw-in\n- lex:siarad\n"))


class TestLoaderForms:
    def test_forms_and_homographs_parse_to_tuples(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        lexemes = (
            "- id: lex:siarad\n  welsh: siarad\n  english: x\n"
            "  part_of_speech: verb\n  forms: [siaradodd]\n"
        )
        lexeme = load_curriculum(write_curriculum(lexemes=lexemes)).get("lex:siarad")
        assert isinstance(lexeme, Lexeme)
        assert lexeme.forms == ("siaradodd",)


GLAW = "- id: lex:glaw\n  welsh: glaw\n  english: rain\n  part_of_speech: noun\n"
WITH_WEATHER = "- name: spine\n- name: weather\n  requires: [spine]\n"


class TestLoaderTopics:
    def test_the_topic_of_an_item_is_the_name_of_its_file(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "- lex:glaw\n"},
            topics=WITH_WEATHER,
        )

        curriculum = load_curriculum(directory)

        assert curriculum.get("lex:glaw").topic == "weather"
        assert curriculum.get("lex:siarad").topic == "spine"
        assert curriculum.get("pat:dw-in").topic == "spine"

    def test_the_order_is_one_topic_after_another_in_the_topic_sequence(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "- lex:glaw\n"},
            topics=WITH_WEATHER,
        )

        assert load_curriculum(directory).order == (
            "lex:siarad",
            "pat:dw-in",
            "lex:glaw",
        )

    def test_the_topic_sequence_decides_the_order_of_topics(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "- lex:glaw\n"},
            topics="- name: weather\n- name: spine\n",
        )

        assert load_curriculum(directory).order[0] == "lex:glaw"

    def test_the_spine_file_is_read_before_the_others(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"aaa": GLAW},
            extra_orders={"aaa": "- lex:glaw\n"},
            topics="- name: aaa\n- name: spine\n",
        )

        curriculum = load_curriculum(directory)

        assert [item.id for item in curriculum.items if isinstance(item, Lexeme)] == [
            "lex:siarad",
            "lex:glaw",
        ]

    def test_topics_are_read_with_what_they_require(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "- lex:glaw\n"},
            topics=WITH_WEATHER,
        )

        assert load_curriculum(directory).topics == (
            Topic(name="spine"),
            Topic(name="weather", requires=("spine",)),
        )

    def test_a_topic_key_in_a_file_is_rejected(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        lexemes = YAML_LEXEMES + "  topic: weather\n"

        with pytest.raises(
            CurriculumError,
            match=r"spine\.yaml \(lex:siarad\): The topic comes from the file name",
        ):
            load_curriculum(write_curriculum(lexemes=lexemes))

    def test_an_invalid_file_name_names_the_file_and_item(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"Weather": GLAW},
            extra_orders={"Weather": "- lex:glaw\n"},
            topics="- name: spine\n",
        )

        with pytest.raises(
            CurriculumError, match=r"Weather\.yaml \(lex:glaw\): .*Invalid topic"
        ):
            load_curriculum(directory)

    def test_files_that_are_not_yaml_are_ignored(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum()
        (directory / "lexemes" / "notes.md").write_text("Not items", encoding="utf-8")
        (directory / "order" / "notes.md").write_text("Not an order", encoding="utf-8")

        assert load_curriculum(directory).order == ("lex:siarad", "pat:dw-in")

    def test_an_item_in_the_wrong_topics_order_file_is_an_error(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "- lex:glaw\n- lex:siarad\n"},
            topics=WITH_WEATHER,
        )

        with pytest.raises(
            CurriculumError,
            match=r"weather\.yaml: lex:siarad belongs to topic spine, not weather",
        ):
            load_curriculum(directory)

    def test_an_order_file_for_an_unknown_topic_is_an_error(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(extra_orders={"weather": "- lex:glaw\n"})

        with pytest.raises(
            CurriculumError, match=r"weather\.yaml: Unknown topic weather"
        ):
            load_curriculum(directory)

    def test_a_topic_without_an_order_file_is_an_error(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW}, topics=WITH_WEATHER
        )

        with pytest.raises(CurriculumError, match="Missing file"):
            load_curriculum(directory)

    def test_an_item_in_no_order_file_is_an_error(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        directory = write_curriculum(
            extra_lexemes={"weather": GLAW},
            extra_orders={"weather": "[]\n"},
            topics=WITH_WEATHER,
        )

        with pytest.raises(CurriculumError, match="lex:glaw is missing from order"):
            load_curriculum(directory)

    def test_a_topic_needs_a_name(self, write_curriculum: CurriculumWriter) -> None:
        with pytest.raises(CurriculumError, match="A topic needs a name"):
            load_curriculum(write_curriculum(topics="- requires: []\n"))

    def test_a_topic_with_an_unknown_field_is_an_error(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        with pytest.raises(
            CurriculumError, match=r"\(spine\): Unknown field\(s\): typo"
        ):
            load_curriculum(write_curriculum(topics="- name: spine\n  typo: 1\n"))

    def test_requires_must_be_a_list_of_names(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        with pytest.raises(CurriculumError, match="Requires must be a list"):
            load_curriculum(write_curriculum(topics="- name: spine\n  requires: 1\n"))

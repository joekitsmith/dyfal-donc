from pathlib import Path

import pytest

from engine.curriculum import (
    CurriculumError,
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

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(CurriculumError, match="Missing file"):
            load_curriculum(tmp_path)

    def test_bad_item_names_file_and_id(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        bad = "- id: lex:siarad\n  welsh: siarad\n  english: x\n  part_of_speech: nonsense\n"
        with pytest.raises(
            CurriculumError, match=r"lexemes\.yaml \(lex:siarad\): part_of_speech"
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
            match=r"lexemes\.yaml \(lex:siarad\).*Gender is only valid for nouns",
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


class TestLoaderTopics:
    def test_a_topic_is_read_from_the_file(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        lexemes = YAML_LEXEMES + "  topic: weather\n"

        curriculum = load_curriculum(write_curriculum(lexemes=lexemes))

        assert curriculum.get("lex:siarad").topic == "weather"
        assert curriculum.get("pat:dw-in").topic == "spine"

    def test_an_invalid_topic_names_the_file_and_item(
        self, write_curriculum: CurriculumWriter
    ) -> None:
        lexemes = YAML_LEXEMES + "  topic: Weather\n"

        with pytest.raises(
            CurriculumError, match=r"lexemes\.yaml \(lex:siarad\): .*Invalid topic"
        ):
            load_curriculum(write_curriculum(lexemes=lexemes))

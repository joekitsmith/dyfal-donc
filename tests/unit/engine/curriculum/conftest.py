from collections.abc import Mapping
from pathlib import Path
from typing import Protocol

import pytest

YAML_PATTERNS = """\
- id: pat:dw-in
  template: "Dw i'n [VERB]"
  english: "I am [VERB]ing"
  slots: {VERB: verb}
  prerequisites: [lex:siarad]
"""
YAML_LEXEMES = """\
- id: lex:siarad
  welsh: siarad
  english: to speak
  part_of_speech: verb
"""
YAML_ORDER = "- lex:siarad\n- pat:dw-in\n"
YAML_TOPICS = "- name: spine\n"


class CurriculumWriter(Protocol):
    def __call__(
        self,
        *,
        patterns: str = YAML_PATTERNS,
        lexemes: str = YAML_LEXEMES,
        order: str = YAML_ORDER,
        topics: str = YAML_TOPICS,
        extra_lexemes: Mapping[str, str] | None = None,
        extra_orders: Mapping[str, str] | None = None,
    ) -> Path: ...


@pytest.fixture
def write_curriculum(tmp_path: Path) -> CurriculumWriter:
    """Write a small valid curriculum into ``tmp_path``; override any file, or add topics."""

    def write(
        *,
        patterns: str = YAML_PATTERNS,
        lexemes: str = YAML_LEXEMES,
        order: str = YAML_ORDER,
        topics: str = YAML_TOPICS,
        extra_lexemes: Mapping[str, str] | None = None,
        extra_orders: Mapping[str, str] | None = None,
    ) -> Path:
        (tmp_path / "patterns").mkdir()
        (tmp_path / "lexemes").mkdir()
        (tmp_path / "patterns" / "spine.yaml").write_text(patterns, encoding="utf-8")
        (tmp_path / "lexemes" / "spine.yaml").write_text(lexemes, encoding="utf-8")
        for topic, content in (extra_lexemes or {}).items():
            (tmp_path / "lexemes" / f"{topic}.yaml").write_text(
                content, encoding="utf-8"
            )

        (tmp_path / "order").mkdir()
        (tmp_path / "order" / "spine.yaml").write_text(order, encoding="utf-8")
        for topic, content in (extra_orders or {}).items():
            (tmp_path / "order" / f"{topic}.yaml").write_text(content, encoding="utf-8")

        (tmp_path / "topics.yaml").write_text(topics, encoding="utf-8")
        return tmp_path

    return write

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


class CurriculumWriter(Protocol):
    def __call__(
        self,
        *,
        patterns: str = YAML_PATTERNS,
        lexemes: str = YAML_LEXEMES,
        order: str = YAML_ORDER,
    ) -> Path: ...


@pytest.fixture
def write_curriculum(tmp_path: Path) -> CurriculumWriter:
    """Write a small valid curriculum into ``tmp_path``; override any file."""

    def write(
        *,
        patterns: str = YAML_PATTERNS,
        lexemes: str = YAML_LEXEMES,
        order: str = YAML_ORDER,
    ) -> Path:
        (tmp_path / "patterns.yaml").write_text(patterns, encoding="utf-8")
        (tmp_path / "lexemes.yaml").write_text(lexemes, encoding="utf-8")
        (tmp_path / "order.yaml").write_text(order, encoding="utf-8")
        return tmp_path

    return write

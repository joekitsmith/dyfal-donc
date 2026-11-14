from pathlib import Path

import pytest

from cymraeg import Mutation
from evals.gold import GoldSetError, Tag, load_gold_sentences

VALID = """\
- id: like-the-welsh
  welsh: "Dw i'n hoffi'r Gymraeg"
  english: I like Welsh
  tags: [clitic, mutation]
  patterns: [pat:dw-in-hoffi-r]
  tokens:
    - {text: Dw, lemma: bod}
    - {text: "'r", lemma: y}
    - {text: Gymraeg, lemma: Cymraeg, item: "lex:cymraeg", mutation: soft}
"""


def write(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "sentences.yaml"
    path.write_text(content, encoding="utf-8")
    return path


class TestLoadGoldSentences:
    def test_loads_sentences_with_typed_fields(self, tmp_path: Path) -> None:
        (sentence,) = load_gold_sentences(write(tmp_path, VALID))
        assert sentence.tags == (Tag.CLITIC, Tag.MUTATION)
        assert sentence.patterns == ("pat:dw-in-hoffi-r",)
        assert sentence.tokens[-1].mutation == Mutation.SOFT
        assert sentence.tokens[-1].item == "lex:cymraeg"
        assert sentence.tokens[0].item is None

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(GoldSetError, match="Missing file"):
            load_gold_sentences(tmp_path / "nothing.yaml")

    def test_top_level_must_be_a_list(self, tmp_path: Path) -> None:
        with pytest.raises(GoldSetError, match="Expected a YAML list"):
            load_gold_sentences(write(tmp_path, "id: x\n"))

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        with pytest.raises(GoldSetError, match="Invalid YAML"):
            load_gold_sentences(write(tmp_path, "- [unclosed\n"))

    def test_unknown_field_names_the_sentence(self, tmp_path: Path) -> None:
        content = VALID + "  typo: 1\n"
        with pytest.raises(
            GoldSetError, match=r"like-the-welsh\): Unknown field\(s\): typo"
        ):
            load_gold_sentences(write(tmp_path, content))

    def test_bad_mutation_names_the_sentence_and_field(self, tmp_path: Path) -> None:
        content = VALID.replace("mutation: soft", "mutation: nonsense")
        with pytest.raises(
            GoldSetError, match=r"like-the-welsh\): tokens\.2\.mutation"
        ):
            load_gold_sentences(write(tmp_path, content))

    def test_domain_error_names_the_sentence(self, tmp_path: Path) -> None:
        content = VALID.replace("tags: [clitic, mutation]", "tags: []")
        with pytest.raises(
            GoldSetError, match=r"like-the-welsh\).*At least one tag is required"
        ):
            load_gold_sentences(write(tmp_path, content))

    def test_duplicate_ids_are_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(
            GoldSetError, match="Duplicate sentence ids: like-the-welsh"
        ):
            load_gold_sentences(write(tmp_path, VALID + "\n" + VALID))

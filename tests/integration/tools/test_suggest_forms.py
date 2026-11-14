import pytest

from cymraeg import RuleLemmatiser, SimplemmaLemmatiser
from engine.curriculum import load_curriculum
from engine.detection import CurriculumIndex
from tools.suggest_forms import CURRICULUM_DIRECTORY, collect_suggestions

INDEX = CurriculumIndex.from_curriculum(load_curriculum(CURRICULUM_DIRECTORY))


class TestSuggestFormsOnTheSeedCurriculum:
    def test_rule_lemmatiser_suggests_no_inflected_forms(self) -> None:
        groups = collect_suggestions(["Gwelais i e neithiwr"], INDEX, RuleLemmatiser())

        assert groups == ()

    def test_simplemma_suggests_the_undeclared_inflected_form(self) -> None:
        pytest.importorskip("simplemma")
        groups = collect_suggestions(
            ["Gwelais i e neithiwr", "Dysgais i Gymraeg"], INDEX, SimplemmaLemmatiser()
        )

        assert {(group.form, group.item_id) for group in groups} >= {
            ("gwelais", "lex:gweld"),
            ("dysgais", "lex:dysgu"),
        }

    def test_sentences_the_curriculum_already_understands_give_nothing(self) -> None:
        pytest.importorskip("simplemma")
        groups = collect_suggestions(
            ["Dw i'n dysgu Cymraeg heddi"], INDEX, SimplemmaLemmatiser()
        )

        assert groups == ()

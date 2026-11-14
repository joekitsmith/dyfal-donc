import sys
from pathlib import Path


import pytest

from cymraeg import Mutation
from engine.detection import CurriculumIndex
from tests.fake_lemmatisers import FixedLemmatiser
from tests.unit.engine.sample_curriculum import GWELD, STANDARD_ITEMS, curriculum_of
from tools.suggest_forms import (
    SuggestionGroup,
    collect_suggestions,
    main,
    render_suggestions,
)

INDEX = CurriculumIndex.from_curriculum(curriculum_of((*STANDARD_ITEMS, GWELD)))
GWELD_GROUP = SuggestionGroup(
    form="gwelais",
    item_id="lex:gweld",
    english="to see",
    lemma="gweld",
    mutation=None,
    sentences=("Gwelais i", "Gwelais e"),
)


class TestCollectSuggestions:
    def test_form_suggested_in_several_sentences_is_merged(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld",)})

        (group,) = collect_suggestions(
            ["Gwelais i", "Gwelais e", "Gwelais i"], INDEX, lemmatiser
        )

        assert group.form == "gwelais"
        assert group.sentences == ("Gwelais i", "Gwelais e")

    def test_sentences_with_nothing_to_suggest_give_no_groups(self) -> None:
        assert collect_suggestions(["Dw i'n dysgu"], INDEX, FixedLemmatiser({})) == ()

    def test_different_forms_are_separate_groups(self) -> None:
        lemmatiser = FixedLemmatiser({"Gwelais": ("gweld",), "Gwelodd": ("gweld",)})

        groups = collect_suggestions(["Gwelais", "Gwelodd"], INDEX, lemmatiser)

        assert [group.form for group in groups] == ["gwelais", "gwelodd"]


class TestRenderSuggestions:
    def test_group_shows_the_form_the_lexeme_and_where_it_was_seen(self) -> None:
        text = render_suggestions([GWELD_GROUP])

        assert text.startswith(
            "gwelais -> lex:gweld (to see)\n"
            "  forms: [gwelais]\n"
            "  lemma: gweld\n"
            "  seen in: Gwelais i\n"
            "  seen in: Gwelais e"
        )

    def test_mutation_is_mentioned(self) -> None:
        group = SuggestionGroup(
            form="gwela",
            item_id="lex:gweld",
            english="to see",
            lemma="gweld",
            mutation=Mutation.SOFT,
            sentences=("Wela i",),
        )

        assert "radical form of a soft mutation" in render_suggestions([group])

    def test_reminds_the_author_to_check(self) -> None:
        assert "check each suggestion" in render_suggestions([GWELD_GROUP])

    def test_no_groups(self) -> None:
        assert render_suggestions([]) == "No suggestions"


class TestMain:
    def test_requires_a_sentence(self) -> None:
        with pytest.raises(SystemExit, match="at least one sentence"):
            main([])

    def test_reads_sentences_from_a_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        sentences = tmp_path / "sentences.txt"
        sentences.write_text("Gwelais i\n\n  Gwelais e  \n", encoding="utf-8")
        seen: list[tuple[str, ...]] = []

        def fake_collect(
            sentences: tuple[str, ...], *_: object
        ) -> tuple[SuggestionGroup, ...]:
            seen.append(tuple(sentences))
            return ()

        monkeypatch.setattr(
            "tools.suggest_forms._build_lemmatiser", lambda _: FixedLemmatiser({})
        )
        monkeypatch.setattr("tools.suggest_forms.collect_suggestions", fake_collect)

        main(["Dw i", "--file", str(sentences)])

        assert seen == [("Dw i", "Gwelais i", "Gwelais e")]

    def test_missing_library_is_reported_as_a_clean_exit(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setitem(sys.modules, "stanza", None)

        with pytest.raises(SystemExit, match="poetry install --with lemmatisers"):
            main(["Gwelais i"])

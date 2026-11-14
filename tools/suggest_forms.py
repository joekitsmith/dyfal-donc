import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from cymraeg import (
    CymraegError,
    Lemmatiser,
    Mutation,
    SimplemmaLemmatiser,
    StanzaLemmatiser,
)
from engine.authoring import FormSuggestion, suggest_forms
from engine.curriculum import load_curriculum
from engine.detection import CurriculumIndex

REPOSITORY_ROOT = Path(__file__).parents[1]
CURRICULUM_DIRECTORY = REPOSITORY_ROOT / "curriculum"
LEMMATISER_NAMES = ("simplemma", "stanza")


@dataclass(frozen=True, slots=True, kw_only=True)
class SuggestionGroup:
    """One suggested form with every sentence it was suggested for."""

    form: str
    item_id: str
    english: str
    lemma: str
    mutation: Mutation | None
    sentences: tuple[str, ...]


def collect_suggestions(
    sentences: Sequence[str], index: CurriculumIndex, lemmatiser: Lemmatiser
) -> tuple[SuggestionGroup, ...]:
    """Suggest forms for each sentence, merging a form suggested more than once."""

    seen: dict[tuple[str, str], tuple[FormSuggestion, list[str]]] = {}
    for sentence in sentences:
        for suggestion in suggest_forms(sentence, index, lemmatiser):
            key = (suggestion.form, suggestion.item_id)
            first, sentences_seen = seen.setdefault(key, (suggestion, []))
            if sentence not in sentences_seen:
                sentences_seen.append(sentence)

    return tuple(
        SuggestionGroup(
            form=first.form,
            item_id=first.item_id,
            english=first.english,
            lemma=first.lemma,
            mutation=first.mutation,
            sentences=tuple(sentences_seen),
        )
        for first, sentences_seen in seen.values()
    )


def render_suggestions(groups: Sequence[SuggestionGroup]) -> str:
    """The suggestions as text an author can read and paste into ``lexemes.yaml``."""
    if not groups:
        return "No suggestions"

    blocks = [_render_group(group) for group in groups]
    footer = "Lemmatisers can be wrong: check each suggestion before declaring it."

    return "\n\n".join((*blocks, footer))


def main(argv: Sequence[str] | None = None) -> None:
    arguments = _build_parser().parse_args(argv)
    sentences = (
        *arguments.sentences,
        *(_read_sentences(Path(arguments.file)) if arguments.file else ()),
    )
    if not sentences:
        raise SystemExit("Give at least one sentence, or --file")

    try:
        lemmatiser = _build_lemmatiser(arguments.lemmatiser)
    except CymraegError as exc:
        raise SystemExit(str(exc)) from exc

    index = CurriculumIndex.from_curriculum(load_curriculum(CURRICULUM_DIRECTORY))
    print(render_suggestions(collect_suggestions(sentences, index, lemmatiser)))


def _render_group(group: SuggestionGroup) -> str:
    lines = [
        f"{group.form} -> {group.item_id} ({group.english})",
        f"  forms: [{group.form}]",
        f"  lemma: {group.lemma}",
    ]
    if group.mutation is not None:
        lines.append(f"  radical form of a {group.mutation.value} mutation")

    lines.extend(f"  seen in: {sentence}" for sentence in group.sentences)

    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="suggest-forms",
        description="Suggest forms to declare so unknown words in Welsh sentences are recognised.",
    )
    parser.add_argument("sentences", nargs="*", help="Welsh sentences to check")
    parser.add_argument("--file", help="a file with one Welsh sentence per line")
    parser.add_argument(
        "--lemmatiser",
        choices=LEMMATISER_NAMES,
        default="simplemma",
        help="which lemmatiser to ask (default: simplemma)",
    )

    return parser


def _read_sentences(path: Path) -> tuple[str, ...]:
    lines = path.read_text(encoding="utf-8").splitlines()

    return tuple(line.strip() for line in lines if line.strip())


def _build_lemmatiser(name: str) -> Lemmatiser:
    if name == "stanza":
        return StanzaLemmatiser()

    return SimplemmaLemmatiser()


if __name__ == "__main__":
    main()

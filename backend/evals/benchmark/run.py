from collections.abc import Mapping, Sequence
from importlib import metadata
from pathlib import Path
from time import perf_counter

from cymraeg import (
    CymraegError,
    DemutatingLemmatiser,
    Lemmatiser,
    RuleLemmatiser,
    SimplemmaLemmatiser,
    StanzaLemmatiser,
    tokenise,
)
from engine.curriculum import Curriculum, load_curriculum
from engine.detection import CurriculumIndex
from evals.benchmark.authoring import score_authoring
from evals.benchmark.combinations import AgreeingLemmatiser, EitherLemmatiser
from evals.benchmark.item_level import score_items
from evals.benchmark.lemma_level import score_lemmas
from evals.benchmark.models import (
    BenchmarkResult,
    LemmatiserResult,
    SentenceCandidates,
)
from evals.benchmark.report import render_report
from evals.gold import GoldSentence, load_gold_sentences

REPOSITORY_ROOT = Path(__file__).parents[3]
CURRICULUM_DIRECTORY = REPOSITORY_ROOT / "curriculum"
REPORT_PATH = Path(__file__).parents[1] / "reports" / "lemmatiser-benchmark.md"
RECOMMENDATION_PATH = Path(__file__).parent / "recommendation.md"
TIMING_REPEATS = 3


def run_benchmark(
    lemmatisers: Mapping[str, Lemmatiser],
    sentences: Sequence[GoldSentence],
    curriculum: Curriculum,
) -> BenchmarkResult:
    """Score every lemmatiser on the gold sentences, against declared forms only."""
    index = CurriculumIndex.from_curriculum(curriculum)

    return BenchmarkResult(
        sentences=len(sentences),
        tokens=sum(len(sentence.tokens) for sentence in sentences),
        declared_forms_only=score_items(sentences, index),
        lemmatisers=tuple(
            _score_lemmatiser(name, lemmatiser, sentences, index)
            for name, lemmatiser in lemmatisers.items()
        ),
    )


def build_lemmatisers() -> dict[str, Lemmatiser]:
    """Every lemmatiser to compare. Needs the optional ``lemmatisers`` group."""
    simplemma = SimplemmaLemmatiser()
    stanza = StanzaLemmatiser()

    return {
        "Rule (demutate)": RuleLemmatiser(),
        "Simplemma": simplemma,
        "Simplemma + demutate": DemutatingLemmatiser(simplemma),
        "Stanza": stanza,
        "Stanza + demutate": DemutatingLemmatiser(stanza),
        "Stanza and Simplemma agree": AgreeingLemmatiser(stanza, simplemma),
        "Stanza or Simplemma": EitherLemmatiser(stanza, simplemma),
    }


def main() -> None:
    try:
        lemmatisers = build_lemmatisers()
    except CymraegError as exc:
        raise SystemExit(str(exc)) from exc

    result = run_benchmark(
        lemmatisers, load_gold_sentences(), load_curriculum(CURRICULUM_DIRECTORY)
    )
    report = render_report(
        result,
        recommendation=RECOMMENDATION_PATH.read_text(encoding="utf-8"),
        environment={
            library: metadata.version(library) for library in ("simplemma", "stanza")
        },
    )
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {REPORT_PATH.relative_to(REPOSITORY_ROOT)}")


def _score_lemmatiser(
    name: str,
    lemmatiser: Lemmatiser,
    sentences: Sequence[GoldSentence],
    index: CurriculumIndex,
) -> LemmatiserResult:
    token_lists = tuple(tokenise(sentence.welsh) for sentence in sentences)
    # The first pass also warms the lemmatiser up before it is timed
    candidates: tuple[SentenceCandidates, ...] = tuple(
        lemmatiser.lemmatise(tokens) for tokens in token_lists
    )

    timings = []
    for _ in range(TIMING_REPEATS):
        start = perf_counter()
        for tokens in token_lists:
            lemmatiser.lemmatise(tokens)

        timings.append(perf_counter() - start)

    return LemmatiserResult(
        name=name,
        lemmas=score_lemmas(sentences, candidates),
        items=score_items(sentences, index, candidates),
        authoring=score_authoring(sentences, index, candidates),
        milliseconds_per_sentence=min(timings) / len(sentences) * 1000,
    )

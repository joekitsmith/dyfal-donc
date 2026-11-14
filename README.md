# dyfal-donc

```
Dyfal donc a dyrr y garreg
Persistent tapping breaks the stone
```

This course operates the same way: a little speaking each day, with each word coming back just before it fades.

A spaced-repetition Welsh speaking course (South Wales Welsh) with LLM-assisted, human-curated content. Each exercise follows the same loop: hear the English, say it in Welsh, then hear the Welsh.

**Work in progress.**

## Layout

- `core/`: the pure domain library. It must never import `backend`, and a unit test enforces it.
  - [`engine/`](core/engine/README.md): the course logic (no I/O beyond loading the curriculum)
  - [`cymraeg/`](core/cymraeg/README.md): rule-based Welsh handling (tokenising, mutations), independent of the engine
- `backend/`: everything that uses `core`: evaluation and authoring tools now, the API later
  - [`evals/`](backend/evals/README.md): hand-annotated gold sentences and the lemmatiser benchmark
  - [`tools/`](backend/tools/suggest_forms.py): command-line helpers for authors, such as `suggest-forms`
- [`curriculum/`](curriculum/README.md): hand-authored YAML seed data
- `tests/`: unit and integration tests, mirroring the package names

## Development

Requires Python 3.14 and Poetry.

```sh
poetry install
poetry run poe format      # ruff format
poetry run poe lint        # ruff check (lint-fix to apply fixes)
poetry run poe mypy
poetry run poe tests-unit
poetry run poe tests-integration
```

The Simplemma and Stanza lemmatisers are optional: `poetry install --with lemmatisers`. With them installed, `poetry run poe benchmark` regenerates the [lemmatiser benchmark](backend/evals/reports/lemmatiser-benchmark.md), and `poetry run poe suggest-forms "Gwelais i"` suggests forms to declare.

## Design decisions

- **The curriculum declares every form.** A word's plurals, inflections and variants are listed in `forms` in `curriculum/lexemes.yaml`, so validating an exercise is exact and curated: it accepts what a learner has been taught, and flags anything else as unknown.
- **Mutations are rules, inflection is data.** Undoing mutations is regular, so `cymraeg` does it by rule. Inflection is not regular enough to guess, so it is declared.
- **Lemmatisers suggest, people decide.** Simplemma and Stanza were [benchmarked](backend/evals/reports/lemmatiser-benchmark.md) on hand-written gold sentences. At about 90% lemma accuracy they find two thirds to 70% of the missing forms (`gwelais` as a form of `gweld`), and both also make mistakes: 9% of Stanza's suggestions and 25% of Simplemma's were wrong in the latest run. Using one inside validation would let those mistakes through silently on every check, so they only power `suggest-forms`. A person approves each suggestion and writes it into `forms`, where it is reviewed like any other change. The benchmark set is small and not yet reviewed by a fluent speaker, so the numbers show direction, not proof.
- **The engine stays pure.** It does no network or database work, and a lemmatiser is passed in rather than imported, so the optional libraries stay out of the default install and CI.
- **Quality and behaviour are measured separately.** `tests/fixtures` check that validation behaves correctly. `backend/evals/` scores how well the tools do, on sentences they were not tuned on.
- **South Wales Welsh.** Content uses southern forms (`moyn`, `e`, `heddi`), and alternatives go in `notes`.

Known limitations: mutated fixed words in a pattern are not matched, a pattern slot takes one word, a mutation is accepted without checking its trigger, and the pronoun `i` is read as the preposition.

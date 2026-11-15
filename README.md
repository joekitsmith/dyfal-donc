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
- `backend/`: everything that uses `core`: the API and its database, plus evaluation and authoring tools
  - [`api/`](backend/api/README.md): a FastAPI app that runs the learn loop (`poe api`)
  - [`persistence/`](backend/persistence/README.md): the Postgres layer for learners, issued exercises and the review-event log
  - [`evals/`](backend/evals/README.md): hand-annotated gold sentences and the lemmatiser benchmark
  - [`tools/`](backend/tools/suggest_forms.py): command-line helpers for authors, such as `suggest-forms`
  - [`simulation/`](backend/simulation/README.md): a seeded fake learner for tuning the scheduler and learner model (`poe simulate`)
- [`curriculum/`](curriculum/README.md): the course content as YAML: topics, lexemes, patterns and exercises
- `tests/`: unit and integration tests, mirroring the package names

## Development

Requires Python 3.14 and Poetry.

```sh
poetry install
poetry run poe format      # ruff format
poetry run poe lint        # ruff check (lint-fix to apply fixes)
poetry run poe mypy
poetry run poe tests-unit
poetry run poe tests-integration   # needs Docker: it starts a throwaway Postgres
```

To run the API with a database, copy `.env.example` to `.env`, then:

```sh
make db-up                 # Postgres in Docker; its data lives in a volume
poetry run poe db-create   # create the tables
poetry run poe api         # the API on http://localhost:8000 (docs at /docs)
make stack-up              # or run the API and Postgres together in Docker
make db-reset              # delete the volume and start with an empty database
```

The Simplemma and Stanza lemmatisers are optional: `poetry install --with lemmatisers`. With them installed, `poetry run poe benchmark` regenerates the [lemmatiser benchmark](backend/evals/reports/lemmatiser-benchmark.md), and `poetry run poe suggest-forms "Gwelais i"` suggests forms to declare.

## Design decisions

- **The curriculum declares every form.** A word's plurals, inflections and variants are listed in `forms` in `curriculum/lexemes/`, so validating an exercise is exact and curated: it accepts what a learner has been taught, and flags anything else as unknown.
- **Mutations are rules, inflection is data.** Undoing mutations is regular, so `cymraeg` does it by rule. Inflection is not regular enough to guess, so it is declared.
- **Lemmatisers suggest, people decide.** Simplemma and Stanza were [benchmarked](backend/evals/reports/lemmatiser-benchmark.md) on hand-written gold sentences. At about 90% lemma accuracy they find two thirds to 70% of the missing forms (`gwelais` as a form of `gweld`), and both also make mistakes: 9% of Stanza's suggestions and 25% of Simplemma's were wrong in the latest run. Using one inside validation would let those mistakes through silently on every check, so they only power `suggest-forms`. A person approves each suggestion and writes it into `forms`, where it is reviewed like any other change. The benchmark set is small and not yet reviewed by a fluent speaker, so the numbers show direction, not proof.
- **The engine stays pure.** It does no network or database work, and a lemmatiser is passed in rather than imported, so the optional libraries stay out of the default install and CI.
- **Each layer has its own types, and dependencies only point down.** The API imports persistence, and persistence never imports the engine. Boundary tests enforce it. The API turns requests into repository commands or engine types, and records and engine results into responses, in `api/mappings/`. A change to an engine model then costs a mapper edit, not a change to the database layer or the public API.
- **Learner state is replayed from an append-only event log.** The server issues each exercise and only accepts an outcome for one it issued, once, before it expires. Events get a per-learner sequence number under a row lock, and repeating an answer returns the original result.
- **Course content stays in versioned files.** The database holds learner data and the hash of the course release a learner started on, not the course.
- **Quality and behaviour are measured separately.** `tests/fixtures` check that validation behaves correctly. `backend/evals/` scores how well the tools do, on sentences they were not tuned on.
- **South Wales Welsh.** Content uses southern forms (`moyn`, `e`, `heddi`), and alternatives go in `notes`.

Known limitations: there is no authentication or database migrations yet (the schema is created from the models and can be rebuilt), a learner is not checked against the course release they started on, the Welsh in the corpus has not been reviewed by a fluent speaker, mutated fixed words in a pattern are not matched, a pattern slot takes one word, a mutation is accepted without checking its trigger, and the pronoun `i` is read as the preposition.

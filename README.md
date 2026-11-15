# dyfal-donc

```
Dyfal donc a dyrr y garreg
Persistent tapping breaks the stone
```

This course operates the same way: a little speaking each day, with each word coming back just before it fades.

A spaced-repetition Welsh speaking course (South Wales Welsh) with LLM-assisted, human-curated content. Each exercise follows the same loop: hear the English, say it in Welsh, then hear the Welsh.

## Layout

- `core/`: the pure domain library. It must never import `backend`, and a unit test enforces it.
  - [`engine/`](core/engine/README.md): the course logic
  - [`cymraeg/`](core/cymraeg/README.md): rule-based Welsh handling, independent of the engine
- `backend/`: everything that uses `core`
  - [`api/`](backend/api/README.md): a FastAPI app that runs the learn loop
  - [`persistence/`](backend/persistence/README.md): the Postgres layer
  - [`tts/`](backend/tts/README.md): the speech service
  - [`evals/`](backend/evals/README.md): gold sentences and the lemmatiser benchmark
  - [`simulation/`](backend/simulation/README.md): a seeded fake learner
  - [`tools/`](backend/tools/suggest_forms.py): command-line helpers for authors
- [`curriculum/`](curriculum/README.md): the course content as YAML
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
make tts-up                # the speech service on localhost:8001, for audio
make stack-up              # or run the API, Postgres and speech together in Docker
make db-reset              # delete the volume and start with an empty database
```

The Simplemma and Stanza lemmatisers are optional: `poetry install --with lemmatisers`.

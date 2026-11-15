# dyfal-donc

```
Dyfal donc a dyrr y garreg
Persistent tapping breaks the stone
```

This course operates the same way: a little speaking each day, with each word coming back just before it fades.

A spaced-repetition Welsh speaking course (South Wales Welsh) with LLM-assisted, human-curated content. Each exercise follows the same loop: hear the English, say it in Welsh, then hear the Welsh.

## Quickstart

Needs Docker, Python 3.14 with Poetry, and Node 26 with pnpm (setup in [`frontend/`](frontend/README.md)).

```sh
cp .env.example .env
poetry install
make stack-up              # the API, Postgres and the speech service in Docker
poetry run poe db-create   # in another terminal, the first time: create the tables
make web-dev               # the lesson player on http://localhost:3000
```

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
- [`frontend/`](frontend/README.md): the lesson player, a Next.js app
- [`curriculum/`](curriculum/README.md): the course content as YAML
- `tests/`: unit and integration tests, mirroring the package names

## Development

```sh
poetry install
poetry run poe format      # ruff format
poetry run poe lint        # ruff check (lint-fix to apply fixes)
poetry run poe mypy
poetry run poe tests-unit
poetry run poe tests-integration   # needs Docker: it starts a throwaway Postgres
make web-check             # the frontend's checks
make web-e2e               # the frontend's browser tests, with the stack running
```

Run the parts yourself instead of `make stack-up`:

```sh
make db-up                 # Postgres in Docker; its data lives in a volume
poetry run poe db-create   # create the tables that are missing (safe to repeat)
make tts-up                # the speech service on localhost:8001, for audio
poetry run poe api         # the API on http://localhost:8000 (docs at /docs)
make web-dev               # the lesson player on http://localhost:3000
```

Start again with an empty database (for example after changing a table). This does the `db-up` and `db-create` steps itself:

```sh
make db-reset              # delete the volume, then start empty with the tables created
```

The Simplemma and Stanza lemmatisers are optional: `poetry install --with lemmatisers`.

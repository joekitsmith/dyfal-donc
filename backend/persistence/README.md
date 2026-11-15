# persistence

Where the app keeps what is not course content, which stays in the files under `curriculum/`.

## `persistence.database`

Postgres, through SQLAlchemy 2 (sync, psycopg 3). The tables are in `models/`: users, their passkeys, login sessions and passkey challenges; learners (one per user), the exercises issued to them, and the append-only log of review events that a learner's state is replayed from. Deleting a user deletes everything that belongs to them. The docstrings and constraints there say what each guarantees.

- `models/`: the tables. Private to this package.
- `commands/`: what the repositories are told to do, each carrying everything needed. Methods that change data take one command, and reads take ids.
- `records/`: what comes back. Callers never hold a table object.
- `mappings/`: table row to record.
- `repositories/`: what the API calls. They never commit, so the caller decides what happens in one transaction (`unit_of_work.py`).

Commands and records are plain frozen dataclasses. This package imports nothing from the engine, and the API never imports `models` or `mappings`. Boundary tests check both.

The tables are created from the models. `create_schema` never alters a table that exists, so after changing a model, run `make db-reset`.

Copy `.env.example` to `.env` first: Docker Compose and the app both read it. `DATABASE_URL` is required.

```
make db-up      # Postgres in Docker (its data lives in a volume)
poe db-create   # create the tables that are missing
make db-reset   # delete the volume, then start empty with the tables created
make db-down    # stop it, keeping the data
```

The integration tests start their own throwaway Postgres with testcontainers, so they need Docker and never touch the development database.

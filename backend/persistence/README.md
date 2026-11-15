# persistence

Where the app keeps what is not course content. The course itself stays in the versioned files under `curriculum/`.

## `persistence.database`

Postgres, through SQLAlchemy 2 (sync, psycopg 3). There are no migrations yet: nothing is deployed, so the tables are created from the models and the database can be thrown away and rebuilt. When data first matters, add Alembic and generate the baseline from the models.

- `learners`: who is learning, and the course release (a hash of `curriculum/`) they started on.
- `issued_selections`: every exercise the server gave a learner, with when it was issued, when it expires and when it was answered. Outcomes are only accepted for selections issued here.
- `review_events`: the append-only log the learner's state is replayed from. `(learner_id, sequence)` is unique, and so is `selection_id`, so an outcome is recorded at most once and events keep their order.

Layout:

- `models/`: the tables (`Learner`, `IssuedSelection`, `ReviewEvent`). Private to this package: only the repositories, the mappings and `create_schema` use them.
- `commands/`: what the repositories are told to do, each carrying everything needed to do it, as plain frozen dataclasses: `AddLearner`, `IssueSelection`, `ConsumeSelection` and `AppendEvent`. Methods that change data take one command. Reads take ids.
- `records/`: what comes back, as plain frozen dataclasses (strings, tuples, datetimes): `LearnerRecord`, `IssuedSelectionRecord` and `EventRecord`. Callers never hold a table object.
- `mappings/`: table row to record, with times converted to UTC.
- `repositories/`: what the API calls. They never commit, so the caller decides what happens in one transaction. Appending an event locks the learner's row, so sequence numbers have no gaps, and answering a selection locks it, so an outcome is recorded once.

This package imports nothing from the engine, and the API never imports `models` or `mappings`. Boundary tests check both. The API's own mappings translate between its types, the engine's and these records, so a change to the engine's models costs a mapper edit here, not a change to the database layer.

`create_schema` never alters a table that already exists, so after changing a model, run `make db-reset`.

Copy `.env.example` to `.env` first. Docker Compose and the app both read it, so the database user, password and URL are written once.

```
make db-up      # Postgres in Docker (its data lives in a volume)
poe db-create   # create the tables that are missing
make db-reset   # delete the volume, then start empty with the tables created
make db-down    # stop it, keeping the data
```

`DATABASE_URL` says where the database is, and has no default, so a missing one is an error. The integration tests start their own throwaway Postgres with testcontainers, so they need Docker and never touch the development database.

Audio storage will go in `persistence.audio` when text-to-speech is added.

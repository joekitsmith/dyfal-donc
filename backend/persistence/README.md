# persistence

Where the app keeps what is not course content. The course itself stays in the versioned files under `curriculum/`.

## `persistence.database`

Postgres, through SQLAlchemy 2 (sync, psycopg 3). There are no migrations yet: nothing is deployed, so the tables are created from the models and the database can be thrown away and rebuilt. When data first matters, add Alembic and generate the baseline from the models.

- `learners`: who is learning, and the course release (a hash of `curriculum/`) they started on.
- `issued_selections`: every exercise the server gave a learner, with when it was issued, when it expires and when it was answered. Outcomes are only accepted for selections issued here.
- `review_events`: the append-only log the learner's state is replayed from. `(learner_id, sequence)` is unique, and so is `selection_id`, so an outcome is recorded at most once and events keep their order.

This is a skeleton: the tables and constraints exist, and there are no repositories yet. `create_schema` never alters a table that already exists, so after changing a model, run `make db-reset`.

Copy `.env.example` to `.env` first. Docker Compose and the app both read it, so the database user, password and URL are written once.

```
make db-up      # Postgres in Docker (its data lives in a volume)
poe db-create   # create the tables that are missing
make db-reset   # delete the volume, then start empty with the tables created
make db-down    # stop it, keeping the data
```

`DATABASE_URL` says where the database is, and has no default, so a missing one is an error. The integration tests start their own throwaway Postgres with testcontainers, so they need Docker and never touch the development database.

Audio storage will go in `persistence.audio` when text-to-speech is added.

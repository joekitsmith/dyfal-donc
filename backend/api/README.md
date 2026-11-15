# api

A FastAPI app. It loads the course release from `curriculum/` at startup, and `GET /course` reports its hash, item count and topics. There is also `GET /health`. The learner endpoints are not built yet.

```
poe api         # run locally with reload
make stack-up   # the API and Postgres in Docker Compose
```

`CURRICULUM_DIRECTORY` and `DATABASE_URL` configure it (copy `.env.example` to `.env`; `DATABASE_URL` is required). The database is not touched until something uses it, so `/health` and `/course` work without one. There is no authentication yet.

## Layout

- `routes/`: the paths. They only deal with HTTP: status codes, and injecting dependencies.
- `controllers/`: plain functions from request data to the domain and back to a response schema. They never import FastAPI, so they are tested without HTTP.
- `schemas/`: the Pydantic request and response models, which are the OpenAPI contract.
- `dependencies/`: what routes need injected (the course release now, a database session later).
- `course.py`: loads the course release and hashes its files. Controllers use it.

A route with no logic, like `/health`, has no controller.

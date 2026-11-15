# api

A FastAPI app that runs the learn loop. It loads the course release (the curriculum and exercises under `curriculum/`, identified by a hash of their files) at startup.

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness. |
| `GET /course` | The release hash, item count and topics. |
| `POST /learners` | Creates a learner on the current release. |
| `GET /learners/{id}/next` | Chooses the next exercise with the scheduler and the server clock, remembers it as issued, and returns the English, Welsh, item ids and a `selection_id`. When nothing can be offered it returns `kind: nothing_eligible` and why, not an error. |
| `POST /learners/{id}/outcomes` | Takes the `selection_id` and `got_it` or `missed_it`, and appends the event. Only selections the server issued are accepted, and each can be answered once. Repeating the same outcome returns the original result (`recorded: false`). |
| `GET /learners/{id}/progress` | Items introduced, learning and in review, how many are due, and the recent error rate. |

Errors: an unknown learner or selection is 404, an expired selection is 410, and a second, different outcome for an answered selection is 409. The server's clock supplies every timestamp.

Known limitations: there is no authentication (the learner id in the path is enough for a local demo), and a learner is not checked against the course release they started on, so changing the curriculum under an existing learner is unsafe.

```
poe api         # run locally with reload
make stack-up   # the API and Postgres in Docker Compose
```

`CURRICULUM_DIRECTORY`, `SELECTION_LIFETIME_SECONDS` (default an hour) and `DATABASE_URL` configure it (copy `.env.example` to `.env`; `DATABASE_URL` is required). The database is not touched until something uses it, so `/health` and `/course` work without one.

## Layout

- `routes/`: the paths. They only deal with HTTP: status codes, and injecting dependencies.
- `controllers/`: coordinate the repositories and the engine to achieve one endpoint's goal: map the request in, do the work, map the result out. They never import FastAPI, so they do not depend on the web framework.
- `mappings/`: every conversion at this boundary. Request (and server-side data such as the time) to a persistence input record or an engine type, and records or engine results to response schemas. The API keeps its own enums, so the OpenAPI contract does not change when the engine's models do, and tests fail when the two drift apart.
- `schemas/`: the Pydantic request and response models, which are the OpenAPI contract. They import nothing from the engine or persistence.
- `dependencies/`: what routes need injected: the course release, a unit of work per request, the clock and the selection lifetime.
- `course.py`: loads the course release and hashes its files. Controllers use it.

A route with no logic, like `/health`, has no controller.

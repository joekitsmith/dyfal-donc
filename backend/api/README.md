# api

A FastAPI app that runs the learn loop. It loads the course release (the files under `curriculum/`, identified by a hash of them) at startup. The endpoints and their schemas are in the generated OpenAPI docs at `/docs`.

```
poe api         # run locally with reload
make stack-up   # the API and Postgres in Docker Compose
```

`CURRICULUM_DIRECTORY`, `SELECTION_LIFETIME_SECONDS` and `DATABASE_URL` (required) configure it, from the environment or `.env`: see `settings.py`.

## Layout

- `routes/`: the paths. HTTP only: status codes and injected dependencies.
- `controllers/`: coordinate the repositories and the engine for one endpoint: map the request in, do the work, map the result out. They never import FastAPI.
- `mappings/`: every conversion at this boundary, between the request and response schemas, the engine's types and persistence's commands and records.
- `schemas/`: the request and response models, which are the OpenAPI contract. They have their own enums and import nothing from the engine or persistence, so the contract does not change when the engine's models do.
- `dependencies/`: what routes need injected: the course release, a unit of work per request, the clock and the selection lifetime.
- `error_handlers.py`: which errors become which status codes.
- `course.py`: loads the course release and hashes its files.

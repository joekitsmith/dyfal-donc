# api

A FastAPI app that runs the learn loop. It loads the course release (the files under `curriculum/`, identified by a hash of them) at startup. The endpoints and their schemas are in the generated OpenAPI docs at `/docs`.

```
poe api         # run locally with reload
make stack-up   # the whole stack in Docker Compose, behind nginx (make stack-up-debug also publishes the API on localhost:8000)
```

`CURRICULUM_DIRECTORY`, `SELECTION_LIFETIME_SECONDS`, `TTS_URL` and `DATABASE_URL` (required) configure it, as do `WEBAUTHN_RP_ID`, `WEBAUTHN_RP_NAME`, `WEBAUTHN_ORIGINS` (comma-separated), `SESSION_COOKIE_SECURE` and `SESSION_LIFETIME_SECONDS`, from the environment or `.env`: see `settings.py`.

A browser starts as a guest (`POST /auth/guest`) and can add a passkey later to keep its progress. The learner's routes are under `/me` and need the session cookie. Requests that change something must carry an `Origin` the app is served from.

## Layout

- `routes/`: the paths. HTTP only: status codes and injected dependencies.
- `controllers/`: coordinate the repositories and the engine for one endpoint: map the request in, do the work, map the result out. They never import FastAPI.
- `mappings/`: every conversion at this boundary, between the request and response schemas, the engine's types and persistence's commands and records.
- `schemas/`: the request and response models, which are the OpenAPI contract. They have their own enums and import nothing from the engine or persistence, so the contract does not change when the engine's models do.
- `dependencies/`: what routes need injected: the course release, a unit of work per request, the clock, the selection lifetime and the speech client.
- `passkeys.py`, `tokens.py`, `login_sessions.py`: the sign-in logic with no web framework or database in it: the WebAuthn ceremonies, the session token and its hash, and when a session expires. A boundary test keeps them that way. `session_cookie.py` sets the cookie.
- `speech.py`: the client for the `tts` service. It speaks only course text, so clients never send any.
- `error_handlers.py`: which errors become which status codes.
- `course.py`: loads the course release and hashes its files.

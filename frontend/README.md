# frontend

The lesson player, a Next.js app that talks to the API only through its `/api` proxy.

Needs Node 26 and pnpm, once per machine:

```
nvm install && nvm use          # reads .nvmrc
npm install -g corepack         # Node 26 no longer bundles it
corepack enable                 # pnpm then installs at the version in package.json
cd frontend && pnpm install
```

Then:

```
make web-dev     # on localhost:3000, with the API on localhost:8000 (make stack-up-debug)
make web-check   # lint, types, formatting, tests, generated-types drift, unused code
make web-e2e     # the browser tests in e2e/, against the stack on make stack-up
make web-build   # the Docker image
make web-types   # regenerate openapi.json and the API types after changing the API
```

In `make web-dev`, `API_URL` says where `/api` is proxied to (default `http://localhost:8000`). In Docker, nginx does that, so the image has no API address in it.

## Layout

- `src/app/`: routes and providers. Nothing else.
- `src/features/<name>/`: one feature, with its own `api/` (requests and their react-query hooks), `components/`, `hooks/`, `constants.ts` and page. Other code imports it only through `index.ts`.
- `src/api/`, `components/`, `config/`, `hooks/`, `theme/`, `types/`, `utils/`: shared code. It never imports a feature.
- `tests/`: mirrors `src/`.
- `e2e/`: Playwright tests that drive the player against the running stack. Install the browser once with `pnpm exec playwright install chromium`.

ESLint enforces these boundaries.

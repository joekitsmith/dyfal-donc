# frontend

The lesson player, a Next.js app that talks to the API only through its `/api` proxy.

```
make web-dev     # on localhost:3000, with the API running (make stack-up)
make web-check   # lint, types, formatting, tests, generated-types drift, unused code
make web-types   # regenerate openapi.json and the API types after changing the API
```

`API_URL` (see `.env.example`) says where `/api` is proxied to.

## Layout

- `src/app/`: routes and providers. Nothing else.
- `src/features/<name>/`: one feature, with its own `api/` (requests and their react-query hooks), `components/`, `hooks/`, `constants.ts` and page. Other code imports it only through `index.ts`.
- `src/api/`, `components/`, `config/`, `hooks/`, `theme/`, `types/`, `utils/`: shared code. It never imports a feature.
- `tests/`: mirrors `src/`.

ESLint enforces these boundaries.

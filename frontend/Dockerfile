# syntax=docker/dockerfile:1
FROM node:26-slim AS base

ENV npm_config_store_dir=/pnpm/store \
    NEXT_TELEMETRY_DISABLED=1

# Node 26 no longer bundles Corepack, which installs the pnpm version in package.json
RUN npm install --global corepack && corepack enable

WORKDIR /app


FROM base AS dependencies

COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store \
    pnpm install --frozen-lockfile


FROM dependencies AS build

COPY . .
RUN pnpm build


FROM node:26-slim AS run

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    HOSTNAME=0.0.0.0 \
    PORT=3000

WORKDIR /app

COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public

USER node

EXPOSE 3000
CMD ["node", "server.js"]

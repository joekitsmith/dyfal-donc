.PHONY: db-up db-down db-reset tts-build tts-up stack-up stack-up-debug stack-down stack-logs web-build web-build-multiarch web-dev web-check web-e2e web-types tunnel tunnel-down

WEB_PORT ?= 8080
TUNNEL_LOG = .tunnel.log
TUNNEL_PID = .tunnel.pid
LOCAL_ORIGINS = http://localhost:$(WEB_PORT),http://localhost:3000
DEBUG_COMPOSE = docker compose --file compose.yaml --file compose.debug.yaml

# Postgres on localhost:POSTGRES_PORT, for poe and psql
db-up:
	$(DEBUG_COMPOSE) up --detach --wait postgres

db-down:
	$(DEBUG_COMPOSE) down

# Deletes the database volume, then starts an empty database with its tables
db-reset:
	$(DEBUG_COMPOSE) down --volumes
	$(MAKE) db-up
	poetry run poe db-create

tts-build:
	docker compose build tts

# Starts the speech service on localhost:TTS_PORT, so `poe api` can reach it
tts-up:
	$(DEBUG_COMPOSE) up --build --detach --wait tts

# Everything in Docker, reached through nginx on http://localhost:WEB_PORT
stack-up:
	docker compose up --build --detach --wait
	@echo "Ready on http://localhost:$(WEB_PORT)"

# The same, with the API, Postgres and speech service also on their own ports, for make web-dev
stack-up-debug:
	$(DEBUG_COMPOSE) up --build --detach --wait

stack-down:
	$(DEBUG_COMPOSE) down

stack-logs:
	docker compose logs --follow

web-build:
	docker compose build web

# Checks that the web image builds for the Raspberry Pi as well as for x86 machines. Nothing is published
web-build-multiarch:
	docker buildx build --platform linux/amd64,linux/arm64 frontend

# The lesson player on localhost:3000, proxying /api to API_URL (default localhost:8000, so make stack-up-debug first)
web-dev:
	cd frontend && pnpm dev

web-check:
	cd frontend && pnpm check

# Drives the lesson player in a browser through nginx. Needs the stack running (make stack-up) and Chromium installed
web-e2e:
	cd frontend && WEB_URL=http://localhost:$(WEB_PORT) pnpm e2e

# Regenerates the API's OpenAPI schema and the frontend's types from it
web-types:
	poetry run poe openapi
	cd frontend && pnpm types

# Puts the running stack on a public https address (a Cloudflare quick tunnel), so a phone can reach it.
# The address is random, so the API is recreated to accept it as an origin and as the passkeys' domain
# (a passkey made through the tunnel stops working when the address changes). Needs: brew install cloudflared
tunnel:
	@command -v cloudflared >/dev/null || { echo "Install cloudflared first: brew install cloudflared"; exit 1; }
	@test ! -f $(TUNNEL_PID) || { echo "A tunnel is already running: make tunnel-down first"; exit 1; }
	@cloudflared tunnel --url http://localhost:$(WEB_PORT) > $(TUNNEL_LOG) 2>&1 & echo $$! > $(TUNNEL_PID)
	@url=""; for attempt in $$(seq 1 30); do \
		url=$$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' $(TUNNEL_LOG) | head -1); \
		test -z "$$url" || break; sleep 1; \
	done; \
	test -n "$$url" || { echo "No tunnel address in $(TUNNEL_LOG)"; $(MAKE) tunnel-down; exit 1; }; \
	WEBAUTHN_RP_ID=$${url#https://} WEBAUTHN_ORIGINS="$(LOCAL_ORIGINS),$$url" docker compose up --detach --wait --no-deps api; \
	caffeinate -i -w $$(cat $(TUNNEL_PID)) & \
	echo "Open $$url/spike/hands-free.html on the phone (the Mac stays awake while the tunnel runs)"

# Stops the tunnel and puts the API's allowed origins back
tunnel-down:
	@test ! -f $(TUNNEL_PID) || kill $$(cat $(TUNNEL_PID)) 2>/dev/null || true
	@$(RM) $(TUNNEL_PID) $(TUNNEL_LOG)
	docker compose up --detach --wait --no-deps api

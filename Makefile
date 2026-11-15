.PHONY: db-up db-down db-reset tts-build tts-up stack-up stack-down web-dev web-check web-types

db-up:
	docker compose up --detach --wait postgres

db-down:
	docker compose down

# Deletes the database volume, then starts an empty database with its tables
db-reset:
	docker compose down --volumes
	$(MAKE) db-up
	poetry run poe db-create

tts-build:
	docker compose build tts

# Starts the speech service on localhost:TTS_PORT, so `poe api` can reach it
tts-up:
	docker compose up --build --detach --wait tts

stack-up:
	docker compose up --build

stack-down:
	docker compose down

# The lesson player on localhost:3000, proxying /api to API_URL (default localhost:8000)
web-dev:
	cd frontend && pnpm dev

web-check:
	cd frontend && pnpm check

# Regenerates the API's OpenAPI schema and the frontend's types from it
web-types:
	poetry run poe openapi
	cd frontend && pnpm types
